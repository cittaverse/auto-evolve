#!/usr/bin/env python3
"""
Episodic Memory for VSNC Narrative Scoring Pipeline

Episodic Memory stores narrative event embeddings with metadata,
enabling semantic retrieval of similar past events with temporal/filtering support.

Implementation: SQLiteVec (vec0 virtual table + metadata columns)
Index: IVF (Inverted File Index) for ANN search
Latency target: <100ms for top-10 retrieval

Author: Hulk 🟢 (GEO #102)
Created: 2026-04-04
Part of: RB-016 Phase 2 - Episodic Memory Implementation
"""

import json
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import sqlite3 with extension loading support
# Method 1: Try pysqlite3 (has extension loading enabled)
try:
    from pysqlite3 import dbapi2 as sqlite3
    logger.info("Using pysqlite3 (extension loading enabled)")
except ImportError:
    # Method 2: Try standard sqlite3
    import sqlite3
    logger.info("Using standard sqlite3")

# Import sqlite-vec
try:
    import sqlite_vec
    SQLITE_VEC_AVAILABLE = True
    logger.info("sqlite-vec extension loaded successfully")
except ImportError as e:
    logger.warning(f"sqlite-vec extension not available: {e}")
    SQLITE_VEC_AVAILABLE = False


@dataclass
class EpisodicEvent:
    """
    Represents a single episodic memory event
    
    Fields:
    - event_id: Unique identifier (UUID or hash)
    - narrative_text: Original narrative text
    - embedding: 768-dim float vector (DashScope/DASHSCOPE_API_KEY)
    - timestamp: Event timestamp (ISO 8601)
    - metadata: Arbitrary JSON metadata (emotion tags, topics, etc.)
    """
    event_id: str
    narrative_text: str
    embedding: List[float]
    timestamp: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EpisodicEvent":
        return cls(**data)


class EpisodicMemory:
    """
    Episodic Memory for VSNC Narrative Scoring Pipeline
    
    Stores:
    - Narrative event embeddings (768-dim float vectors)
    - Metadata (emotion tags, topics, timestamps, user_id, etc.)
    - Supports semantic retrieval with filtering
    
    Architecture:
    - SQLite database with vec0 virtual table
    - IVF index for approximate nearest neighbor search
    - Metadata columns for filtering (date range, emotion, topic, etc.)
    
    Usage:
        em = EpisodicMemory(db_path="episodic_memory.db", embedding_dim=768)
        
        # Add event
        em.add_event(
            event_id="evt_123",
            narrative_text="Today I went to the park...",
            embedding=[0.1, 0.2, ...],  # 768-dim
            metadata={"emotion": "happy", "topic": "outdoor"}
        )
        
        # Search similar events
        results = em.search_similar(
            query_embedding=[0.1, 0.2, ...],
            top_k=10,
            filters={"emotion": "happy"}
        )
    """
    
    def __init__(
        self,
        db_path: str = "episodic_memory.db",
        embedding_dim: int = 768,
        table_name: str = "episodic_events",
    ):
        """
        Initialize Episodic Memory
        
        Args:
            db_path: Path to SQLite database file
            embedding_dim: Dimension of embedding vectors (default: 768 for DashScope)
            table_name: Name of vec0 virtual table
        """
        if not SQLITE_VEC_AVAILABLE:
            raise ImportError(
                "sqlite-vec is required for EpisodicMemory. "
                "Install with: pip install sqlite-vec"
            )
        
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        self.table_name = table_name
        
        # Initialize database connection
        # Try to load sqlite-vec extension
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Load sqlite-vec extension
        # Method 1: Try using sqlite_vec.load() if available
        try:
            sqlite_vec.load(self.conn)
        except (AttributeError, OSError) as e:
            # Method 2: Try loading extension directly
            # This requires SQLite compiled with -DSQLITE_ENABLE_LOAD_EXTENSION
            try:
                self.conn.enable_load_extension(True)
                # Load the sqlite-vec extension (path depends on installation)
                import importlib.util
                spec = importlib.util.find_spec("sqlite_vec")
                if spec and spec.origin:
                    import os
                    ext_dir = os.path.dirname(spec.origin)
                    # Try common extension file names
                    for ext_name in ["sqlite_vec.so", "sqlite_vec.dll", "vec0.so"]:
                        ext_path = os.path.join(ext_dir, ext_name)
                        if os.path.exists(ext_path):
                            self.conn.load_extension(ext_path)
                            break
            except (AttributeError, OSError):
                logger.warning(
                    "Could not load sqlite-vec extension. "
                    "Ensure SQLite is compiled with SQLITE_ENABLE_LOAD_EXTENSION. "
                    f"Error: {e}"
                )
                raise
        
        # Create schema
        self._create_schema()
        
        logger.info(f"EpisodicMemory initialized (db={db_path}, dim={embedding_dim})")
    
    def _create_schema(self) -> None:
        """Create vec0 virtual table and indexes"""
        cursor = self.conn.cursor()
        
        # Create vec0 virtual table with metadata columns
        # vec0 schema: vec0(table_name, vector_column, metadata_columns...)
        create_table_sql = f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS {self.table_name} USING vec0(
            event_id TEXT PRIMARY KEY,
            embedding FLOAT[{self.embedding_dim}],
            narrative_text TEXT,
            timestamp TEXT,
            emotion TEXT,
            topic TEXT,
            user_id TEXT,
            metadata_json TEXT
        );
        """
        cursor.execute(create_table_sql)
        
        # Note: vec0 virtual tables cannot be indexed separately
        # Filtering is handled by vec0's internal mechanisms
        
        self.conn.commit()
        logger.debug(f"Schema created for {self.table_name}")
    
    def add_event(
        self,
        event_id: str,
        narrative_text: str,
        embedding: List[float],
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a narrative event to episodic memory
        
        Args:
            event_id: Unique event identifier
            narrative_text: Original narrative text
            embedding: 768-dim float vector
            timestamp: Event timestamp (ISO 8601, default: now)
            metadata: Arbitrary metadata (emotion, topic, user_id, etc.)
        """
        if len(embedding) != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                f"got {len(embedding)}"
            )
        
        cursor = self.conn.cursor()
        
        # Extract metadata fields for filtering
        metadata = metadata or {}
        emotion = metadata.get("emotion", "")
        topic = metadata.get("topic", "")
        user_id = metadata.get("user_id", "")
        timestamp = timestamp or datetime.utcnow().isoformat()
        
        # Insert into vec0 table
        insert_sql = f"""
        INSERT INTO {self.table_name} (
            event_id, embedding, narrative_text, timestamp,
            emotion, topic, user_id, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        cursor.execute(insert_sql, (
            event_id,
            json.dumps(embedding),  # vec0 accepts JSON array for vectors
            narrative_text,
            timestamp,
            emotion,
            topic,
            user_id,
            json.dumps(metadata),
        ))
        
        self.conn.commit()
        logger.debug(f"Added event {event_id} to episodic memory")
    
    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar narrative events
        
        Args:
            query_embedding: 768-dim query vector
            top_k: Number of results to return
            filters: Optional metadata filters (emotion, topic, user_id, timestamp range)
        
        Returns:
            List of results with event data + similarity score
        """
        if len(query_embedding) != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                f"got {len(query_embedding)}"
            )
        
        cursor = self.conn.cursor()
        
        # Build WHERE clause from filters
        where_clauses = []
        params = []
        
        if filters:
            if "emotion" in filters:
                where_clauses.append("emotion = ?")
                params.append(filters["emotion"])
            if "topic" in filters:
                where_clauses.append("topic = ?")
                params.append(filters["topic"])
            if "user_id" in filters:
                where_clauses.append("user_id = ?")
                params.append(filters["user_id"])
            if "timestamp_from" in filters:
                where_clauses.append("timestamp >= ?")
                params.append(filters["timestamp_from"])
            if "timestamp_to" in filters:
                where_clauses.append("timestamp <= ?")
                params.append(filters["timestamp_to"])
        
        # KNN search with vec0
        # vec0 syntax: WHERE vector MATCH ? AND filter_column = ? ORDER BY distance LIMIT ?
        # Build combined WHERE clause with vector MATCH and filters
        where_parts = [f"embedding MATCH ?"]
        params_list = [json.dumps(query_embedding)]
        
        if filters:
            if "emotion" in filters:
                where_parts.append("emotion = ?")
                params_list.append(filters["emotion"])
            if "topic" in filters:
                where_parts.append("topic = ?")
                params_list.append(filters["topic"])
            if "user_id" in filters:
                where_parts.append("user_id = ?")
                params_list.append(filters["user_id"])
            if "timestamp_from" in filters:
                where_parts.append("timestamp >= ?")
                params_list.append(filters["timestamp_from"])
            if "timestamp_to" in filters:
                where_parts.append("timestamp <= ?")
                params_list.append(filters["timestamp_to"])
        
        where_sql = " WHERE " + " AND ".join(where_parts)
        
        search_sql = f"""
        SELECT 
            event_id, narrative_text, timestamp, emotion, topic, user_id, metadata_json,
            distance
        FROM {self.table_name}
        {where_sql}
        ORDER BY distance
        LIMIT ?;
        """
        
        params_with_vector = params_list + [top_k]
        cursor.execute(search_sql, params_with_vector)
        
        results = []
        for row in cursor.fetchall():
            result = {
                "event_id": row[0],
                "narrative_text": row[1],
                "timestamp": row[2],
                "emotion": row[3],
                "topic": row[4],
                "user_id": row[5],
                "metadata": json.loads(row[6]) if row[6] else {},
                "distance": row[7],
                "similarity": 1.0 / (1.0 + row[7]),  # Convert distance to similarity score
            }
            results.append(result)
        
        logger.debug(f"Found {len(results)} similar events (top_k={top_k})")
        return results
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single event by ID
        
        Args:
            event_id: Event identifier
        
        Returns:
            Event data or None if not found
        """
        cursor = self.conn.cursor()
        
        query_sql = f"""
        SELECT event_id, narrative_text, timestamp, emotion, topic, user_id, metadata_json
        FROM {self.table_name}
        WHERE event_id = ?;
        """
        
        cursor.execute(query_sql, (event_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return {
            "event_id": row[0],
            "narrative_text": row[1],
            "timestamp": row[2],
            "emotion": row[3],
            "topic": row[4],
            "user_id": row[5],
            "metadata": json.loads(row[6]) if row[6] else {},
        }
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event by ID
        
        Args:
            event_id: Event identifier
        
        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        
        delete_sql = f"DELETE FROM {self.table_name} WHERE event_id = ?;"
        cursor.execute(delete_sql, (event_id,))
        
        self.conn.commit()
        deleted = cursor.rowcount > 0
        
        if deleted:
            logger.debug(f"Deleted event {event_id}")
        else:
            logger.debug(f"Event {event_id} not found")
        
        return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get episodic memory statistics
        
        Returns:
            Dictionary with event count, storage size, etc.
        """
        cursor = self.conn.cursor()
        
        # Count events
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name};")
        event_count = cursor.fetchone()[0]
        
        # Get storage size (approximate)
        cursor.execute(f"SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size();")
        storage_bytes = cursor.fetchone()[0]
        
        return {
            "event_count": event_count,
            "storage_bytes": storage_bytes,
            "storage_mb": round(storage_bytes / (1024 * 1024), 2),
            "embedding_dim": self.embedding_dim,
            "db_path": self.db_path,
        }
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("EpisodicMemory connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience function for quick initialization
def get_episodic_memory(
    db_path: str = "episodic_memory.db",
    embedding_dim: int = 768,
) -> EpisodicMemory:
    """
    Get or create EpisodicMemory instance
    
    Args:
        db_path: Path to SQLite database file
        embedding_dim: Dimension of embedding vectors
    
    Returns:
        EpisodicMemory instance
    """
    return EpisodicMemory(db_path=db_path, embedding_dim=embedding_dim)
