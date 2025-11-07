#!/usr/bin/env python3
"""Simple test for search functionality"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import time

print("🧪 Testing search with realistic data...")

# Create FAISS index
dimension = 384
index = faiss.IndexFlatIP(dimension)

# Load model
print("Loading model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Create test content
test_contents = [
    "Gaming laptop with RTX 4060 graphics card, 16GB RAM",
    "Dell XPS 13 ultrabook, lightweight laptop",
    "MacBook Pro M2 chip for developers",
    "Budget laptop under $500 for students",
    "ASUS ROG gaming laptop high refresh rate"
]

print(f"Creating embeddings for {len(test_contents)} items...")
embeddings = model.encode(test_contents, convert_to_numpy=True, normalize_embeddings=True)
index.add(embeddings.astype('float32'))

# Create metadata
current_time = time.time()
metadata_store = {
    i: {
        'url': f'https://bestbuy.com/laptop-{i}',
        'title': test_contents[i][:30],
        'chunk': test_contents[i],
        'category': 'ecommerce',
        'timestamp': current_time - (i * 86400)  # i days ago
    }
    for i in range(len(test_contents))
}

# Test search
query = "gaming laptop"
print(f"\n🔍 Searching for: '{query}'")

query_embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
distances, indices = index.search(query_embedding, k=5)

print(f"\n✅ Found {len(indices[0])} results:")
for i, idx in enumerate(indices[0]):
    if idx != -1 and int(idx) in metadata_store:
        meta = metadata_store[int(idx)]
        age_days = (current_time - meta['timestamp']) / 86400
        
        print(f"\n{i+1}. {meta['title']}")
        print(f"   URL: {meta['url']}")
        print(f"   Similarity: {distances[0][i]:.3f}")
        print(f"   Age: {age_days:.1f} days ago")
        
        # Test temporal score calculation
        age_days_capped = min(age_days, 100)
        temporal_score = np.exp(-age_days_capped / 7)
        print(f"   Temporal score: {temporal_score:.3f}")

print("\n✅ Test complete - no overflow errors!")
