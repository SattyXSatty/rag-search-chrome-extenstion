"""Answer Verification - Check if retrieved content actually answers the query"""
import google.generativeai as genai
import os
import json

class AnswerVerifier:
    """Verifies if search results actually answer the user's question"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("⚠️ No GEMINI_API_KEY - answer verification disabled")
            self.enabled = False
            return
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            generation_config={
                "response_mime_type": "application/json"
            }
        )
        self.enabled = True
    
    def verify_results(self, query: str, results: list, top_n: int = 5) -> dict:
        """
        Verify if the top results actually answer the query
        
        Returns:
        {
            'has_answer': bool,
            'confidence': float,
            'reasoning': str,
            'relevant_results': list  # Only results that actually answer
        }
        """
        if not self.enabled or not results:
            return {
                'has_answer': True,  # Assume yes if verification disabled
                'confidence': 0.5,
                'reasoning': 'Verification disabled',
                'relevant_results': results
            }
        
        # Get top N results to check
        top_results = results[:top_n]
        
        # Combine chunks for context
        context = "\n\n".join([
            f"[Result {i+1}] {r.snippet}"
            for i, r in enumerate(top_results)
        ])
        
        prompt = f"""You are an answer verification system. Your job is to determine if the provided search results actually answer the user's question.

User Question: "{query}"

Search Results:
{context}

Analyze whether these results contain information that answers the question. Return JSON:

{{
  "has_answer": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "answerable_result_indices": [0, 1, 2]  // which results (0-indexed) actually answer the question
}}

Rules:
- has_answer = true if results contain information that could answer or is related to the question
- has_answer = false ONLY if results are completely unrelated or clearly don't contain the answer
- confidence = how certain you are (0.0 = not at all, 1.0 = completely certain)
- answerable_result_indices = list of result indices that contain relevant information
- When in doubt, set has_answer = true (better to show results than hide them)

Example 1:
Question: "Who won the 2025 world cup?"
Results: "The 2024 world cup was exciting. Many teams participated."
Response: {{"has_answer": false, "confidence": 0.9, "reasoning": "Results mention world cup but not 2025 winner", "answerable_result_indices": []}}

Example 2:
Question: "Who won the 2025 world cup?"
Results: "India won the 2025 world cup final against Australia."
Response: {{"has_answer": true, "confidence": 0.95, "reasoning": "Result explicitly states India won 2025 world cup", "answerable_result_indices": [0]}}

Now analyze the results above."""

        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text)
            
            # Filter results to only answerable ones
            answerable_indices = set(data.get('answerable_result_indices', []))
            relevant_results = [
                r for i, r in enumerate(top_results)
                if i in answerable_indices
            ]
            
            # If no answerable results, return empty
            if not data.get('has_answer', False):
                relevant_results = []
            
            return {
                'has_answer': data.get('has_answer', False),
                'confidence': data.get('confidence', 0.5),
                'reasoning': data.get('reasoning', ''),
                'relevant_results': relevant_results
            }
            
        except Exception as e:
            print(f"⚠️ Answer verification error: {e}")
            # On error, return all results (fail open)
            return {
                'has_answer': True,
                'confidence': 0.3,
                'reasoning': f'Verification failed: {str(e)}',
                'relevant_results': results
            }
