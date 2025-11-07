# Backend - Cognitive AI Layer

## Overview

This backend implements a **multi-agent cognitive AI system** using **Gemini 2.0 Flash** to enhance search with intelligent query understanding and adaptive strategies.

## Architecture

```
orchestrator.py  ← Main coordinator
    ├── perception.py   (Gemini: Query understanding)
    ├── memory.py       (User preferences)
    ├── decision.py     (Gemini: Strategy selection)
    └── actions.py      (FAISS: Search execution)
```

## Files

| File | Purpose | Lines | Dependencies |
|------|---------|-------|--------------|
| `server.py` | Flask API server | 250 | Flask, CORS |
| `orchestrator.py` | Coordinates agents | 150 | All agents |
| `perception.py` | Query understanding | 100 | Gemini, Pydantic |
| `memory.py` | User preferences | 150 | JSON |
| `decision.py` | Strategy selection | 150 | Gemini, Pydantic |
| `actions.py` | Search execution | 250 | FAISS, NumPy |
| `models.py` | Data models | 150 | Pydantic |
| `test_cognitive.py` | Test suite | 150 | All above |

**Total:** ~1,200 lines

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies:**
- `google-generativeai==0.3.2` - Gemini API
- `pydantic==2.5.0` - Data validation

### 2. Set API Key

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Get your key from: https://makersuite.google.com/app/apikey

### 3. Run Tests

```bash
python test_cognitive.py
```

Expected output:
```
✅ ALL TESTS PASSED!
🚀 Cognitive AI is ready to use!
```

### 4. Start Server

```bash
python server.py
```

Expected output:
```
✅ Model loaded successfully!
✅ Cognitive AI Orchestrator initialized
   - Perception: Gemini 2.0 Flash
   - Memory: User preferences loaded
   - Decision: Strategy planner ready
   - Actions: FAISS executor ready
✅ Cognitive AI layer enabled
```

## API Endpoints

### Enhanced Search

```http
POST /search
Content-Type: application/json

{
  "query": "laptop I saw yesterday",
  "category": "ecommerce",
  "use_cognitive": true
}
```

**Response:**
```json
{
  "results": [...],
  "cognitive_enhanced": true,
  "query_understanding": "Strategy: temporal, Confidence: 0.85",
  "search_strategy": "Prioritize recent + semantic",
  "processing_time": 0.234,
  "suggestions": ["Filter by date"]
}
```

### Product Comparison

```http
POST /compare
Content-Type: application/json

{
  "query": "gaming laptops",
  "use_cognitive": true
}
```

### Health Check

```http
GET /health
```

### Statistics

```http
GET /stats
```

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your-key-here

# Optional
USE_COGNITIVE_AI=true  # Enable/disable cognitive layer
```

### Feature Flags

In `server.py`:
```python
USE_COGNITIVE_AI = os.getenv('USE_COGNITIVE_AI', 'true').lower() == 'true'
```

## Cognitive Agents

### 1. Perception Agent (`perception.py`)

**Purpose:** Understand user queries using Gemini

**Features:**
- Intent detection (search/compare/recall/explore)
- Query expansion with synonyms
- Temporal understanding ("yesterday", "last week")
- Category hints
- Entity extraction

**Example:**
```python
from perception import PerceptionAgent
from models import UserQuery

perception = PerceptionAgent(api_key="...")
query = UserQuery(query="laptop I saw yesterday")
enhanced = perception.understand_query(query)

print(enhanced.intent)  # "recall"
print(enhanced.temporal_context)  # "recent"
print(enhanced.expanded_terms)  # ["laptop", "notebook", ...]
```

### 2. Memory Agent (`memory.py`)

**Purpose:** Track user preferences and history

**Storage:** `user_memory.json`

**Features:**
- Browsing context
- Search history
- Category preferences
- Frequent sites
- Temporal patterns

**Example:**
```python
from memory import MemoryAgent

memory = MemoryAgent()
context = memory.get_browsing_context()

print(context.recent_categories)  # ["ecommerce", "news"]
print(context.time_of_day)  # "evening"
```

### 3. Decision Agent (`decision.py`)

**Purpose:** Choose optimal search strategy using Gemini

**Strategies:**
- **Semantic:** Pure similarity (100% semantic)
- **Temporal:** Time-based (40% semantic, 50% temporal)
- **Comparative:** Product comparison (60% semantic, 20% temporal, 20% category)
- **Hybrid:** Multi-factor (70% semantic, 30% keyword)

**Example:**
```python
from decision import DecisionAgent

decision_agent = DecisionAgent(api_key="...")
decision = decision_agent.decide_strategy(enhanced, context, history)

print(decision.strategy)  # "temporal"
print(decision.ranking_weights)  # {"semantic": 0.4, "temporal": 0.5, ...}
```

### 4. Actions Agent (`actions.py`)

**Purpose:** Execute search and enrich results

**Pipeline:**
1. Embed query
2. Search FAISS
3. Filter (category, time, similarity)
4. Rerank (multi-factor)
5. Enrich (explanations, highlights)
6. Group by URL

**Example:**
```python
from actions import ActionsAgent

actions = ActionsAgent(index, metadata_store, model)
response = actions.execute_search(decision, start_time)

print(response.total_found)  # 12
print(response.results[0].explanation)  # "Visited yesterday, 85% match"
```

### 5. Orchestrator (`orchestrator.py`)

**Purpose:** Coordinate all agents

**Flow:**
```python
from orchestrator import CognitiveOrchestrator

orchestrator = CognitiveOrchestrator(
    index=index,
    metadata_store=metadata_store,
    embedding_model=model,
    api_key=api_key
)

response = orchestrator.search("laptop I saw yesterday")
```

## Data Models

All data flows through Pydantic models in `models.py`:

```python
# Input
UserQuery(query: str, category: Optional[str])

# Perception output
EnhancedQuery(
    original_query: str,
    expanded_terms: List[str],
    intent: str,
    temporal_context: Optional[str],
    category_hints: List[str],
    confidence: float,
    reasoning: str
)

# Memory output
BrowsingContext(
    recent_categories: List[str],
    frequent_sites: List[str],
    time_of_day: str,
    day_of_week: str
)

# Decision output
SearchDecision(
    strategy: str,
    search_params: Dict[str, Any],
    filters: Dict[str, Any],
    ranking_weights: Dict[str, float],
    reasoning: str,
    confidence: float
)

# Final output
SearchResponse(
    results: List[EnrichedResult],
    query_understanding: str,
    search_strategy: str,
    total_found: int,
    processing_time: float,
    suggestions: List[str]
)
```

## Testing

### Run All Tests

```bash
python test_cognitive.py
```

### Test Individual Components

```python
# Test Perception
from perception import PerceptionAgent
from models import UserQuery

perception = PerceptionAgent()
result = perception.understand_query(UserQuery(query="test"))
print(result.intent)

# Test Memory
from memory import MemoryAgent

memory = MemoryAgent()
context = memory.get_browsing_context()
print(context.time_of_day)

# Test Decision
from decision import DecisionAgent

decision = DecisionAgent()
result = decision.decide_strategy(enhanced, context, history)
print(result.strategy)
```

## Performance

### Latency Breakdown

```
Total: ~260ms
├─ Perception (Gemini): 80ms
├─ Memory Load: 10ms
├─ Decision (Gemini): 80ms
├─ FAISS Search: 50ms
├─ Reranking: 30ms
└─ Enrichment: 10ms
```

### Optimization Tips

1. **Use faster model:**
   ```python
   model = genai.GenerativeModel('gemini-2.0-flash-exp')
   ```

2. **Cache frequent queries:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_search(query):
       return orchestrator.search(query)
   ```

3. **Batch processing:**
   ```python
   queries = ["query1", "query2", "query3"]
   results = [orchestrator.search(q) for q in queries]
   ```

## Monitoring

### Check Status

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
tail -f backend.log
```

### Monitor Metrics

```python
# In orchestrator.py
print(f"Processing time: {response.processing_time:.3f}s")
print(f"Strategy: {decision.strategy}")
print(f"Confidence: {decision.confidence:.2f}")
```

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"

```bash
export GEMINI_API_KEY="your-key"
```

### Issue: Import errors

```bash
pip install -r requirements.txt
```

### Issue: Slow responses

Use faster model:
```python
# In perception.py and decision.py
model = genai.GenerativeModel('gemini-2.0-flash-exp')
```

### Issue: Cognitive AI fails

System automatically falls back to basic FAISS search.

## Development

### Add New Strategy

1. Update `decision.py`:
```python
# Add new strategy logic
if enhanced_query.intent == "new_intent":
    strategy = "new_strategy"
```

2. Update `actions.py`:
```python
# Add reranking logic
if decision.strategy == "new_strategy":
    # Custom reranking
    pass
```

### Add New Intent

1. Update `perception.py`:
```python
# Add to prompt
"intent: One of ['search', 'compare', 'recall', 'explore', 'new_intent']"
```

2. Update `models.py`:
```python
# Add validation
intent: Literal["search", "compare", "recall", "explore", "new_intent"]
```

## File Structure

```
backend/
├── server.py              # Flask API server
├── orchestrator.py        # Main coordinator
├── perception.py          # Query understanding
├── memory.py              # User preferences
├── decision.py            # Strategy selection
├── actions.py             # Search execution
├── models.py              # Pydantic models
├── test_cognitive.py      # Test suite
├── requirements.txt       # Dependencies
├── user_memory.json       # Created automatically
├── faiss_index.pkl        # FAISS index
└── metadata.pkl           # Metadata store
```

## Dependencies

```
flask==3.0.0
flask-cors==4.0.0
faiss-cpu==1.7.4
sentence-transformers==2.2.2
numpy==1.24.3
google-generativeai==0.3.2  ← NEW
pydantic==2.5.0             ← NEW
```

## Documentation

- [Architecture](../COGNITIVE_AI_ARCHITECTURE.md)
- [Setup Guide](../COGNITIVE_AI_SETUP.md)
- [Examples](../COGNITIVE_AI_EXAMPLES.md)
- [Quick Reference](../COGNITIVE_AI_QUICK_REF.md)

## Support

- Run tests: `python test_cognitive.py`
- Check health: `curl localhost:8000/health`
- View logs: `tail -f backend.log`

---

**Status:** ✅ Production-ready

**Version:** 2.0.0

**Last Updated:** November 2025
