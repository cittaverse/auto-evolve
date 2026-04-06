"""
Unit tests for WorkingMemory service

Tests cover:
- Basic set/get operations
- TTL expiration
- Cache statistics
- WorkingMemoryManager session lifecycle
- Cleanup operations

Author: Hulk 🟢 (GEO #101)
Created: 2026-04-03
"""

import pytest
import time
from src.services.working_memory import (
    WorkingMemory,
    WorkingMemoryManager,
    get_working_memory,
    cleanup_all_expired,
    CacheEntry
)


class TestCacheEntry:
    """Test CacheEntry dataclass"""
    
    def test_create_entry(self):
        """Test creating a cache entry"""
        entry = CacheEntry(value="test", timestamp=time.time(), ttl_seconds=3600)
        assert entry.value == "test"
        assert not entry.is_expired()
    
    def test_entry_expiration(self):
        """Test entry expiration detection"""
        # Create entry with 0 second TTL (already expired)
        entry = CacheEntry(
            value="test",
            timestamp=time.time() - 10,  # 10 seconds ago
            ttl_seconds=5  # 5 second TTL
        )
        assert entry.is_expired()
        
        # Create fresh entry
        entry2 = CacheEntry(
            value="test",
            timestamp=time.time(),
            ttl_seconds=3600
        )
        assert not entry2.is_expired()


class TestWorkingMemory:
    """Test WorkingMemory class"""
    
    def test_init(self):
        """Test WorkingMemory initialization"""
        wm = WorkingMemory(session_id="test_123", ttl_seconds=1800)
        assert wm.session_id == "test_123"
        assert wm.default_ttl == 1800
        assert len(wm.cache) == 0
    
    def test_set_and_get(self):
        """Test basic set and get operations"""
        wm = WorkingMemory(session_id="test")
        
        # Set value
        wm.set("key1", "value1")
        wm.set("key2", {"nested": "data"})
        wm.set("key3", [1, 2, 3])
        
        # Get values
        assert wm.get("key1") == "value1"
        assert wm.get("key2") == {"nested": "data"}
        assert wm.get("key3") == [1, 2, 3]
        
        # Get non-existent key
        assert wm.get("nonexistent") is None
    
    def test_has(self):
        """Test has() method"""
        wm = WorkingMemory(session_id="test")
        
        assert not wm.has("key1")
        wm.set("key1", "value1")
        assert wm.has("key1")
    
    def test_delete(self):
        """Test delete() method"""
        wm = WorkingMemory(session_id="test")
        wm.set("key1", "value1")
        
        # Delete existing key
        assert wm.delete("key1") is True
        assert wm.get("key1") is None
        
        # Delete non-existent key
        assert wm.delete("key2") is False
    
    def test_clear(self):
        """Test clear() method"""
        wm = WorkingMemory(session_id="test")
        wm.set("key1", "value1")
        wm.set("key2", "value2")
        wm.set("key3", "value3")
        
        count = wm.clear()
        assert count == 3
        assert len(wm.cache) == 0
    
    def test_ttl_expiration(self):
        """Test TTL-based expiration"""
        wm = WorkingMemory(session_id="test", ttl_seconds=1)
        
        # Set value with short TTL
        wm.set("expiring_key", "value", ttl_seconds=1)
        assert wm.get("expiring_key") == "value"
        
        # Wait for expiration
        time.sleep(1.1)
        assert wm.get("expiring_key") is None
    
    def test_get_stats(self):
        """Test cache statistics"""
        wm = WorkingMemory(session_id="test")
        
        # Initial stats
        stats = wm.get_stats()
        assert stats["session_id"] == "test"
        assert stats["cache_size"] == 0
        assert stats["access_count"] == 0
        assert stats["hit_count"] == 0
        assert stats["miss_count"] == 0
        
        # After some operations
        wm.set("key1", "value1")
        wm.get("key1")  # Hit
        wm.get("key1")  # Hit
        wm.get("nonexistent")  # Miss
        
        stats = wm.get_stats()
        assert stats["cache_size"] == 1
        assert stats["access_count"] == 3
        assert stats["hit_count"] == 2
        assert stats["miss_count"] == 1
        assert stats["hit_rate"] == pytest.approx(2/3, rel=0.01)
    
    def test_keys(self):
        """Test keys() method"""
        wm = WorkingMemory(session_id="test")
        wm.set("key1", "value1")
        wm.set("key2", "value2")
        
        keys = wm.keys()
        assert set(keys) == {"key1", "key2"}
    
    def test_cleanup_expired(self):
        """Test cleanup_expired() method"""
        wm = WorkingMemory(session_id="test", ttl_seconds=1)
        wm.set("key1", "value1", ttl_seconds=10)  # Long TTL
        wm.set("key2", "value2", ttl_seconds=1)   # Short TTL
        
        time.sleep(1.1)
        
        removed = wm.cleanup_expired()
        assert removed == 1
        assert wm.get("key1") == "value1"
        assert wm.get("key2") is None
    
    def test_repr(self):
        """Test string representation"""
        wm = WorkingMemory(session_id="test_session")
        wm.set("key", "value")
        
        repr_str = repr(wm)
        assert "WorkingMemory" in repr_str
        assert "test_session" in repr_str
        assert "cache_size=1" in repr_str


class TestWorkingMemoryManager:
    """Test WorkingMemoryManager class"""
    
    def test_get_or_create(self):
        """Test get_or_create() method"""
        manager = WorkingMemoryManager()
        
        # Create new session
        wm1 = manager.get_or_create("session_1")
        assert wm1.session_id == "session_1"
        
        # Get existing session
        wm2 = manager.get_or_create("session_1")
        assert wm2 is wm1  # Same instance
        
        # Create different session
        wm3 = manager.get_or_create("session_2")
        assert wm3.session_id == "session_2"
        assert wm3 is not wm1
    
    def test_get(self):
        """Test get() method"""
        manager = WorkingMemoryManager()
        
        # Get non-existent session
        assert manager.get("nonexistent") is None
        
        # Create and get
        wm = manager.get_or_create("session_1")
        assert manager.get("session_1") is wm
    
    def test_delete(self):
        """Test delete() method"""
        manager = WorkingMemoryManager()
        manager.get_or_create("session_1")
        
        # Delete existing
        assert manager.delete("session_1") is True
        assert manager.get("session_1") is None
        
        # Delete non-existent
        assert manager.delete("session_2") is False
    
    def test_cleanup_expired_sessions(self):
        """Test cleanup_expired_sessions() method"""
        manager = WorkingMemoryManager(session_ttl_seconds=1)
        manager.get_or_create("session_1")
        manager.get_or_create("session_2")
        
        assert manager.get_active_session_count() == 2
        
        time.sleep(1.1)
        
        removed = manager.cleanup_expired_sessions()
        assert removed == 2
        assert manager.get_active_session_count() == 0
    
    def test_get_active_session_count(self):
        """Test get_active_session_count() method"""
        manager = WorkingMemoryManager()
        
        assert manager.get_active_session_count() == 0
        
        manager.get_or_create("session_1")
        manager.get_or_create("session_2")
        
        assert manager.get_active_session_count() == 2
    
    def test_get_global_stats(self):
        """Test get_global_stats() method"""
        manager = WorkingMemoryManager()
        
        wm1 = manager.get_or_create("session_1")
        wm1.set("key1", "value1")
        wm1.get("key1")  # Hit
        
        wm2 = manager.get_or_create("session_2")
        wm2.set("key2", "value2")
        wm2.get("nonexistent")  # Miss
        
        stats = manager.get_global_stats()
        assert stats["active_sessions"] == 2
        assert stats["total_cache_entries"] == 2
        assert stats["total_accesses"] == 2
        assert stats["total_hits"] == 1
        assert stats["global_hit_rate"] == pytest.approx(0.5, rel=0.01)


class TestConvenienceFunctions:
    """Test module-level convenience functions"""
    
    def test_get_working_memory(self):
        """Test get_working_memory() function"""
        # Reset global manager
        import src.services.working_memory as wm_module
        wm_module._default_manager = None
        
        wm = get_working_memory("test_session")
        assert wm.session_id == "test_session"
        
        # Should return same manager's session
        wm2 = get_working_memory("test_session")
        assert wm2 is wm
    
    def test_cleanup_all_expired(self):
        """Test cleanup_all_expired() function"""
        import src.services.working_memory as wm_module
        wm_module._default_manager = None
        
        # Create session
        wm = get_working_memory("test_session")
        wm.set("key", "value", ttl_seconds=1)
        
        time.sleep(1.1)
        
        # Should cleanup without error
        removed = cleanup_all_expired()
        assert isinstance(removed, int)


class TestWorkingMemoryIntegration:
    """Integration tests for realistic usage scenarios"""
    
    def test_narrative_scoring_workflow(self):
        """Test typical narrative scoring workflow"""
        wm = WorkingMemory(session_id="scoring_session_123")
        
        # Step 1: Cache narrative text
        narrative = "Today I went to the park with my family..."
        wm.set("narrative_text", narrative)
        
        # Step 2: Cache L0 scores
        l0_scores = {
            "coherence": 0.85,
            "detail": 0.72,
            "temporal_structure": 0.68,
            "emotional_content": 0.90,
            "final_score": 76,
            "confidence": 0.78
        }
        wm.set("l0_scores", l0_scores)
        
        # Step 3: Cache L1 arbitration result
        l1_result = {
            "triggered": True,
            "adjustment": -3,
            "reasoning": "Low confidence in temporal_structure dimension"
        }
        wm.set("l1_arbitration", l1_result)
        
        # Step 4: Retrieve and verify
        assert wm.get("narrative_text") == narrative
        assert wm.get("l0_scores")["final_score"] == 76
        assert wm.get("l1_arbitration")["adjustment"] == -3
        
        # Step 5: Check stats
        stats = wm.get_stats()
        assert stats["cache_size"] == 3
        assert stats["hit_rate"] > 0
    
    def test_multi_session_isolation(self):
        """Test that sessions are properly isolated"""
        manager = WorkingMemoryManager()
        
        # Session 1
        wm1 = manager.get_or_create("session_1")
        wm1.set("user_data", "user_1_data")
        wm1.set("score", 85)
        
        # Session 2
        wm2 = manager.get_or_create("session_2")
        wm2.set("user_data", "user_2_data")
        wm2.set("score", 92)
        
        # Verify isolation
        assert wm1.get("user_data") == "user_1_data"
        assert wm2.get("user_data") == "user_2_data"
        assert wm1.get("score") == 85
        assert wm2.get("score") == 92
        
        # Session 1 deletion shouldn't affect session 2
        manager.delete("session_1")
        assert manager.get("session_1") is None
        assert manager.get("session_2") is wm2
        assert wm2.get("score") == 92


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
