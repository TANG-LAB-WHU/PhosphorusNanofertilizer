"""
TEA Module

Provides Techno-Economic Analysis functionality for nanoP production.
"""

from nanop.tea.tea_engine import TEAEngine, TEAResult
from nanop.tea.capex import CAPEXCalculator
from nanop.tea.opex import OPEXCalculator
from nanop.tea.external_cost import ExternalCostCalculator
from nanop.tea.revenue import calculate_revenue

__all__ = [
    "TEAEngine",
    "TEAResult",
    "CAPEXCalculator",
    "OPEXCalculator",
    "ExternalCostCalculator",
    "calculate_revenue",
]
