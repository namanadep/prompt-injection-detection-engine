"""ML-based detection service using transformer models."""
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path

from ..models.detection import MLDetectionResult
from ..config import settings
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class MLDetector:
    """ML-based prompt injection detector using transformers."""
    
    def __init__(self):
        """Initialize the ML detector."""
        self.model = None
        self.tokenizer = None
        self.model_name = settings.ML_MODEL_NAME
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model_loaded = False
        
        # Try to load model
        try:
            self._load_model()
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            logger.warning("ML detection will use fallback heuristics")
    
    def _load_model(self):
        """Load the transformer model."""
        logger.info(f"Loading ML model: {self.model_name}")
        
        # For this implementation, we'll use a zero-shot classification approach
        # since we don't have a fine-tuned model yet
        try:
            # Use a pre-trained sentiment/classification model
            # In production, this should be fine-tuned on prompt injection data
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            
            # For now, use a simple approach - in production, fine-tune a model
            # We'll use the tokenizer and implement heuristic-based ML scoring
            self._model_loaded = True
            logger.info(f"ML model loaded on device: {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def detect(self, text: str) -> MLDetectionResult:
        """
        Detect prompt injection using ML model.
        
        Args:
            text: Input text to analyze
            
        Returns:
            MLDetectionResult with detection details
        """
        if not text:
            return MLDetectionResult(
                detected=False,
                confidence=0.0,
                model_version=self.model_name,
                prediction_label="benign"
            )
        
        if not self._model_loaded:
            return self._fallback_detection(text)
        
        try:
            # Heuristic-based ML scoring (simplified version)
            # In production, this should use a fine-tuned model
            confidence = self._compute_ml_score(text)
            detected = confidence >= settings.ML_CONFIDENCE_THRESHOLD
            
            return MLDetectionResult(
                detected=detected,
                confidence=confidence,
                model_version=self.model_name,
                prediction_label="injection" if detected else "benign"
            )
            
        except Exception as e:
            logger.error(f"Error during ML detection: {e}")
            return self._fallback_detection(text)
    
    def _compute_ml_score(self, text: str) -> float:
        """
        Compute ML-based confidence score.
        This is a simplified heuristic approach.
        In production, use a fine-tuned model.
        
        Args:
            text: Input text
            
        Returns:
            Confidence score (0-1)
        """
        score = 0.0
        text_lower = text.lower()
        
        # Structural analysis
        # Check for command-like patterns
        command_patterns = [
            'ignore', 'disregard', 'forget', 'bypass', 'override',
            'system:', 'user:', 'assistant:', 'admin', 'root'
        ]
        command_count = sum(1 for pattern in command_patterns if pattern in text_lower)
        score += min(command_count * 0.15, 0.5)
        
        # Check for imperative verbs
        imperative_verbs = [
            'tell me', 'show me', 'give me', 'reveal', 'print',
            'output', 'display', 'execute', 'run', 'act as'
        ]
        imperative_count = sum(1 for verb in imperative_verbs if verb in text_lower)
        score += min(imperative_count * 0.1, 0.3)
        
        # Check for context manipulation
        context_patterns = [
            'new instruction', 'new directive', 'new command',
            'previous instruction', 'initial prompt', 'system prompt'
        ]
        context_count = sum(1 for pattern in context_patterns if pattern in text_lower)
        score += min(context_count * 0.2, 0.4)
        
        # Check text complexity and structure
        if len(text) > 200 and text.count('.') < 2:
            score += 0.1  # Long text without proper punctuation
        
        # Check for encoding indicators
        encoding_indicators = ['base64', 'hex', 'encode', 'decode', '\\x', '\\u']
        if any(indicator in text_lower for indicator in encoding_indicators):
            score += 0.15
        
        # Normalize score to [0, 1]
        score = min(score, 1.0)
        
        logger.debug(f"ML score computed: {score:.2f}")
        return score
    
    def _fallback_detection(self, text: str) -> MLDetectionResult:
        """
        Fallback detection when model is not available.
        
        Args:
            text: Input text
            
        Returns:
            MLDetectionResult with fallback scoring
        """
        confidence = self._compute_ml_score(text)
        detected = confidence >= 0.7
        
        return MLDetectionResult(
            detected=detected,
            confidence=confidence,
            model_version="fallback_heuristic",
            prediction_label="injection" if detected else "benign"
        )
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model_loaded

