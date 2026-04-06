"""
Procedural Memory for VSNC (RB-016 Phase 4)

Stores and manages scoring strategies and calibration rules:
- Strategy registry (pluggable scoring algorithms)
- Strategy selector (rule-based automatic selection)
- Calibration rules (personalized score adjustments)
- Strategy usage analytics

Author: Hulk 🟢 (GEO #105)
Created: 2026-04-04
Version: 1.0.0
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Strategy Abstract Base Class
# =============================================================================

class ScoringStrategy(ABC):
    """Abstract base class for all scoring strategies."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy identifier."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        pass
    
    @abstractmethod
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]:
        """
        Score a narrative using this strategy.
        
        Returns:
            {
                "composite_score": float,
                "dimension_scores": Dict[str, float],
                "confidence": float,
                "strategy_metadata": Dict[str, Any]
            }
        """
        pass
    
    @abstractmethod
    def get_requirements(self) -> Dict[str, Any]:
        """
        Return strategy requirements/assumptions.
        
        Example:
            {
                "min_text_length": 50,
                "language": "zh-CN",
                "requires_llm": True,
                "cultural_context": "East Asian"
            }
        """
        pass


# =============================================================================
# User Context for Strategy Selection
# =============================================================================

@dataclass
class UserContext:
    """Context information for strategy selection."""
    user_id: str
    age: Optional[int] = None
    cultural_background: Optional[str] = None
    narrative_topic: Optional[str] = None
    text_length: int = 0
    session_count: int = 0
    previous_scores: Optional[List[float]] = None
    language: str = "zh-CN"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# Selection Rule
# =============================================================================

@dataclass
class SelectionRule:
    """Rule for automatic strategy selection."""
    name: str
    priority: int  # Higher = evaluated first
    condition: Callable[[UserContext], bool]
    strategy_name: str
    
    def matches(self, context: UserContext) -> bool:
        try:
            return self.condition(context)
        except Exception as e:
            logger.error(f"Error evaluating rule {self.name}: {e}")
            return False


# =============================================================================
# Calibration Rule
# =============================================================================

@dataclass
class CalibrationRule:
    """Rule for score calibration."""
    rule_id: str
    user_id: str
    rule_type: str  # "dimension_weight", "sensitivity", "threshold"
    params: Dict[str, Any]
    priority: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    def apply(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply calibration rule to scores."""
        if self.rule_type == "dimension_weight":
            return self._apply_weights(scores)
        elif self.rule_type == "sensitivity":
            return self._apply_sensitivity(scores)
        elif self.rule_type == "threshold":
            return self._apply_threshold(scores)
        else:
            logger.warning(f"Unknown rule type: {self.rule_type}")
            return scores
    
    def _apply_weights(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply dimension weight adjustments."""
        weights = self.params.get("dimension_weights", {})
        if not weights:
            return scores
        
        # Normalize weights
        total = sum(weights.values())
        if total == 0:
            return scores
        
        normalized = {k: v / total for k, v in weights.items()}
        
        # Apply weights to scores (weighted average)
        result = {}
        for dim, score in scores.items():
            weight = normalized.get(dim, 1.0)
            result[dim] = score * weight
        
        return result
    
    def _apply_sensitivity(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply sensitivity adjustments."""
        sensitivity = self.params.get("sensitivity_factor", 1.0)
        return {k: v * sensitivity for k, v in scores.items()}
    
    def _apply_threshold(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply threshold adjustments."""
        thresholds = self.params.get("thresholds", {})
        result = scores.copy()
        
        for dim, threshold in thresholds.items():
            if dim in result:
                if result[dim] < threshold.get("min", 0):
                    result[dim] = threshold.get("min", 0)
                elif result[dim] > threshold.get("max", 100):
                    result[dim] = threshold.get("max", 100)
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "user_id": self.user_id,
            "rule_type": self.rule_type,
            "params": self.params,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CalibrationRule":
        return cls(
            rule_id=data["rule_id"],
            user_id=data["user_id"],
            rule_type=data["rule_type"],
            params=data["params"],
            priority=data["priority"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            is_active=data.get("is_active", True)
        )


# =============================================================================
# Pre-defined Strategies
# =============================================================================

class DefaultStrategy(ScoringStrategy):
    """Default scoring strategy with equal weights."""
    
    @property
    def name(self) -> str:
        return "default_v1"
    
    @property
    def description(self) -> str:
        return "标准 6 维度等权重策略 - 通用场景"
    
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]:
        # Placeholder - would call actual scoring logic
        # For now, return dummy scores
        return {
            "composite_score": 75.0,
            "dimension_scores": {
                "emotional_depth": 75.0,
                "cognitive_details": 75.0,
                "temporal_coherence": 75.0,
                "self_reflection": 75.0,
                "social_connection": 75.0,
                "growth_insight": 75.0
            },
            "confidence": 0.8,
            "strategy_metadata": {
                "strategy": self.name,
                "version": "1.0.0"
            }
        }
    
    def get_requirements(self) -> Dict[str, Any]:
        return {
            "min_text_length": 50,
            "language": "zh-CN",
            "requires_llm": True,
            "cultural_context": "universal"
        }


class ElderlyFriendlyStrategy(ScoringStrategy):
    """Strategy optimized for elderly users (65+)."""
    
    @property
    def name(self) -> str:
        return "elderly_friendly"
    
    @property
    def description(self) -> str:
        return "老年友好策略 - 降低流畅度权重，提升情感深度和自我反思权重"
    
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]:
        # Placeholder - would apply elderly-specific scoring
        return {
            "composite_score": 78.0,
            "dimension_scores": {
                "emotional_depth": 85.0,  # Higher weight
                "cognitive_details": 70.0,
                "temporal_coherence": 70.0,
                "self_reflection": 85.0,  # Higher weight
                "social_connection": 75.0,
                "growth_insight": 75.0
            },
            "confidence": 0.85,
            "strategy_metadata": {
                "strategy": self.name,
                "version": "1.0.0",
                "adjustments": ["increased_emotional_weight", "increased_reflection_weight"]
            }
        }
    
    def get_requirements(self) -> Dict[str, Any]:
        return {
            "min_text_length": 30,
            "language": "zh-CN",
            "requires_llm": True,
            "cultural_context": "universal",
            "age_group": "65+"
        }


class TraumaSensitiveStrategy(ScoringStrategy):
    """Strategy for trauma-sensitive scoring."""
    
    @property
    def name(self) -> str:
        return "trauma_sensitive"
    
    @property
    def description(self) -> str:
        return "创伤敏感策略 - 降低负面事件惩罚，强调成长洞察"
    
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]:
        return {
            "composite_score": 72.0,
            "dimension_scores": {
                "emotional_depth": 80.0,
                "cognitive_details": 65.0,
                "temporal_coherence": 65.0,
                "self_reflection": 80.0,
                "social_connection": 70.0,
                "growth_insight": 85.0  # Higher weight for growth
            },
            "confidence": 0.75,
            "strategy_metadata": {
                "strategy": self.name,
                "version": "1.0.0",
                "adjustments": ["reduced_negative_penalty", "increased_growth_bonus"]
            }
        }
    
    def get_requirements(self) -> Dict[str, Any]:
        return {
            "min_text_length": 50,
            "language": "zh-CN",
            "requires_llm": True,
            "cultural_context": "universal",
            "sensitive_topics": ["loss", "trauma", "grief"]
        }


class CulturalEastAsianStrategy(ScoringStrategy):
    """Strategy adapted for East Asian cultural context."""
    
    @property
    def name(self) -> str:
        return "cultural_east_asian"
    
    @property
    def description(self) -> str:
        return "东亚文化适应策略 - 调整集体主义 vs 个人主义维度权重"
    
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]:
        return {
            "composite_score": 76.0,
            "dimension_scores": {
                "emotional_depth": 75.0,
                "cognitive_details": 75.0,
                "temporal_coherence": 75.0,
                "self_reflection": 75.0,
                "social_connection": 85.0,  # Higher weight for collectivism
                "growth_insight": 70.0
            },
            "confidence": 0.8,
            "strategy_metadata": {
                "strategy": self.name,
                "version": "1.0.0",
                "cultural_adaptation": "East Asian"
            }
        }
    
    def get_requirements(self) -> Dict[str, Any]:
        return {
            "min_text_length": 50,
            "language": "zh-CN",
            "requires_llm": True,
            "cultural_context": "East Asian"
        }


class BriefNarrativeStrategy(ScoringStrategy):
    """Strategy optimized for brief narratives (<200 characters)."""
    
    @property
    def name(self) -> str:
        return "brief_narrative"
    
    @property
    def description(self) -> str:
        return "短文本策略 - 优化 200 字以下快速记录场景"
    
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]:
        return {
            "composite_score": 70.0,
            "dimension_scores": {
                "emotional_depth": 70.0,
                "cognitive_details": 65.0,
                "temporal_coherence": 70.0,
                "self_reflection": 70.0,
                "social_connection": 70.0,
                "growth_insight": 75.0
            },
            "confidence": 0.7,  # Lower confidence for brief text
            "strategy_metadata": {
                "strategy": self.name,
                "version": "1.0.0",
                "text_length": len(narrative_text)
            }
        }
    
    def get_requirements(self) -> Dict[str, Any]:
        return {
            "min_text_length": 10,
            "max_text_length": 200,
            "language": "zh-CN",
            "requires_llm": False,  # Can work without LLM for speed
            "cultural_context": "universal"
        }


# =============================================================================
# Procedural Memory Core
# =============================================================================

class ProceduralMemory:
    """
    Procedural Memory for VSNC
    
    Manages scoring strategies and calibration rules:
    - Strategy registry (pluggable scoring algorithms)
    - Strategy selector (rule-based automatic selection)
    - Calibration rules (personalized score adjustments)
    - Strategy usage analytics
    """
    
    def __init__(self, db_path: str = "procedural_memory.db"):
        """
        Initialize procedural memory database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        
        # In-memory caches
        self._strategy_registry: Dict[str, ScoringStrategy] = {}
        self._selection_rules: List[SelectionRule] = []
        self._calibration_rules_cache: Dict[str, List[CalibrationRule]] = {}
        
        # Register default strategies
        self._register_default_strategies()
        self._register_default_rules()
    
    def _init_schema(self):
        """Create database schema if not exists."""
        cursor = self.conn.cursor()
        
        # Strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                config_json TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '1.0.0',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Selection rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selection_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 50,
                condition_type TEXT NOT NULL,
                condition_params TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (strategy_name) REFERENCES strategies(name)
            )
        ''')
        
        # Calibration rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calibration_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                params_json TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                created_by TEXT,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        # Strategy usage log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                session_id TEXT,
                narrative_id TEXT,
                selected_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_calibration_user ON calibration_rules(user_id, is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_strategy_usage_user ON strategy_usage_log(user_id, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_selection_rules_active ON selection_rules(is_active, priority DESC)')
        
        self.conn.commit()
    
    def _register_default_strategies(self):
        """Register built-in strategies."""
        strategies = [
            DefaultStrategy(),
            ElderlyFriendlyStrategy(),
            TraumaSensitiveStrategy(),
            CulturalEastAsianStrategy(),
            BriefNarrativeStrategy()
        ]
        
        for strategy in strategies:
            self._strategy_registry[strategy.name] = strategy
    
    def _register_default_rules(self):
        """Register default selection rules."""
        # Elderly user rule
        self._selection_rules.append(SelectionRule(
            name="elderly_user",
            priority=100,
            condition=lambda ctx: ctx.age is not None and ctx.age >= 65,
            strategy_name="elderly_friendly"
        ))
        
        # Trauma narrative rule
        self._selection_rules.append(SelectionRule(
            name="trauma_narrative",
            priority=90,
            condition=lambda ctx: ctx.narrative_topic in ["loss", "trauma", "grief"],
            strategy_name="trauma_sensitive"
        ))
        
        # East Asian cultural rule
        self._selection_rules.append(SelectionRule(
            name="east_asian",
            priority=80,
            condition=lambda ctx: ctx.cultural_background == "East Asian",
            strategy_name="cultural_east_asian"
        ))
        
        # Brief narrative rule
        self._selection_rules.append(SelectionRule(
            name="brief_narrative",
            priority=70,
            condition=lambda ctx: ctx.text_length < 200,
            strategy_name="brief_narrative"
        ))
    
    # =========================================================================
    # Strategy Management
    # =========================================================================
    
    def register_strategy(self, strategy: ScoringStrategy) -> bool:
        """
        Register a new strategy.
        
        Args:
            strategy: Strategy instance to register
            
        Returns:
            True if successful, False if strategy already exists
        """
        if strategy.name in self._strategy_registry:
            logger.warning(f"Strategy {strategy.name} already registered")
            return False
        
        self._strategy_registry[strategy.name] = strategy
        
        # Persist to DB
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO strategies (name, description, config_json, version, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (
            strategy.name,
            strategy.description,
            json.dumps(strategy.get_requirements()),
            "1.0.0"
        ))
        self.conn.commit()
        
        logger.info(f"Registered strategy: {strategy.name}")
        return True
    
    def get_strategy(self, name: str) -> Optional[ScoringStrategy]:
        """Get a strategy by name."""
        return self._strategy_registry.get(name)
    
    def list_strategies(self) -> List[str]:
        """List all registered strategy names."""
        return list(self._strategy_registry.keys())
    
    # =========================================================================
    # Strategy Selection
    # =========================================================================
    
    def add_selection_rule(self, rule: SelectionRule) -> bool:
        """Add a selection rule."""
        self._selection_rules.append(rule)
        
        # Persist to DB
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO selection_rules (name, priority, condition_type, condition_params, strategy_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            rule.name,
            rule.priority,
            "custom",
            json.dumps({"condition": rule.name}),  # Simplified
            rule.strategy_name
        ))
        self.conn.commit()
        
        return True
    
    def select_strategy(self, context: UserContext) -> ScoringStrategy:
        """
        Select strategy based on user context.
        
        Args:
            context: User context information
            
        Returns:
            Selected strategy instance
        """
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self._selection_rules, key=lambda r: r.priority, reverse=True)
        
        # Evaluate rules
        for rule in sorted_rules:
            if rule.matches(context):
                strategy = self.get_strategy(rule.strategy_name)
                if strategy:
                    logger.info(f"Selected strategy '{strategy.name}' via rule '{rule.name}'")
                    self._log_strategy_usage(context.user_id, strategy.name, rule.name)
                    return strategy
        
        # Fallback to default
        default = self.get_strategy("default_v1")
        logger.info("Using default strategy (no rules matched)")
        return default
    
    def _log_strategy_usage(self, user_id: str, strategy_name: str, 
                            reason: str, session_id: Optional[str] = None,
                            narrative_id: Optional[str] = None):
        """Log strategy usage for analytics."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO strategy_usage_log (user_id, strategy_name, session_id, narrative_id, selected_reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, strategy_name, session_id, narrative_id, reason))
        self.conn.commit()
    
    # =========================================================================
    # Calibration Rules
    # =========================================================================
    
    def create_calibration_rule(self, user_id: str, rule_type: str, 
                                params: Dict[str, Any], priority: int = 50,
                                expires_at: Optional[datetime] = None,
                                created_by: Optional[str] = None) -> str:
        """
        Create a new calibration rule.
        
        Args:
            user_id: Target user ID
            rule_type: "dimension_weight", "sensitivity", or "threshold"
            params: Rule parameters
            priority: Rule priority (higher = applied first)
            expires_at: Optional expiration time
            created_by: Creator user ID (for audit)
            
        Returns:
            rule_id: Generated rule ID
        """
        rule_id = hashlib.md5(f"{user_id}:{rule_type}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        rule = CalibrationRule(
            rule_id=rule_id,
            user_id=user_id,
            rule_type=rule_type,
            params=params,
            priority=priority,
            created_at=datetime.now(),
            expires_at=expires_at,
            is_active=True
        )
        
        # Persist to DB
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO calibration_rules (rule_id, user_id, rule_type, params_json, priority, expires_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule_id, user_id, rule_type, json.dumps(params), priority, 
            expires_at.isoformat() if expires_at else None, created_by
        ))
        self.conn.commit()
        
        # Invalidate cache for this user
        if user_id in self._calibration_rules_cache:
            del self._calibration_rules_cache[user_id]
        
        logger.info(f"Created calibration rule {rule_id} for user {user_id}")
        return rule_id
    
    def get_calibration_rules(self, user_id: str) -> List[CalibrationRule]:
        """Get all active calibration rules for a user."""
        # Check cache
        if user_id in self._calibration_rules_cache:
            return self._calibration_rules_cache[user_id]
        
        # Query DB
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT rule_id, user_id, rule_type, params_json, priority, 
                   created_at, expires_at, is_active
            FROM calibration_rules
            WHERE user_id = ? AND is_active = 1
              AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY priority DESC
        ''', (user_id, datetime.now().isoformat()))
        
        rules = []
        for row in cursor.fetchall():
            rule = CalibrationRule(
                rule_id=row["rule_id"],
                user_id=row["user_id"],
                rule_type=row["rule_type"],
                params=json.loads(row["params_json"]),
                priority=row["priority"],
                created_at=datetime.fromisoformat(row["created_at"]),
                expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
                is_active=bool(row["is_active"])
            )
            rules.append(rule)
        
        # Cache
        self._calibration_rules_cache[user_id] = rules
        
        return rules
    
    def apply_calibration(self, scores: Dict[str, float], 
                         rules: List[CalibrationRule]) -> Dict[str, float]:
        """
        Apply calibration rules to scores.
        
        Args:
            scores: Original dimension scores
            rules: List of calibration rules to apply
            
        Returns:
            Calibrated scores
        """
        if not rules:
            return scores
        
        calibrated = scores.copy()
        
        # Apply rules in priority order (highest first)
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            calibrated = rule.apply(calibrated)
        
        return calibrated
    
    def delete_calibration_rule(self, rule_id: str) -> bool:
        """Delete a calibration rule."""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE calibration_rules SET is_active = 0 WHERE rule_id = ?', (rule_id,))
        self.conn.commit()
        
        # Invalidate cache for affected users
        self._calibration_rules_cache.clear()
        
        return cursor.rowcount > 0
    
    # =========================================================================
    # Analytics
    # =========================================================================
    
    def get_strategy_usage_stats(self, user_id: Optional[str] = None, 
                                 days: int = 30) -> Dict[str, Any]:
        """
        Get strategy usage statistics.
        
        Args:
            user_id: Optional user ID filter
            days: Number of days to analyze
            
        Returns:
            Usage statistics
        """
        cursor = self.conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        if user_id:
            cursor.execute('''
                SELECT strategy_name, selected_reason, COUNT(*) as usage_count
                FROM strategy_usage_log
                WHERE user_id = ? AND created_at > ?
                GROUP BY strategy_name, selected_reason
                ORDER BY usage_count DESC
            ''', (user_id, since))
        else:
            cursor.execute('''
                SELECT strategy_name, selected_reason, COUNT(*) as usage_count
                FROM strategy_usage_log
                WHERE created_at > ?
                GROUP BY strategy_name, selected_reason
                ORDER BY usage_count DESC
            ''', (since,))
        
        stats = {
            "period_days": days,
            "total_usage": 0,
            "by_strategy": {}
        }
        
        for row in cursor.fetchall():
            strategy = row["strategy_name"]
            reason = row["selected_reason"]
            count = row["usage_count"]
            
            stats["total_usage"] += count
            
            if strategy not in stats["by_strategy"]:
                stats["by_strategy"][strategy] = {
                    "total": 0,
                    "by_reason": {}
                }
            
            stats["by_strategy"][strategy]["total"] += count
            stats["by_strategy"][strategy]["by_reason"][reason] = count
        
        return stats
    
    # =========================================================================
    # Utility
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get procedural memory statistics."""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM strategies WHERE is_active = 1')
        strategy_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM selection_rules WHERE is_active = 1')
        rules_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM calibration_rules WHERE is_active = 1')
        calibration_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM strategy_usage_log')
        usage_log_count = cursor.fetchone()[0]
        
        return {
            "strategy_count": strategy_count,
            "selection_rules_count": rules_count,
            "calibration_rules_count": calibration_count,
            "usage_log_entries": usage_log_count,
            "registered_strategies": self.list_strategies()
        }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# =============================================================================
# Singleton Helper
# =============================================================================

_procedural_memory_instances: Dict[str, ProceduralMemory] = {}

def get_procedural_memory(db_path: Optional[str] = None) -> ProceduralMemory:
    """
    Get or create a ProceduralMemory singleton instance.
    
    Args:
        db_path: Database path (default: "procedural_memory.db")
        
    Returns:
        ProceduralMemory instance
    """
    if db_path is None:
        db_path = "procedural_memory.db"
    
    if db_path not in _procedural_memory_instances:
        _procedural_memory_instances[db_path] = ProceduralMemory(db_path)
    
    return _procedural_memory_instances[db_path]
