"""
NanoP LCA-TEA Framework

Life Cycle Assessment and Techno-Economic Analysis for Nano Hydroxyapatite Phosphorus Fertilizer.
"""

__version__ = "0.1.0"

from nanop.lca.engine import LCAEngine
from nanop.tea.engine import TEAEngine
from nanop.pathways import get_pathway, list_pathways

__all__ = [
    "LCAEngine",
    "TEAEngine",
    "get_pathway",
    "list_pathways",
]
