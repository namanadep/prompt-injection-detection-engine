"""API request models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class DetectionRequest(BaseModel):
    """Request for single text detection."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze for prompt injection")
    session_id: Optional[str] = Field(None, description="Session identifier for behavioral tracking")
    user_fingerprint: Optional[str] = Field(None, description="User fingerprint (IP hash, user-agent hash, etc.)")
    conversation_history: Optional[List[str]] = Field(None, description="Previous messages in conversation for context analysis")
    

class BatchDetectionRequest(BaseModel):
    """Request for batch detection."""
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to analyze")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    models_loaded: bool
    chroma_connected: bool

