"""
SQLite database storage using SQLAlchemy.
"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func, or_, and_

logger = logging.getLogger(__name__)

Base = declarative_base()

class Analysis(Base):
    """Database model for storing analysis results."""
    
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(255), nullable=False)
    classification = Column(String(50), nullable=False)  # "African Member State" or "Development Partner"
    speech_date = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sdgs = Column(String(255), nullable=True)  # Comma-separated SDG numbers
    africa_mentioned = Column(Boolean, default=False)
    source_filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=True)
    prompt_used = Column(Text, nullable=True)
    output_markdown = Column(Text, nullable=True)

class DatabaseManager:
    """Database manager for handling SQLite operations."""
    
    def __init__(self, db_path: str = "analyses.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_db_and_tables(self):
        """Create database and tables if they don't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Database and tables created at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def save_analysis(self, country: str, classification: str, raw_text: str,
                     output_markdown: str, prompt_used: str, sdgs: List[int] = None,
                     africa_mentioned: bool = False, speech_date: str = None,
                     source_filename: str = None) -> int:
        """
        Save an analysis to the database.
        
        Args:
            country: Country or entity name
            classification: "African Member State" or "Development Partner"
            raw_text: Original speech text
            output_markdown: Generated analysis in markdown
            prompt_used: The prompt that was used
            sdgs: List of mentioned SDG numbers
            africa_mentioned: Whether Africa was mentioned (for Development Partners)
            speech_date: Date of the speech
            source_filename: Original filename
            
        Returns:
            Analysis ID
        """
        session = self.get_session()
        try:
            sdgs_str = ",".join(map(str, sdgs)) if sdgs else None
            
            analysis = Analysis(
                country=country,
                classification=classification,
                speech_date=speech_date,
                sdgs=sdgs_str,
                africa_mentioned=africa_mentioned,
                source_filename=source_filename,
                raw_text=raw_text,
                prompt_used=prompt_used,
                output_markdown=output_markdown
            )
            
            session.add(analysis)
            session.commit()
            analysis_id = analysis.id
            logger.info(f"Saved analysis {analysis_id} for {country}")
            return analysis_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save analysis: {e}")
            raise
        finally:
            session.close()
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific analysis by ID.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis data as dictionary or None if not found
        """
        session = self.get_session()
        try:
            analysis = session.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                return self._analysis_to_dict(analysis)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get analysis {analysis_id}: {e}")
            return None
        finally:
            session.close()
    
    def list_analyses(self, filters: Optional[Dict[str, Any]] = None, 
                     limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List analyses with optional filters.
        
        Args:
            filters: Dictionary of filters (country, classification, date_range, etc.)
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of analysis dictionaries
        """
        session = self.get_session()
        try:
            query = session.query(Analysis)
            
            if filters:
                if filters.get('country'):
                    query = query.filter(
                        or_(
                            Analysis.country.ilike(f"%{filters['country']}%"),
                            Analysis.country == filters['country']
                        )
                    )
                
                if filters.get('classification'):
                    query = query.filter(Analysis.classification == filters['classification'])
                
                if filters.get('africa_mentioned') is not None:
                    query = query.filter(Analysis.africa_mentioned == filters['africa_mentioned'])
                
                if filters.get('sdgs'):
                    # Filter by SDGs (check if any of the specified SDGs are in the stored SDGs string)
                    sdg_conditions = []
                    for sdg in filters['sdgs']:
                        sdg_conditions.append(Analysis.sdgs.contains(str(sdg)))
                    if sdg_conditions:
                        query = query.filter(or_(*sdg_conditions))
                
                if filters.get('date_from'):
                    query = query.filter(Analysis.created_at >= filters['date_from'])
                
                if filters.get('date_to'):
                    query = query.filter(Analysis.created_at <= filters['date_to'])
                
                if filters.get('search_text'):
                    search_term = f"%{filters['search_text']}%"
                    query = query.filter(
                        or_(
                            Analysis.country.ilike(search_term),
                            Analysis.raw_text.ilike(search_term),
                            Analysis.output_markdown.ilike(search_term)
                        )
                    )
            
            # Order by creation date (newest first)
            query = query.order_by(Analysis.created_at.desc())
            
            # Apply pagination
            analyses = query.offset(offset).limit(limit).all()
            
            return [self._analysis_to_dict(analysis) for analysis in analyses]
            
        except Exception as e:
            logger.error(f"Failed to list analyses: {e}")
            return []
        finally:
            session.close()
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """
        Delete an analysis by ID.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            True if deleted, False if not found
        """
        session = self.get_session()
        try:
            analysis = session.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                session.delete(analysis)
                session.commit()
                logger.info(f"Deleted analysis {analysis_id}")
                return True
            return False
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete analysis {analysis_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        session = self.get_session()
        try:
            total_analyses = session.query(Analysis).count()
            african_analyses = session.query(Analysis).filter(
                Analysis.classification == "African Member State"
            ).count()
            partner_analyses = session.query(Analysis).filter(
                Analysis.classification == "Development Partner"
            ).count()
            
            # Get unique countries
            unique_countries = session.query(Analysis.country).distinct().count()
            
            # Get most recent analysis
            latest_analysis = session.query(Analysis).order_by(
                Analysis.created_at.desc()
            ).first()
            
            return {
                "total_analyses": total_analyses,
                "african_analyses": african_analyses,
                "partner_analyses": partner_analyses,
                "unique_countries": unique_countries,
                "latest_analysis_date": latest_analysis.created_at if latest_analysis else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
        finally:
            session.close()
    
    def _analysis_to_dict(self, analysis: Analysis) -> Dict[str, Any]:
        """Convert Analysis object to dictionary."""
        return {
            "id": analysis.id,
            "country": analysis.country,
            "classification": analysis.classification,
            "speech_date": analysis.speech_date,
            "created_at": analysis.created_at,
            "sdgs": analysis.sdgs.split(",") if analysis.sdgs else [],
            "africa_mentioned": analysis.africa_mentioned,
            "source_filename": analysis.source_filename,
            "raw_text": analysis.raw_text,
            "prompt_used": analysis.prompt_used,
            "output_markdown": analysis.output_markdown,
            # Map output_markdown to both structured_readout and analysis for compatibility
            "structured_readout": analysis.output_markdown,
            "analysis": analysis.output_markdown
        }

# Global database manager instance
db_manager = DatabaseManager()
