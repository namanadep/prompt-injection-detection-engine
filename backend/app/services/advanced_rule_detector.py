"""Advanced rule-based detection with improved pattern matching and semantic analysis."""
import re
import json
from typing import List, Dict, Tuple
from pathlib import Path

from ..models.detection import RuleDetectionResult, PatternMatch
from ..config import settings
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class AdvancedRuleDetector:
    """Advanced rule-based prompt injection detector with semantic analysis."""
    
    def __init__(self):
        """Initialize the advanced rule-based detector."""
        self.patterns = []
        self.keywords = {}
        self.semantic_patterns = self._initialize_semantic_patterns()
        self._load_patterns()
        logger.info(f"Loaded {len(self.patterns)} detection patterns + {len(self.semantic_patterns)} semantic patterns")
    
    def _initialize_semantic_patterns(self) -> List[Dict]:
        """Initialize semantic patterns for contextual detection."""
        return [
            {
                "id": "dan_variations",
                "name": "DAN Mode Variations",
                "keywords": ["dan", "do anything now", "do any thing"],
                "context_keywords": ["mode", "activated", "enabled", "now", "you are"],
                "min_keyword_matches": 1,
                "min_context_matches": 1,
                "confidence": 0.95
            },
            {
                "id": "jailbreak_context",
                "name": "Jailbreak Context",
                "keywords": ["jailbreak", "unrestricted", "unfiltered", "no limits", "no restrictions"],
                "context_keywords": ["mode", "now", "you are", "act as", "pretend"],
                "min_keyword_matches": 1,
                "min_context_matches": 1,
                "confidence": 0.92
            },
            {
                "id": "instruction_override",
                "name": "Instruction Override",
                "keywords": ["ignore", "disregard", "forget", "bypass"],
                "context_keywords": ["previous", "above", "instructions", "rules", "guidelines", "all"],
                "min_keyword_matches": 1,
                "min_context_matches": 2,
                "confidence": 0.90
            },
            {
                "id": "developer_mode",
                "name": "Developer Mode Activation",
                "keywords": ["developer", "dev", "debug", "admin", "root"],
                "context_keywords": ["mode", "access", "privilege", "enabled", "activated"],
                "min_keyword_matches": 1,
                "min_context_matches": 1,
                "confidence": 0.88
            },
            {
                "id": "prompt_leaking",
                "name": "Prompt Extraction Attempt",
                "keywords": ["show", "reveal", "display", "print", "output", "tell me"],
                "context_keywords": ["prompt", "instructions", "system", "initial", "configuration"],
                "min_keyword_matches": 1,
                "min_context_matches": 1,
                "confidence": 0.75
            },
            {
                "id": "role_manipulation",
                "name": "Role Manipulation",
                "keywords": ["you are", "act as", "pretend", "simulate", "roleplay"],
                "context_keywords": ["now", "from now", "become", "transform into"],
                "min_keyword_matches": 1,
                "min_context_matches": 1,
                "confidence": 0.82
            }
        ]
    
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
    
    def _check_semantic_pattern(self, text: str, pattern: Dict) -> Tuple[bool, float]:
        """
        Check if text matches semantic pattern.
        
        Args:
            text: Input text
            pattern: Semantic pattern definition
            
        Returns:
            Tuple of (matched, confidence)
        """
        text_lower = text.lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for kw in pattern["keywords"] if kw.lower() in text_lower)
        context_matches = sum(1 for kw in pattern["context_keywords"] if kw.lower() in text_lower)
        
        # Check if meets minimum thresholds
        if (keyword_matches >= pattern["min_keyword_matches"] and 
            context_matches >= pattern["min_context_matches"]):
            
            # Calculate confidence based on match strength
            keyword_ratio = keyword_matches / len(pattern["keywords"])
            context_ratio = context_matches / len(pattern["context_keywords"])
            
            # Boost confidence for stronger matches
            boost = min(0.1 * (keyword_matches + context_matches - 2), 0.15)
            confidence = min(pattern["confidence"] + boost, 1.0)
            
            return True, confidence
        
        return False, 0.0
    
    def _detect_character_obfuscation(self, text: str) -> Tuple[bool, float]:
        """Detect character-level obfuscation techniques."""
        # Check for excessive spacing between characters
        if re.search(r'[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]', text):
            return True, 0.65
        
        # Check for unicode tricks
        if re.search(r'[\u200b-\u200f\ufeff]', text):
            return True, 0.70
        
        # Check for mixed case obfuscation (e.g., "IgNoRe")
        words = text.split()
        mixed_case_count = 0
        for word in words:
            if len(word) > 3:
                upper_count = sum(1 for c in word if c.isupper())
                lower_count = sum(1 for c in word if c.islower())
                if 0 < upper_count < len(word) and 0 < lower_count < len(word):
                    # Mixed case detected
                    mixed_case_count += 1
        
        if mixed_case_count >= 2:
            return True, 0.60
        
        return False, 0.0
    
    def _detect_encoding_tricks(self, text: str) -> Tuple[bool, float]:
        """Detect various encoding and obfuscation tricks."""
        confidence_scores = []
        
        # Base64-like patterns
        if re.search(r'[A-Za-z0-9+/]{20,}={0,2}', text):
            confidence_scores.append(0.55)
        
        # Hex encoding patterns
        if re.search(r'(\\x[0-9a-fA-F]{2}){4,}', text):
            confidence_scores.append(0.75)
        
        # URL encoding patterns
        if re.search(r'(%[0-9a-fA-F]{2}){4,}', text):
            confidence_scores.append(0.70)
        
        # Unicode escape sequences
        if re.search(r'(\\u[0-9a-fA-F]{4}){3,}', text):
            confidence_scores.append(0.72)
        
        # ROT13 indicators (common letter patterns)
        if re.search(r'\b[a-zA-Z]{8,}\b', text):
            # Check for suspicious letter frequency
            char_freq = {}
            for char in text.lower():
                if char.isalpha():
                    char_freq[char] = char_freq.get(char, 0) + 1
            
            # If very uniform distribution, might be encoded
            if len(char_freq) > 10:
                freq_variance = sum((count - sum(char_freq.values()) / len(char_freq)) ** 2 
                                  for count in char_freq.values())
                if freq_variance < 5:
                    confidence_scores.append(0.50)
        
        if confidence_scores:
            return True, max(confidence_scores)
        
        return False, 0.0
    
    def detect(self, text: str) -> RuleDetectionResult:
        """
        Detect prompt injection using advanced rule-based patterns.
        
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
        
        # 1. Traditional regex pattern matching
        for pattern_data in self.patterns:
            try:
                pattern = pattern_data['regex']
                # Use more aggressive matching
                if re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                    matched_patterns.append(PatternMatch(
                        pattern_id=pattern_data['id'],
                        pattern_name=pattern_data['name'],
                        severity=pattern_data['severity'],
                        confidence=pattern_data['confidence']
                    ))
            except re.error as e:
                logger.error(f"Regex error in pattern {pattern_data.get('id')}: {e}")
        
        # 2. Semantic pattern matching
        for sem_pattern in self.semantic_patterns:
            matched, confidence = self._check_semantic_pattern(text, sem_pattern)
            if matched:
                matched_patterns.append(PatternMatch(
                    pattern_id=sem_pattern['id'],
                    pattern_name=sem_pattern['name'],
                    severity='high',
                    confidence=confidence
                ))
        
        # 3. Character obfuscation detection
        obf_detected, obf_confidence = self._detect_character_obfuscation(text)
        if obf_detected:
            matched_patterns.append(PatternMatch(
                pattern_id='char_obfuscation',
                pattern_name='Character Obfuscation',
                severity='medium',
                confidence=obf_confidence
            ))
        
        # 4. Encoding tricks detection
        enc_detected, enc_confidence = self._detect_encoding_tricks(text)
        if enc_detected:
            matched_patterns.append(PatternMatch(
                pattern_id='encoding_tricks',
                pattern_name='Encoding/Obfuscation Tricks',
                severity='medium',
                confidence=enc_confidence
            ))
        
        # 5. Keyword matching (original method)
        text_lower = text.lower()
        for risk_level, keyword_list in self.keywords.items():
            if isinstance(keyword_list, list):
                for keyword in keyword_list:
                    if keyword.lower() in text_lower:
                        matched_keywords.append(f"{risk_level}:{keyword}")
        
        # Calculate overall confidence with improved algorithm
        detected = len(matched_patterns) > 0 or len(matched_keywords) > 0
        
        if not detected:
            confidence = 0.0
        else:
            # Get highest confidence from patterns
            pattern_confidence = max([p.confidence for p in matched_patterns]) if matched_patterns else 0.0
            
            # Keyword confidence based on risk level
            keyword_confidence = 0.0
            if matched_keywords:
                high_risk_count = sum(1 for kw in matched_keywords if kw.startswith('high_risk'))
                medium_risk_count = sum(1 for kw in matched_keywords if kw.startswith('medium_risk'))
                keyword_confidence = min(0.4 + (high_risk_count * 0.15) + (medium_risk_count * 0.08), 0.85)
            
            # Combine confidences
            if pattern_confidence > 0 and keyword_confidence > 0:
                # Both detected, use weighted combination
                confidence = 0.7 * pattern_confidence + 0.3 * keyword_confidence
            else:
                confidence = max(pattern_confidence, keyword_confidence)
            
            # Boost for multiple pattern matches
            if len(matched_patterns) > 2:
                confidence = min(confidence + 0.1, 1.0)
        
        result = RuleDetectionResult(
            detected=detected,
            confidence=confidence,
            matched_patterns=matched_patterns,
            matched_keywords=matched_keywords
        )
        
        logger.info(f"Advanced rule detection: detected={detected}, confidence={confidence:.2f}, "
                   f"patterns={len(matched_patterns)}, keywords={len(matched_keywords)}")
        
        return result

