"""Perception Layer - Understanding user queries with Gemini"""
import google.generativeai as genai
from models import UserQuery, EnhancedQuery
import json
import os

class PerceptionAgent:
    """Understands and enhances user search queries"""
    
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
    
    def understand_query(self, user_query: UserQuery) -> EnhancedQuery:
        """
        Analyze user query and extract intent, expand terms, detect context
        """
        prompt = f"""Analyze this search query and provide structured understanding:

Query: "{user_query.query}"
Category hint: {user_query.category or "unknown"}

Provide a JSON response with:
1. expanded_terms: List of related search terms and synonyms (max 5)
2. intent: One of ["search", "compare", "recall", "explore"]
   - search: Looking for specific information
   - compare: Comparing products/options
   - recall: Trying to remember something browsed before
   - explore: General browsing/discovery
3. temporal_context: One of ["recent", "last_week", "last_month", "any_time", null]
4. category_hints: List of likely categories ["ecommerce", "news", "docs", "social", "other"]
5. confidence: Float 0-1 indicating confidence in understanding
6. reasoning: Brief explanation of the analysis

Example:
Query: "laptop I saw yesterday"
{{
  "expanded_terms": ["laptop", "notebook", "computer", "portable computer"],
  "intent": "recall",
  "temporal_context": "recent",
  "category_hints": ["ecommerce"],
  "confidence": 0.9,
  "reasoning": "User is trying to recall a specific laptop viewed recently, likely from shopping"
}}

Now analyze the query above."""

        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text)
            
            return EnhancedQuery(
                original_query=user_query.query,
                expanded_terms=data.get('expanded_terms', []),
                intent=data.get('intent', 'search'),
                temporal_context=data.get('temporal_context'),
                category_hints=data.get('category_hints', []),
                confidence=data.get('confidence', 0.5),
                reasoning=data.get('reasoning', '')
            )
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Perception error: {error_msg[:100]}...")
            
            # Check for quota/auth errors
            if "429" in error_msg or "quota" in error_msg.lower():
                print("💡 Tip: Get a free API key at https://makersuite.google.com/app/apikey")
            elif "401" in error_msg or "API key" in error_msg:
                print("💡 Tip: Set GEMINI_API_KEY environment variable")
            
            # Fallback to basic understanding
            return EnhancedQuery(
                original_query=user_query.query,
                expanded_terms=[user_query.query],
                intent='search',
                confidence=0.3,
                reasoning=f"Fallback: {error_msg[:50]}"
            )
    
    def extract_entities(self, query: str) -> dict:
        """Extract named entities from query"""
        prompt = f"""Extract entities from this search query:

Query: "{query}"

Return JSON with:
- products: List of product names
- brands: List of brand names
- locations: List of locations
- dates: List of date references
- prices: List of price mentions

Example: {{"products": ["laptop"], "brands": ["Dell"], "locations": [], "dates": ["yesterday"], "prices": []}}"""

        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except:
            return {"products": [], "brands": [], "locations": [], "dates": [], "prices": []}
