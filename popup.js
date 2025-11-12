// Popup UI logic

let currentFilter = 'all';
let searchTimeout;
let isCompareMode = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  setupEventListeners();
  checkBackendStatus();
});

// Setup event listeners
function setupEventListeners() {
  const searchInput = document.getElementById('searchInput');
  const searchBtn = document.getElementById('searchBtn');
  const filters = document.querySelectorAll('.filter-btn');
  const compareBtn = document.getElementById('compareBtn');
  
  // Function to perform search
  const doSearch = () => {
    const query = searchInput.value;
    if (isCompareMode) {
      performComparison(query);
    } else {
      performSearch(query);
    }
  };
  
  // Search on button click
  searchBtn.addEventListener('click', doSearch);
  
  // Search on Enter key
  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      doSearch();
    }
  });
  
  filters.forEach(btn => {
    btn.addEventListener('click', () => {
      filters.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.category;
      
      // Enable compare mode for ecommerce
      if (currentFilter === 'ecommerce') {
        isCompareMode = true;
        compareBtn.style.display = 'block';
        compareBtn.classList.add('active');
        searchInput.placeholder = 'Search products to compare...';
      } else {
        isCompareMode = false;
        compareBtn.style.display = 'none';
        searchInput.placeholder = 'Search your browsing history...';
      }
      
      performSearch(searchInput.value);
    });
  });
  
  if (compareBtn) {
    compareBtn.addEventListener('click', () => {
      isCompareMode = !isCompareMode;
      compareBtn.classList.toggle('active');
      
      if (isCompareMode) {
        searchInput.placeholder = 'Search products to compare...';
        currentFilter = 'ecommerce';
        document.querySelector('[data-category="ecommerce"]').click();
      } else {
        searchInput.placeholder = 'Search your browsing history...';
      }
      
      performSearch(searchInput.value);
    });
  }
}

// Load statistics
async function loadStats() {
  const result = await chrome.storage.local.get(['urlIndex', 'categoryIndex']);
  const urlCount = (result.urlIndex || []).length;
  const categoryCount = Object.keys(result.categoryIndex || {}).length;
  
  document.getElementById('stats').textContent = 
    `${urlCount} pages indexed across ${categoryCount} categories`;
}

// Perform search
async function performSearch(query) {
  const resultsDiv = document.getElementById('results');
  
  if (!query.trim()) {
    resultsDiv.innerHTML = '<div class="no-results">Start typing to search your browsing history</div>';
    return;
  }
  
  resultsDiv.innerHTML = '<div class="loading">Searching...</div>';
  
  try {
    const results = await new Promise((resolve) => {
      chrome.runtime.sendMessage({
        type: 'SEARCH_CONTENT',
        query: query,
        category: currentFilter
      }, resolve);
    });
    
    displayResults(results);
  } catch (error) {
    resultsDiv.innerHTML = '<div class="no-results">Error searching. Please try again.</div>';
    console.error('Search error:', error);
  }
}

// Perform product comparison
async function performComparison(query) {
  const resultsDiv = document.getElementById('results');
  
  if (!query.trim()) {
    resultsDiv.innerHTML = '<div class="no-results">Enter a product name to compare across sites</div>';
    return;
  }
  
  resultsDiv.innerHTML = '<div class="loading">Comparing products...</div>';
  
  try {
    const results = await new Promise((resolve) => {
      chrome.runtime.sendMessage({
        type: 'COMPARE_PRODUCTS',
        query: query
      }, resolve);
    });
    
    displayComparisonResults(results);
  } catch (error) {
    resultsDiv.innerHTML = '<div class="no-results">Error comparing. Please try again.</div>';
    console.error('Comparison error:', error);
  }
}

// Load statistics
async function loadStats() {
  try {
    const stats = await new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'GET_STATS' }, resolve);
    });
    
    const total = stats.total_urls || 0;
    const categories = Object.keys(stats.categories || {}).length;
    
    document.getElementById('stats').textContent = 
      `${total} pages indexed across ${categories} categories`;
  } catch (error) {
    document.getElementById('stats').textContent = 'Loading stats...';
  }
}

// Check backend status
async function checkBackendStatus() {
  try {
    const status = await new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'CHECK_BACKEND' }, resolve);
    });
    
    const statusDiv = document.getElementById('backendStatus');
    if (status.status === 'healthy') {
      statusDiv.innerHTML = '🟢 FAISS Backend Connected';
      statusDiv.style.color = '#0f9d58';
    } else {
      statusDiv.innerHTML = '🟡 Using Local Storage';
      statusDiv.style.color = '#f4b400';
    }
  } catch (error) {
    console.error('Backend check error:', error);
  }
}

// Display search results
function displayResults(results) {
  const resultsDiv = document.getElementById('results');
  
  if (!results || results.length === 0) {
    resultsDiv.innerHTML = '<div class="no-results">No results found</div>';
    return;
  }
  
  // Get the current search query
  const searchQuery = document.getElementById('searchInput').value;
  
  resultsDiv.innerHTML = results.map(result => `
    <div class="result-item" data-url="${escapeHtml(result.url)}" data-query="${escapeHtml(searchQuery)}" data-snippet="${escapeHtml(result.matches[0].text)}">
      <div class="result-header">
        ${result.favicon ? `<img src="${escapeHtml(result.favicon)}" class="result-favicon" onerror="this.style.display='none'">` : ''}
        <div class="result-title">${escapeHtml(result.title || 'Untitled')}</div>
        <span class="result-category">${escapeHtml(result.category)}</span>
      </div>
      <div class="result-snippet">${escapeHtml(truncate(result.matches[0].text, 150))}</div>
      <div class="result-url">${escapeHtml(result.url)}</div>
    </div>
  `).join('');
  
  console.log('✅ Displayed', results.length, 'results');
  
  // Add click handlers
  document.querySelectorAll('.result-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('🖱️ Result clicked!', item.dataset.url);
      console.log('🔍 Query:', item.dataset.query);
      console.log('📄 Snippet:', item.dataset.snippet);
      
      // Use the original search query for highlighting (not the snippet)
      openAndHighlight(item.dataset.url, item.dataset.query);
    });
  });
  
  console.log('✅ Click handlers added to', document.querySelectorAll('.result-item').length, 'items');
}

// Display comparison results
function displayComparisonResults(results) {
  const resultsDiv = document.getElementById('results');
  
  if (!results || results.length === 0) {
    resultsDiv.innerHTML = '<div class="no-results">No products found to compare</div>';
    return;
  }
  
  // Get the current search query
  const searchQuery = document.getElementById('searchInput').value;
  
  resultsDiv.innerHTML = `
    <div class="comparison-header">
      <h3>🛒 Product Comparison (${results.length} sites)</h3>
    </div>
    ${results.map((result, idx) => `
      <div class="result-item comparison-item" data-url="${escapeHtml(result.url)}" data-query="${escapeHtml(searchQuery)}">
        <div class="result-header">
          <span class="rank">#${idx + 1}</span>
          ${result.favicon ? `<img src="${escapeHtml(result.favicon)}" class="result-favicon" onerror="this.style.display='none'">` : ''}
          <div class="result-title">${escapeHtml(result.title || 'Untitled')}</div>
          <span class="similarity-badge">${Math.round(result.avg_similarity * 100)}% match</span>
        </div>
        <div class="result-snippet">${escapeHtml(truncate(result.chunks[0].text, 150))}</div>
        <div class="result-url">${escapeHtml(result.url)}</div>
        <div class="match-count">${result.chunks.length} relevant sections found</div>
      </div>
    `).join('')}
  `;
  
  // Add click handlers
  document.querySelectorAll('.result-item').forEach(item => {
    item.addEventListener('click', () => {
      // Use the original search query for highlighting (not the snippet)
      openAndHighlight(item.dataset.url, item.dataset.query);
    });
  });
}

// Helper function to check if content script is ready
async function isContentScriptReady(tabId) {
  try {
    const response = await chrome.tabs.sendMessage(tabId, { type: 'PING' });
    return response && response.ready;
  } catch (error) {
    return false;
  }
}

// Helper function to wait for content script to be ready
async function waitForContentScript(tabId, maxWait = 10000) {
  const startTime = Date.now();
  while (Date.now() - startTime < maxWait) {
    if (await isContentScriptReady(tabId)) {
      console.log('✅ Content script is ready');
      return true;
    }
    console.log('⏳ Waiting for content script...');
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  console.log('⚠️ Content script not ready after timeout');
  return false;
}

// Helper function to send highlight message with retries
async function sendHighlightMessage(tabId, text, maxRetries = 3) {
  // First, wait for content script to be ready
  const isReady = await waitForContentScript(tabId);
  if (!isReady) {
    console.log('❌ Content script not ready, cannot highlight');
    return false;
  }
  
  // Now try to send highlight message
  for (let i = 0; i < maxRetries; i++) {
    try {
      await chrome.tabs.sendMessage(tabId, {
        type: 'HIGHLIGHT_TEXT',
        text: text
      });
      console.log(`✅ Highlight sent successfully (attempt ${i + 1})`);
      return true;
    } catch (error) {
      console.log(`⏳ Highlight attempt ${i + 1} failed: ${error.message}`);
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
  }
  console.log('❌ All highlight attempts failed');
  return false;
}

// Open URL and highlight text
function openAndHighlight(url, text) {
  console.log('🎯 openAndHighlight called!');
  console.log('🎯 URL:', url);
  console.log('🎯 Text:', text);
  
  // Send message to background SYNCHRONOUSLY before popup closes
  chrome.runtime.sendMessage({
    type: 'OPEN_AND_HIGHLIGHT',
    url: url,
    text: text
  }, (response) => {
    console.log('📨 Response from background:', response);
  });
  
  console.log('📤 Message sent to background');
  
  // Close popup after a tiny delay
  setTimeout(() => {
    window.close();
  }, 50);
}

// Utility functions
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function truncate(text, length) {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}
