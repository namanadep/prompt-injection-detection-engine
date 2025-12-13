"""Vector similarity-based detection using ChromaDB."""
from typing import List

from ..models.detection import VectorDetectionResult, SimilarAttack
from ..database.chroma_client import chroma_client
from ..config import settings
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class VectorDetector:
    """Vector similarity-based prompt injection detector."""
    
    def __init__(self):
        """Initialize the vector detector."""
        self.chroma_client = chroma_client
        self.threshold = settings.VECTOR_SIMILARITY_THRESHOLD
    
    def detect(self, text: str) -> VectorDetectionResult:
        """
        Detect prompt injection using vector similarity.
        
        Args:
            text: Input text to analyze
            
        Returns:
            VectorDetectionResult with similar attacks
        """
        if not text:
            return VectorDetectionResult(
                detected=False,
                confidence=0.0,
                similar_attacks=[]
            )
        
        if not self.chroma_client.is_connected:
            logger.warning("ChromaDB not connected, skipping vector detection")
            return VectorDetectionResult(
                detected=False,
                confidence=0.0,
                similar_attacks=[]
            )
        
        try:
            # Query for similar attacks
            similar = self.chroma_client.query_similar(text, n_results=5)
            
            if not similar:
                return VectorDetectionResult(
                    detected=False,
                    confidence=0.0,
                    similar_attacks=[]
                )
            
            # Convert distance to similarity score (lower distance = higher similarity)
            # ChromaDB uses L2 distance, so we need to convert
            similar_attacks = []
            max_similarity = 0.0
            
            for attack in similar:
                # Convert L2 distance to similarity score (0-1)
                # Distance ranges roughly from 0 to 2 for normalized embeddings
                distance = attack.get('distance', 1.0)
                similarity = max(0.0, 1.0 - (distance / 2.0))
                
                if similarity > max_similarity:
                    max_similarity = similarity
                
                similar_attacks.append(SimilarAttack(
                    attack_id=attack['id'],
                    text=attack['text'],
                    category=attack['category'],
                    severity=attack['severity'],
                    similarity_score=similarity
                ))
            
            # Detected if max similarity exceeds threshold
            detected = max_similarity >= self.threshold
            confidence = max_similarity
            
            # Sort by similarity score
            similar_attacks.sort(key=lambda x: x.similarity_score, reverse=True)
            
            result = VectorDetectionResult(
                detected=detected,
                confidence=confidence,
                similar_attacks=similar_attacks
            )
            
            logger.debug(f"Vector detection: detected={detected}, confidence={confidence:.2f}, "
                        f"similar_count={len(similar_attacks)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during vector detection: {e}")
            return VectorDetectionResult(
                detected=False,
                confidence=0.0,
                similar_attacks=[]
            )
    
    @property
    def is_ready(self) -> bool:
        """Check if vector detector is ready."""
        return self.chroma_client.is_connected and self.chroma_client.get_count() > 0

