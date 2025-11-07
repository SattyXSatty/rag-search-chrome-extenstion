# Visual Flow Diagrams

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│                    Types: "laptop I saw yesterday"               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CHROME EXTENSION                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Popup UI   │◄──►│   Content    │◄──►│  Background  │     │
│  │  (Search)    │    │   (Capture)  │    │   (Manage)   │     │
│  └──────────────┘    └──────────────┘    └──────┬───────┘     │
└────────────────────────────────────────────────────┼────────────┘
                                                     │ HTTP
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE AI BACKEND                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              ORCHESTRATOR                              │    │
│  │         (Coordinates all agents)                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐              │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │ PERCEPTION  │    │   MEMORY    │    │  DECISION   │       │
│  │   (Gemini)  │    │  (Storage)  │    │  (Gemini)   │       │
│  └─────────────┘    └─────────────┘    └─────────────┘       │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             ▼                                    │
│                      ┌─────────────┐                           │
│                      │   ACTIONS   │                           │
│                      │   (FAISS)   │                           │
│                      └─────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Search Pipeline Flow

```
START: User Query "laptop I saw yesterday"
│
├─► STEP 1: PERCEPTION AGENT
│   ├─ Input: "laptop I saw yesterday"
│   ├─ LLM: Gemini 2.0 Flash
│   ├─ Process:
│   │   ├─ Detect intent: "recall"
│   │   ├─ Expand terms: ["laptop", "notebook", "computer"]
│   │   ├─ Temporal: "yesterday" → recent
│   │   └─ Category: ["ecommerce"]
│   └─ Output: EnhancedQuery
│       ├─ intent: "recall"
│       ├─ expanded_terms: [...]
│       ├─ temporal_context: "recent"
│       └─ confidence: 0.9
│
├─► STEP 2: MEMORY AGENT
│   ├─ Load: user_memory.json
│   ├─ Process:
│   │   ├─ Recent categories: ["ecommerce", "news"]
│   │   ├─ Frequent sites: ["bestbuy.com", "amazon.com"]
│   │   ├─ Time of day: "evening"
│   │   └─ Search history: last 10 queries
│   └─ Output: BrowsingContext
│       ├─ recent_categories: [...]
│       ├─ frequent_sites: [...]
│       └─ time_of_day: "evening"
│
├─► STEP 3: DECISION AGENT
│   ├─ Input: EnhancedQuery + BrowsingContext
│   ├─ LLM: Gemini 2.0 Flash
│   ├─ Process:
│   │   ├─ Analyze: Intent is "recall" + temporal "recent"
│   │   ├─ Choose: "temporal" strategy
│   │   ├─ Set weights:
│   │   │   ├─ semantic_similarity: 0.4
│   │   │   ├─ temporal_relevance: 0.5
│   │   │   └─ category_match: 0.1
│   │   └─ Time window: 2 days
│   └─ Output: SearchDecision
│       ├─ strategy: "temporal"
│       ├─ search_params: {...}
│       ├─ ranking_weights: {...}
│       └─ confidence: 0.85
│
├─► STEP 4: ACTIONS AGENT
│   ├─ Input: SearchDecision
│   ├─ Process:
│   │   ├─ 4.1: Embed query
│   │   │   └─ "laptop notebook computer" → [0.1, 0.2, ...]
│   │   │
│   │   ├─ 4.2: Search FAISS
│   │   │   ├─ Query vector: [0.1, 0.2, ...]
│   │   │   ├─ k: 50 results
│   │   │   └─ Results: [(idx, similarity), ...]
│   │   │
│   │   ├─ 4.3: Filter
│   │   │   ├─ Category: "ecommerce" only
│   │   │   ├─ Time: last 2 days
│   │   │   └─ Similarity: > 0.6
│   │   │
│   │   ├─ 4.4: Rerank
│   │   │   ├─ For each result:
│   │   │   │   ├─ semantic_score = similarity
│   │   │   │   ├─ temporal_score = exp(-age_days/7)
│   │   │   │   ├─ category_score = 1.0 if match
│   │   │   │   └─ combined = Σ(weight × score)
│   │   │   └─ Sort by combined score
│   │   │
│   │   ├─ 4.5: Enrich
│   │   │   ├─ Add explanations
│   │   │   ├─ Extract highlights
│   │   │   └─ Generate suggestions
│   │   │
│   │   └─ 4.6: Group by URL
│   │       └─ Keep best match per URL
│   │
│   └─ Output: SearchResponse
│       ├─ results: [EnrichedResult, ...]
│       ├─ total_found: 12
│       ├─ processing_time: 0.234s
│       └─ suggestions: [...]
│
├─► STEP 5: MEMORY AGENT (Feedback)
│   ├─ Record search:
│   │   ├─ query: "laptop I saw yesterday"
│   │   ├─ category: "ecommerce"
│   │   ├─ results_count: 12
│   │   └─ timestamp: now
│   └─ Save: user_memory.json
│
└─► END: Return SearchResponse to user
    ├─ Display results in popup
    ├─ Show explanations
    └─ Highlight on click
```

## 3. Intent Detection Flow

```
Query: "laptop I saw yesterday"
│
├─► Perception Agent (Gemini)
│   │
│   ├─ Analyze keywords:
│   │   ├─ "laptop" → product
│   │   ├─ "I saw" → past action
│   │   └─ "yesterday" → temporal
│   │
│   ├─ Detect patterns:
│   │   ├─ Past tense → recall
│   │   ├─ Temporal word → recent
│   │   └─ Product name → ecommerce
│   │
│   └─ Classify intent:
│       ├─ "search" ❌ (not general)
│       ├─ "compare" ❌ (not comparing)
│       ├─ "recall" ✅ (remembering)
│       └─ "explore" ❌ (not browsing)
│
└─► Output: intent = "recall"
```

## 4. Strategy Selection Flow

```
Enhanced Query + Context
│
├─► Decision Agent (Gemini)
│   │
│   ├─ IF intent = "recall" AND temporal = "recent"
│   │   └─► Strategy: "temporal"
│   │       ├─ Weights: 40% semantic, 50% temporal
│   │       └─ Time window: 2 days
│   │
│   ├─ ELSE IF intent = "compare"
│   │   └─► Strategy: "comparative"
│   │       ├─ Weights: 60% semantic, 20% temporal
│   │       └─ Group by URL
│   │
│   ├─ ELSE IF intent = "explore"
│   │   └─► Strategy: "hybrid"
│   │       ├─ Weights: 60% semantic, 20% diversity
│   │       └─ Diverse results
│   │
│   └─ ELSE
│       └─► Strategy: "semantic"
│           ├─ Weights: 100% semantic
│           └─ Pure similarity
│
└─► Output: SearchDecision
```

## 5. Reranking Flow

```
Raw FAISS Results (sorted by similarity)
│
├─► For each result:
│   │
│   ├─ Calculate semantic_score
│   │   └─ = similarity (from FAISS)
│   │
│   ├─ Calculate temporal_score
│   │   ├─ age_days = (now - timestamp) / 86400
│   │   └─ = exp(-age_days / 7)  # Exponential decay
│   │
│   ├─ Calculate category_score
│   │   ├─ IF category matches hint
│   │   │   └─ = 1.0
│   │   └─ ELSE
│   │       └─ = 0.5
│   │
│   └─ Calculate combined_score
│       └─ = w_semantic × semantic_score +
│            w_temporal × temporal_score +
│            w_category × category_score
│
├─► Sort by combined_score (descending)
│
└─► Output: Reranked results

Example:
┌─────────────────────────────────────────────────────────┐
│ Result A: bestbuy.com/laptop-xyz                        │
│ ├─ similarity: 0.83                                     │
│ ├─ age: 1 day                                           │
│ ├─ semantic_score: 0.83                                 │
│ ├─ temporal_score: 0.95 (very recent!)                  │
│ ├─ category_score: 1.0 (matches)                        │
│ └─ combined: 0.4×0.83 + 0.5×0.95 + 0.1×1.0 = 0.907 ✅   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Result B: wikipedia.org/laptop                          │
│ ├─ similarity: 0.87 (higher!)                           │
│ ├─ age: 30 days                                         │
│ ├─ semantic_score: 0.87                                 │
│ ├─ temporal_score: 0.02 (old)                           │
│ ├─ category_score: 0.5 (doesn't match)                  │
│ └─ combined: 0.4×0.87 + 0.5×0.02 + 0.1×0.5 = 0.408 ❌   │
└─────────────────────────────────────────────────────────┘

Result: A ranks higher despite lower similarity!
```

## 6. Data Flow Diagram

```
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ UserQuery (Pydantic)                 │
│ ├─ query: str                        │
│ ├─ category: Optional[str]           │
│ └─ timestamp: datetime               │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ EnhancedQuery (Pydantic)             │
│ ├─ original_query: str               │
│ ├─ expanded_terms: List[str]         │
│ ├─ intent: str                       │
│ ├─ temporal_context: Optional[str]   │
│ ├─ category_hints: List[str]         │
│ ├─ confidence: float                 │
│ └─ reasoning: str                    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ BrowsingContext (Pydantic)           │
│ ├─ recent_categories: List[str]      │
│ ├─ frequent_sites: List[str]         │
│ ├─ time_of_day: str                  │
│ └─ day_of_week: str                  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ SearchDecision (Pydantic)            │
│ ├─ strategy: str                     │
│ ├─ search_params: Dict               │
│ ├─ filters: Dict                     │
│ ├─ ranking_weights: Dict             │
│ ├─ reasoning: str                    │
│ └─ confidence: float                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ SearchResponse (Pydantic)            │
│ ├─ results: List[EnrichedResult]     │
│ ├─ query_understanding: str          │
│ ├─ search_strategy: str              │
│ ├─ total_found: int                  │
│ ├─ processing_time: float            │
│ └─ suggestions: List[str]            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────┐
│ User Sees    │
│ Results      │
└──────────────┘
```

## 7. Feedback Loop

```
┌─────────────────────────────────────────────────────────┐
│                    FEEDBACK LOOP                         │
│                                                          │
│  User Search                                            │
│       │                                                  │
│       ▼                                                  │
│  ┌─────────────┐                                        │
│  │  Perception │                                        │
│  └──────┬──────┘                                        │
│         │                                                │
│         ▼                                                │
│  ┌─────────────┐      ┌──────────────┐                │
│  │   Memory    │◄─────┤ User clicks  │                │
│  │  (learns)   │      │ result       │                │
│  └──────┬──────┘      └──────────────┘                │
│         │                     ▲                         │
│         ▼                     │                         │
│  ┌─────────────┐             │                         │
│  │  Decision   │             │                         │
│  └──────┬──────┘             │                         │
│         │                     │                         │
│         ▼                     │                         │
│  ┌─────────────┐             │                         │
│  │   Actions   │─────────────┘                         │
│  └──────┬──────┘                                        │
│         │                                                │
│         ▼                                                │
│  Results shown                                          │
│                                                          │
│  Memory updates:                                        │
│  ├─ Increment category preference                      │
│  ├─ Track successful strategy                          │
│  ├─ Record click patterns                              │
│  └─ Update temporal patterns                           │
└─────────────────────────────────────────────────────────┘
```

## 8. Error Handling Flow

```
┌─────────────────────────────────────────────────────────┐
│                   ERROR HANDLING                         │
│                                                          │
│  User Query                                             │
│       │                                                  │
│       ▼                                                  │
│  ┌─────────────────────────────────────────┐           │
│  │ TRY: Cognitive AI Pipeline              │           │
│  │  ├─ Perception (Gemini)                 │           │
│  │  ├─ Memory                               │           │
│  │  ├─ Decision (Gemini)                   │           │
│  │  └─ Actions                              │           │
│  └─────────────┬───────────────────────────┘           │
│                │                                         │
│       ┌────────┴────────┐                              │
│       │                 │                              │
│       ▼                 ▼                              │
│  ┌─────────┐      ┌──────────────┐                    │
│  │ SUCCESS │      │ ERROR        │                    │
│  └────┬────┘      └──────┬───────┘                    │
│       │                  │                             │
│       │                  ▼                             │
│       │           ┌──────────────────────┐            │
│       │           │ FALLBACK:            │            │
│       │           │ Basic FAISS Search   │            │
│       │           │ ├─ Embed query       │            │
│       │           │ ├─ Search FAISS      │            │
│       │           │ └─ Return results    │            │
│       │           └──────┬───────────────┘            │
│       │                  │                             │
│       └──────────────────┘                             │
│                  │                                      │
│                  ▼                                      │
│            Results to user                             │
│            (always works!)                             │
└─────────────────────────────────────────────────────────┘
```

---

**These diagrams show the complete flow of the cognitive AI system!**

Print or reference these when understanding or debugging the system.
