"""
Chemicals Module

Chemical species definitions, property database, and ML-based property prediction.
Integrates with MACE universal force field for missing property estimation.
"""

from nanop.chemicals.base_chemical import Chemical, ChemicalConsumption
from nanop.chemicals.registry import (
    CHEMICAL_DATABASE,
    get_chemical,
    list_chemicals,
)
from nanop.chemicals.property_predictor import (
    PropertyPredictor,
    PropertyPrediction,
)
from nanop.chemicals.acids import ACIDS
from nanop.chemicals.bases import BASES
from nanop.chemicals.solvents import SOLVENTS

__all__ = [
    "Chemical",
    "ChemicalConsumption",
    "CHEMICAL_DATABASE",
    "get_chemical",
    "list_chemicals",
    "PropertyPredictor",
    "PropertyPrediction",
    "ACIDS",
    "BASES",
    "SOLVENTS",
]
