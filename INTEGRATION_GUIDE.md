# Integration Guide: Nomic Embeddings & FAISS

This guide shows how to upgrade from the simplified implementation to production-ready Nomic embeddings and FAISS indexing.

## Option 1: Nomic API Integration

### Step 1: Get Nomic API Key
1. Sign up at https://atlas.nomic.ai/
2. Get your API key from the dashboard

### Step 2: Update background.js

Replace the `getEmbeddings` function:

```javascript
async function getEmbeddings(texts) {
  const response = await fetch('https://api-atlas.nomic.ai/v1/embedding/text', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_NOMIC_API_KEY',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      texts: texts,
      model: 'nomic-embed-text-v1.5',
      task_type: 'search_document'
    })
  });
  
  const data = await response.json();
  return data.embeddings;
}
```

## Option 2: Local Python Backend with FAISS

### Step 1: Create Python Backend

Create `backend/server.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

app = Flask(__name__)
CORS(app)

# Load model
model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)

# Initialize FAISS index
dimension = 768  # Nomic embedding dimension
index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
metadata_store = {}

@app.route('/embed', methods=['POST'])
def embed_texts():
    texts = request.json['texts']
    embeddings = model.encode(texts, convert_to_numpy=True)
    return jsonify({'embeddings': embeddings.tolist()})

@app.route('/add', methods=['POST'])
def add_to_index():
    data = request.json
    embeddings = np.array(data['embeddings'], dtype='float32')
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Add to index
    start_id = index.ntotal
    index.add(embeddings)
    
    # Store metadata
    for i, meta in enumerate(data['metadata']):
        metadata_store[start_id + i] = meta
    
    return jsonify({'success': True, 'total': index.ntotal})

@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    k = request.json.get('k', 10)
    
    # Get query embedding
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    
    # Search
    distances, indices = index.search(query_embedding, k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            results.append({
                'metadata': metadata_store.get(int(idx), {}),
                'similarity': float(distances[0][i])
            })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(port=8000)
```

### Step 2: Install Dependencies

```bash
pip install flask flask-cors faiss-cpu sentence-transformers numpy
```

### Step 3: Update Extension background.js

```javascript
const BACKEND_URL = 'http://localhost:8000';

async function getEmbeddings(texts) {
  const response = await fetch(`${BACKEND_URL}/embed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texts })
  });
  const data = await response.json();
  return data.embeddings;
}

async function storePageData(pageData) {
  const { url, embeddings, chunks, ...metadata } = pageData;
  
  // Send to backend
  await fetch(`${BACKEND_URL}/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      embeddings: embeddings,
      metadata: chunks.map((chunk, i) => ({
        url, chunk, chunkIndex: i, ...metadata
      }))
    })
  });
}

async function handleSearch(query) {
  const response = await fetch(`${BACKEND_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, k: 50 })
  });
  
  const data = await response.json();
  
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
      similarity: result.similarity
    });
  }
  
  return Object.values(grouped).slice(0, 10);
}
```

## Option 3: Hybrid Approach

Use Nomic API for embeddings but keep Chrome storage for small-scale deployments:

1. Replace `getEmbeddings` with Nomic API call
2. Keep existing storage and search logic
3. Upgrade to backend when you have >10,000 pages indexed

## Performance Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Simplified (current) | No dependencies, works offline | Less accurate, slower at scale |
| Nomic API | High quality embeddings | Requires API key, online only |
| Local Backend | Best performance, offline | Requires Python setup |

## Next Steps

1. Start with current implementation to test functionality
2. Add Nomic API for better embeddings
3. Scale to FAISS backend when you have significant data

## Testing

Test the integration:

```javascript
// In browser console after loading extension
chrome.runtime.sendMessage({
  type: 'SEARCH_CONTENT',
  query: 'your search query'
}, console.log);
```
