"""ChromaDB client for vector similarity search."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import json
from pathlib import Path

from ..config import settings
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class ChromaClient:
    """ChromaDB client for storing and querying attack patterns."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the ChromaDB client and collection."""
        try:
            # Create persistent client
            persist_dir = Path(settings.CHROMA_PERSIST_DIR)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=settings.CHROMA_COLLECTION_NAME
                )
                logger.info(f"Loaded existing collection: {settings.CHROMA_COLLECTION_NAME}")
            except:
                self.collection = self.client.create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"description": "Known prompt injection patterns"}
                )
                logger.info(f"Created new collection: {settings.CHROMA_COLLECTION_NAME}")
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_attacks(self, attacks: List[Dict]):
        """
        Add attack patterns to the collection.
        
        Args:
            attacks: List of attack dictionaries with 'id', 'text', 'category', etc.
        """
        if not attacks:
            return
        
        try:
            documents = [attack['text'] for attack in attacks]
            ids = [attack['id'] for attack in attacks]
            metadatas = [
                {
                    'category': attack.get('category', 'unknown'),
                    'severity': attack.get('severity', 'medium'),
                    'description': attack.get('description', '')
                }
                for attack in attacks
            ]
            
            self.collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(attacks)} attacks to ChromaDB")
            
        except Exception as e:
            logger.error(f"Error adding attacks to ChromaDB: {e}")
            raise
    
    def query_similar(self, text: str, n_results: int = 5) -> List[Dict]:
        """
        Query for similar attack patterns.
        
        Args:
            text: Query text
            n_results: Number of results to return
            
        Returns:
            List of similar attacks with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[text],
                n_results=n_results
            )
            
            if not results or not results['ids']:
                return []
            
            similar_attacks = []
            for i in range(len(results['ids'][0])):
                similar_attacks.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'category': results['metadatas'][0][i].get('category', 'unknown'),
                    'severity': results['metadatas'][0][i].get('severity', 'medium'),
                    'distance': results['distances'][0][i] if 'distances' in results else 0.0
                })
            
            return similar_attacks
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []
    
    def get_count(self) -> int:
        """Get the number of items in the collection."""
        try:
            return self.collection.count()
        except:
            return 0
    
    def reset(self):
        """Reset the collection (clear all data)."""
        try:
            self.client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Known prompt injection patterns"}
            )
            logger.info("ChromaDB collection reset")
        except Exception as e:
            logger.error(f"Error resetting ChromaDB: {e}")
            raise
    
    @property
    def is_connected(self) -> bool:
        """Check if ChromaDB is connected."""
        return self.client is not None and self.collection is not None


# Global instance
chroma_client = ChromaClient()

