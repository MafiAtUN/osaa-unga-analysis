"""
Use Cases - Application Business Logic
Implements the application's use cases following Clean Architecture principles
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import logging

from .dto import (
    AnalysisRequest, AnalysisResponse,
    AuthenticationRequest, AuthenticationResponse,
    FileProcessingRequest, FileProcessingResponse,
    ListAnalysesRequest, ListAnalysesResponse,
    ChatRequest, ChatResponse
)
from ..domain.entities import Analysis, AnalysisId, Classification
from ..interfaces import (
    IAnalysisRepository,
    ILLMService,
    IFileProcessingService,
    IAuthenticationService,
    ISecurityService
)

logger = logging.getLogger(__name__)

class AnalyzeSpeechUseCase:
    """Use case for analyzing UN speeches."""
    
    def __init__(
        self,
        analysis_repo: IAnalysisRepository,
        llm_service: ILLMService,
        security_service: ISecurityService
    ):
        self.analysis_repo = analysis_repo
        self.llm_service = llm_service
        self.security_service = security_service
    
    async def execute(self, request: AnalysisRequest) -> AnalysisResponse:
        """Execute speech analysis use case."""
        try:
            # Security validation
            if not self.security_service.validate_input(request.raw_text):
                raise ValueError("Invalid input detected")
            
            # Create analysis entity
            analysis = Analysis(
                id=AnalysisId(str()),
                country=request.country,
                classification=Classification(request.classification),
                speech_date=request.speech_date,
                status=AnalysisStatus.PROCESSING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                raw_text=request.raw_text,
                source_filename=request.source_filename
            )
            
            # Save initial analysis
            await self.analysis_repo.save(analysis)
            
            # Process with LLM
            result = await self.llm_service.analyze_speech(
                text=request.raw_text,
                country=request.country,
                classification=request.classification
            )
            
            # Update analysis with results
            analysis.mark_completed(result.output)
            analysis.sdgs = result.sdgs
            analysis.africa_mentioned = result.africa_mentioned
            
            await self.analysis_repo.save(analysis)
            
            return AnalysisResponse(
                id=str(analysis.id),
                country=analysis.country,
                classification=analysis.classification.value,
                status=analysis.status.value,
                created_at=analysis.created_at,
                output_markdown=analysis.output_markdown,
                sdgs=[str(sdg) for sdg in analysis.sdgs],
                africa_mentioned=analysis.africa_mentioned
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            if analysis:
                analysis.mark_failed(str(e))
                await self.analysis_repo.save(analysis)
            
            return AnalysisResponse(
                id=str(analysis.id) if analysis else "",
                country=request.country,
                classification=request.classification,
                status="failed",
                created_at=datetime.now(),
                error_message=str(e)
            )

class GetAnalysisUseCase:
    """Use case for retrieving a specific analysis."""
    
    def __init__(self, analysis_repo: IAnalysisRepository):
        self.analysis_repo = analysis_repo
    
    async def execute(self, analysis_id: str) -> Optional[AnalysisResponse]:
        """Execute get analysis use case."""
        try:
            analysis = await self.analysis_repo.get_by_id(analysis_id)
            if not analysis:
                return None
            
            return AnalysisResponse(
                id=str(analysis.id),
                country=analysis.country,
                classification=analysis.classification.value,
                status=analysis.status.value,
                created_at=analysis.created_at,
                output_markdown=analysis.output_markdown,
                sdgs=[str(sdg) for sdg in analysis.sdgs],
                africa_mentioned=analysis.africa_mentioned
            )
        except Exception as e:
            logger.error(f"Failed to get analysis {analysis_id}: {e}")
            return None

class ListAnalysesUseCase:
    """Use case for listing analyses with filtering."""
    
    def __init__(self, analysis_repo: IAnalysisRepository):
        self.analysis_repo = analysis_repo
    
    async def execute(self, request: ListAnalysesRequest) -> ListAnalysesResponse:
        """Execute list analyses use case."""
        try:
            analyses, total_count = await self.analysis_repo.list(
                limit=request.limit,
                offset=request.offset,
                country_filter=request.country_filter,
                classification_filter=request.classification_filter,
                status_filter=request.status_filter
            )
            
            analysis_responses = [
                AnalysisResponse(
                    id=str(analysis.id),
                    country=analysis.country,
                    classification=analysis.classification.value,
                    status=analysis.status.value,
                    created_at=analysis.created_at,
                    output_markdown=analysis.output_markdown,
                    sdgs=[str(sdg) for sdg in analysis.sdgs],
                    africa_mentioned=analysis.africa_mentioned
                )
                for analysis in analyses
            ]
            
            return ListAnalysesResponse(
                analyses=analysis_responses,
                total_count=total_count,
                has_more=request.offset + len(analyses) < total_count
            )
            
        except Exception as e:
            logger.error(f"Failed to list analyses: {e}")
            return ListAnalysesResponse(analyses=[], total_count=0, has_more=False)

class AuthenticateUserUseCase:
    """Use case for user authentication."""
    
    def __init__(
        self,
        auth_service: IAuthenticationService,
        security_service: ISecurityService
    ):
        self.auth_service = auth_service
        self.security_service = security_service
    
    async def execute(self, request: AuthenticationRequest) -> AuthenticationResponse:
        """Execute authentication use case."""
        try:
            # Security checks
            if not self.security_service.validate_password(request.password):
                return AuthenticationResponse(
                    success=False,
                    message="Invalid password format"
                )
            
            # Rate limiting
            if not self.security_service.check_rate_limit(request.user_id or "anonymous"):
                return AuthenticationResponse(
                    success=False,
                    message="Too many authentication attempts"
                )
            
            # Authenticate
            result = await self.auth_service.authenticate(
                password=request.password,
                user_id=request.user_id
            )
            
            return AuthenticationResponse(
                success=result.success,
                message=result.message,
                user_id=result.user_id,
                session_id=result.session_id
            )
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return AuthenticationResponse(
                success=False,
                message="Authentication error"
            )

class ProcessFileUseCase:
    """Use case for processing uploaded files."""
    
    def __init__(
        self,
        file_service: IFileProcessingService,
        security_service: ISecurityService
    ):
        self.file_service = file_service
        self.security_service = security_service
    
    async def execute(self, request: FileProcessingRequest) -> FileProcessingResponse:
        """Execute file processing use case."""
        try:
            # Security validation
            if not self.security_service.validate_file(request.file_bytes, request.filename):
                return FileProcessingResponse(
                    success=False,
                    error_message="Invalid file type or size"
                )
            
            # Process file
            result = await self.file_service.process_file(
                file_bytes=request.file_bytes,
                filename=request.filename,
                file_type=request.file_type
            )
            
            return FileProcessingResponse(
                success=result.success,
                extracted_text=result.extracted_text,
                error_message=result.error_message,
                metadata=result.metadata
            )
            
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            return FileProcessingResponse(
                success=False,
                error_message=str(e)
            )
