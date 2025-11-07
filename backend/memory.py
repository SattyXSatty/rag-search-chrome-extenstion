"""Memory Layer - User preferences and browsing patterns"""
from models import BrowsingContext, SearchHistory, UserFeedback
from typing import Dict, List
import json
import os
from datetime import datetime, timedelta
from collections import Counter

class MemoryAgent:
    """Manages user preferences and browsing history"""
    
    def __init__(self, storage_path: str = 'user_memory.json'):
        self.storage_path = storage_path
        self.memory = self._load_memory()
    
    def _load_memory(self) -> dict:
        """Load memory from disk"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {
            'search_history': [],
            'feedback': [],
            'category_preferences': {},
            'temporal_patterns': {},
            'frequent_sites': []
        }
    
    def _save_memory(self):
        """Save memory to disk"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2, default=str)
    
    def get_browsing_context(self) -> BrowsingContext:
        """Get current browsing context"""
        now = datetime.now()
        
        # Analyze recent categories (last 7 days)
        recent_searches = [
            s for s in self.memory.get('search_history', [])
            if (now - datetime.fromisoformat(s['timestamp'])).days <= 7
        ]
        
        category_counts = Counter(
            s.get('category') for s in recent_searches if s.get('category')
        )
        recent_categories = [cat for cat, _ in category_counts.most_common(5)]
        
        # Get frequent sites
        frequent_sites = self.memory.get('frequent_sites', [])[:10]
        
        return BrowsingContext(
            recent_categories=recent_categories,
            frequent_sites=frequent_sites,
            time_of_day=self._get_time_of_day(),
            day_of_week=now.strftime('%A')
        )
    
    def get_search_history(self, limit: int = 10) -> SearchHistory:
        """Get recent search history"""
        recent = self.memory.get('search_history', [])[-limit:]
        
        return SearchHistory(
            queries=[s['query'] for s in recent],
            results_clicked=[s.get('clicked_url', '') for s in recent if s.get('clicked_url')]
        )
    
    def record_search(self, query: str, category: str = None, results_count: int = 0):
        """Record a search query"""
        if 'search_history' not in self.memory:
            self.memory['search_history'] = []
        
        self.memory['search_history'].append({
            'query': query,
            'category': category,
            'results_count': results_count,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 1000 searches
        self.memory['search_history'] = self.memory['search_history'][-1000:]
        self._save_memory()
    
    def record_feedback(self, feedback: UserFeedback):
        """Record user feedback"""
        if 'feedback' not in self.memory:
            self.memory['feedback'] = []
        
        self.memory['feedback'].append({
            'query': feedback.query,
            'result_clicked': feedback.result_clicked,
            'time_to_click': feedback.time_to_click,
            'was_helpful': feedback.was_helpful,
            'timestamp': feedback.timestamp.isoformat()
        })
        
        # Update category preferences
        if feedback.result_clicked and feedback.was_helpful:
            # Extract category from feedback (would need to be passed)
            # For now, just increment general preference
            pass
        
        self._save_memory()
    
    def get_category_preferences(self) -> Dict[str, float]:
        """Get user's category preferences (0-1 scores)"""
        return self.memory.get('category_preferences', {
            'ecommerce': 0.5,
            'news': 0.5,
            'docs': 0.5,
            'social': 0.5,
            'other': 0.5
        })
    
    def update_frequent_sites(self, url: str):
        """Update frequently visited sites"""
        if 'frequent_sites' not in self.memory:
            self.memory['frequent_sites'] = []
        
        # Add or move to front
        if url in self.memory['frequent_sites']:
            self.memory['frequent_sites'].remove(url)
        self.memory['frequent_sites'].insert(0, url)
        
        # Keep only top 50
        self.memory['frequent_sites'] = self.memory['frequent_sites'][:50]
        self._save_memory()
    
    def _get_time_of_day(self) -> str:
        """Get current time period"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def get_temporal_patterns(self) -> dict:
        """Analyze when user typically searches for different categories"""
        return self.memory.get('temporal_patterns', {})
