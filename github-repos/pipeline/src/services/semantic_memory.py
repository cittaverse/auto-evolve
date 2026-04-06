"""
Semantic Memory for VSNC

Stores and retrieves cross-session knowledge:
- User-level score aggregation and trends
- Population baselines and percentile ranking
- Calibration parameters for personalized scoring
- General knowledge base (scoring rules, definitions)

Author: Hulk 🟢 (GEO #104)
Created: 2026-04-04
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import statistics


class SemanticMemory:
    """
    Semantic Memory for VSNC
    
    Stores abstract knowledge, scoring patterns, and cross-session statistics.
    Unlike Episodic Memory (raw narrative events), Semantic Memory aggregates
    knowledge across users and sessions.
    """
    
    def __init__(self, db_path: str = "semantic_memory.db"):
        """
        Initialize semantic memory database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Create database schema if not exists."""
        cursor = self.conn.cursor()
        
        # User-level aggregated statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                total_sessions INTEGER DEFAULT 0,
                avg_final_score REAL,
                avg_confidence REAL,
                best_score REAL,
                worst_score REAL,
                score_std REAL,
                last_session_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Individual score records (for time-series analysis)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS score_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                narrative_id TEXT,
                final_score REAL NOT NULL,
                coherence REAL,
                emotional_richness REAL,
                narrative_depth REAL,
                linguistic_complexity REAL,
                authenticity REAL,
                temporal_structure REAL,
                confidence REAL,
                l1_adjustment INTEGER DEFAULT 0,
                l1_reasoning TEXT,
                metadata JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_stats(user_id)
            )
        ''')
        
        # Population baselines (reference groups)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS population_baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference_group TEXT NOT NULL,
                metric TEXT NOT NULL,
                mean REAL NOT NULL,
                std REAL,
                p25 REAL,
                p50 REAL,
                p75 REAL,
                p90 REAL,
                sample_size INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(reference_group, metric)
            )
        ''')
        
        # User-specific calibration parameters
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calibration_params (
                user_id TEXT PRIMARY KEY,
                dimension_weights JSON,
                personal_baseline REAL,
                sensitivity_factor REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_stats(user_id)
            )
        ''')
        
        # General knowledge base
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value JSON NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key, version)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_score_history_user ON score_history(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_score_history_timestamp ON score_history(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_score_history_user_timestamp ON score_history(user_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_population_baselines_group ON population_baselines(reference_group)')
        
        self.conn.commit()
    
    # === Score Storage & Aggregation ===
    
    def store_score(self, user_id: str, session_id: str, scores: Dict,
                   metadata: Optional[Dict] = None) -> None:
        """
        Store a score record and update user stats.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            scores: Dict with final_score and dimension scores
            metadata: Optional metadata (narrative_type, language, etc.)
        """
        cursor = self.conn.cursor()
        
        # Insert score record
        cursor.execute('''
            INSERT INTO score_history (
                user_id, session_id, narrative_id, final_score,
                coherence, emotional_richness, narrative_depth,
                linguistic_complexity, authenticity, temporal_structure,
                confidence, l1_adjustment, l1_reasoning, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, session_id,
            metadata.get('narrative_id') if metadata else None,
            scores.get('final_score'),
            scores.get('coherence'),
            scores.get('emotional_richness'),
            scores.get('narrative_depth'),
            scores.get('linguistic_complexity'),
            scores.get('authenticity'),
            scores.get('temporal_structure'),
            scores.get('confidence'),
            scores.get('l1_adjustment', 0),
            scores.get('l1_reasoning'),
            json.dumps(metadata) if metadata else None
        ))
        
        # Update user stats
        self._update_user_stats(user_id)
        
        self.conn.commit()
    
    def _update_user_stats(self, user_id: str):
        """Recalculate aggregated statistics for a user."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                AVG(final_score) as avg_final_score,
                AVG(confidence) as avg_confidence,
                MAX(final_score) as best_score,
                MIN(final_score) as worst_score,
                MAX(timestamp) as last_session_at
            FROM score_history
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        # Calculate standard deviation
        cursor.execute('''
            SELECT final_score FROM score_history WHERE user_id = ?
        ''', (user_id,))
        scores = [r[0] for r in cursor.fetchall() if r[0] is not None]
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        # Upsert user_stats
        cursor.execute('''
            INSERT INTO user_stats (
                user_id, total_sessions, avg_final_score, avg_confidence,
                best_score, worst_score, score_std, last_session_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                total_sessions = excluded.total_sessions,
                avg_final_score = excluded.avg_final_score,
                avg_confidence = excluded.avg_confidence,
                best_score = excluded.best_score,
                worst_score = excluded.worst_score,
                score_std = excluded.score_std,
                last_session_at = excluded.last_session_at,
                updated_at = CURRENT_TIMESTAMP
        ''', (
            user_id,
            row['total_sessions'],
            row['avg_final_score'],
            row['avg_confidence'],
            row['best_score'],
            row['worst_score'],
            score_std,
            row['last_session_at']
        ))
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """
        Get aggregated statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with user statistics or None if user not found
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return dict(row)
    
    def get_user_trend(self, user_id: str, days: int = 30,
                      granularity: str = 'day') -> List[Dict]:
        """
        Get time-series trend for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            granularity: 'day', 'week', or 'month'
            
        Returns:
            List of dicts with date, avg_score, session_count
        """
        cursor = self.conn.cursor()
        
        # Determine date format based on granularity
        if granularity == 'day':
            date_format = '%Y-%m-%d'
        elif granularity == 'week':
            date_format = '%Y-W%W'
        elif granularity == 'month':
            date_format = '%Y-%m'
        else:
            raise ValueError(f"Unknown granularity: {granularity}")
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor.execute(f'''
            SELECT 
                DATE(timestamp) as date,
                AVG(final_score) as avg_score,
                COUNT(*) as session_count
            FROM score_history
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        ''', (user_id, cutoff_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # === Population Baselines ===
    
    def update_population_baselines(self, reference_group: str = 'all_users') -> Dict:
        """
        Recalculate population baselines from score_history.
        
        Args:
            reference_group: Reference group identifier
            
        Returns:
            Dict with updated baseline statistics
        """
        cursor = self.conn.cursor()
        
        # Get all scores for reference group
        # For 'all_users', include everyone
        # For specific groups, would need user metadata filtering
        if reference_group == 'all_users':
            cursor.execute('SELECT final_score FROM score_history')
        else:
            # Would need to join with user metadata table
            # For now, treat as all_users
            cursor.execute('SELECT final_score FROM score_history')
        
        scores = [r[0] for r in cursor.fetchall() if r[0] is not None]
        
        if not scores:
            return {}
        
        # Calculate statistics
        mean = statistics.mean(scores)
        std = statistics.stdev(scores) if len(scores) > 1 else 0.0
        sorted_scores = sorted(scores)
        
        def percentile(data, p):
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f + 1 < len(data) else f
            return data[f] + (data[c] - data[f]) * (k - f) if c != f else data[f]
        
        p25 = percentile(sorted_scores, 25)
        p50 = percentile(sorted_scores, 50)
        p75 = percentile(sorted_scores, 75)
        p90 = percentile(sorted_scores, 90)
        
        # Upsert baseline
        cursor.execute('''
            INSERT INTO population_baselines (
                reference_group, metric, mean, std, p25, p50, p75, p90, sample_size
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(reference_group, metric) DO UPDATE SET
                mean = excluded.mean,
                std = excluded.std,
                p25 = excluded.p25,
                p50 = excluded.p50,
                p75 = excluded.p75,
                p90 = excluded.p90,
                sample_size = excluded.sample_size,
                last_updated = CURRENT_TIMESTAMP
        ''', (
            reference_group, 'final_score', mean, std, p25, p50, p75, p90, len(scores)
        ))
        
        self.conn.commit()
        
        return {
            'reference_group': reference_group,
            'metric': 'final_score',
            'mean': mean,
            'std': std,
            'p25': p25,
            'p50': p50,
            'p75': p75,
            'p90': p90,
            'sample_size': len(scores)
        }
    
    def get_percentile_rank(self, score: float, user_id: Optional[str] = None,
                           reference_group: str = 'all_users',
                           metric: str = 'final_score') -> float:
        """
        Calculate percentile rank for a score.
        
        Args:
            score: Score to rank
            user_id: Optional user ID (for future personalization)
            reference_group: Reference group for comparison
            metric: Metric to compare
            
        Returns:
            Percentile rank (0-100)
        """
        cursor = self.conn.cursor()
        
        # Get baseline stats
        cursor.execute('''
            SELECT mean, std, p25, p50, p75, p90, sample_size
            FROM population_baselines
            WHERE reference_group = ? AND metric = ?
        ''', (reference_group, metric))
        
        row = cursor.fetchone()
        
        if row is None or row['sample_size'] == 0:
            # No baseline available, return 50 (neutral)
            return 50.0
        
        # Simple z-score based percentile (assuming normal distribution)
        mean = row['mean']
        std = row['std']
        
        if std == 0:
            return 50.0
        
        z = (score - mean) / std
        
        # Approximate cumulative distribution function
        # Using Abramowitz and Stegun approximation
        def norm_cdf(z):
            t = 1.0 / (1.0 + 0.2316419 * abs(z))
            d = 0.3989423 * (2.7182818 ** (-z * z / 2))
            p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
            return 1.0 - p if z > 0 else p
        
        percentile = norm_cdf(z) * 100
        return round(percentile, 2)
    
    def get_baseline_stats(self, reference_group: str = 'all_users',
                          metric: str = 'final_score') -> Optional[Dict]:
        """
        Get baseline statistics for a reference group.
        
        Args:
            reference_group: Reference group identifier
            metric: Metric name
            
        Returns:
            Dict with baseline statistics or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM population_baselines
            WHERE reference_group = ? AND metric = ?
        ''', (reference_group, metric))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # === Calibration ===
    
    def set_calibration_params(self, user_id: str,
                              dimension_weights: Optional[Dict] = None,
                              sensitivity_factor: float = 1.0) -> None:
        """
        Set user-specific calibration parameters.
        
        Args:
            user_id: User identifier
            dimension_weights: Override default dimension weights
            sensitivity_factor: Amplify/reduce score changes (1.0 = normal)
        """
        cursor = self.conn.cursor()
        
        # Get or calculate personal baseline
        cursor.execute('''
            SELECT AVG(final_score) as personal_baseline
            FROM score_history
            WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        personal_baseline = row['personal_baseline'] if row and row['personal_baseline'] else None
        
        # Upsert calibration params
        cursor.execute('''
            INSERT INTO calibration_params (
                user_id, dimension_weights, personal_baseline, sensitivity_factor
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                dimension_weights = excluded.dimension_weights,
                personal_baseline = excluded.personal_baseline,
                sensitivity_factor = excluded.sensitivity_factor,
                updated_at = CURRENT_TIMESTAMP
        ''', (
            user_id,
            json.dumps(dimension_weights) if dimension_weights else None,
            personal_baseline,
            sensitivity_factor
        ))
        
        self.conn.commit()
    
    def get_calibration_params(self, user_id: str) -> Optional[Dict]:
        """
        Get user-specific calibration parameters.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with calibration parameters or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM calibration_params WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        result = dict(row)
        if result.get('dimension_weights'):
            result['dimension_weights'] = json.loads(result['dimension_weights'])
        return result
    
    def apply_calibration(self, user_id: str, raw_scores: Dict) -> Dict:
        """
        Apply calibration to raw scores.
        
        Args:
            user_id: User identifier
            raw_scores: Raw score dict
            
        Returns:
            Calibrated score dict
        """
        params = self.get_calibration_params(user_id)
        
        if params is None:
            return raw_scores
        
        calibrated = raw_scores.copy()
        
        # Apply dimension weights if provided
        weights = params.get('dimension_weights')
        if weights:
            # Recalculate final_score based on custom weights
            dimensions = ['coherence', 'emotional_richness', 'narrative_depth',
                         'linguistic_complexity', 'authenticity', 'temporal_structure']
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for dim in dimensions:
                if dim in weights and dim in raw_scores:
                    weighted_sum += raw_scores[dim] * weights[dim]
                    total_weight += weights[dim]
            
            if total_weight > 0:
                calibrated['final_score'] = (weighted_sum / total_weight) * 100
        
        # Apply sensitivity factor
        sensitivity = params.get('sensitivity_factor', 1.0)
        if sensitivity != 1.0 and params.get('personal_baseline'):
            baseline = params['personal_baseline']
            deviation = calibrated['final_score'] - baseline
            calibrated['final_score'] = baseline + (deviation * sensitivity)
        
        return calibrated
    
    # === Knowledge Base ===
    
    def store_knowledge(self, category: str, key: str, value: Any,
                       version: int = 1) -> None:
        """
        Store a piece of general knowledge.
        
        Args:
            category: Knowledge category (e.g., 'scoring_rules')
            key: Knowledge key
            value: Knowledge value (any JSON-serializable type)
            version: Version number
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_base (category, key, value, version)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(category, key, version) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        ''', (category, key, json.dumps(value), version))
        
        self.conn.commit()
    
    def get_knowledge(self, category: str, key: str,
                     version: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve knowledge by category and key.
        
        Args:
            category: Knowledge category
            key: Knowledge key
            version: Specific version (default: latest)
            
        Returns:
            Knowledge value or None if not found
        """
        cursor = self.conn.cursor()
        
        if version:
            cursor.execute('''
                SELECT value FROM knowledge_base
                WHERE category = ? AND key = ? AND version = ?
            ''', (category, key, version))
        else:
            cursor.execute('''
                SELECT value FROM knowledge_base
                WHERE category = ? AND key = ?
                ORDER BY version DESC LIMIT 1
            ''', (category, key))
        
        row = cursor.fetchone()
        return json.loads(row['value']) if row else None
    
    def list_knowledge(self, category: str) -> List[Dict]:
        """
        List all knowledge entries in a category.
        
        Args:
            category: Knowledge category
            
        Returns:
            List of knowledge entries
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT key, value, version, created_at, updated_at
            FROM knowledge_base
            WHERE category = ?
            ORDER BY key ASC
        ''', (category,))
        
        results = []
        for row in cursor.fetchall():
            entry = dict(row)
            entry['value'] = json.loads(entry['value'])
            results.append(entry)
        
        return results
    
    # === Analytics ===
    
    def get_score_distribution(self, reference_group: str = 'all_users',
                              metric: str = 'final_score',
                              bins: int = 10) -> Dict:
        """
        Get score distribution for analysis.
        
        Args:
            reference_group: Reference group
            metric: Metric name
            bins: Number of bins
            
        Returns:
            Dict with distribution data
        """
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT {metric} FROM score_history WHERE {metric} IS NOT NULL')
        scores = [r[0] for r in cursor.fetchall()]
        
        if not scores:
            return {'bins': [], 'counts': [], 'min': 0, 'max': 0}
        
        min_score = min(scores)
        max_score = max(scores)
        bin_width = (max_score - min_score) / bins
        
        bin_counts = [0] * bins
        for score in scores:
            bin_idx = min(int((score - min_score) / bin_width), bins - 1)
            bin_counts[bin_idx] += 1
        
        return {
            'bins': [min_score + i * bin_width for i in range(bins)],
            'counts': bin_counts,
            'min': min_score,
            'max': max_score,
            'total': len(scores)
        }
    
    def detect_anomalies(self, user_id: str, window_days: int = 7,
                        z_threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalous scores for a user.
        
        Args:
            user_id: User identifier
            window_days: Lookback window in days
            z_threshold: Z-score threshold for anomaly
            
        Returns:
            List of anomalous score records
        """
        cursor = self.conn.cursor()
        
        cutoff_date = (datetime.utcnow() - timedelta(days=window_days)).isoformat()
        
        # Get scores in window
        cursor.execute('''
            SELECT id, session_id, final_score, timestamp
            FROM score_history
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (user_id, cutoff_date))
        
        rows = cursor.fetchall()
        
        if len(rows) < 3:
            return []  # Not enough data for anomaly detection
        
        scores = [r['final_score'] for r in rows if r['final_score'] is not None]
        
        if len(scores) < 3:
            return []
        
        mean = statistics.mean(scores)
        std = statistics.stdev(scores)
        
        if std == 0:
            return []
        
        anomalies = []
        for row in rows:
            if row['final_score'] is None:
                continue
            
            z_score = (row['final_score'] - mean) / std
            
            if abs(z_score) > z_threshold:
                anomalies.append({
                    'session_id': row['session_id'],
                    'score': row['final_score'],
                    'z_score': round(z_score, 2),
                    'timestamp': row['timestamp'],
                    'reason': 'Score significantly below average' if z_score < 0 else 'Score significantly above average'
                })
        
        return anomalies
    
    def get_cohort_analysis(self, cohort_field: str,
                           metric: str = 'final_score') -> Dict:
        """
        Analyze scores by cohort.
        
        Note: Requires user metadata table (not yet implemented).
        This is a placeholder for future implementation.
        
        Args:
            cohort_field: Cohort field name (e.g., 'age_group', 'education')
            metric: Metric to analyze
            
        Returns:
            Dict with cohort statistics
        """
        # Placeholder - would need user metadata table
        return {
            'error': 'Cohort analysis requires user metadata table (not yet implemented)',
            'cohorts': []
        }
    
    # === Maintenance ===
    
    def get_stats(self) -> Dict:
        """
        Get semantic memory statistics.
        
        Returns:
            Dict with database statistics
        """
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM score_history')
        total_scores = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM user_stats')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM population_baselines')
        total_baselines = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_base')
        total_knowledge = cursor.fetchone()[0]
        
        # Get database file size
        db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
        
        return {
            'total_scores': total_scores,
            'total_users': total_users,
            'total_baselines': total_baselines,
            'total_knowledge_entries': total_knowledge,
            'database_size_mb': round(db_size / 1024 / 1024, 2)
        }
    
    def export_user_data(self, user_id: str) -> Dict:
        """
        Export all data for a user (GDPR compliance).
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with all user data
        """
        cursor = self.conn.cursor()
        
        # Get user stats
        cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        user_stats = dict(row) if row else None
        
        # Get score history
        cursor.execute('SELECT * FROM score_history WHERE user_id = ?', (user_id,))
        score_history = [dict(row) for row in cursor.fetchall()]
        
        # Get calibration params
        cursor.execute('SELECT * FROM calibration_params WHERE user_id = ?', (user_id,))
        calibration = dict(cursor.fetchone()) if cursor.fetchone() else None
        
        return {
            'user_id': user_id,
            'exported_at': datetime.utcnow().isoformat(),
            'user_stats': user_stats,
            'score_history': score_history,
            'calibration_params': calibration
        }
    
    def delete_user_data(self, user_id: str) -> None:
        """
        Delete all data for a user (GDPR compliance).
        
        Args:
            user_id: User identifier
        """
        cursor = self.conn.cursor()
        
        # Delete in order (respect foreign keys)
        cursor.execute('DELETE FROM calibration_params WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM score_history WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM user_stats WHERE user_id = ?', (user_id,))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# === Singleton Helper ===

_semantic_memory_instances: Dict[str, SemanticMemory] = {}


def get_semantic_memory(db_path: Optional[str] = None) -> SemanticMemory:
    """
    Get or create a SemanticMemory singleton instance.
    
    Args:
        db_path: Database path (default: "semantic_memory.db" in current directory)
    
    Returns:
        SemanticMemory instance (singleton per db_path)
    """
    if db_path is None:
        db_path = "semantic_memory.db"
    
    if db_path not in _semantic_memory_instances:
        _semantic_memory_instances[db_path] = SemanticMemory(db_path=db_path)
    
    return _semantic_memory_instances[db_path]
