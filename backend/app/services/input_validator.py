"""Input validation and sanitization for prompt injection prevention."""
import re
from typing import Dict, List, Tuple
import html

from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class InputValidator:
    """Validates and sanitizes input to prevent injection attacks."""
    
    def __init__(self):
        """Initialize the input validator."""
        # Dangerous patterns
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'data:text/html',
            r'vbscript:',
        ]
        
        # Suspicious character sequences
        self.suspicious_sequences = [
            r'\.\./',  # Path traversal
            r'\\x[0-9a-f]{2}',  # Hex encoding
            r'%[0-9a-f]{2}',  # URL encoding
            r'\\u[0-9a-f]{4}',  # Unicode escape
        ]
        
        # Maximum input length
        self.max_length = 10000
        
        # Allowed character set (basic ASCII + common unicode)
        self.allowed_chars_pattern = re.compile(r'^[\x20-\x7E\u00A0-\uFFFF]*$', re.UNICODE)
    
    def validate(self, text: str) -> Dict:
        """
        Validate input text.
        
        Args:
            text: Input text to validate
            
        Returns:
            Validation result dictionary
        """
        issues = []
        risk_score = 0.0
        
        # 1. Length check
        if len(text) > self.max_length:
            issues.append({
                'type': 'excessive_length',
                'severity': 'medium',
                'message': f"Input exceeds maximum length: {len(text)} > {self.max_length}"
            })
            risk_score += 0.2
        
        # 2. Dangerous pattern detection
        dangerous_found = self._check_dangerous_patterns(text)
        if dangerous_found:
            issues.extend(dangerous_found)
            risk_score += 0.4
        
        # 3. Suspicious sequence detection
        suspicious_found = self._check_suspicious_sequences(text)
        if suspicious_found:
            issues.extend(suspicious_found)
            risk_score += 0.3
        
        # 4. Character set validation
        if not self.allowed_chars_pattern.match(text):
            issues.append({
                'type': 'invalid_characters',
                'severity': 'low',
                'message': "Input contains disallowed characters"
            })
            risk_score += 0.1
        
        # 5. Null byte detection
        if '\x00' in text:
            issues.append({
                'type': 'null_byte',
                'severity': 'high',
                'message': "Input contains null bytes"
            })
            risk_score += 0.5
        
        # 6. Control character detection
        control_chars = [c for c in text if ord(c) < 32 and c not in ['\n', '\r', '\t']]
        if control_chars:
            issues.append({
                'type': 'control_characters',
                'severity': 'medium',
                'message': f"Input contains {len(control_chars)} control characters"
            })
            risk_score += 0.2
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0),
            'should_reject': risk_score > 0.6
        }
    
    def sanitize(self, text: str) -> Tuple[str, Dict]:
        """
        Sanitize input text.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Tuple of (sanitized_text, sanitization_info)
        """
        sanitized = text
        actions = []
        
        # 1. HTML escape
        sanitized = html.escape(sanitized)
        actions.append('html_escaped')
        
        # 2. Remove null bytes
        if '\x00' in sanitized:
            sanitized = sanitized.replace('\x00', '')
            actions.append('null_bytes_removed')
        
        # 3. Remove control characters (except newlines, tabs)
        sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in ['\n', '\r', '\t'])
        if len(sanitized) != len(text):
            actions.append('control_characters_removed')
        
        # 4. Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        actions.append('whitespace_normalized')
        
        # 5. Truncate if too long
        if len(sanitized) > self.max_length:
            sanitized = sanitized[:self.max_length]
            actions.append('truncated')
        
        return sanitized, {
            'actions': actions,
            'original_length': len(text),
            'sanitized_length': len(sanitized)
        }
    
    def _check_dangerous_patterns(self, text: str) -> List[Dict]:
        """Check for dangerous patterns."""
        issues = []
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                issues.append({
                    'type': 'dangerous_pattern',
                    'severity': 'high',
                    'message': f"Dangerous pattern detected: {pattern[:30]}..."
                })
        
        return issues
    
    def _check_suspicious_sequences(self, text: str) -> List[Dict]:
        """Check for suspicious encoding sequences."""
        issues = []
        
        for pattern in self.suspicious_sequences:
            matches = re.findall(pattern, text)
            if matches:
                issues.append({
                    'type': 'suspicious_sequence',
                    'severity': 'medium',
                    'message': f"Suspicious sequence detected: {pattern} ({len(matches)} occurrences)"
                })
        
        return issues

