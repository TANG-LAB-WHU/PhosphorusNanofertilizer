"""
Equipment / Unit Operations Module

Modular equipment components for LCA-TEA calculations.
Equipment classes provide standardized interfaces for LCI, CAPEX, and OPEX.
"""

from nanop.equipment.base_equipment import BaseEquipment
from nanop.equipment.reactors import (
    CSTRReactor,
    BatchReactor,
    LeachingTank,
    MixingTank,
)
from nanop.equipment.separations import (
    FilterPress,
    Centrifuge,
    Evaporator,
    SolventExtractor,
)
from nanop.equipment.material_handling import (
    Crusher,
    Dryer,
    Conveyor,
    StorageSilo,
)
from nanop.equipment.heat_exchange import (
    ShellTubeExchanger,
    CoolingTower,
)

__all__ = [
    "BaseEquipment",
    "CSTRReactor",
    "BatchReactor",
    "LeachingTank",
    "MixingTank",
    "FilterPress",
    "Centrifuge",
    "Evaporator",
    "SolventExtractor",
    "Crusher",
    "Dryer",
    "Conveyor",
    "StorageSilo",
    "ShellTubeExchanger",
    "CoolingTower",
]
