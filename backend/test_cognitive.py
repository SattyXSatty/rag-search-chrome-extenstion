#!/usr/bin/env python3
"""
Test script for Cognitive AI layer
Run: python test_cognitive.py
"""

import os
import sys

# Check environment
print("🔍 Checking environment...")
print(f"   Python: {sys.version.split()[0]}")

# Check API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not set!")
    print("   Run: export GEMINI_API_KEY='your-key-here'")
    sys.exit(1)
else:
    print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...")

# Check dependencies
print("\n📦 Checking dependencies...")
try:
    import google.generativeai as genai
    print("✅ google-generativeai installed")
except ImportError:
    print("❌ google-generativeai not installed")
    print("   Run: pip install google-generativeai")
    sys.exit(1)

try:
    from pydantic import BaseModel
    print("✅ pydantic installed")
except ImportError:
    print("❌ pydantic not installed")
    print("   Run: pip install pydantic")
    sys.exit(1)

try:
    import faiss
    print("✅ faiss installed")
except ImportError:
    print("❌ faiss not installed")
    print("   Run: pip install faiss-cpu")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers installed")
except ImportError:
    print("❌ sentence-transformers not installed")
    print("   Run: pip install sentence-transformers")
    sys.exit(1)

# Test Gemini connection
print("\n🧪 Testing Gemini API...")
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Say 'Hello from Gemini!'")
    print(f"✅ Gemini response: {response.text[:50]}...")
except Exception as e:
    print(f"❌ Gemini API error: {e}")
    sys.exit(1)

# Test Perception Agent
print("\n🧪 Testing Perception Agent...")
try:
    from perception import PerceptionAgent
    from models import UserQuery
    
    perception = PerceptionAgent(api_key=api_key)
    query = UserQuery(query="laptop I saw yesterday")
    enhanced = perception.understand_query(query)
    
    print(f"✅ Perception working!")
    print(f"   Original: {enhanced.original_query}")
    print(f"   Intent: {enhanced.intent}")
    print(f"   Expanded: {enhanced.expanded_terms[:3]}")
    print(f"   Confidence: {enhanced.confidence:.2f}")
except Exception as e:
    print(f"❌ Perception error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Memory Agent
print("\n🧪 Testing Memory Agent...")
try:
    from memory import MemoryAgent
    
    memory = MemoryAgent()
    context = memory.get_browsing_context()
    
    print(f"✅ Memory working!")
    print(f"   Time of day: {context.time_of_day}")
    print(f"   Day: {context.day_of_week}")
except Exception as e:
    print(f"❌ Memory error: {e}")
    sys.exit(1)

# Test Decision Agent
print("\n🧪 Testing Decision Agent...")
try:
    from decision import DecisionAgent
    
    decision_agent = DecisionAgent(api_key=api_key)
    history = memory.get_search_history()
    decision = decision_agent.decide_strategy(enhanced, context, history)
    
    print(f"✅ Decision working!")
    print(f"   Strategy: {decision.strategy}")
    print(f"   Confidence: {decision.confidence:.2f}")
    print(f"   Reasoning: {decision.reasoning[:60]}...")
except Exception as e:
    print(f"❌ Decision error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test full pipeline
print("\n🧪 Testing Full Pipeline...")
try:
    import numpy as np
    import pickle
    
    # Create dummy FAISS index
    dimension = 384
    index = faiss.IndexFlatIP(dimension)
    
    # Load model for realistic embeddings
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Create realistic test content
    test_contents = [
        "Gaming laptop with RTX 4060 graphics card, 16GB RAM, perfect for gaming",
        "Dell XPS 13 ultrabook, lightweight and portable laptop for work",
        "MacBook Pro M2 chip, excellent for developers and creative work",
        "Budget laptop under $500, good for students and basic tasks",
        "ASUS ROG gaming laptop with high refresh rate display",
        "Lenovo ThinkPad business laptop with long battery life",
        "HP Pavilion laptop for everyday computing and entertainment",
        "Microsoft Surface laptop with touchscreen display",
        "Acer Aspire laptop with SSD storage and fast performance",
        "Samsung Galaxy Book laptop with AMOLED display"
    ]
    
    # Generate realistic embeddings
    embeddings = model.encode(test_contents, convert_to_numpy=True, normalize_embeddings=True)
    index.add(embeddings.astype('float32'))
    
    # Create realistic metadata with recent timestamps
    import time
    current_time = time.time()
    metadata_store = {
        i: {
            'url': f'https://bestbuy.com/laptop-{i}',
            'title': f'Laptop {i}: {test_contents[i][:30]}...',
            'chunk': test_contents[i],
            'category': 'ecommerce',
            'timestamp': current_time - (i * 86400)  # Each laptop from i days ago
        }
        for i in range(10)
    }
    
    # Load model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Test orchestrator
    from orchestrator import CognitiveOrchestrator
    
    orchestrator = CognitiveOrchestrator(
        index=index,
        metadata_store=metadata_store,
        embedding_model=model,
        api_key=api_key
    )
    
    print(f"✅ Orchestrator initialized!")
    
    # Test search
    print("\n🔍 Testing search: 'laptop I saw yesterday'")
    response = orchestrator.search("laptop I saw yesterday", category="ecommerce")
    
    print(f"✅ Search complete!")
    print(f"   Found: {response.total_found} results")
    print(f"   Processing time: {response.processing_time:.3f}s")
    print(f"   Strategy: {response.search_strategy[:60]}...")
    
    if response.results:
        print(f"\n   Top result:")
        top = response.results[0]
        print(f"   - URL: {top.url}")
        print(f"   - Title: {top.title[:50]}...")
        print(f"   - Similarity: {top.similarity:.2f}")
        print(f"   - Relevance: {top.relevance_score:.2f}")
        print(f"   - Explanation: {top.explanation}")
    
except Exception as e:
    print(f"❌ Pipeline error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\n🚀 Cognitive AI is ready to use!")
print("\nNext steps:")
print("1. Start the server: python server.py")
print("2. Load the Chrome extension")
print("3. Start browsing and searching!")
