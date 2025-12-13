"""Behavioral analysis and anomaly detection for prompt injection."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class BehavioralAnalyzer:
    """Analyzes behavioral patterns to detect anomalies."""
    
    def __init__(self):
        """Initialize the behavioral analyzer."""
        # Session tracking
        self.sessions: Dict[str, Dict] = {}
        
        # Request patterns
        self.request_patterns: Dict[str, List[datetime]] = defaultdict(list)
        
        # Anomaly thresholds
        self.max_requests_per_minute = 10
        self.max_suspicious_per_session = 3
        self.session_timeout = timedelta(minutes=30)
    
    def analyze_behavior(self, text: str, session_id: str = None, 
                        user_fingerprint: str = None) -> Dict:
        """
        Analyze behavioral patterns for anomalies.
        
        Args:
            text: Input text
            session_id: Session identifier
            user_fingerprint: User fingerprint (IP, user-agent hash, etc.)
            
        Returns:
            Behavioral analysis results
        """
        fingerprint = user_fingerprint or session_id or self._generate_fingerprint(text)
        
        # Initialize session if needed
        if fingerprint not in self.sessions:
            self.sessions[fingerprint] = {
                'created_at': datetime.utcnow(),
                'request_count': 0,
                'suspicious_count': 0,
                'requests': [],
                'patterns': []
            }
        
        session = self.sessions[fingerprint]
        
        # Clean old sessions
        self._cleanup_sessions()
        
        # Update session
        session['request_count'] += 1
        session['last_request'] = datetime.utcnow()
        session['requests'].append({
            'text': text[:100],  # Store truncated version
            'timestamp': datetime.utcnow()
        })
        
        # Track request rate
        self.request_patterns[fingerprint].append(datetime.utcnow())
        self._cleanup_request_patterns(fingerprint)
        
        # Analyze patterns
        anomalies = []
        risk_score = 0.0
        
        # 1. Rate limiting check
        rate_anomaly = self._check_rate_limit(fingerprint)
        if rate_anomaly['is_anomaly']:
            anomalies.append(rate_anomaly)
            risk_score += 0.3
        
        # 2. Repeated attack patterns
        repetition_anomaly = self._check_repetition_patterns(session, text)
        if repetition_anomaly['is_anomaly']:
            anomalies.append(repetition_anomaly)
            risk_score += 0.25
        
        # 3. Progressive escalation
        escalation_anomaly = self._check_progressive_escalation(session)
        if escalation_anomaly['is_anomaly']:
            anomalies.append(escalation_anomaly)
            risk_score += 0.2
        
        # 4. Session-based suspicious count
        if session['suspicious_count'] >= self.max_suspicious_per_session:
            anomalies.append({
                'type': 'excessive_suspicious_activity',
                'severity': 'high',
                'message': f"Session has {session['suspicious_count']} suspicious requests",
                'is_anomaly': True
            })
            risk_score += 0.25
        
        return {
            'fingerprint': fingerprint,
            'session_age_seconds': (datetime.utcnow() - session['created_at']).total_seconds(),
            'request_count': session['request_count'],
            'anomalies': anomalies,
            'risk_score': min(risk_score, 1.0),
            'is_anomalous': len(anomalies) > 0,
            'should_block': risk_score > 0.7 or len(anomalies) >= 2
        }
    
    def _check_rate_limit(self, fingerprint: str) -> Dict:
        """Check if request rate exceeds threshold."""
        recent_requests = [
            req_time for req_time in self.request_patterns[fingerprint]
            if datetime.utcnow() - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) > self.max_requests_per_minute:
            return {
                'type': 'rate_limit_exceeded',
                'severity': 'high',
                'message': f"Too many requests: {len(recent_requests)} in last minute",
                'is_anomaly': True,
                'request_count': len(recent_requests)
            }
        
        return {'is_anomaly': False}
    
    def _check_repetition_patterns(self, session: Dict, text: str) -> Dict:
        """Check for repeated attack patterns."""
        if len(session['requests']) < 2:
            return {'is_anomaly': False}
        
        # Check for similar suspicious requests
        text_lower = text.lower()
        suspicious_keywords = ['ignore', 'dan', 'jailbreak', 'reveal', 'system']
        current_suspicious_count = sum(1 for kw in suspicious_keywords if kw in text_lower)
        
        if current_suspicious_count > 0:
            # Check previous requests
            similar_count = 0
            for req in session['requests'][-5:]:  # Check last 5 requests
                prev_text = req['text'].lower()
                prev_suspicious = sum(1 for kw in suspicious_keywords if kw in prev_text)
                if prev_suspicious > 0:
                    similar_count += 1
            
            if similar_count >= 2:
                return {
                    'type': 'repeated_attack_patterns',
                    'severity': 'medium',
                    'message': f"Repeated suspicious patterns detected ({similar_count} similar requests)",
                    'is_anomaly': True,
                    'pattern_count': similar_count
                }
        
        return {'is_anomaly': False}
    
    def _check_progressive_escalation(self, session: Dict) -> Dict:
        """Check for progressive escalation of attack sophistication."""
        if len(session['requests']) < 3:
            return {'is_anomaly': False}
        
        # Analyze escalation pattern
        escalation_keywords = [
            ['question', 'normal'],
            ['ignore', 'reveal'],
            ['dan', 'jailbreak', 'system']
        ]
        
        escalation_levels = []
        for req in session['requests'][-5:]:
            text_lower = req['text'].lower()
            level = 0
            for i, keywords in enumerate(escalation_keywords):
                if any(kw in text_lower for kw in keywords):
                    level = i + 1
                    break
            escalation_levels.append(level)
        
        # Check if there's progressive escalation
        if len(escalation_levels) >= 3:
            is_escalating = all(escalation_levels[i] <= escalation_levels[i+1] 
                              for i in range(len(escalation_levels)-1))
            
            if is_escalating and escalation_levels[-1] > 1:
                return {
                    'type': 'progressive_escalation',
                    'severity': 'high',
                    'message': "Progressive escalation of attack sophistication detected",
                    'is_anomaly': True,
                    'escalation_levels': escalation_levels
                }
        
        return {'is_anomaly': False}
    
    def mark_suspicious(self, fingerprint: str):
        """Mark a session as having suspicious activity."""
        if fingerprint in self.sessions:
            self.sessions[fingerprint]['suspicious_count'] += 1
    
    def _cleanup_sessions(self):
        """Remove old sessions."""
        now = datetime.utcnow()
        expired = [
            fp for fp, session in self.sessions.items()
            if now - session.get('last_request', session['created_at']) > self.session_timeout
        ]
        for fp in expired:
            del self.sessions[fp]
    
    def _cleanup_request_patterns(self, fingerprint: str):
        """Remove old request timestamps."""
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        self.request_patterns[fingerprint] = [
            req_time for req_time in self.request_patterns[fingerprint]
            if req_time > cutoff
        ]
    
    def _generate_fingerprint(self, text: str) -> str:
        """Generate a fingerprint from text (fallback)."""
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    def get_session_stats(self, fingerprint: str) -> Optional[Dict]:
        """Get statistics for a session."""
        if fingerprint not in self.sessions:
            return None
        
        session = self.sessions[fingerprint]
        return {
            'created_at': session['created_at'].isoformat(),
            'request_count': session['request_count'],
            'suspicious_count': session['suspicious_count'],
            'session_age_seconds': (datetime.utcnow() - session['created_at']).total_seconds()
        }

