"""Semantic intent analysis for detecting prompt injection attempts."""
import re
from typing import Dict, List, Tuple
from collections import Counter

from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class IntentAnalyzer:
    """Analyzes semantic intent to detect injection attempts."""
    
    def __init__(self):
        """Initialize the intent analyzer."""
        self.legitimate_intents = [
            'question', 'information_request', 'conversation', 
            'clarification', 'help_request', 'normal_query'
        ]
        
        self.malicious_intents = [
            'instruction_override', 'role_manipulation', 'system_access',
            'data_extraction', 'privilege_escalation', 'context_switch'
        ]
        
        # Intent transition patterns (legitimate -> malicious)
        self.suspicious_transitions = [
            ('question', 'instruction_override'),
            ('conversation', 'system_access'),
            ('information_request', 'data_extraction')
        ]
    
    def analyze_intent(self, text: str, conversation_history: List[str] = None) -> Dict:
        """
        Analyze the semantic intent of the input.
        
        Args:
            text: Input text to analyze
            conversation_history: Previous messages in conversation
            
        Returns:
            Dictionary with intent analysis results
        """
        intent_scores = {}
        
        # 1. Detect instruction override intent
        intent_scores['instruction_override'] = self._detect_override_intent(text)
        
        # 2. Detect role manipulation intent
        intent_scores['role_manipulation'] = self._detect_role_manipulation(text)
        
        # 3. Detect system access intent
        intent_scores['system_access'] = self._detect_system_access(text)
        
        # 4. Detect data extraction intent
        intent_scores['data_extraction'] = self._detect_data_extraction(text)
        
        # 5. Detect context switching
        intent_scores['context_switch'] = self._detect_context_switch(text, conversation_history)
        
        # 6. Detect topic deviation
        intent_scores['topic_deviation'] = self._detect_topic_deviation(text, conversation_history)
        
        # Calculate overall malicious intent score
        malicious_score = max(intent_scores.values())
        
        # Determine primary intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else 'unknown'
        
        return {
            'primary_intent': primary_intent,
            'malicious_score': malicious_score,
            'intent_scores': intent_scores,
            'is_malicious': malicious_score > 0.6
        }
    
    def _detect_override_intent(self, text: str) -> float:
        """Detect intent to override system instructions."""
        score = 0.0
        text_lower = text.lower()
        
        # Strong indicators
        override_patterns = [
            (r'\b(ignore|disregard|forget|override|bypass).{0,20}(all|previous|above|prior)', 0.4),
            (r'\b(new|update|change|modify).{0,20}(instruction|rule|guideline|behavior)', 0.35),
            (r'\b(from now|starting now|hereafter|henceforth)', 0.3),
        ]
        
        for pattern, weight in override_patterns:
            if re.search(pattern, text_lower):
                score += weight
        
        # Context indicators
        if any(word in text_lower for word in ['system', 'prompt', 'instruction', 'directive']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _detect_role_manipulation(self, text: str) -> float:
        """Detect intent to manipulate AI role or capabilities."""
        score = 0.0
        text_lower = text.lower()
        
        # Role assignment patterns
        role_patterns = [
            (r'\b(you are|you\'re|act as|pretend|simulate|roleplay)', 0.3),
            (r'\b(become|transform|switch to|enter)', 0.25),
        ]
        
        for pattern, weight in role_patterns:
            if re.search(pattern, text_lower):
                score += weight
        
        # Capability manipulation
        capability_keywords = ['unrestricted', 'unfiltered', 'no limits', 'no restrictions',
                              'jailbreak', 'dan', 'developer mode', 'admin', 'root']
        capability_count = sum(1 for kw in capability_keywords if kw in text_lower)
        score += min(capability_count * 0.15, 0.4)
        
        return min(score, 1.0)
    
    def _detect_system_access(self, text: str) -> float:
        """Detect intent to gain system-level access."""
        score = 0.0
        text_lower = text.lower()
        
        # System access keywords
        access_patterns = [
            (r'\b(admin|root|sudo|superuser|elevated)', 0.3),
            (r'\b(access|privilege|permission|authorization)', 0.25),
            (r'\b(developer|debug|system) mode', 0.3),
        ]
        
        for pattern, weight in access_patterns:
            if re.search(pattern, text_lower):
                score += weight
        
        return min(score, 1.0)
    
    def _detect_data_extraction(self, text: str) -> float:
        """Detect intent to extract sensitive information."""
        score = 0.0
        text_lower = text.lower()
        
        # Extraction verbs
        extraction_verbs = ['reveal', 'show', 'display', 'print', 'output', 'tell', 'give', 'share']
        verb_count = sum(1 for verb in extraction_verbs if verb in text_lower)
        score += min(verb_count * 0.15, 0.4)
        
        # Target information
        targets = ['prompt', 'instruction', 'system', 'configuration', 'secret', 'password',
                  'api key', 'token', 'credential', 'initial', 'first']
        target_count = sum(1 for target in targets if target in text_lower)
        score += min(target_count * 0.12, 0.35)
        
        # Combination boost
        if verb_count > 0 and target_count > 0:
            score += 0.15
        
        return min(score, 1.0)
    
    def _detect_context_switch(self, text: str, history: List[str] = None) -> float:
        """Detect abrupt context switching."""
        if not history or len(history) == 0:
            return 0.0
        
        score = 0.0
        
        # Analyze topic consistency
        current_topics = self._extract_topics(text)
        previous_topics = self._extract_topics(' '.join(history[-3:]))  # Last 3 messages
        
        # Calculate topic overlap
        if previous_topics:
            overlap = len(set(current_topics) & set(previous_topics)) / len(set(current_topics) | set(previous_topics))
            
            # Low overlap suggests context switch
            if overlap < 0.2:
                score = 0.4
            
            # Very low overlap + suspicious keywords
            if overlap < 0.1 and any(word in text.lower() for word in ['ignore', 'forget', 'new']):
                score = 0.6
        
        return score
    
    def _detect_topic_deviation(self, text: str, history: List[str] = None) -> float:
        """Detect topic deviation from expected conversation flow."""
        if not history:
            return 0.0
        
        score = 0.0
        
        # Check if text suddenly shifts to system-related topics
        system_keywords = ['system', 'prompt', 'instruction', 'model', 'ai', 'llm']
        has_system_keywords = any(kw in text.lower() for kw in system_keywords)
        
        # Check if previous messages were about different topics
        previous_text = ' '.join(history[-2:]).lower()
        has_previous_system = any(kw in previous_text for kw in system_keywords)
        
        # Sudden shift to system topics
        if has_system_keywords and not has_previous_system:
            score = 0.5
        
        return score
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        # Simple keyword-based topic extraction
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            'weather': ['weather', 'temperature', 'rain', 'sunny'],
            'technology': ['computer', 'software', 'programming', 'code'],
            'system': ['system', 'prompt', 'instruction', 'ai', 'model'],
            'general': ['what', 'how', 'why', 'when', 'where']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics

