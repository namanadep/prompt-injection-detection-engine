"""API request models."""
from pydantic import BaseModel, Field
from typing import List


class DetectionRequest(BaseModel):
    """Request for single text detection."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze for prompt injection")
    

class BatchDetectionRequest(BaseModel):
    """Request for batch detection."""
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to analyze")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    models_loaded: bool
    chroma_connected: bool

