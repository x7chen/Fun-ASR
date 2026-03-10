"""
Fun-ASR RESTful API
"""
from api.config import config
from api.schemas import (
    BatchTranscriptionRequest,
    BatchTranscriptionResult,
    ErrorResponse,
    HealthResponse,
    Timestamp,
    TranscriptionRequest,
    TranscriptionResult,
)

__version__ = "1.0.0"
__all__ = [
    "config",
    "TranscriptionRequest",
    "TranscriptionResult",
    "BatchTranscriptionRequest",
    "BatchTranscriptionResult",
    "Timestamp",
    "HealthResponse",
    "ErrorResponse",
    "__version__",
]
