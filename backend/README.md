# FAISS Backend Server

Python backend for Web Memory RAG extension using Nomic embeddings and FAISS indexing.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run server:
```bash
python server.py
```

Server will start on http://localhost:8000

## Endpoints

- `GET /health` - Health check
- `POST /embed` - Generate embeddings
- `POST /add` - Add to FAISS index
- `POST /search` - Search similar content
- `POST /compare` - Compare ecommerce products
- `GET /stats` - Get statistics
- `POST /save` - Manually save index

## Data Persistence

- `faiss_index.pkl` - FAISS index
- `metadata.pkl` - Metadata store

These files are automatically saved and loaded on startup.
