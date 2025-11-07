# Web Memory RAG with Cognitive AI

> Intelligent browsing history search powered by RAG, FAISS, and Gemini 2.0 Flash - Chrome Extension

A Chrome extension that captures website content, builds a RAG (Retrieval-Augmented Generation) system with embeddings, and enables intelligent search with text highlighting.

## Features

1. **Automatic Content Capture**: Monitors websites you visit and stores content (excludes confidential sites like Gmail, WhatsApp)
2. **Nomic-style Embeddings**: Creates vector embeddings for semantic search
3. **FAISS-like Index**: Builds an efficient search index with URLs
4. **Smart Search & Highlight**: Search your browsing history and automatically highlights matching content on the page
5. **Website Categorization**: Automatically categorizes websites (ecommerce, news, docs, social, video) for comparison and filtering

## Installation

### Quick Start (5 minutes)

**1. Start Backend:**
```bash
./start-backend.sh  # macOS/Linux
# or
start-backend.bat   # Windows
```

**2. Install Extension:**
- Chrome → `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked" → Select this folder

**3. Browse & Search!**

See [QUICKSTART.md](QUICKSTART.md) for step-by-step guide.

## Usage

### Automatic Capture
- Browse any website - content is automatically captured
- Confidential sites (Gmail, WhatsApp, login pages) are excluded
- Backend status shown in popup (🟢 = FAISS connected, 🟡 = local mode)

### Search Your History
1. Click extension icon
2. Type search query (semantic search powered by Nomic)
3. Filter by category
4. Click result → opens page with highlighted text

### Product Comparison
1. Click "🛒 Shopping" filter
2. Search for product (e.g., "wireless headphones")
3. See ranked results from all ecommerce sites you've visited
4. Match percentage shows relevance
5. Click to open and compare

### Categories
- **Shopping**: Ecommerce sites with product comparison
- **News**: Articles and blog posts
- **Docs**: Documentation and technical guides
- **Social**: Social media content
- **Video**: YouTube and video platforms

## Architecture

### Components

- **manifest.json**: Extension configuration
- **background.js**: Service worker handling content capture, embedding generation, and search
- **content.js**: Content script for page content extraction and text highlighting
- **popup.html/js**: User interface for searching and browsing captured content

### Data Storage

- Uses Chrome's local storage API
- Stores page metadata, text chunks, and embeddings
- Maintains URL and category indexes for fast retrieval

### Embedding System

**✅ IMPLEMENTED: Nomic Embeddings**
- Uses `nomic-embed-text-v1.5` model via Python backend
- 768-dimensional vectors optimized for semantic search
- Automatic fallback to simplified embeddings if backend offline

### FAISS Integration

**✅ IMPLEMENTED: FAISS Backend**
- Python Flask server with FAISS IndexFlatIP
- Persistent storage (auto-saves index)
- Handles 100k+ vectors efficiently
- Cosine similarity search with metadata

**Backend Features:**
- `/embed` - Generate Nomic embeddings
- `/add` - Add to FAISS index
- `/search` - Semantic search with category filtering
- `/compare` - Product comparison for ecommerce
- `/stats` - Index statistics

Set `USE_BACKEND = false` in `background.js` to use local-only mode.

## Excluded Domains

The following domains are automatically excluded from capture:
- mail.google.com (Gmail)
- web.whatsapp.com (WhatsApp)
- Any URL containing: accounts.google.com, login., signin., auth.

Add more in `background.js`:
```javascript
const EXCLUDED_DOMAINS = [
  'mail.google.com',
  'web.whatsapp.com',
  // Add more here
];
```

## Category Patterns

Customize website categorization in `background.js`:
```javascript
const CATEGORY_PATTERNS = {
  ecommerce: ['amazon', 'ebay', 'shopify', 'shop', 'cart', 'product'],
  // Add or modify categories
};
```

## Performance Considerations

- Content is captured 2 seconds after page load to allow dynamic content to render
- Text is limited to 50,000 characters per page
- Chunks are 500 characters each for optimal embedding
- Search results are limited to top 10 URLs with 50 total matches

## Future Enhancements

1. **Real Nomic API Integration**: Replace simplified embeddings with actual Nomic API
2. **FAISS Backend**: Set up Python backend with FAISS for better performance
3. **Advanced Comparison**: Build UI for side-by-side product/content comparison
4. **Export/Import**: Allow backing up and syncing captured data
5. **Privacy Controls**: Fine-grained control over what gets captured
6. **Analytics**: Visualize browsing patterns and categories

## Privacy

- All data is stored locally in Chrome's storage
- No data is sent to external servers (in current implementation)
- You control what gets captured through excluded domains list

## License

MIT
