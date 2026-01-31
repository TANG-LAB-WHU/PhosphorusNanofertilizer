"""
Utils Module

Common utilities for currency conversion, unit conversion,
annotations, and physical constants.
"""

from nanop.utils.currency import (
    convert_currency,
    adjust_inflation,
    get_exchange_rate,
    CurrencyConverter,
)
from nanop.utils.units import (
    convert_mass,
    convert_energy,
    convert_volume,
    convert_temperature,
    UnitConverter,
)
from nanop.utils.annotations import (
    DataSource,
    Assumption,
    Annotation,
    annotate,
)
from nanop.utils.constants import (
    PHYSICAL_CONSTANTS,
    ATOMIC_MASSES,
    LCA_REFERENCE_VALUES,
)

__all__ = [
    "convert_currency",
    "adjust_inflation",
    "get_exchange_rate",
    "CurrencyConverter",
    "convert_mass",
    "convert_energy",
    "convert_volume",
    "convert_temperature",
    "UnitConverter",
    "DataSource",
    "Assumption",
    "Annotation",
    "annotate",
    "PHYSICAL_CONSTANTS",
    "ATOMIC_MASSES",
    "LCA_REFERENCE_VALUES",
]
