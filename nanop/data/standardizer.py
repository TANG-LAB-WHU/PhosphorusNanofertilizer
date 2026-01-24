"""
Data Standardizer Module

Standardizes data from various sources into consistent LCI format.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class StandardizedFlow:
    """Standardized flow data."""
    
    name: str
    quantity: float
    unit: str
    category: str  # input, output, emission_air, emission_water
    subcategory: str = ""
    source: str = ""
    uncertainty: float = 0.0
    data_quality: str = "medium"


class UnitConverter:
    """
    Unit conversion for LCA-TEA calculations.
    """
    
    # Mass conversions (to kg)
    MASS_FACTORS = {
        "kg": 1.0,
        "g": 0.001,
        "mg": 1e-6,
        "tonne": 1000,
        "t": 1000,
        "lb": 0.453592,
        "oz": 0.0283495,
    }
    
    # Energy conversions (to kWh)
    ENERGY_FACTORS = {
        "kwh": 1.0,
        "kWh": 1.0,
        "mwh": 1000,
        "MWh": 1000,
        "j": 2.778e-7,
        "kj": 2.778e-4,
        "mj": 0.2778,
        "MJ": 0.2778,
        "gj": 277.8,
        "GJ": 277.8,
        "btu": 0.000293,
    }
    
    # Volume conversions (to L)
    VOLUME_FACTORS = {
        "l": 1.0,
        "L": 1.0,
        "ml": 0.001,
        "mL": 0.001,
        "m3": 1000,
        "gal": 3.78541,
    }
    
    def __init__(self):
        self.conversions = {
            "mass": self.MASS_FACTORS,
            "energy": self.ENERGY_FACTORS,
            "volume": self.VOLUME_FACTORS,
        }
    
    def convert(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        unit_type: Optional[str] = None
    ) -> float:
        """
        Convert between units.
        
        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            unit_type: Optional type hint (mass, energy, volume)
            
        Returns:
            Converted value
        """
        # Auto-detect unit type
        if unit_type is None:
            unit_type = self._detect_unit_type(from_unit)
        
        if unit_type is None:
            return value  # Unknown, return as-is
        
        factors = self.conversions.get(unit_type, {})
        from_factor = factors.get(from_unit.lower(), 1.0)
        to_factor = factors.get(to_unit.lower(), 1.0)
        
        # Convert to base, then to target
        base_value = value * from_factor
        return base_value / to_factor
    
    def _detect_unit_type(self, unit: str) -> Optional[str]:
        """Detect unit type from unit string."""
        unit_lower = unit.lower()
        
        if unit_lower in self.MASS_FACTORS:
            return "mass"
        elif unit_lower in self.ENERGY_FACTORS:
            return "energy"
        elif unit_lower in self.VOLUME_FACTORS:
            return "volume"
        
        return None
    
    def to_kg(self, value: float, unit: str) -> float:
        """Convert to kg."""
        return self.convert(value, unit, "kg", "mass")
    
    def to_kwh(self, value: float, unit: str) -> float:
        """Convert to kWh."""
        return self.convert(value, unit, "kWh", "energy")


class DataStandardizer:
    """
    Standardize LCI data from various sources.
    """
    
    # Mapping of common substance names to standard names
    SUBSTANCE_MAPPING = {
        "carbon dioxide": "CO2",
        "co2": "CO2",
        "nitrogen oxides": "NOx",
        "nox": "NOx",
        "sulfur dioxide": "SO2",
        "so2": "SO2",
        "particulate matter": "PM",
        "pm2.5": "PM2.5",
        "pm10": "PM10",
        "ammonia": "NH3",
        "nh3": "NH3",
        "phosphoric acid": "H3PO4",
        "calcium chloride": "CaCl2",
        "ammonium hydroxide": "NH4OH",
        "hydroxyapatite": "HAP",
        "nano hydroxyapatite": "NanoP",
    }
    
    # Category mapping
    CATEGORY_MAPPING = {
        "raw material": "input",
        "material": "input",
        "energy": "input",
        "electricity": "input",
        "product": "output",
        "byproduct": "output",
        "by-product": "output",
        "emission to air": "emission_air",
        "air emission": "emission_air",
        "emission to water": "emission_water",
        "water emission": "emission_water",
    }
    
    def __init__(self):
        self.unit_converter = UnitConverter()
    
    def standardize_flow(self, raw_data: Dict) -> StandardizedFlow:
        """
        Standardize a single flow record.
        
        Args:
            raw_data: Dict with name, quantity, unit, category
            
        Returns:
            StandardizedFlow
        """
        # Standardize name
        name = raw_data.get("name", "")
        std_name = self._standardize_name(name)
        
        # Standardize quantity
        quantity = float(raw_data.get("quantity", 0))
        unit = raw_data.get("unit", "kg")
        
        # Try to convert to standard units
        if self.unit_converter._detect_unit_type(unit) == "mass":
            quantity = self.unit_converter.to_kg(quantity, unit)
            unit = "kg"
        elif self.unit_converter._detect_unit_type(unit) == "energy":
            quantity = self.unit_converter.to_kwh(quantity, unit)
            unit = "kWh"
        
        # Standardize category
        category = raw_data.get("category", "input").lower()
        std_category = self.CATEGORY_MAPPING.get(category, category)
        
        return StandardizedFlow(
            name=std_name,
            quantity=quantity,
            unit=unit,
            category=std_category,
            subcategory=raw_data.get("subcategory", ""),
            source=raw_data.get("source", ""),
            uncertainty=float(raw_data.get("uncertainty", 0.1)),
            data_quality=raw_data.get("data_quality", "medium")
        )
    
    def standardize_batch(self, raw_data: List[Dict]) -> List[StandardizedFlow]:
        """Standardize multiple flow records."""
        return [self.standardize_flow(d) for d in raw_data]
    
    def _standardize_name(self, name: str) -> str:
        """Standardize substance name."""
        name_lower = name.lower().strip()
        return self.SUBSTANCE_MAPPING.get(name_lower, name)
    
    def validate_flow(self, flow: StandardizedFlow) -> Tuple[bool, List[str]]:
        """
        Validate a standardized flow.
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        if not flow.name:
            issues.append("Missing name")
        if flow.quantity < 0:
            issues.append("Negative quantity")
        if not flow.unit:
            issues.append("Missing unit")
        if flow.category not in ["input", "output", "emission_air", 
                                  "emission_water", "emission_soil"]:
            issues.append(f"Unknown category: {flow.category}")
        
        return len(issues) == 0, issues


if __name__ == "__main__":
    converter = UnitConverter()
    print(f"1 tonne = {converter.to_kg(1, 'tonne')} kg")
    print(f"1 MJ = {converter.to_kwh(1, 'MJ')} kWh")
    
    standardizer = DataStandardizer()
    test_flow = {"name": "carbon dioxide", "quantity": "100", "unit": "kg", "category": "emission to air"}
    result = standardizer.standardize_flow(test_flow)
    print(f"Standardized: {result}")
