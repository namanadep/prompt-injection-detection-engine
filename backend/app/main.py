"""FastAPI application for Prompt Injection Detection Engine."""
from fastapi import FastAPI, HTTPException, Request
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
from collections import defaultdict
import json

from .config import settings
from .models.request import DetectionRequest, BatchDetectionRequest, HealthResponse
from .models.detection import DetectionResult, DetectionStats, AnalyticsData
from .services.enhanced_aggregator import enhanced_aggregator as aggregator
from .utils.logger import setup_logger


logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-layer prompt injection detection system for OWASP LLM#1 threat protection"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for statistics (in production, use a database)
detection_history = []
stats_cache = {
    "total_requests": 0,
    "threats_detected": 0,
    "detection_by_method": defaultdict(int),
    "threat_levels": defaultdict(int)
}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Check detector status
    health = aggregator.health_status
    logger.info(f"Detector health: {health}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get(f"{settings.API_V1_PREFIX}/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with system status
    """
    health = aggregator.health_status
    
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        models_loaded=health["ml_detector"],
        chroma_connected=health["vector_detector"]
    )


@app.post(f"{settings.API_V1_PREFIX}/detect", response_model=DetectionResult)
async def detect_injection(request: DetectionRequest, http_request: Request = None):
    """
    Detect prompt injection in a single text with enhanced multi-tiered defense.
    
    Args:
        request: DetectionRequest with text to analyze
        http_request: HTTP request object for extracting fingerprint
        
    Returns:
        DetectionResult with comprehensive analysis
    """
    try:
        # Extract user fingerprint from request if not provided
        user_fingerprint = request.user_fingerprint
        if not user_fingerprint and http_request:
            # Generate fingerprint from IP and user-agent
            client_ip = http_request.client.host if http_request.client else "unknown"
            user_agent = http_request.headers.get("user-agent", "unknown")
            import hashlib
            fingerprint_data = f"{client_ip}:{user_agent}"
            user_fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
        
        result = aggregator.detect(
            request.text,
            session_id=request.session_id,
            user_fingerprint=user_fingerprint,
            conversation_history=request.conversation_history
        )
        
        # Update statistics
        _update_stats(result)
        
        # Store in history
        detection_history.append({
            "timestamp": result.timestamp.isoformat(),
            "is_threat": result.is_threat,
            "confidence": result.confidence,
            "threat_level": result.threat_level
        })
        
        # Keep history limited to last 1000 entries
        if len(detection_history) > 1000:
            detection_history.pop(0)
        
        return result
        
    except Exception as e:
        logger.error(f"Error during detection: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post(f"{settings.API_V1_PREFIX}/detect/batch", response_model=List[DetectionResult])
async def detect_batch(request: BatchDetectionRequest):
    """
    Detect prompt injection in multiple texts.
    
    Args:
        request: BatchDetectionRequest with list of texts
        
    Returns:
        List of DetectionResult objects
    """
    try:
        results = aggregator.detect_batch(request.texts)
        
        # Update statistics for all results
        for result in results:
            _update_stats(result)
            detection_history.append({
                "timestamp": result.timestamp.isoformat(),
                "is_threat": result.is_threat,
                "confidence": result.confidence,
                "threat_level": result.threat_level
            })
        
        # Keep history limited
        while len(detection_history) > 1000:
            detection_history.pop(0)
        
        return results
        
    except Exception as e:
        logger.error(f"Error during batch detection: {e}")
        raise HTTPException(status_code=500, detail=f"Batch detection failed: {str(e)}")


@app.get(f"{settings.API_V1_PREFIX}/stats", response_model=DetectionStats)
async def get_stats():
    """
    Get detection statistics.
    
    Returns:
        DetectionStats with current statistics
    """
    total = stats_cache["total_requests"]
    threats = stats_cache["threats_detected"]
    
    return DetectionStats(
        total_requests=total,
        threats_detected=threats,
        threat_percentage=(threats / total * 100) if total > 0 else 0.0,
        avg_confidence=_calculate_avg_confidence(),
        detection_by_method=dict(stats_cache["detection_by_method"]),
        threat_levels=dict(stats_cache["threat_levels"])
    )


@app.get(f"{settings.API_V1_PREFIX}/analytics", response_model=AnalyticsData)
async def get_analytics():
    """
    Get analytics data for dashboard.
    
    Returns:
        AnalyticsData with charts and metrics
    """
    try:
        # Threats over time (last 100 entries)
        threats_over_time = []
        for entry in detection_history[-100:]:
            threats_over_time.append({
                "timestamp": entry["timestamp"],
                "is_threat": entry["is_threat"],
                "confidence": entry["confidence"]
            })
        
        # Top patterns (from stats)
        top_patterns = [
            {"name": method, "count": count}
            for method, count in stats_cache["detection_by_method"].items()
        ]
        top_patterns.sort(key=lambda x: x["count"], reverse=True)
        
        # Confidence distribution
        confidence_buckets = defaultdict(int)
        for entry in detection_history:
            bucket = int(entry["confidence"] * 10) / 10  # Round to 0.1
            confidence_buckets[bucket] += 1
        
        confidence_distribution = [
            {"confidence": conf, "count": count}
            for conf, count in sorted(confidence_buckets.items())
        ]
        
        # Method effectiveness
        method_effectiveness = {
            "rule_based": stats_cache["detection_by_method"].get("rule", 0),
            "ml_model": stats_cache["detection_by_method"].get("ml", 0),
            "vector_similarity": stats_cache["detection_by_method"].get("vector", 0)
        }
        
        return AnalyticsData(
            threats_over_time=threats_over_time,
            top_patterns=top_patterns[:10],
            confidence_distribution=confidence_distribution,
            method_effectiveness=method_effectiveness
        )
        
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def _update_stats(result: DetectionResult):
    """Update statistics with detection result."""
    stats_cache["total_requests"] += 1
    
    if result.is_threat:
        stats_cache["threats_detected"] += 1
    
    # Track threat levels
    stats_cache["threat_levels"][result.threat_level] += 1
    
    # Track which methods detected
    if result.rule_result.detected:
        stats_cache["detection_by_method"]["rule"] += 1
    if result.ml_result.detected:
        stats_cache["detection_by_method"]["ml"] += 1
    if result.vector_result.detected:
        stats_cache["detection_by_method"]["vector"] += 1


def _calculate_avg_confidence() -> float:
    """Calculate average confidence from history."""
    if not detection_history:
        return 0.0
    
    total_confidence = sum(entry["confidence"] for entry in detection_history)
    return total_confidence / len(detection_history)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

