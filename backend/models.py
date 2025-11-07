"""Pydantic models for cognitive AI layer"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# User Query Models
class UserQuery(BaseModel):
    """Initial user search query"""
    query: str
    category: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class EnhancedQuery(BaseModel):
    """Enhanced query after cognitive processing"""
    original_query: str
    expanded_terms: List[str] = Field(default_factory=list)
    intent: str  # "search", "compare", "recall", "explore"
    temporal_context: Optional[str] = None  # "recent", "last_week", "specific_date"
    category_hints: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

# Context Models
class BrowsingContext(BaseModel):
    """User's browsing context"""
    recent_categories: List[str] = Field(default_factory=list)
    frequent_sites: List[str] = Field(default_factory=list)
    time_of_day: str
    day_of_week: str
    session_duration: Optional[int] = None

class SearchHistory(BaseModel):
    """Recent search history"""
    queries: List[str] = Field(default_factory=list)
    results_clicked: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

# Decision Models
class SearchDecision(BaseModel):
    """Decision on how to execute search"""
    strategy: str  # "semantic", "hybrid", "temporal", "comparative"
    search_params: Dict[str, Any]
    filters: Dict[str, Any] = Field(default_factory=dict)
    ranking_weights: Dict[str, float] = Field(default_factory=dict)
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)

class ActionPlan(BaseModel):
    """Plan for executing search actions"""
    actions: List[str]  # ["embed_query", "search_faiss", "rerank", "highlight"]
    parameters: Dict[str, Any]
    expected_results: int
    reasoning: str

# Result Models
class EnrichedResult(BaseModel):
    """Search result with cognitive enrichment"""
    url: str
    title: str
    snippet: str
    category: str
    similarity: float
    relevance_score: float  # Adjusted by cognitive layer
    temporal_relevance: float
    context_match: float
    explanation: str  # Why this result is relevant
    highlight_suggestions: List[str] = Field(default_factory=list)

class SearchResponse(BaseModel):
    """Final search response"""
    results: List[EnrichedResult]
    query_understanding: str
    search_strategy: str
    total_found: int
    processing_time: float
    suggestions: List[str] = Field(default_factory=list)

# Feedback Models
class UserFeedback(BaseModel):
    """User interaction feedback"""
    query: str
    result_clicked: Optional[str] = None
    time_to_click: Optional[float] = None
    was_helpful: Optional[bool] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class LearningUpdate(BaseModel):
    """Updates to improve future searches"""
    query_patterns: Dict[str, Any] = Field(default_factory=dict)
    category_preferences: Dict[str, float] = Field(default_factory=dict)
    temporal_patterns: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
