#!/usr/bin/env python3
"""Check FAISS index status"""
import pickle
import os

if os.path.exists('faiss_index.pkl'):
    with open('faiss_index.pkl', 'rb') as f:
        index = pickle.load(f)
    print(f'✅ Index exists')
    print(f'📊 Total vectors: {index.ntotal}')
    
    if os.path.exists('metadata.pkl'):
        with open('metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
        print(f'📝 Metadata entries: {len(metadata)}')
        
        # Show sample
        if metadata:
            sample_key = list(metadata.keys())[0]
            sample = metadata[sample_key]
            print(f'\n📄 Sample entry:')
            print(f'   URL: {sample.get("url", "N/A")}')
            print(f'   Title: {sample.get("title", "N/A")[:50]}...')
            print(f'   Category: {sample.get("category", "N/A")}')
    else:
        print('⚠️ No metadata file found')
else:
    print('❌ No index file found')
    print('💡 The index will be created when you visit websites')
