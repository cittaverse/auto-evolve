"""
Working Memory for VSNC Narrative Scoring Pipeline

Working Memory provides session-level short-term caching for intermediate states
during narrative scoring. It reduces redundant computation and improves latency.

Lifecycle: Session end → automatic cleanup
Access latency: <10ms (in-memory access)

Author: Hulk 🟢 (GEO #101)
Created: 2026-04-03
"""

import time
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """A single cache entry with TTL support"""
    value: Any
    timestamp: float
    ttl_seconds: int = 3600  # Default 1 hour
    
    def is_expired(self) -> bool:
        """Check if this entry has expired"""
        return time.time() - self.timestamp > self.ttl_seconds


class WorkingMemory:
    """
    Working Memory for VSNC Narrative Scoring Pipeline
    
    Stores:
    - Current session's narrative text cache
    - L0 scoring intermediate results (dimension scores, confidence)
    - L1 arbitration requests/responses
    - Temporary computation results (information density, diversity, etc.)
    
    Lifecycle: Cleared when session ends
    Access latency: <10ms (memory access)
    
    Example usage:
        wm = WorkingMemory(session_id="sess_123")
        wm.set("narrative_text", "Today I went to the park...")
        wm.set("l0_scores", {"coherence": 0.8, "detail": 0.6})
        
        scores = wm.get("l0_scores")
        if scores is None:
            # Cache miss, recompute
            scores = compute_l0_scores(narrative)
            wm.set("l0_scores", scores)
    """
    
    def __init__(self, session_id: str, ttl_seconds: int = 3600):
        """
        Initialize Working Memory for a session
        
        Args:
            session_id: Unique identifier for this scoring session
            ttl_seconds: Time-to-live for cache entries (default 1 hour)
        """
        self.session_id = session_id
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = ttl_seconds
        self.created_at = time.time()
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Store a value in working memory
        
        Args:
            key: Cache key (e.g., "narrative_text", "l0_scores", "l1_arbitration")
            value: Any Python object to cache
            ttl_seconds: Optional TTL override for this entry
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self.cache[key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl_seconds=ttl
        )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from working memory
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        self.access_count += 1
        entry = self.cache.get(key)
        
        if entry is None:
            self.miss_count += 1
            return None
        
        # Check expiration
        if entry.is_expired():
            del self.cache[key]
            self.miss_count += 1
            return None
        
        self.hit_count += 1
        return entry.value
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists and is not expired
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists and is valid, False otherwise
        """
        return self.get(key) is not None
    
    def delete(self, key: str) -> bool:
        """
        Delete a specific key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False if key didn't exist
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """
        Clear all cached entries
        
        Returns:
            Number of entries cleared
        """
        count = len(self.cache)
        self.cache.clear()
        return count
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with hit rate, access counts, etc.
        """
        hit_rate = (
            self.hit_count / self.access_count
            if self.access_count > 0 else 0.0
        )
        
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "age_seconds": time.time() - self.created_at,
            "cache_size": len(self.cache),
            "access_count": self.access_count,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "default_ttl_seconds": self.default_ttl
        }
    
    def keys(self) -> list:
        """
        Get all non-expired cache keys
        
        Returns:
            List of cache keys
        """
        # Cleanup expired first
        self.cleanup_expired()
        return list(self.cache.keys())
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"WorkingMemory(session_id={self.session_id!r}, "
            f"cache_size={stats['cache_size']}, "
            f"hit_rate={stats['hit_rate']:.2f})"
        )


class WorkingMemoryManager:
    """
    Manager for multiple WorkingMemory instances across sessions
    
    Provides:
    - Session lifecycle management
    - Global cleanup of expired sessions
    - Memory usage monitoring
    
    Example usage:
        manager = WorkingMemoryManager()
        wm = manager.get_or_create("sess_123")
        wm.set("narrative", "Today I...")
        
        # Later, cleanup old sessions
        manager.cleanup_expired_sessions()
    """
    
    def __init__(self, session_ttl_seconds: int = 7200):
        """
        Initialize WorkingMemory manager
        
        Args:
            session_ttl_seconds: TTL for entire sessions (default 2 hours)
        """
        self.sessions: Dict[str, WorkingMemory] = {}
        self.session_ttl = session_ttl_seconds
    
    def get_or_create(self, session_id: str, ttl_seconds: int = 3600) -> WorkingMemory:
        """
        Get existing WorkingMemory or create new one
        
        Args:
            session_id: Session identifier
            ttl_seconds: TTL for cache entries in this session
            
        Returns:
            WorkingMemory instance for this session
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = WorkingMemory(
                session_id=session_id,
                ttl_seconds=ttl_seconds
            )
        return self.sessions[session_id]
    
    def get(self, session_id: str) -> Optional[WorkingMemory]:
        """
        Get existing WorkingMemory if it exists
        
        Args:
            session_id: Session identifier
            
        Returns:
            WorkingMemory instance or None if not found
        """
        return self.sessions.get(session_id)
    
    def delete(self, session_id: str) -> bool:
        """
        Delete a session's WorkingMemory
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if session didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove sessions that haven't been accessed recently
        
        Returns:
            Number of sessions removed
        """
        expired_sessions = [
            session_id for session_id, wm in self.sessions.items()
            if time.time() - wm.created_at > self.session_ttl
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]
        return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions"""
        self.cleanup_expired_sessions()
        return len(self.sessions)
    
    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get global statistics across all sessions
        
        Returns:
            Dictionary with session count, total cache size, etc.
        """
        total_cache_size = sum(len(wm.cache) for wm in self.sessions.values())
        total_accesses = sum(wm.access_count for wm in self.sessions.values())
        total_hits = sum(wm.hit_count for wm in self.sessions.values())
        
        return {
            "active_sessions": len(self.sessions),
            "total_cache_entries": total_cache_size,
            "total_accesses": total_accesses,
            "total_hits": total_hits,
            "global_hit_rate": total_hits / total_accesses if total_accesses > 0 else 0.0
        }


# Convenience function for quick session access
_default_manager: Optional[WorkingMemoryManager] = None


def get_working_memory(session_id: str, ttl_seconds: int = 3600) -> WorkingMemory:
    """
    Get or create WorkingMemory for a session using default manager
    
    Args:
        session_id: Session identifier
        ttl_seconds: TTL for cache entries
        
    Returns:
        WorkingMemory instance
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = WorkingMemoryManager()
    return _default_manager.get_or_create(session_id, ttl_seconds)


def cleanup_all_expired() -> int:
    """
    Cleanup all expired sessions using default manager
    
    Returns:
        Number of sessions removed
    """
    global _default_manager
    if _default_manager is None:
        return 0
    return _default_manager.cleanup_expired_sessions()
