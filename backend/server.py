from flask import Flask, request, jsonify
from flask_cors import CORS
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
INDEX_FILE = 'faiss_index.pkl'
METADATA_FILE = 'metadata.pkl'

# Use all-MiniLM-L6-v2 (lighter, faster, more stable)
# To use Nomic, change MODEL_NAME to 'nomic-ai/nomic-embed-text-v1.5' and DIMENSION to 768
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
DIMENSION = 384

# Cognitive AI flag - DISABLED BY DEFAULT until you want to enable it
USE_COGNITIVE_AI = os.getenv('USE_COGNITIVE_AI', 'false').lower() == 'true'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize
print(f"Loading embedding model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("✅ Model loaded successfully!")

# Load or create FAISS index
if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
    print("Loading existing index...")
    with open(INDEX_FILE, 'rb') as f:
        index = pickle.load(f)
    with open(METADATA_FILE, 'rb') as f:
        metadata_store = pickle.load(f)
    print(f"Loaded index with {index.ntotal} vectors")
else:
    print("Creating new index...")
    index = faiss.IndexFlatIP(DIMENSION)  # Inner product for cosine similarity
    metadata_store = {}

# Initialize Cognitive AI Orchestrator
orchestrator = None
if USE_COGNITIVE_AI and GEMINI_API_KEY:
    try:
        from orchestrator import CognitiveOrchestrator
        orchestrator = CognitiveOrchestrator(
            index=index,
            metadata_store=metadata_store,
            embedding_model=model,
            api_key=GEMINI_API_KEY
        )
        print("✅ Cognitive AI layer enabled")
    except Exception as e:
        print(f"⚠️ Cognitive AI initialization failed: {e}")
        print("   Falling back to basic search")
        USE_COGNITIVE_AI = False
else:
    print("ℹ️ Cognitive AI disabled (set GEMINI_API_KEY to enable)")

def save_index():
    """Save index and metadata to disk"""
    with open(INDEX_FILE, 'wb') as f:
        pickle.dump(index, f)
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(metadata_store, f)
    print(f"Index saved with {index.ntotal} vectors")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': MODEL_NAME,
        'total_vectors': index.ntotal,
        'dimension': DIMENSION
    })

@app.route('/embed', methods=['POST'])
def embed_texts():
    """Generate embeddings for texts"""
    try:
        data = request.json
        texts = data['texts']
        
        # Generate embeddings
        embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        
        return jsonify({
            'embeddings': embeddings.tolist(),
            'dimension': embeddings.shape[1]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add', methods=['POST'])
def add_to_index():
    """Add embeddings to FAISS index"""
    try:
        data = request.json
        embeddings = np.array(data['embeddings'], dtype='float32')
        metadata_list = data['metadata']
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        start_id = index.ntotal
        index.add(embeddings)
        
        # Store metadata
        for i, meta in enumerate(metadata_list):
            metadata_store[start_id + i] = {
                **meta,
                'added_at': datetime.now().isoformat()
            }
        
        # Save periodically
        if index.ntotal % 100 == 0:
            save_index()
        
        return jsonify({
            'success': True,
            'total_vectors': index.ntotal,
            'added': len(embeddings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Search for similar content with optional cognitive AI enhancement"""
    try:
        data = request.json
        query = data['query']
        k = data.get('k', 50)
        category_filter = data.get('category')
        use_cognitive = data.get('use_cognitive', USE_COGNITIVE_AI)
        
        # Use Cognitive AI if available and enabled
        if use_cognitive and orchestrator:
            print(f"🧠 Using Cognitive AI for query: {query}")
            response = orchestrator.search(query, category_filter)
            
            # Convert to legacy format for compatibility
            results = []
            for result in response.results:
                results.append({
                    'metadata': {
                        'url': result.url,
                        'title': result.title,
                        'chunk': result.snippet,
                        'category': result.category
                    },
                    'similarity': result.similarity,
                    'relevance_score': result.relevance_score,
                    'explanation': result.explanation,
                    'highlight_suggestions': result.highlight_suggestions
                })
            
            return jsonify({
                'results': results,
                'total_searched': index.ntotal,
                'cognitive_enhanced': True,
                'query_understanding': response.query_understanding,
                'search_strategy': response.search_strategy,
                'processing_time': response.processing_time,
                'suggestions': response.suggestions
            })
        
        # Fallback to basic search
        print(f"🔍 Using basic search for query: {query}")
        
        # Generate query embedding
        query_embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        
        # Search (get more results for filtering)
        search_k = k * 5 if category_filter else k
        distances, indices = index.search(query_embedding, min(search_k, index.ntotal))
        
        # Collect results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and int(idx) in metadata_store:
                meta = metadata_store[int(idx)]
                
                # Apply category filter
                if category_filter and meta.get('category') != category_filter:
                    continue
                
                results.append({
                    'metadata': meta,
                    'similarity': float(distances[0][i]),
                    'index': int(idx)
                })
                
                if len(results) >= k:
                    break
        
        return jsonify({
            'results': results,
            'total_searched': index.ntotal,
            'cognitive_enhanced': False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get index statistics"""
    try:
        categories = {}
        urls = set()
        
        for meta in metadata_store.values():
            cat = meta.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            urls.add(meta.get('url'))
        
        return jsonify({
            'total_vectors': index.ntotal,
            'total_urls': len(urls),
            'categories': categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare_products():
    """Compare products from ecommerce sites with cognitive AI"""
    try:
        data = request.json
        query = data['query']
        use_cognitive = data.get('use_cognitive', USE_COGNITIVE_AI)
        
        # Use Cognitive AI if available
        if use_cognitive and orchestrator:
            print(f"🧠 Using Cognitive AI for product comparison: {query}")
            response = orchestrator.compare_products(query)
            
            # Convert to product comparison format
            products = {}
            for result in response.results:
                url = result.url
                if url not in products:
                    products[url] = {
                        'url': url,
                        'title': result.title,
                        'favicon': '',
                        'chunks': [],
                        'avg_similarity': result.relevance_score,
                        'explanation': result.explanation
                    }
                
                products[url]['chunks'].append({
                    'text': result.snippet,
                    'similarity': result.similarity
                })
            
            sorted_products = sorted(products.values(), key=lambda x: x['avg_similarity'], reverse=True)
            
            return jsonify({
                'products': sorted_products[:10],
                'total_found': len(products),
                'cognitive_enhanced': True,
                'query_understanding': response.query_understanding,
                'suggestions': response.suggestions
            })
        
        # Fallback to basic comparison
        print(f"🔍 Using basic comparison for: {query}")
        
        # Search only in ecommerce category
        query_embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        distances, indices = index.search(query_embedding, min(100, index.ntotal))
        
        # Group by URL
        products = {}
        for i, idx in enumerate(indices[0]):
            if idx != -1 and int(idx) in metadata_store:
                meta = metadata_store[int(idx)]
                
                # Only ecommerce
                if meta.get('category') != 'ecommerce':
                    continue
                
                url = meta.get('url')
                if url not in products:
                    products[url] = {
                        'url': url,
                        'title': meta.get('title'),
                        'favicon': meta.get('favicon'),
                        'chunks': [],
                        'avg_similarity': 0
                    }
                
                products[url]['chunks'].append({
                    'text': meta.get('chunk'),
                    'similarity': float(distances[0][i])
                })
        
        # Calculate average similarity
        for product in products.values():
            product['avg_similarity'] = sum(c['similarity'] for c in product['chunks']) / len(product['chunks'])
        
        # Sort by similarity
        sorted_products = sorted(products.values(), key=lambda x: x['avg_similarity'], reverse=True)
        
        return jsonify({
            'products': sorted_products[:10],
            'total_found': len(products),
            'cognitive_enhanced': False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def manual_save():
    """Manually trigger save"""
    try:
        save_index()
        return jsonify({'success': True, 'message': 'Index saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug_index():
    """Debug endpoint to see what's in the index"""
    try:
        # Get sample URLs
        urls = set()
        categories = {}
        sample_chunks = []
        
        for idx, meta in list(metadata_store.items())[:10]:
            urls.add(meta.get('url'))
            cat = meta.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            sample_chunks.append({
                'url': meta.get('url'),
                'title': meta.get('title', '')[:50],
                'chunk': meta.get('chunk', '')[:100],
                'category': cat
            })
        
        return jsonify({
            'total_vectors': index.ntotal,
            'total_urls': len(urls),
            'categories': categories,
            'sample_urls': list(urls)[:5],
            'sample_chunks': sample_chunks[:5]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print("FAISS Backend Server Starting")
    print(f"Model: {MODEL_NAME}")
    print(f"Dimension: {DIMENSION}")
    print(f"Total vectors: {index.ntotal}")
    print(f"{'='*50}\n")
    
    try:
        app.run(host='0.0.0.0', port=8000, debug=True)
    finally:
        print("\nShutting down... Saving index...")
        save_index()
        print("Index saved. Goodbye!")
