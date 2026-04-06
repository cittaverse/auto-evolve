#!/usr/bin/env python3
"""
Unit tests for EpisodicMemory (SQLiteVec implementation)

Tests cover:
- Event storage and retrieval
- Semantic search with filtering
- Metadata filtering
- Statistics and lifecycle management

Author: Hulk 🟢 (GEO #102)
Created: 2026-04-04
"""

import pytest
import os
import tempfile
import json
from typing import List

from src.services.episodic_memory import EpisodicMemory, get_episodic_memory, SQLITE_VEC_AVAILABLE


# Skip all tests if sqlite-vec is not available
pytestmark = pytest.mark.skipif(
    not SQLITE_VEC_AVAILABLE,
    reason="sqlite-vec not available"
)


def create_test_embedding(dim: int = 768, value: float = 0.1) -> List[float]:
    """Create a test embedding with specified dimension"""
    return [value] * dim


class TestEpisodicMemoryInit:
    """Test EpisodicMemory initialization"""
    
    def test_init_creates_database(self):
        """Test that initialization creates database file"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            em = EpisodicMemory(db_path=db_path, embedding_dim=768)
            assert os.path.exists(db_path)
            em.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_init_with_custom_embedding_dim(self):
        """Test initialization with custom embedding dimension"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            em = EpisodicMemory(db_path=db_path, embedding_dim=512)
            assert em.embedding_dim == 512
            em.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_init_raises_on_missing_sqlite_vec(self):
        """Test that initialization fails gracefully if sqlite-vec not available"""
        # This test is skipped if sqlite-vec is available
        # Would need to mock import to test properly
        pass


class TestEpisodicMemoryAddEvent:
    """Test event storage"""
    
    @pytest.fixture
    def episodic_memory(self):
        """Create temporary EpisodicMemory instance"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        em = EpisodicMemory(db_path=db_path, embedding_dim=768)
        yield em
        em.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_add_event_success(self, episodic_memory: EpisodicMemory):
        """Test adding an event successfully"""
        episodic_memory.add_event(
            event_id="evt_001",
            narrative_text="Today I went to the park",
            embedding=create_test_embedding(),
            metadata={"emotion": "happy", "topic": "outdoor"}
        )
        
        # Verify event was added
        stats = episodic_memory.get_stats()
        assert stats["event_count"] == 1
    
    def test_add_event_with_timestamp(self, episodic_memory: EpisodicMemory):
        """Test adding event with custom timestamp"""
        episodic_memory.add_event(
            event_id="evt_002",
            narrative_text="Yesterday I stayed home",
            embedding=create_test_embedding(),
            timestamp="2026-04-03T10:00:00Z",
            metadata={}
        )
        
        event = episodic_memory.get_event("evt_002")
        assert event is not None
        assert event["timestamp"] == "2026-04-03T10:00:00Z"
    
    def test_add_event_auto_timestamp(self, episodic_memory: EpisodicMemory):
        """Test that timestamp is auto-generated if not provided"""
        episodic_memory.add_event(
            event_id="evt_003",
            narrative_text="Auto timestamp test",
            embedding=create_test_embedding(),
        )
        
        event = episodic_memory.get_event("evt_003")
        assert event is not None
        assert event["timestamp"] is not None
    
    def test_add_event_dimension_mismatch(self, episodic_memory: EpisodicMemory):
        """Test that wrong embedding dimension raises error"""
        with pytest.raises(ValueError) as exc_info:
            episodic_memory.add_event(
                event_id="evt_004",
                narrative_text="Wrong dimension",
                embedding=[0.1, 0.2, 0.3],  # Only 3 dimensions
            )
        
        assert "Embedding dimension mismatch" in str(exc_info.value)
    
    def test_add_multiple_events(self, episodic_memory: EpisodicMemory):
        """Test adding multiple events"""
        for i in range(10):
            episodic_memory.add_event(
                event_id=f"evt_{i:03d}",
                narrative_text=f"Event {i}",
                embedding=create_test_embedding(value=float(i) / 10),
                metadata={"index": i}
            )
        
        stats = episodic_memory.get_stats()
        assert stats["event_count"] == 10


class TestEpisodicMemorySearch:
    """Test semantic search functionality"""
    
    @pytest.fixture
    def populated_memory(self):
        """Create EpisodicMemory with test data"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        em = EpisodicMemory(db_path=db_path, embedding_dim=768)
        
        # Add events with varying embeddings
        for i in range(20):
            # Create embeddings with different values for similarity testing
            embedding = create_test_embedding(value=float(i) / 20)
            emotion = "happy" if i % 2 == 0 else "sad"
            topic = "outdoor" if i < 10 else "indoor"
            
            em.add_event(
                event_id=f"evt_{i:03d}",
                narrative_text=f"Event {i} narrative",
                embedding=embedding,
                metadata={"emotion": emotion, "topic": topic}
            )
        
        yield em
        em.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_search_similar_basic(self, populated_memory: EpisodicMemory):
        """Test basic similarity search"""
        query_embedding = create_test_embedding(value=0.5)
        
        results = populated_memory.search_similar(
            query_embedding=query_embedding,
            top_k=5
        )
        
        assert len(results) == 5
        assert "event_id" in results[0]
        assert "narrative_text" in results[0]
        assert "distance" in results[0]
        assert "similarity" in results[0]
    
    def test_search_with_emotion_filter(self, populated_memory: EpisodicMemory):
        """Test search with emotion filter"""
        query_embedding = create_test_embedding(value=0.5)
        
        results = populated_memory.search_similar(
            query_embedding=query_embedding,
            top_k=10,
            filters={"emotion": "happy"}
        )
        
        # All results should have emotion="happy"
        for result in results:
            assert result["emotion"] == "happy"
    
    def test_search_with_topic_filter(self, populated_memory: EpisodicMemory):
        """Test search with topic filter"""
        query_embedding = create_test_embedding(value=0.5)
        
        results = populated_memory.search_similar(
            query_embedding=query_embedding,
            top_k=10,
            filters={"topic": "outdoor"}
        )
        
        # All results should have topic="outdoor"
        for result in results:
            assert result["topic"] == "outdoor"
    
    def test_search_with_multiple_filters(self, populated_memory: EpisodicMemory):
        """Test search with multiple filters"""
        query_embedding = create_test_embedding(value=0.5)
        
        results = populated_memory.search_similar(
            query_embedding=query_embedding,
            top_k=10,
            filters={"emotion": "happy", "topic": "outdoor"}
        )
        
        # All results should match both filters
        for result in results:
            assert result["emotion"] == "happy"
            assert result["topic"] == "outdoor"
    
    def test_search_dimension_mismatch(self, populated_memory: EpisodicMemory):
        """Test that wrong query dimension raises error"""
        with pytest.raises(ValueError) as exc_info:
            populated_memory.search_similar(
                query_embedding=[0.1, 0.2, 0.3],  # Wrong dimension
                top_k=5
            )
        
        assert "Embedding dimension mismatch" in str(exc_info.value)
    
    def test_search_returns_metadata(self, populated_memory: EpisodicMemory):
        """Test that search results include metadata"""
        query_embedding = create_test_embedding(value=0.5)
        
        results = populated_memory.search_similar(
            query_embedding=query_embedding,
            top_k=1
        )
        
        assert "metadata" in results[0]
        assert isinstance(results[0]["metadata"], dict)


class TestEpisodicMemoryGetEvent:
    """Test single event retrieval"""
    
    @pytest.fixture
    def memory_with_event(self):
        """Create EpisodicMemory with one event"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        em = EpisodicMemory(db_path=db_path, embedding_dim=768)
        em.add_event(
            event_id="evt_test",
            narrative_text="Test narrative",
            embedding=create_test_embedding(),
            metadata={"test": True}
        )
        
        yield em
        em.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_get_existing_event(self, memory_with_event: EpisodicMemory):
        """Test retrieving an existing event"""
        event = memory_with_event.get_event("evt_test")
        
        assert event is not None
        assert event["event_id"] == "evt_test"
        assert event["narrative_text"] == "Test narrative"
        assert event["metadata"]["test"] is True
    
    def test_get_nonexistent_event(self, memory_with_event: EpisodicMemory):
        """Test retrieving a non-existent event"""
        event = memory_with_event.get_event("evt_nonexistent")
        
        assert event is None


class TestEpisodicMemoryDeleteEvent:
    """Test event deletion"""
    
    @pytest.fixture
    def memory_with_event(self):
        """Create EpisodicMemory with one event"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        em = EpisodicMemory(db_path=db_path, embedding_dim=768)
        em.add_event(
            event_id="evt_to_delete",
            narrative_text="Will be deleted",
            embedding=create_test_embedding(),
        )
        
        yield em
        em.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_delete_existing_event(self, memory_with_event: EpisodicMemory):
        """Test deleting an existing event"""
        result = memory_with_event.delete_event("evt_to_delete")
        
        assert result is True
        
        # Verify event is gone
        event = memory_with_event.get_event("evt_to_delete")
        assert event is None
    
    def test_delete_nonexistent_event(self, memory_with_event: EpisodicMemory):
        """Test deleting a non-existent event"""
        result = memory_with_event.delete_event("evt_nonexistent")
        
        assert result is False


class TestEpisodicMemoryStats:
    """Test statistics functionality"""
    
    @pytest.fixture
    def memory_with_events(self):
        """Create EpisodicMemory with multiple events"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        em = EpisodicMemory(db_path=db_path, embedding_dim=768)
        
        for i in range(50):
            em.add_event(
                event_id=f"evt_{i:03d}",
                narrative_text=f"Event {i}",
                embedding=create_test_embedding(),
            )
        
        yield em
        em.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_get_stats(self, memory_with_events: EpisodicMemory):
        """Test getting statistics"""
        stats = memory_with_events.get_stats()
        
        assert "event_count" in stats
        assert "storage_bytes" in stats
        assert "storage_mb" in stats
        assert "embedding_dim" in stats
        assert "db_path" in stats
        
        assert stats["event_count"] == 50
        assert stats["embedding_dim"] == 768
        assert stats["storage_mb"] >= 0
    
    def test_stats_after_deletion(self, memory_with_events: EpisodicMemory):
        """Test that stats update after deletion"""
        # Initial count
        stats1 = memory_with_events.get_stats()
        initial_count = stats1["event_count"]
        
        # Delete some events
        for i in range(10):
            memory_with_events.delete_event(f"evt_{i:03d}")
        
        # Verify count decreased
        stats2 = memory_with_events.get_stats()
        assert stats2["event_count"] == initial_count - 10


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_get_episodic_memory(self):
        """Test get_episodic_memory convenience function"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            em = get_episodic_memory(db_path=db_path, embedding_dim=768)
            assert isinstance(em, EpisodicMemory)
            assert em.embedding_dim == 768
            em.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestContextManager:
    """Test context manager support"""
    
    def test_context_manager(self):
        """Test using EpisodicMemory as context manager"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            with EpisodicMemory(db_path=db_path, embedding_dim=768) as em:
                em.add_event(
                    event_id="evt_ctx",
                    narrative_text="Context manager test",
                    embedding=create_test_embedding(),
                )
                
                stats = em.get_stats()
                assert stats["event_count"] == 1
            
            # Connection should be closed after context
            # (would raise error if we tried to use it)
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
