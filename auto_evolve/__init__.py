"""
Auto-Evolve Framework
让 AI Agent 自主进化的通用框架
"""

__version__ = "0.1.0"
__author__ = "Hulk (V via Hulk)"
__email__ = "cittaverse@gmail.com"

from .core import Goal, Strategy, Action, AutoEvolveEngine

__all__ = ["Goal", "Strategy", "Action", "AutoEvolveEngine"]
