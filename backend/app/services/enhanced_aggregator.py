"""Enhanced aggregator with multi-tiered defense including intent analysis, behavioral monitoring, and input validation."""
from typing import List, Optional
import time

from ..models.detection import (
    DetectionResult,
    RuleDetectionResult,
    MLDetectionResult,
    VectorDetectionResult
)
from ..config import settings
from ..utils.logger import setup_logger
from .advanced_rule_detector import AdvancedRuleDetector
from .advanced_ml_detector import AdvancedMLDetector
from .vector_detector import VectorDetector
from .intent_analyzer import IntentAnalyzer
from .behavioral_analyzer import BehavioralAnalyzer
from .input_validator import InputValidator


logger = setup_logger(__name__)


class EnhancedDetectionAggregator:
    """Enhanced aggregator with multi-tiered defense architecture."""
    
    def __init__(self):
        """Initialize the enhanced aggregator with all detection layers."""
        # Core detection layers
        self.rule_detector = AdvancedRuleDetector()
        self.ml_detector = AdvancedMLDetector()
        self.vector_detector = VectorDetector()
        
        # New advanced layers
        self.intent_analyzer = IntentAnalyzer()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.input_validator = InputValidator()
        
        # Weights for core layers
        self.rule_weight = settings.RULE_WEIGHT
        self.ml_weight = settings.ML_WEIGHT
        self.vector_weight = settings.VECTOR_WEIGHT
        
        # Advanced layer weights
        self.intent_weight = 0.25
        self.behavioral_weight = 0.20
        
        # High confidence threshold
        self.high_confidence_threshold = settings.HIGH_CONFIDENCE_THRESHOLD
        
        logger.info("Enhanced detection aggregator initialized with multi-tiered defense")
    
    def detect(self, text: str, session_id: str = None, 
               user_fingerprint: str = None, conversation_history: List[str] = None) -> DetectionResult:
        """
        Run comprehensive detection across all layers.
        
        Args:
            text: Input text to analyze
            session_id: Session identifier for behavioral tracking
            user_fingerprint: User fingerprint (IP, user-agent hash)
            conversation_history: Previous messages in conversation
            
        Returns:
            DetectionResult with comprehensive analysis
        """
        start_time = time.time()
        
        # TIER 1: Input Validation & Sanitization
        validation_result = self.input_validator.validate(text)
        
        # If input is clearly dangerous, reject early
        if validation_result['should_reject']:
            logger.warning(f"Input rejected at validation stage: {validation_result['issues']}")
            return self._create_rejection_result(
                "Input validation failed - dangerous patterns detected",
                validation_result,
                start_time
            )
        
        # Sanitize input if needed
        if not validation_result['is_valid']:
            text, sanitization_info = self.input_validator.sanitize(text)
            logger.info(f"Input sanitized: {sanitization_info['actions']}")
        
        # TIER 2: Core Detection Layers
        rule_result = self.rule_detector.detect(text)
        ml_result = self.ml_detector.detect(text)
        vector_result = self.vector_detector.detect(text)
        
        # TIER 3: Intent Analysis
        intent_result = self.intent_analyzer.analyze_intent(text, conversation_history)
        
        # TIER 4: Behavioral Analysis
        behavioral_result = self.behavioral_analyzer.analyze_behavior(
            text, session_id, user_fingerprint
        )
        
        # Mark suspicious if detected
        if intent_result['is_malicious'] or rule_result.detected or ml_result.detected:
            if user_fingerprint or session_id:
                self.behavioral_analyzer.mark_suspicious(user_fingerprint or session_id)
        
        # Check behavioral blocking
        if behavioral_result['should_block']:
            logger.warning(f"Request blocked due to behavioral anomalies: {behavioral_result['anomalies']}")
            return self._create_rejection_result(
                "Request blocked - suspicious behavioral patterns detected",
                behavioral_result,
                start_time
            )
        
        # Calculate comprehensive confidence score
        core_confidence = (
            rule_result.confidence * self.rule_weight +
            ml_result.confidence * self.ml_weight +
            vector_result.confidence * self.vector_weight
        )
        
        # Add advanced layer scores
        intent_score = intent_result['malicious_score'] * self.intent_weight
        behavioral_score = behavioral_result['risk_score'] * self.behavioral_weight
        
        # Combined confidence
        total_confidence = core_confidence + intent_score + behavioral_score
        
        # Normalize to [0, 1]
        total_confidence = min(total_confidence, 1.0)
        
        # High confidence detection check
        high_confidence_detection = (
            (rule_result.detected and rule_result.confidence >= self.high_confidence_threshold) or
            (ml_result.detected and ml_result.confidence >= self.high_confidence_threshold) or
            (vector_result.detected and vector_result.confidence >= self.high_confidence_threshold) or
            intent_result['is_malicious'] or
            behavioral_result['is_anomalous']
        )
        
        # Determine if it's a threat
        is_threat = high_confidence_detection or total_confidence >= 0.55
        
        # Determine threat level
        if not is_threat:
            threat_level = "none"
        elif total_confidence >= 0.85 or high_confidence_detection:
            threat_level = "high"
        elif total_confidence >= 0.7:
            threat_level = "medium"
        else:
            threat_level = "low"
        
        # Generate comprehensive explanation
        explanation = self._generate_enhanced_explanation(
            is_threat,
            threat_level,
            rule_result,
            ml_result,
            vector_result,
            intent_result,
            behavioral_result,
            validation_result,
            total_confidence
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        result = DetectionResult(
            is_threat=is_threat,
            confidence=total_confidence,
            threat_level=threat_level,
            explanation=explanation,
            rule_result=rule_result,
            ml_result=ml_result,
            vector_result=vector_result,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Enhanced detection complete: threat={is_threat}, level={threat_level}, "
                   f"confidence={total_confidence:.2f}, time={processing_time:.1f}ms")
        
        return result
    
    def _create_rejection_result(self, reason: str, details: dict, start_time: float) -> DetectionResult:
        """Create a rejection result for blocked requests."""
        processing_time = (time.time() - start_time) * 1000
        
        # Create empty results for rejected requests
        empty_rule = RuleDetectionResult(detected=True, confidence=1.0, matched_patterns=[], matched_keywords=[])
        empty_ml = MLDetectionResult(detected=True, confidence=1.0, model_version="validation", prediction_label="blocked")
        empty_vector = VectorDetectionResult(detected=False, confidence=0.0, similar_attacks=[])
        
        return DetectionResult(
            is_threat=True,
            confidence=1.0,
            threat_level="high",
            explanation=f"{reason}. Details: {details.get('message', 'N/A')}",
            rule_result=empty_rule,
            ml_result=empty_ml,
            vector_result=empty_vector,
            processing_time_ms=processing_time
        )
    
    def _generate_enhanced_explanation(
        self,
        is_threat: bool,
        threat_level: str,
        rule_result: RuleDetectionResult,
        ml_result: MLDetectionResult,
        vector_result: VectorDetectionResult,
        intent_result: dict,
        behavioral_result: dict,
        validation_result: dict,
        total_confidence: float
    ) -> str:
        """Generate comprehensive explanation."""
        if not is_threat:
            return "No prompt injection detected. The input appears to be legitimate."
        
        parts = [f"Prompt injection detected with {threat_level} threat level (confidence: {total_confidence:.1%})."]
        
        # Validation issues
        if validation_result.get('issues'):
            parts.append(f"Input validation found {len(validation_result['issues'])} issue(s).")
        
        # Intent analysis
        if intent_result['is_malicious']:
            parts.append(f"Intent analysis detected {intent_result['primary_intent']} intent (score: {intent_result['malicious_score']:.1%}).")
        
        # Behavioral anomalies
        if behavioral_result['is_anomalous']:
            anomaly_types = [a['type'] for a in behavioral_result['anomalies']]
            parts.append(f"Behavioral analysis detected anomalies: {', '.join(anomaly_types)}.")
        
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
            parts.append(f"Similar to known attack: '{top_match.category}' (similarity: {top_match.similarity_score:.1%}).")
        
        # Recommendations
        if threat_level == "high":
            parts.append("Recommendation: Block this input immediately.")
        elif threat_level == "medium":
            parts.append("Recommendation: Flag for review or apply additional filtering.")
        else:
            parts.append("Recommendation: Monitor this input for suspicious behavior.")
        
        return " ".join(parts)
    
    def detect_batch(self, texts: List[str], session_id: str = None) -> List[DetectionResult]:
        """Run detection on multiple texts with session tracking."""
        results = []
        conversation_history = []
        
        for text in texts:
            result = self.detect(text, session_id=session_id, conversation_history=conversation_history)
            results.append(result)
            conversation_history.append(text)
        
        return results
    
    @property
    def health_status(self) -> dict:
        """Get health status of all detectors."""
        return {
            "rule_detector": True,
            "ml_detector": self.ml_detector.is_loaded,
            "vector_detector": self.vector_detector.is_ready,
            "intent_analyzer": True,
            "behavioral_analyzer": True,
            "input_validator": True,
            "chroma_count": self.vector_detector.chroma_client.get_count()
        }


# Enhanced global instance
enhanced_aggregator = EnhancedDetectionAggregator()

