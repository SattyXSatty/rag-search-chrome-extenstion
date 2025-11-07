# Test & Demo Guide

Quick tests to verify everything works!

## 1. Backend Test

### Start Backend:
```bash
./start-backend.sh
```

### Test Endpoints:

**Health Check:**
```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "model": "nomic-ai/nomic-embed-text-v1.5",
  "total_vectors": 0,
  "dimension": 768
}
```

**Test Embedding:**
```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["hello world", "test embedding"]}'
```

Should return 768-dimensional vectors.

**Test Search (after adding data):**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "k": 5}'
```

## 2. Extension Test

### Install Extension:
1. Chrome → `chrome://extensions/`
2. Enable Developer mode
3. Load unpacked → select this folder

### Test Capture:

1. **Visit test sites:**
   - https://news.ycombinator.com
   - https://www.amazon.com
   - https://github.com
   - https://stackoverflow.com

2. **Check backend logs:**
   - Should see "Captured: [URL] [category]"
   - Wait 2-3 seconds per page

3. **Verify storage:**
   ```bash
   curl http://localhost:8000/stats
   ```

### Test Search:

1. Click extension icon
2. Should show: "🟢 FAISS Backend Connected"
3. Type: "programming"
4. Should see results from visited pages

### Test Categories:

1. Click each category filter
2. Results should filter accordingly
3. Try "📰 News" → should show HN
4. Try "📚 Docs" → should show GitHub/SO

### Test Product Comparison:

1. **Visit shopping sites:**
   - Amazon: search "laptop"
   - eBay: search "laptop"
   - BestBuy: search "laptop"

2. **Compare in extension:**
   - Click "🛒 Shopping" filter
   - Type: "laptop"
   - Should see comparison with match %

3. **Click result:**
   - Should open page
   - Should highlight matching text

## 3. Feature Tests

### Test Highlighting:

1. Search for specific text
2. Click result
3. Page should open with yellow highlights
4. Should scroll to first match

### Test Excluded Sites:

1. Visit Gmail (mail.google.com)
2. Check backend logs
3. Should NOT see "Captured: mail.google.com"

### Test Category Detection:

Visit these and check category in extension:

| Site | Expected Category |
|------|------------------|
| amazon.com | ecommerce |
| nytimes.com | news |
| docs.python.org | documentation |
| twitter.com | social |
| youtube.com | video |

## 4. Performance Test

### Small Dataset (10 pages):
- Capture time: ~2s per page
- Search time: <100ms
- Memory: ~50MB

### Medium Dataset (100 pages):
- Index size: ~50MB
- Search time: <200ms
- Backend RAM: ~2GB

### Large Dataset (1000+ pages):
- Index size: ~500MB
- Search time: <500ms
- Backend RAM: ~3GB

## 5. Demo Scenario

### Scenario: Shopping for Headphones

1. **Research Phase:**
   - Visit Amazon, search "wireless headphones"
   - Visit eBay, search "wireless headphones"
   - Visit BestBuy, search "wireless headphones"
   - Read reviews on each

2. **Comparison Phase:**
   - Open extension
   - Click "🛒 Shopping"
   - Type: "wireless headphones"
   - See all 3 sites ranked by relevance

3. **Review Phase:**
   - Click each result
   - See highlighted product descriptions
   - Compare prices and features

### Scenario: Research Project

1. **Gather Information:**
   - Visit Wikipedia articles
   - Read blog posts
   - Check documentation
   - Watch YouTube tutorials

2. **Search Phase:**
   - Type: "neural networks"
   - See all relevant pages
   - Filter by category (Docs, Video, etc.)

3. **Revisit Phase:**
   - Click results to revisit pages
   - Highlights show exact sections you need

## 6. Troubleshooting Tests

### Backend Not Connecting:

```bash
# Check if running
curl http://localhost:8000/health

# Check logs
cd backend
tail -f *.log

# Restart
pkill -f "python server.py"
./start-backend.sh
```

### Extension Not Working:

1. Open DevTools (F12)
2. Check Console for errors
3. Check Network tab for backend calls
4. Reload extension

### No Search Results:

```bash
# Check if data exists
curl http://localhost:8000/stats

# Should show:
# "total_vectors": > 0
# "total_urls": > 0
```

## 7. Expected Behavior

### ✅ Should Work:

- Capture most websites automatically
- Search with semantic understanding
- Filter by category
- Highlight text on page
- Compare products
- Work offline (local mode)

### ❌ Won't Work:

- Gmail, WhatsApp (excluded)
- Login pages (excluded)
- Sites blocking content scripts
- Dynamic content loaded after 2s

## 8. Success Metrics

After 1 hour of browsing:
- ✅ 20+ pages captured
- ✅ Search returns relevant results
- ✅ Categories auto-detected
- ✅ Highlights work on most sites
- ✅ Backend shows healthy status

After 1 day of browsing:
- ✅ 100+ pages captured
- ✅ Product comparison works
- ✅ Search is fast (<500ms)
- ✅ Multiple categories populated

After 1 week of browsing:
- ✅ 500+ pages captured
- ✅ Personal search engine ready
- ✅ Useful for daily work
- ✅ Finding old pages easily

## 9. Demo Commands

Quick demo for showing others:

```bash
# Terminal 1: Start backend
./start-backend.sh

# Terminal 2: Test it
curl http://localhost:8000/health
curl http://localhost:8000/stats

# Browser: Show extension
# 1. Click icon
# 2. Show backend status
# 3. Search something
# 4. Show categories
# 5. Demo product comparison
```

## 10. Video Demo Script

1. **Intro (30s):**
   - "Personal web memory with AI"
   - Show extension icon

2. **Capture (1min):**
   - Browse 3-4 sites
   - Show backend logs capturing

3. **Search (1min):**
   - Open extension
   - Search for content
   - Show results
   - Click → highlight

4. **Compare (1min):**
   - Show shopping sites
   - Click Shopping filter
   - Search product
   - Show comparison

5. **Outro (30s):**
   - Show stats
   - Mention features
   - Call to action

Total: ~4 minutes

Enjoy testing! 🧪✨
