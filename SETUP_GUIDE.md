# Complete Setup Guide

## Quick Start (3 Steps)

### 1. Install Chrome Extension

```bash
# Create placeholder icons (or add your own)
mkdir -p icons
# Add icon16.png, icon48.png, icon128.png to icons folder
```

1. Open Chrome: `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this directory

### 2. Setup Python Backend (FAISS + Nomic)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python server.py
```

The server will:
- Download Nomic embedding model (~1GB, first time only)
- Start on http://localhost:8000
- Auto-save index periodically

### 3. Start Browsing!

- Browse any website (except Gmail, WhatsApp, etc.)
- Content is automatically captured and indexed
- Click extension icon to search
- Try "Shopping" filter for product comparison

## Configuration

### Enable/Disable Backend

In `background.js`, line 3:
```javascript
const USE_BACKEND = true;  // Set to false for local-only mode
```

### Add Excluded Domains

In `background.js`:
```javascript
const EXCLUDED_DOMAINS = [
  'mail.google.com',
  'web.whatsapp.com',
  'your-domain.com',  // Add more here
];
```

### Customize Categories

In `background.js`:
```javascript
const CATEGORY_PATTERNS = {
  ecommerce: ['amazon', 'ebay', 'your-store'],
  // Add or modify categories
};
```

## Features

### 1. Automatic Content Capture
- Captures page content 2 seconds after load
- Excludes confidential sites
- Chunks text into 500-character segments
- Generates embeddings for each chunk

### 2. Nomic Embeddings
- Uses `nomic-embed-text-v1.5` model
- 768-dimensional vectors
- Optimized for semantic search
- Normalized for cosine similarity

### 3. FAISS Indexing
- IndexFlatIP for exact cosine similarity
- Persistent storage (auto-saves)
- Fast retrieval even with 100k+ vectors
- Metadata stored separately

### 4. Smart Search
- Semantic search across all captured content
- Filter by category
- Returns top 10 URLs with relevant snippets
- Highlights matching text on page

### 5. Product Comparison
- Click "Shopping" category
- Search for product name
- See results from all ecommerce sites you've visited
- Ranked by relevance
- Shows match percentage

## Usage Examples

### Search Your History
1. Click extension icon
2. Type: "machine learning tutorial"
3. See all relevant pages you've visited

### Compare Products
1. Click "🛒 Shopping" filter
2. Type: "wireless headphones"
3. See product pages from Amazon, eBay, etc.
4. Click any result to open with highlights

### Filter by Category
- 📰 News: Articles and blog posts
- 📚 Docs: Documentation and guides
- 👥 Social: Social media content
- 🎥 Video: YouTube and video sites

## Backend API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/stats

# Manual save
curl -X POST http://localhost:8000/save
```

## Troubleshooting

### Backend Won't Start

**Error: "No module named 'sentence_transformers'"**
```bash
pip install -r requirements.txt
```

**Error: "Model download failed"**
- Check internet connection
- Model is ~1GB, may take time
- Try: `pip install --upgrade sentence-transformers`

### Extension Not Capturing

1. Check excluded domains in `background.js`
2. Open DevTools → Console for errors
3. Verify backend is running (check popup status)

### Search Returns No Results

1. Browse some websites first
2. Wait 2-3 seconds per page for capture
3. Check backend logs for errors
4. Try disabling backend: `USE_BACKEND = false`

### Highlights Not Working

1. Page must be fully loaded
2. Some sites block content scripts
3. Try refreshing the page after search

## Performance Tips

### For Large Datasets (10k+ pages)

1. **Use FAISS Backend**: Much faster than local storage
2. **Increase Chunk Size**: Edit `content.js`, line 24
3. **Adjust Similarity Threshold**: Edit `background.js`, search functions
4. **Use IVF Index**: For 100k+ vectors, switch to `IndexIVFFlat`

### Memory Usage

- Backend: ~2GB RAM (model + index)
- Extension: ~50MB per 1000 pages
- Chrome storage limit: 10MB (use backend for more)

## Advanced Configuration

### Switch to IVF Index (for 100k+ vectors)

In `backend/server.py`:
```python
# Replace IndexFlatIP with:
quantizer = faiss.IndexFlatIP(DIMENSION)
index = faiss.IndexIVFFlat(quantizer, DIMENSION, 100)  # 100 clusters
index.train(initial_embeddings)  # Need training data
```

### Add Custom Embedding Model

In `backend/server.py`:
```python
MODEL_NAME = 'your-model-name'
# Or use OpenAI:
# from openai import OpenAI
# client = OpenAI(api_key='your-key')
```

### Export/Import Data

```bash
# Backup
cp backend/faiss_index.pkl backup/
cp backend/metadata.pkl backup/

# Restore
cp backup/*.pkl backend/
```

## What's Next?

1. **Try it out**: Browse 10-20 pages, then search
2. **Test comparison**: Visit Amazon, eBay, search for products
3. **Customize**: Add your own categories and patterns
4. **Scale up**: Let it run for a week, build your personal search engine

## Support

- Check logs: Backend terminal + Chrome DevTools Console
- Test backend: `curl http://localhost:8000/health`
- Verify extension: Check popup status indicator

Enjoy your personal web memory! 🧠
