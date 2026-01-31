"""
Decision Support Module

Multi-criteria decision analysis for pathway selection.
Integrates LCA, TEA, and risk assessments.
"""

from nanop.decision.criteria import (
    Criterion,
    CriteriaSet,
    create_default_criteria,
)
from nanop.decision.mcda import (
    TOPSIS,
    AHP,
    WeightedSum,
)
from nanop.decision.pareto import (
    ParetoAnalyzer,
    ParetoSolution,
)
from nanop.decision.scenario import (
    Scenario,
    ScenarioAnalyzer,
)
from nanop.decision.recommender import (
    PathwayRanker,
    Recommendation,
)

__all__ = [
    "Criterion",
    "CriteriaSet",
    "create_default_criteria",
    "TOPSIS",
    "AHP",
    "WeightedSum",
    "ParetoAnalyzer",
    "ParetoSolution",
    "Scenario",
    "ScenarioAnalyzer",
    "PathwayRanker",
    "Recommendation",
]
