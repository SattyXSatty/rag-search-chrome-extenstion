# Cognitive AI Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New dependencies added:**
- `google-generativeai==0.3.2` - Gemini API
- `pydantic==2.5.0` - Data validation

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 3. Set Environment Variable

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Windows:**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Or create `.env` file:**
```bash
# backend/.env
GEMINI_API_KEY=your-api-key-here
USE_COGNITIVE_AI=true
```

### 4. Start Backend

```bash
cd backend
python server.py
```

You should see:
```
✅ Model loaded successfully!
✅ Cognitive AI Orchestrator initialized
   - Perception: Gemini 2.0 Flash
   - Memory: User preferences loaded
   - Decision: Strategy planner ready
   - Actions: FAISS executor ready
✅ Cognitive AI layer enabled
```

## Verification

### Test Cognitive AI

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop I saw yesterday",
    "use_cognitive": true
  }'
```

**Expected response:**
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

### Check Logs

Look for cognitive pipeline logs:
```
🧠 COGNITIVE SEARCH PIPELINE
1️⃣ PERCEPTION: Understanding query...
2️⃣ MEMORY: Loading user context...
3️⃣ DECISION: Planning search strategy...
4️⃣ ACTIONS: Executing search...
5️⃣ MEMORY: Recording search...
✅ SEARCH COMPLETE
```

## Configuration

### Enable/Disable Cognitive AI

**Disable temporarily:**
```bash
export USE_COGNITIVE_AI=false
python server.py
```

**Disable per request:**
```json
{
  "query": "test",
  "use_cognitive": false
}
```

### Adjust Gemini Model

Edit `perception.py` and `decision.py`:
```python
self.model = genai.GenerativeModel(
    'gemini-2.0-flash-exp',  # Change model here
    generation_config={
        "response_mime_type": "application/json"
    }
)
```

**Available models:**
- `gemini-2.0-flash-exp` - Fast, recommended
- `gemini-1.5-pro` - More accurate, slower
- `gemini-1.5-flash` - Balanced

## File Structure

```
backend/
├── server.py              # Main Flask server (updated)
├── orchestrator.py        # NEW: Main coordinator
├── perception.py          # NEW: Query understanding
├── memory.py              # NEW: User preferences
├── decision.py            # NEW: Strategy selection
├── actions.py             # NEW: Search execution
├── models.py              # NEW: Pydantic models
├── requirements.txt       # Updated dependencies
├── user_memory.json       # Created automatically
├── faiss_index.pkl        # Existing
└── metadata.pkl           # Existing
```

## Usage Examples

### Example 1: Recall Recent Content

**Query:** "laptop I saw yesterday"

**Cognitive AI Processing:**
1. **Perception:** Detects "recall" intent, temporal context "recent"
2. **Memory:** Loads recent ecommerce browsing
3. **Decision:** Chooses "temporal" strategy, prioritizes last 2 days
4. **Actions:** Searches with 50% temporal weight, 40% semantic
5. **Result:** Returns laptop pages from yesterday, ranked by recency

### Example 2: Product Comparison

**Query:** "compare gaming laptops"

**Cognitive AI Processing:**
1. **Perception:** Detects "compare" intent, category "ecommerce"
2. **Memory:** Loads shopping preferences
3. **Decision:** Chooses "comparative" strategy
4. **Actions:** Groups by URL, ranks by avg similarity
5. **Result:** Returns top 10 laptop products across sites

### Example 3: General Search

**Query:** "machine learning tutorials"

**Cognitive AI Processing:**
1. **Perception:** Detects "search" intent, category "docs"
2. **Memory:** Loads recent doc browsing
3. **Decision:** Chooses "semantic" strategy
4. **Actions:** Pure similarity search
5. **Result:** Returns most relevant tutorial pages

### Example 4: Exploratory Browsing

**Query:** "interesting tech news"

**Cognitive AI Processing:**
1. **Perception:** Detects "explore" intent, category "news"
2. **Memory:** Loads news preferences
3. **Decision:** Chooses "hybrid" strategy
4. **Actions:** Balances semantic + diversity
5. **Result:** Returns varied tech news articles

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"

**Solution:**
```bash
export GEMINI_API_KEY="your-key"
# Or add to .env file
```

### Issue: "Cognitive AI initialization failed"

**Check:**
1. API key is valid
2. Internet connection works
3. Dependencies installed: `pip install google-generativeai pydantic`

**Fallback:**
System automatically falls back to basic search if cognitive AI fails.

### Issue: Slow responses (>1s)

**Solutions:**
1. Use faster model: `gemini-2.0-flash-exp`
2. Disable cognitive AI for speed: `use_cognitive: false`
3. Cache frequent queries (future enhancement)

### Issue: "Module not found"

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Memory file errors

**Solution:**
```bash
# Delete and recreate
rm user_memory.json
# Will be created automatically on first search
```

## API Reference

### Search with Cognitive AI

```http
POST /search
Content-Type: application/json

{
  "query": "your search query",
  "category": "ecommerce",  // optional
  "k": 50,                  // optional, default 50
  "use_cognitive": true     // optional, default true
}
```

**Response:**
```json
{
  "results": [
    {
      "metadata": {...},
      "similarity": 0.85,
      "relevance_score": 0.92,
      "explanation": "Visited yesterday, 85% match",
      "highlight_suggestions": ["keyword1", "keyword2"]
    }
  ],
  "cognitive_enhanced": true,
  "query_understanding": "Strategy: temporal, Confidence: 0.85",
  "search_strategy": "Prioritize recent + semantic",
  "processing_time": 0.234,
  "suggestions": ["Filter by date", "Compare products"]
}
```

### Compare Products

```http
POST /compare
Content-Type: application/json

{
  "query": "gaming laptop",
  "use_cognitive": true
}
```

**Response:**
```json
{
  "products": [
    {
      "url": "...",
      "title": "...",
      "avg_similarity": 0.92,
      "explanation": "Product match: 92%",
      "chunks": [...]
    }
  ],
  "cognitive_enhanced": true,
  "query_understanding": "...",
  "suggestions": [...]
}
```

## Performance Tuning

### Optimize for Speed

```python
# In orchestrator.py
# Reduce LLM calls by caching
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_perception(query: str):
    return perception.understand_query(query)
```

### Optimize for Accuracy

```python
# In decision.py
# Use more powerful model
self.model = genai.GenerativeModel('gemini-1.5-pro')
```

### Batch Processing

```python
# Process multiple queries at once
queries = ["query1", "query2", "query3"]
results = [orchestrator.search(q) for q in queries]
```

## Monitoring

### Check System Status

```bash
curl http://localhost:8000/health
```

### View Statistics

```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "total_vectors": 1234,
  "total_urls": 567,
  "categories": {
    "ecommerce": 234,
    "news": 123,
    "docs": 89
  }
}
```

### Monitor Logs

```bash
# Watch logs in real-time
tail -f backend.log

# Or run with verbose logging
python server.py --verbose
```

## Best Practices

1. **Always set GEMINI_API_KEY** before starting server
2. **Monitor API usage** - Gemini has rate limits
3. **Use fallback** - Set `use_cognitive: false` for speed-critical queries
4. **Clear memory** - Delete `user_memory.json` to reset preferences
5. **Test strategies** - Try different queries to see which strategy is chosen

## Next Steps

1. ✅ Set up Gemini API key
2. ✅ Install dependencies
3. ✅ Start backend server
4. ✅ Test with sample queries
5. 📝 Monitor logs and performance
6. 🎯 Customize strategies in `decision.py`
7. 🚀 Deploy to production

## Support

- **Architecture:** See `COGNITIVE_AI_ARCHITECTURE.md`
- **Issues:** Check troubleshooting section above
- **Logs:** Enable verbose logging for debugging

---

**Ready to use!** 🚀

The cognitive AI layer is now integrated and will automatically enhance all searches when enabled.
