# Visual Guide & Screenshots

## What You'll See

### 1. Extension Popup

```
┌─────────────────────────────────────────────┐
│  🧠 Web Memory                              │
│  50 pages indexed across 5 categories      │
│  🟢 FAISS Backend Connected                │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │ Search your browsing history...     │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│  [All] [🛒 Shopping] [📰 News] [📚 Docs]   │
│  [👥 Social] [🎥 Video] [⚖️ Compare]       │
├─────────────────────────────────────────────┤
│  ┌───────────────────────────────────────┐ │
│  │ 🌐 Machine Learning Tutorial          │ │
│  │    documentation                      │ │
│  │ Learn about neural networks and...    │ │
│  │ https://example.com/ml-tutorial       │ │
│  └───────────────────────────────────────┘ │
│  ┌───────────────────────────────────────┐ │
│  │ 🌐 Deep Learning Guide                │ │
│  │    documentation                      │ │
│  │ Complete guide to deep learning...    │ │
│  │ https://example.com/dl-guide          │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 2. Product Comparison Mode

```
┌─────────────────────────────────────────────┐
│  🧠 Web Memory                              │
│  50 pages indexed across 5 categories      │
│  🟢 FAISS Backend Connected                │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │ Search products to compare...       │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│  [All] [🛒 Shopping*] [📰 News] [📚 Docs]  │
│  [👥 Social] [🎥 Video] [⚖️ Compare*]      │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │ 🛒 Product Comparison (3 sites)     │   │
│  └─────────────────────────────────────┘   │
│  ┌───────────────────────────────────────┐ │
│  │ #1 🌐 Wireless Headphones      [92%] │ │
│  │       ecommerce                       │ │
│  │ Premium noise-cancelling headphones...│ │
│  │ https://amazon.com/headphones         │ │
│  │ 5 relevant sections found             │ │
│  └───────────────────────────────────────┘ │
│  ┌───────────────────────────────────────┐ │
│  │ #2 🌐 Wireless Headphones      [87%] │ │
│  │       ecommerce                       │ │
│  │ High-quality wireless audio...        │ │
│  │ https://ebay.com/headphones           │ │
│  │ 3 relevant sections found             │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 3. Highlighted Page

```
┌─────────────────────────────────────────────┐
│  ← → ⟳  https://example.com/article        │
├─────────────────────────────────────────────┤
│                                             │
│  Article Title                              │
│  ═══════════                                │
│                                             │
│  Lorem ipsum dolor sit amet, consectetur    │
│  adipiscing elit. ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │
│  ▓ This is the highlighted text that  ▓    │
│  ▓ matches your search query exactly  ▓    │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │
│  sed do eiusmod tempor incididunt ut        │
│  labore et dolore magna aliqua.             │
│                                             │
└─────────────────────────────────────────────┘
        ▲
        │
   Scrolls here automatically
```

### 4. Backend Terminal

```
$ ./start-backend.sh

🚀 Starting Web Memory RAG Backend
==================================
📦 Creating virtual environment...
🔧 Activating virtual environment...
📥 Installing dependencies...
✅ Dependencies installed!

🎯 Starting FAISS backend server...
   URL: http://localhost:8000
   Press Ctrl+C to stop

Loading Nomic embedding model...
Model loaded successfully!
Creating new index...

==================================================
FAISS Backend Server Starting
Model: nomic-ai/nomic-embed-text-v1.5
Dimension: 768
Total vectors: 0
==================================================

 * Serving Flask app 'server'
 * Debug mode: on
 * Running on http://0.0.0.0:8000

Captured: https://example.com [documentation]
Stored in FAISS: 10 chunks, total: 10
Captured: https://amazon.com/product [ecommerce]
Stored in FAISS: 15 chunks, total: 25
Index saved with 25 vectors
```

### 5. Chrome Extensions Page

```
┌─────────────────────────────────────────────┐
│  Extensions                                 │
├─────────────────────────────────────────────┤
│  Developer mode [ON]                        │
│  [Load unpacked] [Pack extension] [Update]  │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │ 🧠 Web Memory RAG                   │   │
│  │ ID: abcdefghijklmnopqrstuvwxyz      │   │
│  │ Version: 1.0.0                      │   │
│  │ Capture and search web content      │   │
│  │ using RAG with embeddings           │   │
│  │                                     │   │
│  │ [Details] [Remove] [Errors]         │   │
│  │ Inspect views: popup.html           │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## UI Elements Explained

### Status Indicators

**🟢 FAISS Backend Connected**
- Green circle = Backend is running
- FAISS index is active
- Using Nomic embeddings

**🟡 Using Local Storage**
- Yellow circle = Backend offline
- Using simplified embeddings
- Still functional, less accurate

### Category Badges

```
┌──────────────┐
│  ecommerce   │  Blue badge for shopping sites
└──────────────┘

┌──────────────┐
│     news     │  Blue badge for news/articles
└──────────────┘

┌──────────────┐
│documentation │  Blue badge for docs
└──────────────┘
```

### Match Percentage

```
┌──────┐
│ 92% │  Green badge = High match (>80%)
└──────┘

┌──────┐
│ 75% │  Yellow badge = Medium match (60-80%)
└──────┘

┌──────┐
│ 55% │  Orange badge = Low match (<60%)
└──────┘
```

### Filter Buttons

```
[All]  ← Active (blue background)
[🛒 Shopping]  ← Inactive (white background)
[📰 News]  ← Inactive
```

## User Interactions

### 1. Search Flow

```
User types "machine learning"
        ↓
Input debounces (300ms)
        ↓
Query sent to backend
        ↓
Shows "Searching..."
        ↓
Results appear (10 URLs)
        ↓
User clicks result
        ↓
Page opens with highlights
```

### 2. Filter Flow

```
User clicks "🛒 Shopping"
        ↓
Button turns blue
        ↓
Compare button appears
        ↓
Search placeholder changes
        ↓
Results filter to ecommerce
```

### 3. Compare Flow

```
User clicks "⚖️ Compare"
        ↓
Compare mode activates
        ↓
Shopping filter auto-selected
        ↓
User types product name
        ↓
Shows comparison header
        ↓
Results ranked with %
```

## Color Scheme

### Primary Colors
- **Blue (#4285f4)**: Active states, links
- **Green (#34a853)**: Success, high match
- **Yellow (#ffeb3b)**: Highlights, warnings
- **Gray (#70757a)**: Secondary text

### Backgrounds
- **White (#ffffff)**: Cards, buttons
- **Light Gray (#f5f5f5)**: Page background
- **Light Blue (#e8f0fe)**: Category badges

### Text
- **Dark Gray (#333)**: Primary text
- **Medium Gray (#5f6368)**: Snippets
- **Light Gray (#70757a)**: URLs, metadata

## Responsive Design

### Popup Size
- Width: 450px (fixed)
- Min Height: 500px
- Max Height: 600px (scrollable)

### Elements
- Search input: Full width, 12px padding
- Filter buttons: Flex wrap, 8px gap
- Result cards: Full width, 12px padding
- Scrollable results: Max 400px height

## Animations

### Hover Effects
```
Button hover:
  background: #f0f0f0
  transition: 0.2s

Card hover:
  box-shadow: 0 2px 8px rgba(0,0,0,0.1)
  transform: translateY(-1px)
  transition: 0.2s
```

### Loading States
```
"Searching..." → Pulsing animation
"Loading..." → Fade in/out
```

## Accessibility

### Keyboard Navigation
- Tab through filters
- Enter to search
- Arrow keys in results
- Escape to close

### Screen Readers
- Alt text for icons
- ARIA labels
- Semantic HTML
- Focus indicators

## Browser Compatibility

### Tested On
- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Brave 1.30+
- ⚠️ Firefox (needs Manifest V3 support)
- ❌ Safari (no Manifest V3)

## Mobile View

Not applicable - Chrome extensions are desktop-only.

## Dark Mode

Currently uses light theme. Dark mode can be added:

```css
@media (prefers-color-scheme: dark) {
  body {
    background: #202124;
    color: #e8eaed;
  }
  /* ... more dark styles */
}
```

## Icon Sizes

### Required Icons
- 16x16px - Toolbar icon
- 48x48px - Extension management
- 128x128px - Chrome Web Store

### Current Status
- Icons folder created
- Placeholder icons needed
- Extension works without icons

## Performance Indicators

### Visual Feedback
- Instant: Button clicks
- <100ms: Filter changes
- <300ms: Search debounce
- <500ms: Results appear
- <1s: Page highlights

### Loading States
- "Loading..." - Initial load
- "Searching..." - Active search
- "Comparing..." - Comparison mode
- "No results" - Empty state

## Error States

### Backend Offline
```
┌─────────────────────────────────────┐
│  🟡 Using Local Storage             │
│  Backend is offline. Using          │
│  simplified embeddings.             │
└─────────────────────────────────────┘
```

### No Results
```
┌─────────────────────────────────────┐
│         No results found            │
│  Try different search terms or      │
│  browse more pages first.           │
└─────────────────────────────────────┘
```

### Search Error
```
┌─────────────────────────────────────┐
│  Error searching. Please try again. │
│  Check backend status.              │
└─────────────────────────────────────┘
```

## Tips for Screenshots

When creating actual screenshots:

1. **Popup**: Capture with 5-10 results
2. **Comparison**: Show 3-4 products with different %
3. **Highlights**: Show yellow highlights on real page
4. **Backend**: Show terminal with capture logs
5. **Stats**: Show with realistic numbers (50+ pages)

## Demo Data

For best screenshots, visit:
- Amazon, eBay (for comparison)
- HackerNews, Medium (for news)
- GitHub, MDN (for docs)
- YouTube (for video)
- Twitter (for social)

Then search for:
- "machine learning" (docs)
- "wireless headphones" (comparison)
- "javascript tutorial" (mixed)

---

**Visual Guide Complete** ✅
**Ready for Screenshots** ✅
**UI/UX Documented** ✅
