"""
CittaVerse Narrative Assessment Pipeline
=========================================

神经符号叙事评估引擎 | Neuro-symbolic pipeline for narrative assessment

Copyright (c) 2026 CittaVerse (一念万相科技)
MIT License
"""

from .assessor import NarrativeAssessor
from .scoring import ScoreCalculator
from .events import EventDetector
from .report import ReportGenerator

__version__ = "0.2.0"
__author__ = "CittaVerse Research Team"
__all__ = [
    "NarrativeAssessor",
    "ScoreCalculator",
    "EventDetector",
    "ReportGenerator",
]
