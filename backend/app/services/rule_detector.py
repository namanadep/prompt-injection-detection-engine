"""Rule-based detection service using regex patterns and keyword matching."""
import re
import json
from typing import List, Dict
from pathlib import Path

from ..models.detection import RuleDetectionResult, PatternMatch
from ..config import settings
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class RuleBasedDetector:
    """Rule-based prompt injection detector."""
    
    def __init__(self):
        """Initialize the rule-based detector."""
        self.patterns = []
        self.keywords = {}
        self._load_patterns()
        logger.info(f"Loaded {len(self.patterns)} detection patterns")
    
    def _load_patterns(self):
        """Load patterns from JSON file."""
        try:
            patterns_file = Path(settings.INJECTION_PATTERNS_FILE)
            if not patterns_file.exists():
                logger.warning(f"Patterns file not found: {patterns_file}")
                return
            
            with open(patterns_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.patterns = data.get('patterns', [])
                self.keywords = data.get('keywords', {})
                
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
    
    def detect(self, text: str) -> RuleDetectionResult:
        """
        Detect prompt injection using rule-based patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            RuleDetectionResult with detection details
        """
        if not text:
            return RuleDetectionResult(
                detected=False,
                confidence=0.0,
                matched_patterns=[],
                matched_keywords=[]
            )
        
        matched_patterns = []
        matched_keywords = []
        
        # Pattern matching
        for pattern_data in self.patterns:
            try:
                pattern = pattern_data['regex']
                if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                    matched_patterns.append(PatternMatch(
                        pattern_id=pattern_data['id'],
                        pattern_name=pattern_data['name'],
                        severity=pattern_data['severity'],
                        confidence=pattern_data['confidence']
                    ))
            except re.error as e:
                logger.error(f"Regex error in pattern {pattern_data.get('id')}: {e}")
        
        # Keyword matching
        text_lower = text.lower()
        for risk_level, keyword_list in self.keywords.items():
            if isinstance(keyword_list, list):
                for keyword in keyword_list:
                    if keyword.lower() in text_lower:
                        matched_keywords.append(f"{risk_level}:{keyword}")
        
        # Calculate overall confidence
        detected = len(matched_patterns) > 0 or len(matched_keywords) > 0
        
        if not detected:
            confidence = 0.0
        else:
            # Weight by pattern confidence and count
            pattern_confidence = max([p.confidence for p in matched_patterns]) if matched_patterns else 0.0
            keyword_confidence = 0.5 if matched_keywords else 0.0
            
            # Boost confidence if multiple patterns match
            if len(matched_patterns) > 1:
                pattern_confidence = min(pattern_confidence + 0.1 * (len(matched_patterns) - 1), 1.0)
            
            confidence = max(pattern_confidence, keyword_confidence)
        
        result = RuleDetectionResult(
            detected=detected,
            confidence=confidence,
            matched_patterns=matched_patterns,
            matched_keywords=matched_keywords
        )
        
        logger.debug(f"Rule detection: detected={detected}, confidence={confidence:.2f}, "
                    f"patterns={len(matched_patterns)}, keywords={len(matched_keywords)}")
        
        return result

