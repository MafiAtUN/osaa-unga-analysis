"""
Advanced Vector Storage System using DuckDB with Embeddings
Full implementation with vector similarity search and semantic analysis
"""

import os
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import pandas as pd
import duckdb
import pickle

# Try to import sentence-transformers, but don't fail if it's not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except (ImportError, Exception) as e:
    print(f"Warning: sentence-transformers not available: {e}")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SimpleVectorStorageManager:
    """Advanced vector storage manager using DuckDB with embeddings."""
    
    def __init__(self, db_path: str = "unga_vector.db"):
        self.db_path = db_path
        
        # Initialize DuckDB connection
        self.conn = duckdb.connect(db_path)
        
        # Initialize sentence transformer for embeddings
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
                self.embeddings_enabled = True
                logger.info("Embeddings enabled with sentence-transformers")
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformers: {e}")
                self.embedding_model = None
                self.embedding_dimension = 384
                self.embeddings_enabled = False
                logger.info("Embeddings disabled - using fallback mode")
        else:
            logger.warning("sentence-transformers not available")
            self.embedding_model = None
            self.embedding_dimension = 384
            self.embeddings_enabled = False
            logger.info("Embeddings disabled - sentence-transformers not available")
        
        # Create tables
        self._create_tables()
        
        logger.info("Advanced vector storage initialized with embeddings")
    
    def _create_tables(self):
        """Create optimized tables for vector storage."""
        
        # Main speeches table with vector embeddings
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS speeches (
                id INTEGER PRIMARY KEY,
                country_code VARCHAR(3) NOT NULL,
                country_name VARCHAR(255) NOT NULL,
                region VARCHAR(100) NOT NULL,
                session INTEGER NOT NULL,
                year INTEGER NOT NULL,
                speech_text TEXT NOT NULL,
                word_count INTEGER,
                embedding FLOAT[384],
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_african_member BOOLEAN DEFAULT FALSE,
                source_filename VARCHAR(255)
            )
        """)
        
        # Analysis results table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY,
                country VARCHAR(255) NOT NULL,
                classification VARCHAR(50) NOT NULL,
                speech_date VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sdgs VARCHAR(255),
                africa_mentioned BOOLEAN DEFAULT FALSE,
                source_filename VARCHAR(255),
                raw_text TEXT,
                prompt_used TEXT,
                output_markdown TEXT,
                metadata JSON
            )
        """)
        
        # Create indexes for performance
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_speeches_country ON speeches(country_code)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_speeches_year ON speeches(year)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_speeches_region ON speeches(region)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_country ON analyses(country)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_classification ON analyses(classification)")
        
        # Note: DuckDB doesn't support vector indexes on FLOAT arrays yet
        # Vector similarity search will work without indexes, just slower for large datasets
        
        # Create custom cosine similarity function (only if it doesn't exist)
        try:
            # Check if function already exists
            result = self.conn.execute("SELECT 1 FROM duckdb_functions() WHERE function_name = 'array_cosine_similarity'").fetchone()
            if not result:
                self.conn.create_function('array_cosine_similarity', self._cosine_similarity)
                logger.info("Created array_cosine_similarity function")
            else:
                logger.info("array_cosine_similarity function already exists")
        except Exception as e:
            if "already exists" in str(e):
                logger.info("array_cosine_similarity function already exists (caught exception)")
            else:
                logger.warning(f"Could not create cosine similarity function: {e}")
        
        logger.info("Database tables and indexes created successfully")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0
            
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence transformer or fallback method."""
        try:
            if not self.embeddings_enabled or not self.embedding_model:
                # Use simple hash-based embedding as fallback
                return self._generate_hash_embedding(text)
            
            # Clean and truncate text if too long
            if len(text) > 5000:  # Limit text length for embedding
                text = text[:5000]
            
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return self._generate_hash_embedding(text)
    
    def _generate_hash_embedding(self, text: str) -> List[float]:
        """Generate a simple hash-based embedding as fallback."""
        import hashlib
        
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to a vector of floats
        embedding = []
        for i in range(0, len(text_hash), 2):
            # Convert hex pairs to float values between -1 and 1
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0 * 2 - 1  # Scale to [-1, 1]
            embedding.append(value)
        
        # Pad or truncate to the required dimension
        while len(embedding) < self.embedding_dimension:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dimension]
    
    def save_speech(self, country_code: str, country_name: str, region: str, 
                   session: int, year: int, speech_text: str, 
                   source_filename: str = None, is_african_member: bool = False,
                   metadata: Dict = None) -> int:
        """Save speech to database with embedding."""
        try:
            # Calculate word count
            word_count = len(speech_text.split()) if speech_text else 0
            
            # Generate embedding
            embedding = self.generate_embedding(speech_text)
            
            # Prepare metadata
            metadata_json = json.dumps(metadata or {})
            
            # Get next ID
            max_id_result = self.conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM speeches").fetchone()
            speech_id = max_id_result[0]
            
            # Insert into database with embedding
            self.conn.execute("""
                INSERT INTO speeches 
                (id, country_code, country_name, region, session, year, speech_text, 
                 word_count, embedding, metadata, is_african_member, source_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [speech_id, country_code, country_name, region, session, year, speech_text,
                  word_count, embedding, metadata_json, is_african_member, source_filename])
            logger.info(f"Saved speech {speech_id} for {country_name} ({country_code}) with embedding")
            return speech_id
            
        except Exception as e:
            logger.error(f"Failed to save speech: {e}")
            raise
    
    def save_analysis(self, country: str, classification: str, raw_text: str,
                     output_markdown: str, prompt_used: str, sdgs: List[int] = None,
                     africa_mentioned: bool = False, speech_date: str = None,
                     source_filename: str = None, metadata: Dict = None) -> int:
        """Save analysis to database."""
        try:
            # Prepare data
            sdgs_str = ",".join(map(str, sdgs)) if sdgs else None
            metadata_json = json.dumps(metadata or {})
            
            # Get next ID
            max_id_result = self.conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM analyses").fetchone()
            analysis_id = max_id_result[0]
            
            # Insert into database
            self.conn.execute("""
                INSERT INTO analyses 
                (id, country, classification, speech_date, sdgs, africa_mentioned, 
                 source_filename, raw_text, prompt_used, output_markdown, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [analysis_id, country, classification, speech_date, sdgs_str, africa_mentioned,
                  source_filename, raw_text, prompt_used, output_markdown, metadata_json])
            logger.info(f"Saved analysis {analysis_id} for {country}")
            return analysis_id
            
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            raise
    
    def search_speeches(self, query_text: str = None, countries: List[str] = None, 
                       years: List[int] = None, regions: List[str] = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """Search speeches with basic text search."""
        try:
            where_conditions = []
            params = []
            
            # Text search
            if query_text:
                where_conditions.append("speech_text ILIKE ?")
                params.append(f"%{query_text}%")
            
            # Country filter (search by both country_code and country_name)
            if countries:
                placeholders = ",".join(["?" for _ in countries])
                where_conditions.append(f"(country_code IN ({placeholders}) OR country_name IN ({placeholders}))")
                params.extend(countries)
                params.extend(countries)  # Add countries twice for both code and name search
            
            # Year filter
            if years:
                # Check if years form a consecutive range
                sorted_years = sorted(years)
                if len(sorted_years) > 20 and sorted_years == list(range(min(sorted_years), max(sorted_years) + 1)):
                    # Use BETWEEN for consecutive ranges to avoid SQL limits
                    where_conditions.append("year BETWEEN ? AND ?")
                    params.extend([min(sorted_years), max(sorted_years)])
                else:
                    # Use IN for non-consecutive or small ranges
                    placeholders = ",".join(["?" for _ in years])
                    where_conditions.append(f"year IN ({placeholders})")
                    params.extend(years)
            
            # Region filter
            if regions:
                placeholders = ",".join(["?" for _ in regions])
                where_conditions.append(f"region IN ({placeholders})")
                params.extend(regions)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Execute search with better distribution across years
            # For comprehensive analysis, we want to ensure good coverage
            if limit > 1000:  # For large limits, use a more systematic approach
                result = self.conn.execute(f"""
                    SELECT id, country_code, country_name, region, session, year, 
                           speech_text, word_count, source_filename, is_african_member, created_at
                    FROM speeches 
                    WHERE {where_clause}
                    ORDER BY year DESC, country_name
                    LIMIT ?
                """, params + [limit]).fetchall()
            else:  # For smaller limits, use random for variety
                result = self.conn.execute(f"""
                    SELECT id, country_code, country_name, region, session, year, 
                           speech_text, word_count, source_filename, is_african_member, created_at
                    FROM speeches 
                    WHERE {where_clause}
                    ORDER BY RANDOM()
                    LIMIT ?
                """, params + [limit]).fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in result:
                results.append({
                    'id': row[0],
                    'country_code': row[1],
                    'country_name': row[2],
                    'region': row[3],
                    'session': row[4],
                    'year': row[5],
                    'speech_text': row[6],
                    'word_count': row[7],
                    'source_filename': row[8],
                    'is_african_member': row[9],
                    'created_at': row[10]
                })
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def semantic_search(self, query_text: str, limit: int = 10, 
                       countries: List[str] = None, years: List[int] = None, 
                       regions: List[str] = None, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity."""
        try:
            if not self.embeddings_enabled:
                # Fall back to text search if embeddings are disabled
                logger.warning("Embeddings disabled, falling back to text search")
                return self.search_speeches(
                    query_text=query_text,
                    countries=countries,
                    years=years,
                    regions=regions,
                    limit=limit
                )
            
            # Generate embedding for query
            query_embedding = self.generate_embedding(query_text)
            
            # Ensure the query embedding is the same type as stored embeddings (tuple of floats)
            query_embedding = tuple(float(x) for x in query_embedding)
            
            # Build where conditions for filters
            where_conditions = []
            params = []
            
            # Country filter
            if countries:
                placeholders = ",".join(["?" for _ in countries])
                where_conditions.append(f"(country_code IN ({placeholders}) OR country_name IN ({placeholders}))")
                params.extend(countries)
                params.extend(countries)
            
            # Year filter
            if years:
                placeholders = ",".join(["?" for _ in years])
                where_conditions.append(f"year IN ({placeholders})")
                params.extend(years)
            
            # Region filter
            if regions:
                placeholders = ",".join(["?" for _ in regions])
                where_conditions.append(f"region IN ({placeholders})")
                params.extend(regions)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Perform vector similarity search using cosine similarity
            # Use a simpler approach with DuckDB's built-in functions
            result = self.conn.execute(f"""
                SELECT id, country_code, country_name, region, session, year, 
                       speech_text, word_count, source_filename, is_african_member, created_at,
                       array_cosine_similarity(embedding, ?::FLOAT[]) as similarity
                FROM speeches 
                WHERE {where_clause} AND embedding IS NOT NULL
                ORDER BY similarity DESC
                LIMIT ?
            """, [str(query_embedding)] + params + [limit]).fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in result:
                if row[11] >= similarity_threshold:  # Check similarity threshold
                    results.append({
                        'id': row[0],
                        'country_code': row[1],
                        'country_name': row[2],
                        'region': row[3],
                        'session': row[4],
                        'year': row[5],
                        'speech_text': row[6],
                        'word_count': row[7],
                        'source_filename': row[8],
                        'is_african_member': row[9],
                        'created_at': row[10],
                        'similarity': row[11]
                    })
            
            logger.info(f"Semantic search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def find_similar_speeches(self, speech_id: int, limit: int = 5, 
                             similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find speeches similar to a given speech."""
        try:
            # Get the embedding of the reference speech
            ref_result = self.conn.execute("""
                SELECT embedding FROM speeches WHERE id = ?
            """, [speech_id]).fetchone()
            
            if not ref_result or not ref_result[0]:
                logger.warning(f"No embedding found for speech {speech_id}")
                return []
            
            ref_embedding = ref_result[0]
            
            # Find similar speeches
            result = self.conn.execute("""
                SELECT id, country_code, country_name, region, session, year, 
                       speech_text, word_count, source_filename, is_african_member, created_at,
                       array_cosine_similarity(embedding, ?) as similarity
                FROM speeches 
                WHERE id != ? AND embedding IS NOT NULL
                ORDER BY similarity DESC
                LIMIT ?
            """, [ref_embedding, speech_id, limit]).fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in result:
                if row[11] >= similarity_threshold:
                    results.append({
                        'id': row[0],
                        'country_code': row[1],
                        'country_name': row[2],
                        'region': row[3],
                        'session': row[4],
                        'year': row[5],
                        'speech_text': row[6],
                        'word_count': row[7],
                        'source_filename': row[8],
                        'is_african_member': row[9],
                        'created_at': row[10],
                        'similarity': row[11]
                    })
            
            logger.info(f"Found {len(results)} similar speeches to {speech_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar speeches: {e}")
            return []
    
    def get_speeches_by_country(self, country_code: str = None, year: int = None) -> List[Dict[str, Any]]:
        """Get speeches by country and/or year."""
        return self.search_speeches(countries=[country_code] if country_code else None, 
                                  years=[year] if year else None)
    
    def get_speech_data_by_country(self, country_code: str = None, year: int = None) -> List[Dict[str, Any]]:
        """Get speech data by country and/or year (alias for compatibility)."""
        return self.get_speeches_by_country(country_code, year)
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific analysis by ID."""
        try:
            result = self.conn.execute("""
                SELECT id, country, classification, speech_date, created_at, sdgs, 
                       africa_mentioned, source_filename, raw_text, prompt_used, output_markdown
                FROM analyses 
                WHERE id = ?
            """, [analysis_id]).fetchone()
            
            if result:
                return {
                    "id": result[0],
                    "country": result[1],
                    "classification": result[2],
                    "speech_date": result[3],
                    "created_at": result[4],
                    "sdgs": result[5].split(",") if result[5] else [],
                    "africa_mentioned": result[6],
                    "source_filename": result[7],
                    "raw_text": result[8],
                    "prompt_used": result[9],
                    "output_markdown": result[10],
                    "structured_readout": result[10],  # For compatibility
                    "analysis": result[10]  # For compatibility
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get analysis {analysis_id}: {e}")
            return None
    
    def list_analyses(self, filters: Optional[Dict[str, Any]] = None, 
                     limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List analyses with optional filters."""
        try:
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('country'):
                    where_conditions.append("country ILIKE ?")
                    params.append(f"%{filters['country']}%")
                
                if filters.get('classification'):
                    where_conditions.append("classification = ?")
                    params.append(filters['classification'])
                
                if filters.get('africa_mentioned') is not None:
                    where_conditions.append("africa_mentioned = ?")
                    params.append(filters['africa_mentioned'])
                
                if filters.get('search_text'):
                    where_conditions.append("(country ILIKE ? OR raw_text ILIKE ? OR output_markdown ILIKE ?)")
                    search_term = f"%{filters['search_text']}%"
                    params.extend([search_term, search_term, search_term])
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            result = self.conn.execute(f"""
                SELECT id, country, classification, speech_date, created_at, sdgs, 
                       africa_mentioned, source_filename, raw_text, prompt_used, output_markdown
                FROM analyses 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset]).fetchall()
            
            # Convert to list of dictionaries
            analyses = []
            for row in result:
                analyses.append({
                    "id": row[0],
                    "country": row[1],
                    "classification": row[2],
                    "speech_date": row[3],
                    "created_at": row[4],
                    "sdgs": row[5].split(",") if row[5] else [],
                    "africa_mentioned": row[6],
                    "source_filename": row[7],
                    "raw_text": row[8],
                    "prompt_used": row[9],
                    "output_markdown": row[10],
                    "structured_readout": row[10],  # For compatibility
                    "analysis": row[10]  # For compatibility
                })
            
            return analyses
            
        except Exception as e:
            logger.error(f"Failed to list analyses: {e}")
            return []
    
    def save_speech_data(self, country_code: str, country_name: str, region: str, 
                        session: int, year: int, speech_text: str, 
                        source_filename: str = None, is_african_member: bool = False) -> int:
        """Save speech data (alias for save_speech for compatibility)."""
        return self.save_speech(
            country_code=country_code,
            country_name=country_name,
            region=region,
            session=session,
            year=year,
            speech_text=speech_text,
            source_filename=source_filename,
            is_african_member=is_african_member
        )
    
    def create_db_and_tables(self):
        """Create database and tables (for compatibility)."""
        # Tables are already created in __init__, this is just for compatibility
        logger.info("Database and tables are ready")
    
    def get_available_countries_by_region(self, year: int = 2025) -> Dict[str, List[Dict[str, Any]]]:
        """Get available countries grouped by region for a specific year."""
        try:
            speeches = self.search_speeches(years=[year])
            
            regions = {}
            for speech in speeches:
                region = speech['region']
                if region not in regions:
                    regions[region] = []
                
                regions[region].append({
                    "country_code": speech['country_code'],
                    "country_name": speech['country_name'],
                    "word_count": speech['word_count'],
                    "uploaded_at": speech.get('created_at'),
                    "is_african_member": speech['is_african_member'],
                    "year": speech['year']  # Add year for compatibility
                })
            
            return regions
            
        except Exception as e:
            logger.error(f"Failed to get countries by region: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        try:
            # Basic counts
            total_speeches = self.conn.execute("SELECT COUNT(*) FROM speeches").fetchone()[0]
            total_analyses = self.conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
            total_countries = self.conn.execute("SELECT COUNT(DISTINCT country_code) FROM speeches").fetchone()[0]
            total_years = self.conn.execute("SELECT COUNT(DISTINCT year) FROM speeches").fetchone()[0]
            
            # Year statistics
            year_stats = self.conn.execute("""
                SELECT year, COUNT(*) as count 
                FROM speeches 
                GROUP BY year 
                ORDER BY year DESC
            """).fetchall()
            
            # Region statistics
            region_stats = self.conn.execute("""
                SELECT region, COUNT(*) as count 
                FROM speeches 
                GROUP BY region 
                ORDER BY count DESC
            """).fetchall()
            
            return {
                "total_speeches": total_speeches,
                "total_analyses": total_analyses,
                "total_countries": total_countries,
                "total_years": total_years,
                "year_statistics": {year: count for year, count in year_stats},
                "region_statistics": {region: count for region, count in region_stats}
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def get_speech_statistics(self) -> Dict[str, Any]:
        """Get speech statistics (alias for get_statistics for compatibility)."""
        return self.get_statistics()
    
    def migrate_from_sqlite(self, sqlite_db_path: str = "analyses.db"):
        """Migrate data from existing SQLite database."""
        try:
            logger.info(f"Starting migration from {sqlite_db_path}")
            
            # Connect to SQLite database
            sqlite_conn = duckdb.connect(sqlite_db_path)
            
            # Migrate speech data
            speech_data = sqlite_conn.execute("""
                SELECT country_code, country_name, region, session, year, 
                       speech_text, word_count, source_filename, is_african_member
                FROM speech_data
            """).fetchall()
            
            logger.info(f"Found {len(speech_data)} speeches to migrate")
            
            for speech in speech_data:
                try:
                    self.save_speech(
                        country_code=speech[0],
                        country_name=speech[1],
                        region=speech[2],
                        session=speech[3],
                        year=speech[4],
                        speech_text=speech[5],
                        source_filename=speech[7],
                        is_african_member=speech[8]
                    )
                except Exception as e:
                    logger.error(f"Failed to migrate speech {speech[0]}: {e}")
            
            # Migrate analysis data
            analysis_data = sqlite_conn.execute("""
                SELECT country, classification, speech_date, sdgs, africa_mentioned,
                       source_filename, raw_text, prompt_used, output_markdown
                FROM analyses
            """).fetchall()
            
            logger.info(f"Found {len(analysis_data)} analyses to migrate")
            
            for analysis in analysis_data:
                try:
                    sdgs = analysis[3].split(",") if analysis[3] else None
                    sdgs = [int(s.strip()) for s in sdgs if s.strip().isdigit()] if sdgs else None
                    
                    self.save_analysis(
                        country=analysis[0],
                        classification=analysis[1],
                        raw_text=analysis[6],
                        output_markdown=analysis[8],
                        prompt_used=analysis[7],
                        sdgs=sdgs,
                        africa_mentioned=analysis[4],
                        speech_date=analysis[2],
                        source_filename=analysis[5]
                    )
                except Exception as e:
                    logger.error(f"Failed to migrate analysis {analysis[0]}: {e}")
            
            sqlite_conn.close()
            logger.info("Migration completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

# Global instance
simple_vector_storage = SimpleVectorStorageManager()
