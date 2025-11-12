// Content script to capture page content and highlight search results

let captureTimeout;

// Capture page content after load
function capturePageContent() {
  // Check if extension context is valid before trying to capture
  if (!isExtensionContextValid()) {
    return; // Silently skip if extension was reloaded
  }
  
  clearTimeout(captureTimeout);
  captureTimeout = setTimeout(() => {
    // Check again before sending
    if (!isExtensionContextValid()) {
      return;
    }
    
    console.log('📸 Capturing page content...');
    const content = extractContent();
    const chunks = chunkText(content, 500); // 500 char chunks
    console.log(`📦 Extracted ${content.length} characters, ${chunks.length} chunks`);
    
    try {
      chrome.runtime.sendMessage({
        type: 'CAPTURE_CONTENT',
        data: {
          title: document.title,
          content: content,
          chunks: chunks
        }
      });
      console.log('✅ Content sent to background for processing');
    } catch (error) {
      // Extension context invalidated - silently ignore
      // This happens when extension is reloaded while page is open
    }
  }, 2000); // Wait 2s for dynamic content
}

// Extract meaningful content from page
function extractContent() {
  // Remove script, style, and other non-content elements
  const clone = document.body.cloneNode(true);
  const unwanted = clone.querySelectorAll('script, style, nav, footer, iframe, noscript');
  unwanted.forEach(el => el.remove());
  
  let text = clone.innerText || clone.textContent;
  text = text.replace(/\s+/g, ' ').trim();
  
  return text.substring(0, 50000); // Limit to 50k chars
}

// Chunk text for embedding
function chunkText(text, chunkSize) {
  const chunks = [];
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
  
  let currentChunk = '';
  for (const sentence of sentences) {
    if ((currentChunk + sentence).length > chunkSize && currentChunk) {
      chunks.push(currentChunk.trim());
      currentChunk = sentence;
    } else {
      currentChunk += ' ' + sentence;
    }
  }
  
  if (currentChunk) {
    chunks.push(currentChunk.trim());
  }
  
  return chunks;
}

// Highlight text on page
function highlightText(searchText, chunkIndex) {
  console.log('Highlighting snippet:', searchText.substring(0, 100));
  removeHighlights();
  
  // Extract words from snippet (at least 5 chars to avoid common short words)
  const allWords = searchText.toLowerCase().match(/\b\w{5,}\b/g) || [];
  
  // Filter out ONLY the most common words
  const veryCommonWords = new Set(['india', 'women', 'national', 'cricket', 'team']);
  const filteredWords = allWords.filter(word => !veryCommonWords.has(word));
  
  // Take only the top 3 words to avoid over-highlighting
  const snippetWords = filteredWords.length > 0 ? filteredWords.slice(0, 3) : allWords.slice(0, 3);
  
  console.log('✨ Distinctive words for highlighting:', snippetWords, '(filtered from', allWords.length, 'total words)');
  
  // Find text nodes containing any of the words
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: function(node) {
        // Skip script and style elements
        if (node.parentElement.tagName === 'SCRIPT' || 
            node.parentElement.tagName === 'STYLE') {
          return NodeFilter.FILTER_REJECT;
        }
        // Skip empty or whitespace-only nodes
        if (!node.textContent.trim()) {
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
    
    // Count how many snippet words appear in this node
    const matchingWords = snippetWords.filter(word => textLower.includes(word));
    const matchRatio = matchingWords.length / snippetWords.length;
    
    // Only highlight nodes that contain MOST of the distinctive words
    // This ensures we only highlight the most relevant section
    if (matchRatio >= 0.67) {  // At least 67% of words (2 out of 3)
      nodesToHighlight.push({
        node: node,
        matchRatio: matchRatio,
        matchCount: matchingWords.length
      });
    }
  }
  
  console.log('Found candidate nodes:', nodesToHighlight.length);
  
  if (nodesToHighlight.length === 0) {
    console.log('No matching text found on page');
    return;
  }
  
  // Sort by match ratio (nodes with more snippet words rank higher)
  nodesToHighlight.sort((a, b) => {
    if (b.matchRatio !== a.matchRatio) {
      return b.matchRatio - a.matchRatio;
    }
    return b.matchCount - a.matchCount;
  });
  
  // Take top 5 nodes (most similar to snippet)
  const topNodes = nodesToHighlight.slice(0, 5).map(item => item.node);
  
  console.log('Highlighting top 5 nodes most similar to snippet');
  
  // Highlight nodes
  let firstHighlight = null;
  topNodes.forEach((node, index) => {
    
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
        block: 'center',
        inline: 'nearest'
      });
    }, 100);
    console.log('Scrolled to first highlight');
  }
}

// Remove existing highlights
function removeHighlights() {
  const highlights = document.querySelectorAll('.web-memory-highlight');
  highlights.forEach(span => {
    const text = document.createTextNode(span.textContent);
    span.parentNode.replaceChild(text, span);
  });
}

// Listen for highlight requests
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  try {
    if (message.type === 'HIGHLIGHT_TEXT') {
      console.log('📨 Received highlight request');
      highlightText(message.text, message.chunkIndex);
      sendResponse({ success: true });
    } else if (message.type === 'REMOVE_HIGHLIGHTS') {
      console.log('📨 Received remove highlights request');
      removeHighlights();
      sendResponse({ success: true });
    } else if (message.type === 'PING') {
      // Respond to ping to check if content script is ready
      console.log('📨 Received ping');
      sendResponse({ success: true, ready: true });
    }
  } catch (error) {
    console.error('Error handling message:', error);
    sendResponse({ success: false, error: error.message });
  }
  return true; // Keep message channel open for async response
});

// Check if extension context is valid
function isExtensionContextValid() {
  try {
    return chrome.runtime && chrome.runtime.id;
  } catch (error) {
    return false;
  }
}

// Log that content script is loaded
console.log('🧠 Web Memory RAG content script loaded v2.0.1 - NEW VERSION');

// Capture content on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, capturing content...');
    capturePageContent();
  });
} else {
  console.log('📄 Page already loaded, capturing content...');
  capturePageContent();
}

// Re-capture on significant DOM changes (but throttle it heavily)
let mutationTimeout;
const observer = new MutationObserver(() => {
  // Don't even try if context is invalid
  if (!isExtensionContextValid()) {
    return;
  }
  
  clearTimeout(mutationTimeout);
  mutationTimeout = setTimeout(() => {
    if (isExtensionContextValid()) {
      capturePageContent();
    }
  }, 10000); // Only re-capture every 10 seconds max (reduced frequency)
});

// Only observe if body exists and context is valid
if (document.body && isExtensionContextValid()) {
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}
