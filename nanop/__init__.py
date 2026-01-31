"""
NanoP LCA-TEA Framework

Main package for Nano Hydroxyapatite Phosphorus Fertilizer life cycle assessment and techno-economic analysis.
"""

__version__ = "0.1.0"

from nanop.lca.lca_engine import LCAEngine
from nanop.tea.tea_engine import TEAEngine
from nanop.pathways import get_pathway, list_pathways
from nanop.risk.aggregator import RiskAggregator
from nanop.decision.recommender import PathwayRanker
from nanop.uncertainty.direct_sampling import MonteCarloSimulator

__all__ = [
    "LCAEngine",
    "TEAEngine",
    "get_pathway",
    "list_pathways",
    "RiskAggregator",
    "PathwayRanker",
    "MonteCarloSimulator",
]

