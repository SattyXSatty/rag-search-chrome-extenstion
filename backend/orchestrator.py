"""Main Orchestrator - Coordinates all cognitive agents"""
from models import UserQuery, SearchResponse
from perception import PerceptionAgent
from memory import MemoryAgent
from decision import DecisionAgent
from actions import ActionsAgent
from answer_verification import AnswerVerifier
from datetime import datetime
import os

class CognitiveOrchestrator:
    """
    Main orchestrator that coordinates:
    1. Perception - Understanding queries
    2. Memory - User context and history
    3. Decision - Search strategy
    4. Actions - Execute search
    """
    
    def __init__(self, index, metadata_store, embedding_model, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        # Initialize agents
        self.perception = PerceptionAgent(api_key=self.api_key)
        self.memory = MemoryAgent()
        self.decision = DecisionAgent(api_key=self.api_key)
        self.actions = ActionsAgent(index, metadata_store, embedding_model)
        self.verifier = AnswerVerifier(api_key=self.api_key)
        
        print("✅ Cognitive AI Orchestrator initialized")
        print(f"   - Perception: Gemini 2.0 Flash")
        print(f"   - Memory: User preferences loaded")
        print(f"   - Decision: Strategy planner ready")
        print(f"   - Actions: FAISS executor ready")
    
    def search(self, query: str, category: str = None) -> SearchResponse:
        """
        Execute cognitive search pipeline:
        1. Understand query (Perception)
        2. Get user context (Memory)
        3. Decide strategy (Decision)
        4. Execute search (Actions)
        5. Record feedback (Memory)
        """
        start_time = datetime.now().timestamp()
        
        print(f"\n{'='*60}")
        print(f"🧠 COGNITIVE SEARCH PIPELINE")
        print(f"{'='*60}")
        
        # Step 1: Perception - Understand query
        print(f"\n1️⃣ PERCEPTION: Understanding query...")
        user_query = UserQuery(query=query, category=category)
        enhanced_query = self.perception.understand_query(user_query)
        
        print(f"   Original: {enhanced_query.original_query}")
        print(f"   Intent: {enhanced_query.intent}")
        print(f"   Expanded: {enhanced_query.expanded_terms[:3]}")
        print(f"   Confidence: {enhanced_query.confidence:.2f}")
        print(f"   Reasoning: {enhanced_query.reasoning[:80]}...")
        print(f"   Will verify: {enhanced_query.intent in ['search', 'recall']}")
        
        # Step 2: Memory - Get context
        print(f"\n2️⃣ MEMORY: Loading user context...")
        browsing_context = self.memory.get_browsing_context()
        search_history = self.memory.get_search_history()
        
        print(f"   Recent categories: {browsing_context.recent_categories[:3]}")
        print(f"   Time of day: {browsing_context.time_of_day}")
        print(f"   Recent queries: {len(search_history.queries)}")
        
        # Step 3: Decision - Determine strategy
        print(f"\n3️⃣ DECISION: Planning search strategy...")
        search_decision = self.decision.decide_strategy(
            enhanced_query,
            browsing_context,
            search_history
        )
        
        # IMPORTANT: Use original query, not expanded version
        # The expanded query dilutes search results
        search_decision.search_params['query_text'] = enhanced_query.original_query
        
        print(f"   Strategy: {search_decision.strategy}")
        print(f"   Query text: {search_decision.search_params.get('query_text', '')[:50]}")
        print(f"   Results: {search_decision.search_params.get('k', 50)}")
        print(f"   Confidence: {search_decision.confidence:.2f}")
        print(f"   Reasoning: {search_decision.reasoning[:80]}...")
        
        # Step 4: Actions - Execute search
        print(f"\n4️⃣ ACTIONS: Executing search...")
        search_response = self.actions.execute_search(search_decision, start_time)
        
        print(f"   Found: {search_response.total_found} results")
        print(f"   Processing time: {search_response.processing_time:.3f}s")
        print(f"   Suggestions: {search_response.suggestions}")
        
        # Step 4.5: Verify if results actually answer the question
        # Check if it's a factual question
        question_starters = ['who', 'what', 'when', 'where', 'why', 'how', 'which', 'whose']
        is_specific_question = any(query.lower().startswith(word) for word in question_starters) or '?' in query
        
        try:
            if search_response.results and is_specific_question and enhanced_query.intent in ['search', 'recall']:
                print(f"\n4️⃣.5 VERIFICATION: Checking if results answer the question...")
                verification = self.verifier.verify_results(query, search_response.results)
                
                print(f"   Has answer: {verification['has_answer']}")
                print(f"   Confidence: {verification['confidence']:.2f}")
                print(f"   Reasoning: {verification['reasoning'][:80]}...")
                
                # Filter out if no answer (even with low confidence for specific questions)
                if not verification['has_answer']:
                    if verification['confidence'] > 0.5 or is_specific_question:
                        print(f"   ⚠️ Results don't answer the question - returning empty")
                        search_response.results = []
                        search_response.total_found = 0
                        search_response.suggestions = [
                            "No results contain the answer to your question",
                            "Try rephrasing your query",
                            "The information might not be in your browsing history"
                        ]
                    else:
                        print(f"   ⚠️ Very low confidence no answer - keeping results anyway")
                elif verification['relevant_results']:
                    # Only return results that actually answer
                    original_count = len(search_response.results)
                    search_response.results = verification['relevant_results']
                    search_response.total_found = len(verification['relevant_results'])
                    if len(verification['relevant_results']) < original_count:
                        print(f"   Filtered: {original_count} → {len(verification['relevant_results'])} relevant results")
        except Exception as e:
            print(f"   ⚠️ Verification error: {e}")
            print(f"   Continuing with unverified results")
        
        # Step 5: Memory - Record search
        print(f"\n5️⃣ MEMORY: Recording search...")
        self.memory.record_search(
            query=query,
            category=category,
            results_count=search_response.total_found
        )
        
        print(f"\n{'='*60}")
        print(f"✅ SEARCH COMPLETE")
        print(f"{'='*60}\n")
        
        return search_response
    
    def compare_products(self, query: str) -> SearchResponse:
        """
        Specialized product comparison flow
        """
        # Force comparative strategy
        user_query = UserQuery(query=query, category='ecommerce')
        enhanced_query = self.perception.understand_query(user_query)
        enhanced_query.intent = 'compare'
        
        browsing_context = self.memory.get_browsing_context()
        search_history = self.memory.get_search_history()
        
        search_decision = self.decision.decide_strategy(
            enhanced_query,
            browsing_context,
            search_history
        )
        
        # Override to comparative strategy
        search_decision.strategy = 'comparative'
        search_decision.search_params['category_filter'] = 'ecommerce'
        
        start_time = datetime.now().timestamp()
        search_response = self.actions.execute_search(search_decision, start_time)
        
        self.memory.record_search(
            query=query,
            category='ecommerce',
            results_count=search_response.total_found
        )
        
        return search_response
    
    def get_stats(self) -> dict:
        """Get system statistics"""
        return {
            'memory': {
                'total_searches': len(self.memory.memory.get('search_history', [])),
                'category_preferences': self.memory.get_category_preferences(),
                'frequent_sites': len(self.memory.memory.get('frequent_sites', []))
            },
            'index': {
                'total_vectors': self.actions.index.ntotal
            }
        }
