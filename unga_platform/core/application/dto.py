"""
Data Transfer Objects (DTOs) for Application Layer
Clean data structures for communication between layers
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..domain.entities import AnalysisStatus, Classification, SDGReference

@dataclass
class AnalysisRequest:
    """Request DTO for analysis operations."""
    country: str
    classification: str
    speech_date: Optional[datetime]
    raw_text: str
    source_filename: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AnalysisResponse:
    """Response DTO for analysis operations."""
    id: str
    country: str
    classification: str
    status: str
    created_at: datetime
    output_markdown: Optional[str] = None
    sdgs: List[str] = None
    africa_mentioned: bool = False
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.sdgs is None:
            self.sdgs = []

@dataclass
class AuthenticationRequest:
    """Request DTO for authentication."""
    password: str
    user_id: Optional[str] = None

@dataclass
class AuthenticationResponse:
    """Response DTO for authentication."""
    success: bool
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class FileProcessingRequest:
    """Request DTO for file processing."""
    file_bytes: bytes
    filename: str
    file_type: str

@dataclass
class FileProcessingResponse:
    """Response DTO for file processing."""
    success: bool
    extracted_text: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ListAnalysesRequest:
    """Request DTO for listing analyses."""
    limit: int = 50
    offset: int = 0
    country_filter: Optional[str] = None
    classification_filter: Optional[str] = None
    status_filter: Optional[str] = None

@dataclass
class ListAnalysesResponse:
    """Response DTO for listing analyses."""
    analyses: List[AnalysisResponse]
    total_count: int
    has_more: bool

@dataclass
class ChatRequest:
    """Request DTO for chat operations."""
    question: str
    analysis_id: str
    context: Optional[str] = None

@dataclass
class ChatResponse:
    """Response DTO for chat operations."""
    answer: str
    sources: List[str] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
