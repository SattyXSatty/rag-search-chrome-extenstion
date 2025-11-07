# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Chrome Browser                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Popup UI   │      │   Content    │      │ Background│ │
│  │  (popup.js)  │◄────►│   Script     │◄────►│  Service  │ │
│  │              │      │ (content.js) │      │  Worker   │ │
│  └──────────────┘      └──────────────┘      └─────┬─────┘ │
│         │                     │                     │        │
│         │                     │                     │        │
│         └─────────────────────┴─────────────────────┘        │
│                               │                               │
└───────────────────────────────┼───────────────────────────────┘
                                │
                                │ HTTP REST API
                                │
                    ┌───────────▼───────────┐
                    │   Python Backend      │
                    │   (Flask Server)      │
                    │   Port: 8000          │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐    ┌────────▼────────┐
            │ Nomic Embedder │    │  FAISS Index    │
            │ (768-dim)      │    │  (Cosine Sim)   │
            └────────────────┘    └─────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Persistent Storage  │
                    │  - faiss_index.pkl    │
                    │  - metadata.pkl       │
                    └───────────────────────┘
```

## Data Flow

### 1. Content Capture Flow

```
User visits website
        │
        ▼
┌───────────────────┐
│   content.js      │
│ - Extract text    │
│ - Remove scripts  │
│ - Chunk (500ch)   │
└────────┬──────────┘
         │ Message
         ▼
┌───────────────────┐
│  background.js    │
│ - Categorize URL  │
│ - Check excluded  │
└────────┬──────────┘
         │ HTTP POST /embed
         ▼
┌───────────────────┐
│  Backend Server   │
│ - Generate embed  │
│ - Normalize       │
└────────┬──────────┘
         │ Return embeddings
         ▼
┌───────────────────┐
│  background.js    │
│ - Store metadata  │
└────────┬──────────┘
         │ HTTP POST /add
         ▼
┌───────────────────┐
│  FAISS Index      │
│ - Add vectors     │
│ - Store metadata  │
│ - Auto-save       │
└───────────────────┘
```

### 2. Search Flow

```
User types query
        │
        ▼
┌───────────────────┐
│    popup.js       │
│ - Get query       │
│ - Get filter      │
└────────┬──────────┘
         │ Message
         ▼
┌───────────────────┐
│  background.js    │
│ - Forward query   │
└────────┬──────────┘
         │ HTTP POST /search
         ▼
┌───────────────────┐
│  Backend Server   │
│ - Embed query     │
│ - Search FAISS    │
│ - Filter category │
│ - Rank results    │
└────────┬──────────┘
         │ Return results
         ▼
┌───────────────────┐
│  background.js    │
│ - Group by URL    │
│ - Format results  │
└────────┬──────────┘
         │ Response
         ▼
┌───────────────────┐
│    popup.js       │
│ - Display results │
│ - Show snippets   │
└────────┬──────────┘
         │ User clicks
         ▼
┌───────────────────┐
│   content.js      │
│ - Highlight text  │
│ - Scroll to match │
└───────────────────┘
```

### 3. Product Comparison Flow

```
User clicks Shopping filter
        │
        ▼
┌───────────────────┐
│    popup.js       │
│ - Enable compare  │
│ - Set category    │
└────────┬──────────┘
         │
User types product name
         │
         ▼
┌───────────────────┐
│    popup.js       │
│ - Send query      │
└────────┬──────────┘
         │ Message (COMPARE_PRODUCTS)
         ▼
┌───────────────────┐
│  background.js    │
│ - Forward query   │
└────────┬──────────┘
         │ HTTP POST /compare
         ▼
┌───────────────────┐
│  Backend Server   │
│ - Embed query     │
│ - Search ecommerce│
│ - Group by URL    │
│ - Calc avg sim    │
│ - Rank products   │
└────────┬──────────┘
         │ Return products
         ▼
┌───────────────────┐
│    popup.js       │
│ - Show comparison │
│ - Display % match │
│ - Rank by score   │
└───────────────────┘
```

## Component Details

### Extension Components

#### 1. popup.html/js
**Purpose:** User interface for search and results

**Features:**
- Search input with debouncing
- Category filters
- Results display
- Comparison mode
- Backend status indicator

**State:**
- `currentFilter`: Active category
- `isCompareMode`: Comparison enabled
- `searchTimeout`: Debounce timer

#### 2. content.js
**Purpose:** Extract content and highlight matches

**Features:**
- DOM traversal
- Text extraction
- Content chunking
- Text highlighting
- Scroll to match

**Triggers:**
- Page load (DOMContentLoaded)
- DOM mutations (MutationObserver)
- Highlight requests (message)

#### 3. background.js
**Purpose:** Service worker for capture and search

**Features:**
- Content capture orchestration
- Embedding generation
- FAISS communication
- Local storage fallback
- Category detection

**Configuration:**
- `USE_BACKEND`: Enable/disable backend
- `BACKEND_URL`: Backend endpoint
- `EXCLUDED_DOMAINS`: Sites to skip
- `CATEGORY_PATTERNS`: Classification rules

### Backend Components

#### 1. Flask Server
**Purpose:** REST API for embeddings and search

**Endpoints:**
- `GET /health` - Health check
- `POST /embed` - Generate embeddings
- `POST /add` - Add to index
- `POST /search` - Search similar
- `POST /compare` - Compare products
- `GET /stats` - Get statistics
- `POST /save` - Manual save

#### 2. Nomic Embedder
**Purpose:** Generate semantic embeddings

**Model:** `nomic-ai/nomic-embed-text-v1.5`
**Dimension:** 768
**Normalization:** L2 (for cosine similarity)

**Features:**
- Batch processing
- GPU support (if available)
- Automatic normalization

#### 3. FAISS Index
**Purpose:** Fast similarity search

**Type:** IndexFlatIP (Inner Product)
**Similarity:** Cosine (via normalized vectors)
**Persistence:** Pickle serialization

**Operations:**
- `add()` - Add vectors
- `search()` - Find similar
- `ntotal` - Count vectors

#### 4. Metadata Store
**Purpose:** Store page information

**Structure:**
```python
{
  index_id: {
    'url': str,
    'title': str,
    'chunk': str,
    'chunkIndex': int,
    'category': str,
    'favicon': str,
    'timestamp': int,
    'added_at': str
  }
}
```

## Communication Protocol

### Extension ↔ Backend

#### Request: Embed
```json
POST /embed
{
  "texts": ["chunk1", "chunk2", ...]
}
```

#### Response: Embed
```json
{
  "embeddings": [[0.1, 0.2, ...], ...],
  "dimension": 768
}
```

#### Request: Add
```json
POST /add
{
  "embeddings": [[0.1, 0.2, ...], ...],
  "metadata": [
    {
      "url": "https://...",
      "chunk": "text...",
      "chunkIndex": 0,
      "title": "Page Title",
      "category": "ecommerce",
      ...
    }
  ]
}
```

#### Response: Add
```json
{
  "success": true,
  "total_vectors": 1234,
  "added": 10
}
```

#### Request: Search
```json
POST /search
{
  "query": "search text",
  "k": 50,
  "category": "ecommerce"  // optional
}
```

#### Response: Search
```json
{
  "results": [
    {
      "metadata": {...},
      "similarity": 0.85,
      "index": 123
    }
  ],
  "total_searched": 1234
}
```

## Storage Strategy

### Chrome Storage (Fallback)
```
meta_<hash>: {
  title, category, favicon, timestamp
}

chunk_<hash>_<index>: {
  text, embedding, url, chunkIndex
}

urlIndex: [url1, url2, ...]

categoryIndex: {
  ecommerce: [url1, url2],
  news: [url3, url4],
  ...
}
```

### Backend Storage
```
faiss_index.pkl:
  - FAISS IndexFlatIP
  - All vectors

metadata.pkl:
  - Dict[int, metadata]
  - Indexed by vector ID
```

## Scalability

### Current Capacity
- **Vectors:** 100k+
- **RAM:** ~2GB
- **Search Time:** <500ms
- **Storage:** ~500MB

### Optimization Options

#### 1. IVF Index (100k+ vectors)
```python
quantizer = faiss.IndexFlatIP(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
index.train(training_vectors)
```

#### 2. PQ Compression (1M+ vectors)
```python
index = faiss.IndexIVFPQ(
    quantizer, dimension, nlist, m, nbits
)
```

#### 3. GPU Acceleration
```python
res = faiss.StandardGpuResources()
index = faiss.index_cpu_to_gpu(res, 0, index)
```

## Security Considerations

### 1. Excluded Domains
- Gmail, WhatsApp, banking sites
- Login/auth pages
- Sensitive content

### 2. Local Storage
- All data stored locally
- No cloud sync
- User controls data

### 3. Backend Security
- Localhost only (no external access)
- No authentication (local use)
- CORS enabled for extension

### 4. Privacy
- No telemetry
- No external API calls (except model)
- User can disable backend

## Performance Optimization

### 1. Debouncing
- Search input: 300ms delay
- Prevents excessive API calls

### 2. Batching
- Embed multiple chunks together
- Reduces API overhead

### 3. Caching
- Chrome storage for metadata
- Quick stats without backend

### 4. Lazy Loading
- Load results on demand
- Paginate if needed

### 5. Auto-save
- Save index every 100 additions
- Prevents data loss

## Error Handling

### 1. Backend Offline
- Fallback to local embeddings
- Show status in popup
- Continue capturing

### 2. Embedding Failure
- Retry with exponential backoff
- Use simplified embeddings
- Log error

### 3. Storage Full
- Chrome storage limit: 10MB
- Backend: disk space
- Show warning to user

### 4. Search Timeout
- 5s timeout on backend calls
- Show error message
- Suggest retry

## Monitoring

### Backend Logs
```
Captured: <url> [<category>]
Stored in FAISS: X chunks, total: Y
Index saved with Z vectors
```

### Extension Console
```
Backend embedding error, using local
Backend search error, using local
Highlight error: <error>
```

### Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:8000/stats
```

## Future Enhancements

### 1. Distributed FAISS
- Multiple backend instances
- Load balancing
- Sharding by category

### 2. Real-time Sync
- WebSocket connection
- Live updates
- Multi-device sync

### 3. Advanced Analytics
- Browsing patterns
- Category trends
- Search analytics

### 4. ML Improvements
- Fine-tune embeddings
- Custom category models
- Personalized ranking

---

**Architecture Status:** Production-ready ✅
**Last Updated:** November 2025
**Version:** 1.0.0
