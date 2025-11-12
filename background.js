// Background service worker for content capture and processing

const BACKEND_URL = 'http://localhost:8000';
const USE_BACKEND = true; // Set to false to use simplified local embeddings

const EXCLUDED_DOMAINS = [
    'mail.google.com',
    'web.whatsapp.com',
    'accounts.google.com',
    'login.',
    'signin.',
    'auth.',
    'localhost:8000'
];

const CATEGORY_PATTERNS = {
    ecommerce: ['amazon', 'ebay', 'shopify', 'shop', 'cart', 'product', 'buy', 'price', 'store'],
    social: ['facebook', 'twitter', 'instagram', 'linkedin', 'reddit', 'tiktok'],
    news: ['news', 'article', 'blog', 'post', 'medium'],
    documentation: ['docs', 'documentation', 'api', 'reference', 'guide', 'github'],
    video: ['youtube', 'vimeo', 'video', 'watch', 'netflix']
};

// Check if URL should be excluded
function shouldExclude(url) {
    return EXCLUDED_DOMAINS.some(domain => url.includes(domain));
}

// Categorize website based on URL and content
function categorizeWebsite(url, content) {
    const urlLower = url.toLowerCase();
    const contentLower = content.toLowerCase();

    for (const [category, patterns] of Object.entries(CATEGORY_PATTERNS)) {
        const matches = patterns.filter(pattern =>
            urlLower.includes(pattern) || contentLower.includes(pattern)
        );
        if (matches.length >= 2) {
            return category;
        }
    }
    return 'general';
}

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('📨 Background received message:', message.type);
    
    if (message.type === 'CAPTURE_CONTENT') {
        handleContentCapture(message.data, sender.tab);
    } else if (message.type === 'SEARCH_CONTENT') {
        console.log('🔍 Search request:', message.query, 'category:', message.category);
        handleSearch(message.query, message.category).then(sendResponse);
        return true;
    } else if (message.type === 'COMPARE_PRODUCTS') {
        handleProductComparison(message.query).then(sendResponse);
        return true;
    } else if (message.type === 'GET_STATS') {
        getStats().then(sendResponse);
        return true;
    } else if (message.type === 'CHECK_BACKEND') {
        checkBackendHealth().then(sendResponse);
        return true;
    } else if (message.type === 'SCHEDULE_HIGHLIGHT') {
        console.log('🎯 SCHEDULE_HIGHLIGHT received!', 'tabId:', message.tabId, 'text:', message.text);
        handleScheduledHighlight(message.tabId, message.text, message.url);
    } else if (message.type === 'OPEN_AND_HIGHLIGHT') {
        console.log('🎯 OPEN_AND_HIGHLIGHT received!', 'url:', message.url, 'text:', message.text);
        handleOpenAndHighlight(message.url, message.text);
        sendResponse({ success: true });
    }
});

// Handle open and highlight request from popup
async function handleOpenAndHighlight(url, text) {
    console.log('🚀 Opening URL:', url);
    console.log('🔍 Search query:', text);
    
    try {
        // Check if tab already exists
        const tabs = await chrome.tabs.query({ url: url });
        
        if (tabs.length > 0) {
            // Tab exists, activate it
            const tab = tabs[0];
            await chrome.tabs.update(tab.id, { active: true });
            console.log('✅ Existing tab activated:', tab.id);
            
            // Highlight immediately
            setTimeout(() => {
                handleScheduledHighlight(tab.id, text, url);
            }, 500);
        } else {
            // Create new tab
            const tab = await chrome.tabs.create({ url: url });
            console.log('✅ New tab created:', tab.id);
            
            // Schedule highlight
            handleScheduledHighlight(tab.id, text, url);
        }
    } catch (error) {
        console.error('❌ Error in handleOpenAndHighlight:', error);
    }
}

// Handle scheduled highlight for new tabs
async function handleScheduledHighlight(tabId, text, url) {
    console.log('📅 Scheduled highlight for tab:', tabId, 'query:', text);
    
    // Function to execute the highlight
    const executeHighlight = async () => {
        console.log('🎯 Executing highlight for tab:', tabId);
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: highlightTextInPage,
                args: [text]
            });
            console.log('✅ Highlight script executed successfully');
        } catch (error) {
            console.error('❌ Failed to execute highlight script:', error);
        }
    };
    
    // First, check if the tab is already loaded
    try {
        const tab = await chrome.tabs.get(tabId);
        console.log('📊 Tab status:', tab.status, 'URL:', tab.url);
        
        if (tab.status === 'complete') {
            // Tab already loaded, execute immediately
            console.log('✅ Tab already loaded, executing highlight now');
            setTimeout(executeHighlight, 1000);
            return;
        }
    } catch (error) {
        console.error('❌ Error getting tab:', error);
    }
    
    // Tab not loaded yet, wait for it
    console.log('⏳ Waiting for tab to load...');
    const listener = async (updatedTabId, changeInfo, tab) => {
        if (updatedTabId === tabId) {
            console.log(`📊 Tab ${tabId} update:`, changeInfo.status);
            
            if (changeInfo.status === 'complete') {
                console.log('✅ Page loaded completely');
                chrome.tabs.onUpdated.removeListener(listener);
                
                // Wait a moment for page to settle
                setTimeout(executeHighlight, 1000);
            }
        }
    };
    
    chrome.tabs.onUpdated.addListener(listener);
    
    // Cleanup after 20 seconds
    setTimeout(() => {
        chrome.tabs.onUpdated.removeListener(listener);
        console.log('⏱️ Highlight listener cleaned up');
    }, 20000);
}

// Function that will be injected into the page to highlight text
function highlightTextInPage(searchQuery) {
    console.log('🎨 Highlighting in page:', searchQuery);
    
    // Remove old highlights first
    document.querySelectorAll('.web-memory-highlight').forEach(el => {
        const text = document.createTextNode(el.textContent);
        el.parentNode.replaceChild(text, el);
    });
    
    // Normalize the search query
    const queryLower = searchQuery.toLowerCase().trim();
    if (!queryLower) {
        console.log('Empty query, nothing to highlight');
        return;
    }
    
    // Extract meaningful words (5+ characters to avoid common words)
    const words = queryLower.match(/\b\w{5,}\b/g) || [];
    console.log('Looking for words:', words);
    
    if (words.length === 0) {
        console.log('No significant words to highlight');
        return;
    }
    
    // Limit to top 5 most distinctive words to avoid over-highlighting
    const distinctiveWords = words.slice(0, 5);
    console.log('Using distinctive words:', distinctiveWords);
    
    // Find text nodes that contain at least 2 of the search words (or 1 if only 1 word)
    const minMatches = distinctiveWords.length === 1 ? 1 : 2;
    
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                if (node.parentElement.tagName === 'SCRIPT' || 
                    node.parentElement.tagName === 'STYLE' ||
                    node.parentElement.tagName === 'NOSCRIPT' ||
                    node.parentElement.classList.contains('web-memory-highlight') ||
                    !node.textContent.trim()) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );
    
    const nodesToHighlight = [];
    let node;
    
    while (node = walker.nextNode()) {
        const textLower = node.textContent.toLowerCase();
        
        // Count how many search words appear in this node
        const matchCount = distinctiveWords.filter(word => textLower.includes(word)).length;
        
        if (matchCount >= minMatches) {
            nodesToHighlight.push({
                node: node,
                matchCount: matchCount
            });
        }
    }
    
    // Sort by match count (highest first) and limit to top 20 nodes
    nodesToHighlight.sort((a, b) => b.matchCount - a.matchCount);
    const topNodes = nodesToHighlight.slice(0, 20);
    
    console.log(`Found ${nodesToHighlight.length} matching nodes, highlighting top ${topNodes.length}`);
    
    // Highlight the top matching nodes
    let firstHighlight = null;
    topNodes.forEach(({ node, matchCount }) => {
        try {
            const span = document.createElement('span');
            span.className = 'web-memory-highlight';
            span.style.backgroundColor = '#ffeb3b';
            span.style.padding = '2px 4px';
            span.style.borderRadius = '3px';
            span.style.boxShadow = '0 0 0 2px rgba(255, 235, 59, 0.3)';
            span.textContent = node.textContent;
            
            if (node.parentNode) {
                node.parentNode.replaceChild(span, node);
                if (!firstHighlight) {
                    firstHighlight = span;
                }
            }
        } catch (error) {
            console.error('Error highlighting node:', error);
        }
    });
    
    // Scroll to first highlight
    if (firstHighlight) {
        setTimeout(() => {
            firstHighlight.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center'
            });
            console.log('✅ Scrolled to first highlight');
        }, 100);
    } else {
        console.log('⚠️ No highlights created');
    }
}

// Handle content capture
async function handleContentCapture(data, tab) {
    if (!tab || shouldExclude(tab.url)) {
        console.log('⏭️  Skipping excluded URL:', tab?.url);
        return;
    }

    console.log('📄 Processing page:', tab.title);
    console.log('🔗 URL:', tab.url);
    console.log('📊 Content length:', data.content.length, 'characters');
    console.log('📦 Chunks:', data.chunks.length);

    const category = categorizeWebsite(tab.url, data.content);
    console.log('🏷️  Category:', category);

    const pageData = {
        url: tab.url,
        title: data.title,
        content: data.content,
        chunks: data.chunks,
        timestamp: Date.now(),
        category: category,
        favicon: tab.favIconUrl
    };

    // Get embeddings for chunks
    console.log('🧮 Generating embeddings for', data.chunks.length, 'chunks...');
    const embeddings = await getEmbeddings(data.chunks);
    pageData.embeddings = embeddings;
    console.log('✅ Embeddings generated:', embeddings.length, 'vectors');

    // Store in Chrome storage
    console.log('💾 Storing in FAISS...');
    await storePageData(pageData);

    console.log(`✅ Captured: ${tab.url} [${category}]`);
    console.log('─'.repeat(80));
}

// Store page data with FAISS backend or local storage
async function storePageData(pageData) {
    const { url, embeddings, chunks, ...metadata } = pageData;

    if (USE_BACKEND) {
        try {
            console.log('📤 Sending to FAISS backend...');
            // Send to FAISS backend
            const response = await fetch(`${BACKEND_URL}/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    embeddings: embeddings,
                    metadata: chunks.map((chunk, i) => ({
                        url,
                        chunk,
                        chunkIndex: i,
                        title: metadata.title,
                        category: metadata.category,
                        favicon: metadata.favicon,
                        timestamp: metadata.timestamp
                    }))
                })
            });

            if (!response.ok) throw new Error('Backend storage failed');

            const result = await response.json();
            console.log(`✅ FAISS indexed: ${result.added} chunks`);
            console.log(`📊 Total vectors in FAISS: ${result.total_vectors}`);
        } catch (error) {
            console.error('❌ Backend storage error, falling back to local:', error);
            await storePageDataLocal(pageData);
        }
    } else {
        console.log('💾 Storing locally...');
        await storePageDataLocal(pageData);
    }

    // Always update local index for quick stats
    await updateIndex(url, metadata.category);
    console.log('✅ Local index updated');
}

// Local storage fallback
async function storePageDataLocal(pageData) {
    const { url, embeddings, chunks, ...metadata } = pageData;

    const metadataKey = `meta_${hashUrl(url)}`;
    await chrome.storage.local.set({ [metadataKey]: metadata });

    for (let i = 0; i < chunks.length; i++) {
        const chunkKey = `chunk_${hashUrl(url)}_${i}`;
        await chrome.storage.local.set({
            [chunkKey]: {
                text: chunks[i],
                embedding: embeddings[i],
                url: url,
                chunkIndex: i
            }
        });
    }
}

// Simple URL hashing
function hashUrl(url) {
    let hash = 0;
    for (let i = 0; i < url.length; i++) {
        const char = url.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
}

// Update search index
async function updateIndex(url, category) {
    const result = await chrome.storage.local.get(['urlIndex', 'categoryIndex']);

    const urlIndex = result.urlIndex || [];
    const categoryIndex = result.categoryIndex || {};

    if (!urlIndex.includes(url)) {
        urlIndex.push(url);
    }

    if (!categoryIndex[category]) {
        categoryIndex[category] = [];
    }
    if (!categoryIndex[category].includes(url)) {
        categoryIndex[category].push(url);
    }

    await chrome.storage.local.set({ urlIndex, categoryIndex });
}

// Get embeddings using Nomic backend or simplified approach
async function getEmbeddings(texts) {
    if (USE_BACKEND) {
        try {
            console.log('🌐 Calling backend for embeddings...');
            const response = await fetch(`${BACKEND_URL}/embed`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texts })
            });

            if (!response.ok) throw new Error('Backend embedding failed');

            const data = await response.json();
            console.log('✅ Backend returned', data.embeddings.length, 'embeddings (dimension:', data.dimension + ')');
            return data.embeddings;
        } catch (error) {
            console.error('❌ Backend embedding error, using local:', error);
            console.log('🔄 Falling back to local embeddings...');
            return texts.map(text => createSimpleEmbedding(text));
        }
    } else {
        console.log('💻 Using local embeddings...');
        return texts.map(text => createSimpleEmbedding(text));
    }
}

// Create simple embedding (replace with Nomic API call)
function createSimpleEmbedding(text) {
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    const embedding = new Array(384).fill(0); // Nomic uses 768, simplified to 384

    words.forEach((word, idx) => {
        const hash = word.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        embedding[hash % 384] += 1;
    });

    // Normalize
    const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    return embedding.map(val => magnitude > 0 ? val / magnitude : 0);
}

// Handle search with FAISS backend or local similarity
async function handleSearch(query, category = null) {
    console.log('🔍 Search query:', query);
    console.log('🏷️  Category filter:', category || 'all');
    
    if (USE_BACKEND) {
        try {
            console.log('🌐 Querying FAISS backend...');
            const response = await fetch(`${BACKEND_URL}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    k: 50,
                    category: category !== 'all' ? category : null
                })
            });

            if (!response.ok) throw new Error('Backend search failed');

            const data = await response.json();
            console.log(`✅ FAISS returned ${data.results.length} chunk matches`);

            // Group by URL
            const grouped = {};
            for (const result of data.results) {
                const url = result.metadata.url;
                if (!grouped[url]) {
                    grouped[url] = {
                        url,
                        title: result.metadata.title,
                        category: result.metadata.category,
                        favicon: result.metadata.favicon,
                        matches: []
                    };
                }
                grouped[url].matches.push({
                    text: result.metadata.chunk,
                    chunkIndex: result.metadata.chunkIndex,
                    similarity: result.similarity
                });
            }

            const results = Object.values(grouped).slice(0, 10);
            console.log(`📊 Grouped into ${results.length} unique URLs`);
            results.forEach((r, i) => {
                console.log(`  ${i + 1}. ${r.title} (${r.matches.length} matches)`);
            });
            console.log('─'.repeat(80));
            
            return results;
        } catch (error) {
            console.error('❌ Backend search error, using local:', error);
            return await handleSearchLocal(query, category);
        }
    } else {
        console.log('💻 Using local search...');
        return await handleSearchLocal(query, category);
    }
}

// Local search fallback
async function handleSearchLocal(query, category) {
    const queryEmbedding = createSimpleEmbedding(query);
    const results = await chrome.storage.local.get(null);

    const matches = [];

    for (const [key, value] of Object.entries(results)) {
        if (key.startsWith('chunk_')) {
            const similarity = cosineSimilarity(queryEmbedding, value.embedding);
            if (similarity > 0.3) {
                matches.push({
                    url: value.url,
                    text: value.text,
                    chunkIndex: value.chunkIndex,
                    similarity: similarity
                });
            }
        }
    }

    matches.sort((a, b) => b.similarity - a.similarity);

    const groupedResults = {};
    for (const match of matches.slice(0, 50)) {
        if (!groupedResults[match.url]) {
            const metaKey = `meta_${hashUrl(match.url)}`;
            const metadata = results[metaKey] || {};

            // Apply category filter
            if (category && category !== 'all' && metadata.category !== category) {
                continue;
            }

            groupedResults[match.url] = {
                url: match.url,
                title: metadata.title,
                category: metadata.category,
                favicon: metadata.favicon,
                matches: []
            };
        }
        if (groupedResults[match.url]) {
            groupedResults[match.url].matches.push({
                text: match.text,
                chunkIndex: match.chunkIndex,
                similarity: match.similarity
            });
        }
    }

    return Object.values(groupedResults).slice(0, 10);
}

// Cosine similarity calculation
function cosineSimilarity(vec1, vec2) {
    let dotProduct = 0;
    let mag1 = 0;
    let mag2 = 0;

    for (let i = 0; i < vec1.length; i++) {
        dotProduct += vec1[i] * vec2[i];
        mag1 += vec1[i] * vec1[i];
        mag2 += vec2[i] * vec2[i];
    }

    return dotProduct / (Math.sqrt(mag1) * Math.sqrt(mag2));
}

// Product comparison for ecommerce sites
async function handleProductComparison(query) {
    if (USE_BACKEND) {
        try {
            const response = await fetch(`${BACKEND_URL}/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error('Backend comparison failed');

            const data = await response.json();
            return data.products;
        } catch (error) {
            console.error('Backend comparison error:', error);
            return await handleSearch(query, 'ecommerce');
        }
    } else {
        return await handleSearch(query, 'ecommerce');
    }
}

// Get statistics
async function getStats() {
    if (USE_BACKEND) {
        try {
            const response = await fetch(`${BACKEND_URL}/stats`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Backend stats error:', error);
        }
    }

    // Fallback to local stats
    const result = await chrome.storage.local.get(['urlIndex', 'categoryIndex']);
    return {
        total_urls: (result.urlIndex || []).length,
        categories: Object.entries(result.categoryIndex || {}).reduce((acc, [cat, urls]) => {
            acc[cat] = urls.length;
            return acc;
        }, {})
    };
}

// Check backend health
async function checkBackendHealth() {
    try {
        const response = await fetch(`${BACKEND_URL}/health`, { timeout: 2000 });
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        return { status: 'offline', error: error.message };
    }
    return { status: 'offline' };
}
