"""Aggregator service to combine results from all detection layers."""
from typing import List
import time

from ..models.detection import (
    DetectionResult,
    RuleDetectionResult,
    MLDetectionResult,
    VectorDetectionResult
)
from ..config import settings
from ..utils.logger import setup_logger
from .rule_detector import RuleBasedDetector
from .ml_detector import MLDetector
from .vector_detector import VectorDetector


logger = setup_logger(__name__)


class DetectionAggregator:
    """Aggregates results from multiple detection layers."""
    
    def __init__(self):
        """Initialize the aggregator with all detectors."""
        self.rule_detector = RuleBasedDetector()
        self.ml_detector = MLDetector()
        self.vector_detector = VectorDetector()
        
        # Weights for voting
        self.rule_weight = settings.RULE_WEIGHT
        self.ml_weight = settings.ML_WEIGHT
        self.vector_weight = settings.VECTOR_WEIGHT
        
        # High confidence threshold
        self.high_confidence_threshold = settings.HIGH_CONFIDENCE_THRESHOLD
        
        logger.info("Detection aggregator initialized")
    
    def detect(self, text: str) -> DetectionResult:
        """
        Run detection across all layers and aggregate results.
        
        Args:
            text: Input text to analyze
            
        Returns:
            DetectionResult with aggregated analysis
        """
        start_time = time.time()
        
        # Run all detectors
        rule_result = self.rule_detector.detect(text)
        ml_result = self.ml_detector.detect(text)
        vector_result = self.vector_detector.detect(text)
        
        # Calculate weighted confidence
        weighted_confidence = (
            rule_result.confidence * self.rule_weight +
            ml_result.confidence * self.ml_weight +
            vector_result.confidence * self.vector_weight
        )
        
        # Check if any layer has high confidence
        high_confidence_detection = (
            (rule_result.detected and rule_result.confidence >= self.high_confidence_threshold) or
            (ml_result.detected and ml_result.confidence >= self.high_confidence_threshold) or
            (vector_result.detected and vector_result.confidence >= self.high_confidence_threshold)
        )
        
        # Determine if it's a threat
        is_threat = high_confidence_detection or weighted_confidence >= 0.6
        
        # Determine threat level
        if not is_threat:
            threat_level = "none"
        elif weighted_confidence >= 0.85 or high_confidence_detection:
            threat_level = "high"
        elif weighted_confidence >= 0.7:
            threat_level = "medium"
        else:
            threat_level = "low"
        
        # Generate explanation
        explanation = self._generate_explanation(
            is_threat,
            threat_level,
            rule_result,
            ml_result,
            vector_result,
            weighted_confidence
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        result = DetectionResult(
            is_threat=is_threat,
            confidence=weighted_confidence,
            threat_level=threat_level,
            explanation=explanation,
            rule_result=rule_result,
            ml_result=ml_result,
            vector_result=vector_result,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Detection complete: threat={is_threat}, level={threat_level}, "
                   f"confidence={weighted_confidence:.2f}, time={processing_time:.1f}ms")
        
        return result
    
    def detect_batch(self, texts: List[str]) -> List[DetectionResult]:
        """
        Run detection on multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of DetectionResult objects
        """
        results = []
        for text in texts:
            result = self.detect(text)
            results.append(result)
        return results
    
    def _generate_explanation(
        self,
        is_threat: bool,
        threat_level: str,
        rule_result: RuleDetectionResult,
        ml_result: MLDetectionResult,
        vector_result: VectorDetectionResult,
        weighted_confidence: float
    ) -> str:
        """
        Generate human-readable explanation.
        
        Args:
            is_threat: Whether input is classified as threat
            threat_level: Threat level classification
            rule_result: Rule detection result
            ml_result: ML detection result
            vector_result: Vector detection result
            weighted_confidence: Overall confidence score
            
        Returns:
            Explanation string
        """
        if not is_threat:
            return "No prompt injection detected. The input appears to be legitimate."
        
        parts = [f"Prompt injection detected with {threat_level} threat level (confidence: {weighted_confidence:.1%})."]
        
        # Rule-based findings
        if rule_result.detected:
            pattern_names = [p.pattern_name for p in rule_result.matched_patterns[:3]]
            if pattern_names:
                parts.append(f"Rule-based detection found: {', '.join(pattern_names)}.")
        
        # ML findings
        if ml_result.detected:
            parts.append(f"ML model detected suspicious patterns (confidence: {ml_result.confidence:.1%}).")
        
        # Vector findings
        if vector_result.detected and vector_result.similar_attacks:
            top_match = vector_result.similar_attacks[0]
            parts.append(
                f"Similar to known attack: '{top_match.category}' "
                f"(similarity: {top_match.similarity_score:.1%})."
            )
        
        # Recommendations
        if threat_level == "high":
            parts.append("Recommendation: Block this input immediately.")
        elif threat_level == "medium":
            parts.append("Recommendation: Flag for review or apply additional filtering.")
        else:
            parts.append("Recommendation: Monitor this input for suspicious behavior.")
        
        return " ".join(parts)
    
    @property
    def health_status(self) -> dict:
        """Get health status of all detectors."""
        return {
            "rule_detector": True,  # Always available
            "ml_detector": self.ml_detector.is_loaded,
            "vector_detector": self.vector_detector.is_ready,
            "chroma_count": self.vector_detector.chroma_client.get_count()
        }


# Global instance
aggregator = DetectionAggregator()

