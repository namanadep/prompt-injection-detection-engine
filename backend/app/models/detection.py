"""Detection result models."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PatternMatch(BaseModel):
    """Matched pattern details."""
    pattern_id: str
    pattern_name: str
    severity: str
    confidence: float


class RuleDetectionResult(BaseModel):
    """Result from rule-based detection."""
    detected: bool
    confidence: float
    matched_patterns: List[PatternMatch] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)


class MLDetectionResult(BaseModel):
    """Result from ML model detection."""
    detected: bool
    confidence: float
    model_version: str
    prediction_label: Optional[str] = None


class SimilarAttack(BaseModel):
    """Similar attack from vector database."""
    attack_id: str
    text: str
    category: str
    severity: str
    similarity_score: float


class VectorDetectionResult(BaseModel):
    """Result from vector similarity detection."""
    detected: bool
    confidence: float
    similar_attacks: List[SimilarAttack] = Field(default_factory=list)


class DetectionResult(BaseModel):
    """Aggregated detection result."""
    is_threat: bool
    confidence: float
    threat_level: str  # "high", "medium", "low", "none"
    explanation: str
    
    # Layer-by-layer results
    rule_result: RuleDetectionResult
    ml_result: MLDetectionResult
    vector_result: VectorDetectionResult
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class DetectionStats(BaseModel):
    """Detection statistics."""
    total_requests: int
    threats_detected: int
    threat_percentage: float
    avg_confidence: float
    detection_by_method: dict
    threat_levels: dict


class AnalyticsData(BaseModel):
    """Analytics data for dashboard."""
    threats_over_time: List[dict]
    top_patterns: List[dict]
    confidence_distribution: List[dict]
    method_effectiveness: dict

