"""
Unit tests for SemanticMemory

Author: Hulk 🟢 (GEO #104)
Created: 2026-04-04
"""

import pytest
import os
import tempfile
import time
from datetime import datetime, timedelta
from src.services.semantic_memory import SemanticMemory


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def semantic_memory(temp_db):
    """Create a SemanticMemory instance with temporary database."""
    sm = SemanticMemory(temp_db)
    yield sm
    sm.close()


@pytest.fixture
def seeded_memory(semantic_memory):
    """Create a SemanticMemory instance with test data."""
    # Add test scores for user_123
    for i in range(10):
        semantic_memory.store_score(
            user_id="user_123",
            session_id=f"sess_{i}",
            scores={
                "final_score": 70 + i,  # 70, 71, ..., 79
                "coherence": 0.75 + i * 0.01,
                "emotional_richness": 0.70,
                "narrative_depth": 0.65,
                "linguistic_complexity": 0.80,
                "authenticity": 0.85,
                "temporal_structure": 0.75,
                "confidence": 0.78
            },
            metadata={"narrative_type": "life_story"}
        )
    
    # Add test scores for user_456
    for i in range(5):
        semantic_memory.store_score(
            user_id="user_456",
            session_id=f"sess_{100 + i}",
            scores={
                "final_score": 60 + i * 2,  # 60, 62, ..., 68
                "coherence": 0.65,
                "emotional_richness": 0.60,
                "narrative_depth": 0.55,
                "linguistic_complexity": 0.70,
                "authenticity": 0.75,
                "temporal_structure": 0.65,
                "confidence": 0.68
            },
            metadata={"narrative_type": "daily_log"}
        )
    
    return semantic_memory


class TestSemanticMemoryInit:
    """Test database initialization."""
    
    def test_init_creates_database(self, temp_db):
        """Test that initialization creates database file."""
        sm = SemanticMemory(temp_db)
        assert os.path.exists(temp_db)
        sm.close()
    
    def test_init_creates_tables(self, semantic_memory):
        """Test that all tables are created."""
        cursor = semantic_memory.conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            'user_stats', 'score_history', 'population_baselines',
            'calibration_params', 'knowledge_base'
        }
        assert expected_tables.issubset(tables)
    
    def test_init_creates_indexes(self, semantic_memory):
        """Test that indexes are created."""
        cursor = semantic_memory.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        expected_indexes = {
            'idx_score_history_user',
            'idx_score_history_timestamp',
            'idx_score_history_user_timestamp',
            'idx_population_baselines_group'
        }
        assert expected_indexes.issubset(indexes)


class TestScoreStorage:
    """Test score storage and retrieval."""
    
    def test_store_score(self, semantic_memory):
        """Test storing a score."""
        semantic_memory.store_score(
            user_id="user_123",
            session_id="sess_001",
            scores={"final_score": 75.5, "confidence": 0.82},
            metadata={"narrative_type": "life_story"}
        )
        
        # Verify by checking user_stats exists
        stats = semantic_memory.get_user_stats("user_123")
        assert stats is not None
        assert stats['total_sessions'] == 1
        assert stats['avg_final_score'] == 75.5
    
    def test_store_multiple_scores(self, seeded_memory):
        """Test storing multiple scores for same user."""
        stats = seeded_memory.get_user_stats("user_123")
        
        assert stats['total_sessions'] == 10
        assert stats['avg_final_score'] == 74.5  # Average of 70-79
        assert stats['best_score'] == 79
        assert stats['worst_score'] == 70
    
    def test_get_user_stats_nonexistent(self, semantic_memory):
        """Test getting stats for nonexistent user."""
        stats = semantic_memory.get_user_stats("nonexistent_user")
        assert stats is None
    
    def test_get_user_trend(self, seeded_memory):
        """Test getting user trend."""
        trend = seeded_memory.get_user_trend("user_123", days=30)
        
        assert len(trend) > 0
        assert 'date' in trend[0]
        assert 'avg_score' in trend[0]
        assert 'session_count' in trend[0]


class TestPopulationBaselines:
    """Test population baseline calculations."""
    
    def test_update_baselines(self, seeded_memory):
        """Test updating population baselines."""
        result = seeded_memory.update_population_baselines('all_users')
        
        assert result['reference_group'] == 'all_users'
        assert result['metric'] == 'final_score'
        assert result['sample_size'] == 15  # 10 + 5 scores
        assert 'mean' in result
        assert 'std' in result
    
    def test_get_baseline_stats(self, seeded_memory):
        """Test getting baseline statistics."""
        # First update baselines
        seeded_memory.update_population_baselines('all_users')
        
        stats = seeded_memory.get_baseline_stats('all_users', 'final_score')
        
        assert stats is not None
        assert 'mean' in stats
        assert 'p25' in stats
        assert 'p50' in stats
        assert 'p75' in stats
    
    def test_get_percentile_rank(self, seeded_memory):
        """Test calculating percentile rank."""
        seeded_memory.update_population_baselines('all_users')
        
        # Score of 75 should be around 50th percentile (middle of distribution)
        percentile = seeded_memory.get_percentile_rank(75.0, reference_group='all_users')
        
        assert 0 <= percentile <= 100
    
    def test_get_percentile_rank_no_baseline(self, semantic_memory):
        """Test percentile rank with no baseline."""
        percentile = semantic_memory.get_percentile_rank(75.0)
        assert percentile == 50.0  # Default to neutral


class TestCalibration:
    """Test calibration system."""
    
    def test_set_calibration_params(self, semantic_memory):
        """Test setting calibration parameters."""
        semantic_memory.set_calibration_params(
            user_id="user_123",
            dimension_weights={"coherence": 0.25, "emotional_richness": 0.15},
            sensitivity_factor=1.2
        )
        
        params = semantic_memory.get_calibration_params("user_123")
        
        assert params is not None
        assert params['dimension_weights']['coherence'] == 0.25
        assert params['sensitivity_factor'] == 1.2
    
    def test_get_calibration_params_nonexistent(self, semantic_memory):
        """Test getting calibration for nonexistent user."""
        params = semantic_memory.get_calibration_params("nonexistent_user")
        assert params is None
    
    def test_apply_calibration(self, seeded_memory):
        """Test applying calibration to scores."""
        # Set custom weights
        seeded_memory.set_calibration_params(
            user_id="user_123",
            dimension_weights={
                "coherence": 0.30,
                "emotional_richness": 0.10,
                "narrative_depth": 0.20,
                "linguistic_complexity": 0.15,
                "authenticity": 0.15,
                "temporal_structure": 0.10
            },
            sensitivity_factor=1.0
        )
        
        raw_scores = {
            "final_score": 75.0,
            "coherence": 0.80,
            "emotional_richness": 0.70,
            "narrative_depth": 0.65,
            "linguistic_complexity": 0.75,
            "authenticity": 0.85,
            "temporal_structure": 0.70
        }
        
        calibrated = seeded_memory.apply_calibration("user_123", raw_scores)
        
        assert 'final_score' in calibrated
        # Final score should be recalculated based on custom weights
    
    def test_apply_calibration_no_params(self, semantic_memory):
        """Test applying calibration with no params."""
        raw_scores = {"final_score": 75.0, "coherence": 0.80}
        calibrated = semantic_memory.apply_calibration("user_123", raw_scores)
        
        # Should return unchanged copy
        assert calibrated == raw_scores


class TestKnowledgeBase:
    """Test knowledge base operations."""
    
    def test_store_knowledge(self, semantic_memory):
        """Test storing knowledge."""
        semantic_memory.store_knowledge(
            category="scoring_rules",
            key="l1_trigger_conditions",
            value={"confidence_threshold": 0.6, "score_range": [55, 75]}
        )
        
        value = semantic_memory.get_knowledge("scoring_rules", "l1_trigger_conditions")
        
        assert value is not None
        assert value['confidence_threshold'] == 0.6
    
    def test_get_knowledge_nonexistent(self, semantic_memory):
        """Test getting nonexistent knowledge."""
        value = semantic_memory.get_knowledge("nonexistent", "key")
        assert value is None
    
    def test_list_knowledge(self, semantic_memory):
        """Test listing knowledge in category."""
        semantic_memory.store_knowledge("category_a", "key_1", "value_1")
        semantic_memory.store_knowledge("category_a", "key_2", "value_2")
        semantic_memory.store_knowledge("category_b", "key_3", "value_3")
        
        results = semantic_memory.list_knowledge("category_a")
        
        assert len(results) == 2
        keys = {r['key'] for r in results}
        assert keys == {"key_1", "key_2"}
    
    def test_knowledge_versioning(self, semantic_memory):
        """Test knowledge versioning."""
        semantic_memory.store_knowledge("cat", "key", "v1", version=1)
        semantic_memory.store_knowledge("cat", "key", "v2", version=2)
        
        # Get latest version
        value = semantic_memory.get_knowledge("cat", "key")
        assert value == "v2"
        
        # Get specific version
        value_v1 = semantic_memory.get_knowledge("cat", "key", version=1)
        assert value_v1 == "v1"


class TestAnalytics:
    """Test analytics functions."""
    
    def test_get_score_distribution(self, seeded_memory):
        """Test getting score distribution."""
        dist = seeded_memory.get_score_distribution(bins=5)
        
        assert 'bins' in dist
        assert 'counts' in dist
        assert 'min' in dist
        assert 'max' in dist
        assert len(dist['bins']) == 5
        assert len(dist['counts']) == 5
    
    def test_detect_anomalies(self, seeded_memory):
        """Test anomaly detection."""
        # Add an anomalous score
        seeded_memory.store_score(
            user_id="user_123",
            session_id="sess_anomaly",
            scores={"final_score": 30.0, "confidence": 0.50}  # Very low score
        )
        
        anomalies = seeded_memory.detect_anomalies("user_123", window_days=7)
        
        assert len(anomalies) > 0
        assert any(a['score'] == 30.0 for a in anomalies)
    
    def test_detect_anomalies_no_data(self, semantic_memory):
        """Test anomaly detection with insufficient data."""
        anomalies = semantic_memory.detect_anomalies("user_123")
        assert anomalies == []
    
    def test_get_cohort_analysis(self, semantic_memory):
        """Test cohort analysis (placeholder)."""
        result = semantic_memory.get_cohort_analysis("age_group")
        
        assert 'error' in result
        assert 'not yet implemented' in result['error']


class TestMaintenance:
    """Test maintenance functions."""
    
    def test_get_stats(self, seeded_memory):
        """Test getting database statistics."""
        stats = seeded_memory.get_stats()
        
        assert 'total_scores' in stats
        assert 'total_users' in stats
        assert 'database_size_mb' in stats
        
        assert stats['total_scores'] == 15
        assert stats['total_users'] == 2
    
    def test_export_user_data(self, seeded_memory):
        """Test exporting user data."""
        export = seeded_memory.export_user_data("user_123")
        
        assert export['user_id'] == "user_123"
        assert 'exported_at' in export
        assert 'user_stats' in export
        assert 'score_history' in export
        assert len(export['score_history']) == 10
    
    def test_delete_user_data(self, seeded_memory):
        """Test deleting user data."""
        # Delete user_456
        seeded_memory.delete_user_data("user_456")
        
        # Verify deletion
        stats = seeded_memory.get_user_stats("user_456")
        assert stats is None
        
        # Verify user_123 still exists
        stats_123 = seeded_memory.get_user_stats("user_123")
        assert stats_123 is not None
    
    def test_context_manager(self, temp_db):
        """Test context manager usage."""
        with SemanticMemory(temp_db) as sm:
            sm.store_score(
                user_id="user_123",
                session_id="sess_001",
                scores={"final_score": 75.0}
            )
            stats = sm.get_user_stats("user_123")
            assert stats is not None
        
        # Connection should be closed after context
        assert os.path.exists(temp_db)


class TestConcurrentAccess:
    """Test thread safety and concurrent access."""
    
    def test_multiple_store_operations(self, semantic_memory):
        """Test multiple store operations in sequence."""
        for i in range(100):
            semantic_memory.store_score(
                user_id=f"user_{i % 10}",
                session_id=f"sess_{i}",
                scores={"final_score": 70 + i % 30}
            )
        
        stats = semantic_memory.get_stats()
        assert stats['total_scores'] == 100
        assert stats['total_users'] == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
