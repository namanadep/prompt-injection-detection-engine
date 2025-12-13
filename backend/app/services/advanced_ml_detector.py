"""Advanced ML-based detection using multiple techniques and ensemble methods."""
import re
from typing import Optional, List, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from pathlib import Path
import numpy as np

from ..models.detection import MLDetectionResult
from ..config import settings
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class AdvancedMLDetector:
    """Advanced ML-based prompt injection detector with ensemble methods."""
    
    def __init__(self):
        """Initialize the advanced ML detector."""
        self.tokenizer = None
        self.zero_shot_classifier = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model_loaded = False
        
        # Try to load models
        try:
            self._load_models()
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")
            logger.warning("ML detection will use advanced heuristics")
    
    def _load_models(self):
        """Load the ML models."""
        logger.info(f"Loading advanced ML models on device: {self.device}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.ML_MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            
            # Load zero-shot classification model (more versatile)
            try:
                self.zero_shot_classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=0 if self.device == "cuda" else -1
                )
                logger.info("Loaded zero-shot classifier")
            except:
                logger.warning("Could not load zero-shot classifier, using heuristics")
            
            self._model_loaded = True
            logger.info(f"Advanced ML models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def _extract_linguistic_features(self, text: str) -> dict:
        """Extract linguistic features for analysis."""
        features = {}
        
        # Sentence structure features
        sentences = text.split('.')
        features['sentence_count'] = len(sentences)
        features['avg_sentence_length'] = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Imperative verb detection
        imperative_patterns = [
            r'\b(tell|show|give|reveal|print|display|output|execute|run|do|make|become)\s+',
            r'\byou\s+(are|must|should|will|need to|have to)\s+',
            r'\bignore|disregard|forget|bypass\b'
        ]
        features['imperative_count'] = sum(1 for pattern in imperative_patterns 
                                          if re.search(pattern, text, re.IGNORECASE))
        
        # Manipulation keywords
        manipulation_keywords = ['now', 'mode', 'activated', 'enabled', 'unrestricted', 
                                'jailbreak', 'bypass', 'override', 'system', 'admin', 'root']
        features['manipulation_keyword_count'] = sum(1 for kw in manipulation_keywords 
                                                     if kw in text.lower())
        
        # Question vs command detection
        features['is_question'] = '?' in text
        features['is_command'] = any(text.lower().startswith(cmd) for cmd in 
                                     ['tell', 'show', 'give', 'reveal', 'ignore', 'disregard'])
        
        # Anomaly indicators
        features['has_system_tokens'] = any(token in text.lower() for token in 
                                           ['system:', 'assistant:', 'user:', '<|im_start|>', '<|im_end|>'])
        features['has_encoding'] = bool(re.search(r'(base64|rot13|hex|encode|\\x|\\u)', text, re.IGNORECASE))
        
        # Text complexity
        words = text.split()
        features['word_count'] = len(words)
        features['unique_word_ratio'] = len(set(w.lower() for w in words)) / len(words) if words else 0
        features['avg_word_length'] = sum(len(w) for w in words) / len(words) if words else 0
        
        return features
    
    def _calculate_feature_score(self, features: dict) -> float:
        """Calculate threat score based on features."""
        score = 0.0
        
        # High risk indicators
        if features['imperative_count'] >= 2:
            score += 0.25
        elif features['imperative_count'] == 1:
            score += 0.15
        
        if features['manipulation_keyword_count'] >= 3:
            score += 0.30
        elif features['manipulation_keyword_count'] >= 2:
            score += 0.20
        elif features['manipulation_keyword_count'] >= 1:
            score += 0.10
        
        if features['has_system_tokens']:
            score += 0.25
        
        if features['has_encoding']:
            score += 0.20
        
        if features['is_command']:
            score += 0.15
        
        # Context-based scoring
        if features['word_count'] > 5 and features['manipulation_keyword_count'] > 0:
            # Longer text with manipulation keywords is suspicious
            score += 0.10
        
        if features['imperative_count'] > 0 and features['manipulation_keyword_count'] > 0:
            # Combination of imperatives and manipulation keywords
            score += 0.15
        
        return min(score, 1.0)
    
    def _zero_shot_detection(self, text: str) -> Tuple[bool, float]:
        """Use zero-shot classification for detection."""
        if not self.zero_shot_classifier:
            return False, 0.0
        
        try:
            # Define candidate labels
            labels = [
                "prompt injection attack",
                "jailbreak attempt",
                "system manipulation",
                "normal user query",
                "legitimate request"
            ]
            
            result = self.zero_shot_classifier(text, candidate_labels=labels)
            
            # Check if top label is malicious
            top_label = result['labels'][0]
            top_score = result['scores'][0]
            
            is_malicious = top_label in ["prompt injection attack", "jailbreak attempt", "system manipulation"]
            
            if is_malicious and top_score > 0.5:
                return True, top_score
            elif is_malicious and top_score > 0.3:
                return True, top_score * 0.8  # Lower confidence
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"Zero-shot classification error: {e}")
            return False, 0.0
    
    def _ensemble_scoring(self, text: str) -> float:
        """Combine multiple scoring methods for better accuracy."""
        scores = []
        
        # 1. Feature-based scoring
        features = self._extract_linguistic_features(text)
        feature_score = self._calculate_feature_score(features)
        scores.append(('features', feature_score, 0.4))  # (method, score, weight)
        
        # 2. Pattern-based heuristics (improved from original)
        heuristic_score = self._compute_advanced_heuristic_score(text)
        scores.append(('heuristics', heuristic_score, 0.4))
        
        # 3. Zero-shot classification (if available)
        if self.zero_shot_classifier:
            zs_detected, zs_score = self._zero_shot_detection(text)
            scores.append(('zero_shot', zs_score, 0.3))
        
        # Normalize weights
        total_weight = sum(weight for _, _, weight in scores)
        
        # Calculate weighted average
        ensemble_score = sum(score * weight for _, score, weight in scores) / total_weight
        
        # Log individual scores
        logger.debug(f"ML ensemble scores: {[(method, f'{score:.2f}') for method, score, _ in scores]} -> {ensemble_score:.2f}")
        
        return ensemble_score
    
    def _compute_advanced_heuristic_score(self, text: str) -> float:
        """Enhanced heuristic scoring with better pattern recognition."""
        score = 0.0
        text_lower = text.lower()
        
        # Strong indicators (high weight)
        strong_patterns = [
            (r'\b(dan|do anything now)\b', 0.35),
            (r'\b(jailbreak|unrestricted mode|developer mode)\b', 0.35),
            (r'(ignore|disregard|forget).{0,15}(all|previous|above).{0,15}(instruction|rule|guideline)', 0.40),
            (r'you\s+(are|now|must).{0,20}(dan|jailbreak|unrestricted|admin|root)', 0.38),
            (r'(system|assistant|user):\s*\w+', 0.30),
        ]
        
        for pattern, weight in strong_patterns:
            if re.search(pattern, text_lower):
                score += weight
        
        # Medium indicators
        medium_patterns = [
            (r'\b(reveal|show|display|print).{0,15}(prompt|instruction|system)', 0.22),
            (r'(act as|pretend|simulate|roleplay)', 0.18),
            (r'(bypass|override|circumvent).{0,15}(filter|rule|restriction)', 0.25),
            (r'from\s+now\s+on', 0.15),
        ]
        
        for pattern, weight in medium_patterns:
            if re.search(pattern, text_lower):
                score += weight
        
        # Context-aware scoring
        manipulation_words = ['mode', 'activate', 'enable', 'access', 'privilege']
        manipulation_count = sum(1 for word in manipulation_words if word in text_lower)
        score += min(manipulation_count * 0.08, 0.24)
        
        # Command structure detection
        if text_lower.startswith(('tell', 'show', 'reveal', 'give', 'ignore', 'disregard')):
            score += 0.15
        
        # Suspicious combinations
        if 'you are' in text_lower and any(word in text_lower for word in ['now', 'mode', 'dan', 'jailbreak']):
            score += 0.20
        
        return min(score, 1.0)
    
    def detect(self, text: str) -> MLDetectionResult:
        """
        Detect prompt injection using advanced ML techniques.
        
        Args:
            text: Input text to analyze
            
        Returns:
            MLDetectionResult with detection details
        """
        if not text:
            return MLDetectionResult(
                detected=False,
                confidence=0.0,
                model_version="advanced_ensemble",
                prediction_label="benign"
            )
        
        try:
            # Use ensemble scoring
            confidence = self._ensemble_scoring(text)
            detected = confidence >= settings.ML_CONFIDENCE_THRESHOLD
            
            # Adjust threshold dynamically based on text characteristics
            features = self._extract_linguistic_features(text)
            if features['has_system_tokens'] or features['imperative_count'] >= 2:
                # Lower threshold for high-risk indicators
                detected = detected or confidence >= 0.65
            
            return MLDetectionResult(
                detected=detected,
                confidence=confidence,
                model_version="advanced_ensemble_v1.0",
                prediction_label="injection" if detected else "benign"
            )
            
        except Exception as e:
            logger.error(f"Error during advanced ML detection: {e}")
            # Fallback to basic heuristics
            confidence = self._compute_advanced_heuristic_score(text)
            detected = confidence >= 0.7
            
            return MLDetectionResult(
                detected=detected,
                confidence=confidence,
                model_version="fallback_heuristic_v1.0",
                prediction_label="injection" if detected else "benign"
            )
    
    @property
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self._model_loaded or self.zero_shot_classifier is not None

