"""
LCA Module

Provides Life Cycle Assessment functionality for nanoP production.
"""

from nanop.lca.lca_engine import LCAEngine, LCAResult
from nanop.lca.inventory import LifeCycleInventory, Flow
from nanop.lca.characterization import CharacterizationFactors
from nanop.lca.impact_assessment import ImpactAssessment
from nanop.lca.normalization import LCANormalizer

__all__ = [
    "LCAEngine",
    "LCAResult",
    "LifeCycleInventory",
    "Flow",
    "CharacterizationFactors",
    "ImpactAssessment",
    "LCANormalizer",
]
