"""Actions Layer - Execute search operations"""
from models import SearchDecision, EnrichedResult, SearchResponse
from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta
import faiss

class ActionsAgent:
    """Executes search actions on FAISS index"""
    
    def __init__(self, index: faiss.Index, metadata_store: dict, model):
        self.index = index
        self.metadata_store = metadata_store
        self.model = model  # SentenceTransformer model
    
    def execute_search(
        self,
        decision: SearchDecision,
        start_time: float
    ) -> SearchResponse:
        """Execute search based on decision"""
        
        # 1. Embed query
        query_text = decision.search_params.get('query_text', '')
        query_embedding = self.model.encode(
            [query_text],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # 2. Search FAISS
        k = decision.search_params.get('k', 50)
        distances, indices = self.index.search(
            query_embedding,
            min(k * 2, self.index.ntotal)  # Get extra for filtering
        )
        
        # 3. Collect and filter results
        raw_results = []
        filtered_count = {'category': 0, 'temporal': 0, 'similarity': 0}
        
        # Log filter settings
        min_sim_requested = decision.filters.get('min_similarity', 0.0)
        min_sim_actual = min(min_sim_requested, 0.3)
        if min_sim_requested > 0.3:
            print(f"   ⚠️ Similarity threshold capped: {min_sim_requested:.2f} → {min_sim_actual:.2f}")
        
        for i, idx in enumerate(indices[0]):
            if idx != -1 and int(idx) in self.metadata_store:
                meta = self.metadata_store[int(idx)]
                
                # Apply category filter
                category_filter = decision.search_params.get('category_filter')
                if category_filter and meta.get('category') != category_filter:
                    filtered_count['category'] += 1
                    continue
                
                # Apply temporal filter
                time_window = decision.search_params.get('time_window_days')
                if time_window:
                    timestamp = meta.get('timestamp', 0)
                    age_days = (datetime.now().timestamp() - timestamp) / 86400
                    if age_days > time_window:
                        filtered_count['temporal'] += 1
                        continue
                
                # Apply similarity threshold (cap at 0.3 to prevent over-filtering)
                min_sim = min(decision.filters.get('min_similarity', 0.0), 0.3)
                if float(distances[0][i]) < min_sim:
                    filtered_count['similarity'] += 1
                    continue
                
                raw_results.append({
                    'metadata': meta,
                    'similarity': float(distances[0][i]),
                    'index': int(idx)
                })
                
                if len(raw_results) >= k:
                    break
        
        # Log filtering stats
        if sum(filtered_count.values()) > 0:
            print(f"   Filtered: {filtered_count['category']} by category, "
                  f"{filtered_count['temporal']} by time, "
                  f"{filtered_count['similarity']} by similarity")
        
        # 4. Rerank if needed
        if decision.strategy in ['hybrid', 'comparative', 'temporal']:
            raw_results = self._rerank_results(raw_results, decision)
        
        # 5. Enrich results
        enriched = self._enrich_results(raw_results, decision, query_text)
        
        # 6. Group by URL for final results
        grouped = self._group_by_url(enriched)
        
        processing_time = datetime.now().timestamp() - start_time
        
        return SearchResponse(
            results=grouped[:decision.search_params.get('k', 50)],
            query_understanding=f"Strategy: {decision.strategy}, Confidence: {decision.confidence:.2f}",
            search_strategy=decision.reasoning,
            total_found=len(grouped),
            processing_time=processing_time,
            suggestions=self._generate_suggestions(query_text, grouped)
        )
    
    def _rerank_results(
        self,
        results: List[Dict],
        decision: SearchDecision
    ) -> List[Dict]:
        """Rerank results based on multiple factors"""
        weights = decision.ranking_weights
        
        for result in results:
            meta = result['metadata']
            
            # Semantic similarity score (already normalized)
            semantic_score = result['similarity']
            
            # Temporal relevance (decay over time)
            timestamp = meta.get('timestamp', 0)
            if timestamp > 0:
                age_days = (datetime.now().timestamp() - timestamp) / 86400
                # Cap age_days to prevent overflow (max ~100 days)
                age_days = min(max(age_days, 0), 100)
                temporal_score = np.exp(-age_days / 7)  # Decay with 7-day half-life
            else:
                # No timestamp, use neutral score
                temporal_score = 0.5
            
            # Category match score
            category_hints = decision.search_params.get('category_hints', [])
            category_score = 1.0 if meta.get('category') in category_hints else 0.5
            
            # Frequency score (how often this URL appears in results)
            # For now, just use 0.5 as baseline
            frequency_score = 0.5
            
            # Combined score
            combined_score = (
                weights.get('semantic_similarity', 1.0) * semantic_score +
                weights.get('temporal_relevance', 0.0) * temporal_score +
                weights.get('category_match', 0.0) * category_score +
                weights.get('frequency', 0.0) * frequency_score
            )
            
            result['relevance_score'] = combined_score
            result['temporal_relevance'] = temporal_score
            result['context_match'] = category_score
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get('relevance_score', x['similarity']), reverse=True)
        
        return results
    
    def _enrich_results(
        self,
        results: List[Dict],
        decision: SearchDecision,
        query: str
    ) -> List[EnrichedResult]:
        """Convert raw results to enriched results"""
        enriched = []
        
        for result in results:
            meta = result['metadata']
            
            # Generate explanation
            explanation = self._generate_explanation(result, decision, query)
            
            # Extract highlight suggestions (key terms from chunk)
            chunk_text = meta.get('chunk', '')
            highlight_suggestions = self._extract_highlights(chunk_text, query)
            
            enriched.append(EnrichedResult(
                url=meta.get('url', ''),
                title=meta.get('title', 'Untitled'),
                snippet=chunk_text[:200],
                category=meta.get('category', 'other'),
                similarity=result['similarity'],
                relevance_score=result.get('relevance_score', result['similarity']),
                temporal_relevance=result.get('temporal_relevance', 0.5),
                context_match=result.get('context_match', 0.5),
                explanation=explanation,
                highlight_suggestions=highlight_suggestions
            ))
        
        return enriched
    
    def _generate_explanation(
        self,
        result: Dict,
        decision: SearchDecision,
        query: str
    ) -> str:
        """Generate human-readable explanation for why result is relevant"""
        meta = result['metadata']
        similarity = result['similarity']
        
        if decision.strategy == 'temporal':
            timestamp = meta.get('timestamp', 0)
            age_days = int((datetime.now().timestamp() - timestamp) / 86400)
            if age_days == 0:
                return f"Visited today, {int(similarity * 100)}% match"
            elif age_days == 1:
                return f"Visited yesterday, {int(similarity * 100)}% match"
            else:
                return f"Visited {age_days} days ago, {int(similarity * 100)}% match"
        
        elif decision.strategy == 'comparative':
            return f"Product match: {int(similarity * 100)}%"
        
        else:
            return f"Relevance: {int(similarity * 100)}%"
    
    def _extract_highlights(self, text: str, query: str) -> List[str]:
        """Extract key phrases to highlight"""
        # Simple word extraction (could be enhanced with NER)
        query_words = set(query.lower().split())
        text_words = text.lower().split()
        
        highlights = []
        for i, word in enumerate(text_words):
            if word in query_words and len(word) > 3:
                # Get context around word
                start = max(0, i - 3)
                end = min(len(text_words), i + 4)
                phrase = ' '.join(text_words[start:end])
                highlights.append(phrase)
        
        return highlights[:5]  # Top 5 highlights
    
    def _group_by_url(self, results: List[EnrichedResult]) -> List[EnrichedResult]:
        """Group results by URL, keeping best match per URL"""
        url_map = {}
        
        for result in results:
            url = result.url
            if url not in url_map or result.relevance_score > url_map[url].relevance_score:
                url_map[url] = result
        
        # Return sorted by relevance
        grouped = list(url_map.values())
        grouped.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return grouped
    
    def _generate_suggestions(
        self,
        query: str,
        results: List[EnrichedResult]
    ) -> List[str]:
        """Generate search suggestions based on results"""
        if not results:
            return ["Try different keywords", "Check your spelling", "Browse by category"]
        
        # Extract common categories
        categories = set(r.category for r in results[:10])
        suggestions = [f"Filter by {cat}" for cat in categories if cat != 'other']
        
        # Add temporal suggestions if results span time
        timestamps = [r.temporal_relevance for r in results[:10]]
        if max(timestamps) - min(timestamps) > 0.3:
            suggestions.append("Filter by date")
        
        return suggestions[:3]
