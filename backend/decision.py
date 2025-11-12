"""Decision Layer - Determines search strategy with Gemini"""
import google.generativeai as genai
from models import (
    EnhancedQuery, BrowsingContext, SearchHistory,
    SearchDecision, ActionPlan
)
import json
import os

class DecisionAgent:
    """Decides optimal search strategy based on context"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            generation_config={
                "response_mime_type": "application/json"
            }
        )
    
    def decide_strategy(
        self,
        enhanced_query: EnhancedQuery,
        context: BrowsingContext,
        history: SearchHistory
    ) -> SearchDecision:
        """
        Decide the best search strategy based on query understanding and context
        """
        prompt = f"""Decide the optimal search strategy for this query:

Enhanced Query:
- Original: "{enhanced_query.original_query}"
- Expanded terms: {enhanced_query.expanded_terms}
- Intent: {enhanced_query.intent}
- Temporal context: {enhanced_query.temporal_context}
- Category hints: {enhanced_query.category_hints}

Browsing Context:
- Recent categories: {context.recent_categories}
- Time of day: {context.time_of_day}
- Day: {context.day_of_week}

Recent Search History:
- Queries: {history.queries[-5:]}

Provide JSON response with:
1. strategy: One of ["semantic", "hybrid", "temporal", "comparative"]
   - semantic: Pure semantic similarity search
   - hybrid: Combine semantic + keyword matching
   - temporal: Prioritize recent/time-based results
   - comparative: Compare multiple items (for shopping)

2. search_params: {{
     "query_text": "USE ORIGINAL QUERY - DO NOT EXPAND OR MODIFY",
     "k": number of results (20-100),
     "category_filter": "category name or null",
     "time_window_days": number or null
   }}

3. filters: {{
     "min_similarity": 0.0-1.0 (RECOMMENDED: 0.65-0.75 for high precision, 0.75-0.85 for very strict),
     "categories": ["list", "of", "categories"],
     "exclude_urls": ["urls", "to", "exclude"]
   }}

4. ranking_weights: {{
     "semantic_similarity": 0.0-1.0,
     "temporal_relevance": 0.0-1.0,
     "category_match": 0.0-1.0,
     "frequency": 0.0-1.0
   }}

5. reasoning: Brief explanation
6. confidence: 0-1 score

Example for "laptop I saw yesterday":
{{
  "strategy": "temporal",
  "search_params": {{
    "query_text": "laptop",
    "k": 50,
    "category_filter": "ecommerce",
    "time_window_days": 2
  }},
  "filters": {{
    "min_similarity": 0.7,
    "categories": ["ecommerce"],
    "exclude_urls": []
  }},
  "ranking_weights": {{
    "semantic_similarity": 0.4,
    "temporal_relevance": 0.5,
    "category_match": 0.1,
    "frequency": 0.0
  }},
  "reasoning": "User recalls recent shopping, prioritize temporal + semantic",
  "confidence": 0.85
}}

Now decide for the query above."""

        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text)
            
            return SearchDecision(
                strategy=data.get('strategy', 'semantic'),
                search_params=data.get('search_params', {}),
                filters=data.get('filters', {}),
                ranking_weights=data.get('ranking_weights', {
                    'semantic_similarity': 1.0,
                    'temporal_relevance': 0.0,
                    'category_match': 0.0,
                    'frequency': 0.0
                }),
                reasoning=data.get('reasoning', ''),
                confidence=data.get('confidence', 0.5)
            )
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Decision error: {error_msg[:100]}...")
            
            # Check for quota/auth errors
            if "429" in error_msg or "quota" in error_msg.lower():
                print("💡 Tip: Get a free API key at https://makersuite.google.com/app/apikey")
            elif "401" in error_msg or "API key" in error_msg:
                print("💡 Tip: Set GEMINI_API_KEY environment variable")
            
            # Fallback to basic semantic search with LOW threshold
            return SearchDecision(
                strategy='semantic',
                search_params={
                    'query_text': enhanced_query.original_query,
                    'k': 50,
                    'category_filter': None  # Don't filter by category in fallback
                },
                filters={'min_similarity': 0.0},  # No similarity filter in fallback
                ranking_weights={
                    'semantic_similarity': 1.0,
                    'temporal_relevance': 0.0,
                    'category_match': 0.0,
                    'frequency': 0.0
                },
                reasoning=f"Fallback: {error_msg[:50]}",
                confidence=0.3
            )
    
    def create_action_plan(self, decision: SearchDecision) -> ActionPlan:
        """Create execution plan from decision"""
        actions = ['embed_query', 'search_faiss']
        
        # Add reranking if using hybrid or comparative strategy
        if decision.strategy in ['hybrid', 'comparative']:
            actions.append('rerank_results')
        
        # Add temporal filtering if needed
        if decision.search_params.get('time_window_days'):
            actions.append('filter_temporal')
        
        # Always add result enrichment
        actions.append('enrich_results')
        
        return ActionPlan(
            actions=actions,
            parameters={
                'strategy': decision.strategy,
                'search_params': decision.search_params,
                'filters': decision.filters,
                'weights': decision.ranking_weights
            },
            expected_results=decision.search_params.get('k', 50),
            reasoning=f"Execute {decision.strategy} search with {len(actions)} steps"
        )
