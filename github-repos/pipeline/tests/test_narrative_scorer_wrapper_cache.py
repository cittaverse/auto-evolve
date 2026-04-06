#!/usr/bin/env python3
"""
Unit tests for NarrativeScorerService WorkingMemory caching

Tests cover:
- Cache hit/miss behavior
- Cache key computation
- Cache statistics tracking
- Batch scoring with caching

Author: Hulk 🟢 (GEO #102)
Created: 2026-04-04
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from src.services.narrative_scorer_wrapper import NarrativeScorerService


class TestNarrativeScorerServiceCaching:
    """Test WorkingMemory caching integration"""
    
    def test_service_initialization_with_cache(self):
        """Test service initializes WorkingMemory when enabled"""
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session_123",
            enable_cache=True,
        )
        
        assert scorer.working_memory is not None
        assert scorer.working_memory.session_id == "test_session_123"
        assert scorer.enable_cache is True
    
    def test_service_initialization_without_cache(self):
        """Test service works without caching"""
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id=None,
            enable_cache=False,
        )
        
        assert scorer.working_memory is None
        assert scorer.enable_cache is False
    
    @patch('src.services.narrative_scorer_wrapper.score_narrative')
    def test_cache_miss_computes_and_caches(self, mock_score):
        """Test that cache miss triggers computation and caching"""
        # Setup mock
        mock_score.return_value = {
            'composite_score': 0.75,
            'event_richness': 0.8,
            'metadata': {'version': '1.0'}
        }
        
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session_456",
            enable_cache=True,
        )
        
        # First call - cache miss
        result1 = scorer.score("Today I went to the park...")
        
        # Verify score_narrative was called
        mock_score.assert_called_once()
        assert result1['composite_score'] == 0.75
        
        # Verify result was cached
        assert scorer.working_memory is not None
        stats = scorer.working_memory.get_stats()
        assert stats['cache_size'] == 1
    
    @patch('src.services.narrative_scorer_wrapper.score_narrative')
    def test_cache_hit_returns_cached_result(self, mock_score):
        """Test that cache hit returns cached result without recomputation"""
        # Setup mock
        mock_score.return_value = {
            'composite_score': 0.75,
            'event_richness': 0.8,
            'metadata': {'version': '1.0'}
        }
        
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session_789",
            enable_cache=True,
        )
        
        # First call - cache miss
        result1 = scorer.score("Today I went to the park...")
        assert mock_score.call_count == 1
        
        # Second call with same text - cache hit
        result2 = scorer.score("Today I went to the park...")
        assert mock_score.call_count == 1  # Not called again!
        
        # Verify both results are identical
        assert result1['composite_score'] == result2['composite_score']
        
        # Verify cache stats show hit
        stats = scorer.get_cache_stats()
        assert stats['access_count'] == 2
        assert stats['hit_count'] == 1
        assert stats['hit_rate'] == 0.5
    
    @patch('src.services.narrative_scorer_wrapper.score_narrative')
    def test_different_texts_have_different_cache_keys(self, mock_score):
        """Test that different texts produce different cache keys"""
        mock_score.return_value = {'composite_score': 0.75}
        
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session_abc",
            enable_cache=True,
        )
        
        # Score two different narratives
        scorer.score("Today I went to the park...")
        scorer.score("Yesterday I stayed at home...")
        
        # Both should trigger computation (different cache keys)
        assert mock_score.call_count == 2
        
        # Cache should have 2 entries
        stats = scorer.get_cache_stats()
        assert stats['cache_size'] == 2
    
    @patch('src.services.narrative_scorer_wrapper.score_narrative')
    def test_cache_key_includes_use_llm_flag(self, mock_score):
        """Test that cache key includes use_llm flag"""
        mock_score.return_value = {'composite_score': 0.75}
        
        # Create two scorers with different use_llm settings
        scorer_llm = NarrativeScorerService(
            use_llm=True,
            session_id="test_session_llm",
            enable_cache=True,
        )
        
        scorer_rule = NarrativeScorerService(
            use_llm=False,
            session_id="test_session_rule",
            enable_cache=True,
        )
        
        # Score same text with different settings
        text = "Today I went to the park..."
        scorer_llm.score(text)
        scorer_rule.score(text)
        
        # Both should compute (different cache keys due to use_llm flag)
        assert mock_score.call_count == 2
    
    def test_get_cache_stats_returns_none_when_disabled(self):
        """Test that get_cache_stats returns None when caching disabled"""
        scorer = NarrativeScorerService(
            use_llm=False,
            enable_cache=False,
        )
        
        stats = scorer.get_cache_stats()
        assert stats is None
    
    @patch('src.services.narrative_scorer_wrapper.score_narrative')
    def test_batch_scoring_uses_cache(self, mock_score):
        """Test that batch scoring benefits from caching"""
        mock_score.return_value = {'composite_score': 0.75}
        
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session_batch",
            enable_cache=True,
        )
        
        # Batch with repeated narratives
        texts = [
            "Today I went to the park...",
            "Yesterday I stayed at home...",
            "Today I went to the park...",  # Duplicate
        ]
        
        results = scorer.score_batch(texts)
        
        # Should only compute twice (duplicate is cached)
        assert mock_score.call_count == 2
        assert len(results) == 3
        
        # Verify cache stats
        stats = scorer.get_cache_stats()
        assert stats['cache_size'] == 2
        assert stats['access_count'] == 3
        assert stats['hit_count'] == 1
    
    @patch('src.services.narrative_scorer_wrapper.score_narrative')
    def test_cache_ttl_configuration(self, mock_score):
        """Test that cache TTL can be configured"""
        mock_score.return_value = {'composite_score': 0.75}
        
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session_ttl",
            enable_cache=True,
            cache_ttl_seconds=60,  # 1 minute TTL
        )
        
        scorer.score("Test narrative...")
        
        # Verify TTL is set correctly
        entry = scorer.working_memory.cache.get(list(scorer.working_memory.cache.keys())[0])
        assert entry is not None
        assert entry.ttl_seconds == 60


class TestCacheKeyComputation:
    """Test cache key computation logic"""
    
    def test_cache_key_is_deterministic(self):
        """Test that same input produces same cache key"""
        scorer1 = NarrativeScorerService(
            use_llm=False,
            session_id="session1",
            enable_cache=True,
        )
        
        scorer2 = NarrativeScorerService(
            use_llm=False,
            session_id="session2",
            enable_cache=True,
        )
        
        text = "Test narrative..."
        key1 = scorer1._compute_cache_key(text, use_llm=False)
        key2 = scorer2._compute_cache_key(text, use_llm=False)
        
        # Keys should be identical (based on text + use_llm, not session_id)
        assert key1 == key2
    
    def test_cache_key_changes_with_use_llm(self):
        """Test that cache key changes when use_llm flag changes"""
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session",
            enable_cache=True,
        )
        
        text = "Test narrative..."
        key_llm_true = scorer._compute_cache_key(text, use_llm=True)
        key_llm_false = scorer._compute_cache_key(text, use_llm=False)
        
        # Keys should be different
        assert key_llm_true != key_llm_false
    
    def test_cache_key_changes_with_text(self):
        """Test that cache key changes when text changes"""
        scorer = NarrativeScorerService(
            use_llm=False,
            session_id="test_session",
            enable_cache=True,
        )
        
        key1 = scorer._compute_cache_key("Text A", use_llm=False)
        key2 = scorer._compute_cache_key("Text B", use_llm=False)
        
        # Keys should be different
        assert key1 != key2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
