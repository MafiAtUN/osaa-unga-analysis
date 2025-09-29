"""
Domain Entities - Core Business Objects
Represents the main business entities in the UN GA analysis system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

class AnalysisStatus(Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FileType(Enum):
    """Supported file types."""
    PDF = "pdf"
    DOCX = "docx"
    MP3 = "mp3"
    TXT = "txt"

class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

@dataclass
class AnalysisId:
    """Value object for Analysis ID."""
    value: str
    
    def __post_init__(self):
        if not self.value:
            self.value = str(uuid.uuid4())
    
    def __str__(self) -> str:
        return self.value

@dataclass
class CountryCode:
    """Value object for country code."""
    code: str
    
    def __post_init__(self):
        if len(self.code) != 3:
            raise ValueError("Country code must be 3 characters")
        self.code = self.code.upper()
    
    def __str__(self) -> str:
        return self.code

@dataclass
class Classification:
    """Value object for entity classification."""
    value: str
    
    VALID_CLASSIFICATIONS = ["African Member State", "Development Partner"]
    
    def __post_init__(self):
        if self.value not in self.VALID_CLASSIFICATIONS:
            raise ValueError(f"Invalid classification: {self.value}")
    
    def __str__(self) -> str:
        return self.value

@dataclass
class SDGReference:
    """Value object for SDG reference."""
    sdg_number: int
    description: str
    
    def __post_init__(self):
        if not 1 <= self.sdg_number <= 17:
            raise ValueError("SDG number must be between 1 and 17")

@dataclass
class SecurityLevel:
    """Value object for security level."""
    level: int
    
    def __post_init__(self):
        if not 1 <= self.level <= 5:
            raise ValueError("Security level must be between 1 and 5")

@dataclass
class Analysis:
    """Core Analysis entity."""
    id: AnalysisId
    country: str
    classification: Classification
    speech_date: Optional[datetime]
    status: AnalysisStatus
    created_at: datetime
    updated_at: datetime
    raw_text: str
    output_markdown: Optional[str] = None
    sdgs: List[SDGReference] = field(default_factory=list)
    africa_mentioned: bool = False
    source_filename: Optional[str] = None
    prompt_used: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def mark_completed(self, output: str) -> None:
        """Mark analysis as completed."""
        self.status = AnalysisStatus.COMPLETED
        self.output_markdown = output
        self.updated_at = datetime.now()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark analysis as failed."""
        self.status = AnalysisStatus.FAILED
        self.metadata['error'] = error_message
        self.updated_at = datetime.now()
    
    def add_sdg(self, sdg: SDGReference) -> None:
        """Add SDG reference to analysis."""
        if sdg not in self.sdgs:
            self.sdgs.append(sdg)
    
    def is_completed(self) -> bool:
        """Check if analysis is completed."""
        return self.status == AnalysisStatus.COMPLETED
    
    def is_african_member_state(self) -> bool:
        """Check if this is an African Member State."""
        return self.classification.value == "African Member State"

@dataclass
class Speech:
    """Speech entity."""
    id: str
    country: str
    session: int
    year: int
    content: str
    word_count: int
    language: str = "en"
    translated: bool = False
    
    def get_preview(self, max_length: int = 200) -> str:
        """Get speech preview."""
        return self.content[:max_length] + "..." if len(self.content) > max_length else self.content

@dataclass
class Country:
    """Country entity."""
    code: CountryCode
    name: str
    is_african_member: bool
    region: Optional[str] = None
    population: Optional[int] = None
    
    def is_african_union_member(self) -> bool:
        """Check if country is African Union member."""
        return self.is_african_member

@dataclass
class User:
    """User entity."""
    id: str
    username: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def can_analyze(self) -> bool:
        """Check if user can perform analysis."""
        return self.role in [UserRole.ADMIN, UserRole.ANALYST]
    
    def can_view_all(self) -> bool:
        """Check if user can view all analyses."""
        return self.role == UserRole.ADMIN

@dataclass
class Session:
    """User session entity."""
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid."""
        return not self.is_expired()
