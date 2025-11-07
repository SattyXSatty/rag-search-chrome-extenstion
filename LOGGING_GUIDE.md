# 📊 Comprehensive Logging Guide

## Overview

The extension now has detailed logging at every step. Here's what you'll see in each console.

## 🌐 When You Visit a New Website

### Page Console (F12 on the page):
```
📸 Capturing page content...
📦 Extracted 15234 characters, 31 chunks
✅ Content sent to background for processing
```

### Service Worker Console (chrome://extensions/ → service worker):
```
📨 Background received message: CAPTURE_CONTENT
📄 Processing page: Machine Learning Tutorial
🔗 URL: https://example.com/ml-tutorial
📊 Content length: 15234 characters
📦 Chunks: 31
🏷️  Category: documentation
🧮 Generating embeddings for 31 chunks...
🌐 Calling backend for embeddings...
✅ Backend returned 31 embeddings (dimension: 384)
✅ Embeddings generated: 31 vectors
💾 Storing in FAISS...
📤 Sending to FAISS backend...
✅ FAISS indexed: 31 chunks
📊 Total vectors in FAISS: 892
✅ Local index updated
✅ Captured: https://example.com/ml-tutorial [documentation]
────────────────────────────────────────────────────────────────────────────────
```

## 🔍 When You Search

### Service Worker Console:
```
📨 Background received message: SEARCH_CONTENT
🔍 Search request: machine learning category: all
🔍 Search query: machine learning
🏷️  Category filter: all
🌐 Querying FAISS backend...
✅ FAISS returned 45 chunk matches
📊 Grouped into 8 unique URLs
  1. Machine Learning Tutorial (12 matches)
  2. Deep Learning Guide (8 matches)
  3. Neural Networks Explained (7 matches)
  4. AI Fundamentals (6 matches)
  5. Python ML Libraries (5 matches)
  6. Data Science Basics (3 matches)
  7. TensorFlow Guide (2 matches)
  8. Keras Documentation (2 matches)
────────────────────────────────────────────────────────────────────────────────
```

### Popup Console (Right-click popup → Inspect):
```
✅ Displayed 8 results
✅ Click handlers added to 8 items
```

## 🖱️ When You Click a Result

### Popup Console:
```
🖱️ Result clicked! https://example.com/ml-tutorial
🔍 Query: machine learning
🎯 openAndHighlight called!
🎯 URL: https://example.com/ml-tutorial
🎯 Text: machine learning
📤 Message sent to background
```

### Service Worker Console:
```
📨 Background received message: OPEN_AND_HIGHLIGHT
🎯 OPEN_AND_HIGHLIGHT received! url: https://example.com/ml-tutorial text: machine learning
🚀 Opening URL: https://example.com/ml-tutorial
🔍 Search query: machine learning
✅ New tab created: 456
📅 Scheduled highlight for tab: 456 query: machine learning
📊 Tab status: loading URL: https://example.com/ml-tutorial
⏳ Waiting for tab to load...
📊 Tab 456 update: loading
📊 Tab 456 update: complete
✅ Page loaded completely
🎯 Executing highlight for tab: 456
✅ Highlight script executed successfully
```

### Page Console (on the opened page):
```
🎨 Highlighting in page: machine learning
Looking for words: ["machine", "learning"]
Found nodes to highlight: 12
✅ Scrolled to first highlight
```

## 📊 Log Symbols Explained

### Status Indicators:
- 📨 Message received
- 📄 Page processing
- 🔗 URL information
- 📊 Statistics/counts
- 📦 Data chunks
- 🏷️  Categorization
- 🧮 Computation
- 🌐 Backend API call
- ✅ Success
- ❌ Error
- ⏭️  Skipped
- 🔄 Fallback
- 💾 Storage
- 📤 Sending data
- 🔍 Search
- 🖱️ User interaction
- 🎯 Action triggered
- 🚀 Opening/creating
- ⏳ Waiting
- 🎨 Highlighting
- ─── Separator

## 🎯 Complete Flow Example

### Scenario: Visit a page, search, and highlight

```
═══════════════════════════════════════════════════════════════════════════════
STEP 1: VISIT PAGE
═══════════════════════════════════════════════════════════════════════════════

[Page Console]
📸 Capturing page content...
📦 Extracted 15234 characters, 31 chunks
✅ Content sent to background for processing

[Service Worker]
📨 Background received message: CAPTURE_CONTENT
📄 Processing page: Machine Learning Tutorial
🔗 URL: https://example.com/ml-tutorial
📊 Content length: 15234 characters
📦 Chunks: 31
🏷️  Category: documentation
🧮 Generating embeddings for 31 chunks...
🌐 Calling backend for embeddings...
✅ Backend returned 31 embeddings (dimension: 384)
✅ Embeddings generated: 31 vectors
💾 Storing in FAISS...
📤 Sending to FAISS backend...
✅ FAISS indexed: 31 chunks
📊 Total vectors in FAISS: 892
✅ Local index updated
✅ Captured: https://example.com/ml-tutorial [documentation]
────────────────────────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════════════════════
STEP 2: SEARCH
═══════════════════════════════════════════════════════════════════════════════

[Service Worker]
📨 Background received message: SEARCH_CONTENT
🔍 Search request: machine learning category: all
🔍 Search query: machine learning
🏷️  Category filter: all
🌐 Querying FAISS backend...
✅ FAISS returned 45 chunk matches
📊 Grouped into 8 unique URLs
  1. Machine Learning Tutorial (12 matches)
  2. Deep Learning Guide (8 matches)
  3. Neural Networks Explained (7 matches)
  4. AI Fundamentals (6 matches)
  5. Python ML Libraries (5 matches)
  6. Data Science Basics (3 matches)
  7. TensorFlow Guide (2 matches)
  8. Keras Documentation (2 matches)
────────────────────────────────────────────────────────────────────────────────

[Popup Console]
✅ Displayed 8 results
✅ Click handlers added to 8 items

═══════════════════════════════════════════════════════════════════════════════
STEP 3: CLICK RESULT
═══════════════════════════════════════════════════════════════════════════════

[Popup Console]
🖱️ Result clicked! https://example.com/ml-tutorial
🔍 Query: machine learning
🎯 openAndHighlight called!
🎯 URL: https://example.com/ml-tutorial
🎯 Text: machine learning
📤 Message sent to background

[Service Worker]
📨 Background received message: OPEN_AND_HIGHLIGHT
🎯 OPEN_AND_HIGHLIGHT received! url: https://example.com/ml-tutorial text: machine learning
🚀 Opening URL: https://example.com/ml-tutorial
🔍 Search query: machine learning
✅ New tab created: 456
📅 Scheduled highlight for tab: 456 query: machine learning
📊 Tab status: loading URL: https://example.com/ml-tutorial
⏳ Waiting for tab to load...
📊 Tab 456 update: loading
📊 Tab 456 update: complete
✅ Page loaded completely
🎯 Executing highlight for tab: 456
✅ Highlight script executed successfully

[Page Console]
🎨 Highlighting in page: machine learning
Looking for words: ["machine", "learning"]
Found nodes to highlight: 12
✅ Scrolled to first highlight

═══════════════════════════════════════════════════════════════════════════════
COMPLETE! ✅
═══════════════════════════════════════════════════════════════════════════════
```

## 🔧 Debugging Tips

### If Capture Fails:
Look for:
- ⏭️  Skipping excluded URL (site is in exclusion list)
- ❌ Backend embedding error (backend down)
- 🔄 Falling back to local (backend issue)

### If Search Fails:
Look for:
- ❌ Backend search error (backend down)
- 💻 Using local search (fallback mode)
- 📊 Grouped into 0 unique URLs (no results)

### If Highlighting Fails:
Look for:
- ❌ Failed to execute highlight script (page blocking)
- Found nodes to highlight: 0 (no matching text)
- Tab status: loading (page not loaded yet)

## 📈 Performance Monitoring

### Capture Performance:
```
📦 Chunks: 31                    ← Number of chunks
🧮 Generating embeddings...      ← Start time
✅ Embeddings generated: 31      ← End time (measure gap)
📊 Total vectors in FAISS: 892   ← Index size
```

### Search Performance:
```
🌐 Querying FAISS backend...     ← Start time
✅ FAISS returned 45 matches     ← End time (measure gap)
📊 Grouped into 8 unique URLs    ← Result count
```

### Highlighting Performance:
```
📊 Tab status: loading           ← Page load start
📊 Tab update: complete          ← Page load end
🎯 Executing highlight...        ← Highlight start
✅ Highlight script executed     ← Highlight end
```

## 🎓 Understanding the Logs

### Capture Flow:
1. Page loads → Content script captures
2. Sends to background
3. Background generates embeddings
4. Stores in FAISS
5. Updates local index

### Search Flow:
1. User types query
2. Background queries FAISS
3. FAISS returns chunk matches
4. Background groups by URL
5. Returns top 10 URLs

### Highlight Flow:
1. User clicks result
2. Popup sends message
3. Background opens/activates tab
4. Waits for page load
5. Injects highlighting script
6. Script highlights and scrolls

---

**All logs are now comprehensive and easy to follow!** 📊✨
