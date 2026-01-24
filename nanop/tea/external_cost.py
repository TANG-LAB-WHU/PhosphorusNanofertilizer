"""
External Cost Calculator Module

Monetizes environmental damages from emissions using shadow prices.
"""

from typing import Any, Dict, Optional
from pathlib import Path
import yaml


class ExternalCostCalculator:
    """
    External Cost Calculator.
    
    Converts environmental emissions to monetary costs using shadow prices.
    Based on environmental economics principles (Pigouvian taxation).
    """
    
    # Default shadow prices (USD per kg) - fallback values
    DEFAULT_PRICES = {
        "CO2": 0.130,      # ~130 USD/tonne
        "CH4": 3.87,       # 29.8 * 0.130
        "N2O": 35.5,       # 273 * 0.130
        "SO2": 11.88,
        "NOx": 8.64,
        "PM2.5": 108.0,
        "PM10": 43.2,
        "NH3": 18.36,
        "phosphorus": 12.96,
        "nitrogen": 4.86,
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize external cost calculator.
        
        Args:
            config_path: Path to config directory with shadow_prices.yaml
        """
        self.prices = {}
        self._load_prices(config_path)
    
    def _load_prices(self, config_path: Optional[Path]) -> None:
        """Load shadow prices from YAML file."""
        prices_file = None
        
        if config_path:
            prices_file = Path(config_path) / "shadow_prices.yaml"
        else:
            default_paths = [
                Path("./config/shadow_prices.yaml"),
                Path(__file__).parent.parent.parent / "config" / "shadow_prices.yaml",
            ]
            for path in default_paths:
                if path.exists():
                    prices_file = path
                    break
        
        if prices_file and prices_file.exists():
            try:
                with open(prices_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    
                    # Extract central values from direct_substances
                    if "direct_substances" in data:
                        for substance, values in data["direct_substances"].items():
                            if isinstance(values, dict):
                                self.prices[substance] = values.get("central", 0)
                            else:
                                self.prices[substance] = values
                    else:
                        self.prices = self.DEFAULT_PRICES.copy()
                        
            except Exception as e:
                print(f"Warning: Could not load shadow prices: {e}")
                self.prices = self.DEFAULT_PRICES.copy()
        else:
            self.prices = self.DEFAULT_PRICES.copy()
    
    def calculate(self, emissions: Dict) -> Dict:
        """
        Calculate external costs from emissions.
        
        Args:
            emissions: Dict with emissions_air, emissions_water, emissions_soil
            
        Returns:
            Dict with total external cost and breakdown
        """
        breakdown = {}
        total = 0.0
        
        # Process emissions from all compartments
        for compartment in ["emissions_air", "emissions_water", "emissions_soil"]:
            for emission in emissions.get(compartment, []):
                name = emission.get("name", "")
                quantity = emission.get("quantity", 0)
                unit = emission.get("unit", "kg")
                
                # Get shadow price
                price = self._get_price(name)
                
                if price > 0:
                    # Convert to kg if necessary
                    if unit == "g":
                        quantity = quantity / 1000
                    elif unit == "mg":
                        quantity = quantity / 1000000
                    elif unit == "tonne":
                        quantity = quantity * 1000
                    
                    cost = quantity * price
                    total += cost
                    breakdown[f"{compartment}:{name}"] = cost
        
        # Avoided products reduce external cost
        for avoided in emissions.get("avoided_products", []):
            name = avoided.get("name", "")
            quantity = avoided.get("quantity", 0)
            price = self._get_price(name)
            
            if price > 0:
                cost = quantity * price
                total -= cost
                breakdown[f"avoided:{name}"] = -cost
        
        return {
            "total": total,
            "breakdown": breakdown
        }
    
    def _get_price(self, substance: str) -> float:
        """Get shadow price for a substance."""
        # Exact match
        if substance in self.prices:
            return self.prices[substance]
        
        # Case-insensitive match
        substance_lower = substance.lower()
        for key, value in self.prices.items():
            if key.lower() == substance_lower:
                return value
        
        # Partial match
        for key, value in self.prices.items():
            if key.lower() in substance_lower or substance_lower in key.lower():
                return value
        
        return 0.0
    
    def update_prices(self, prices: Dict) -> None:
        """Update shadow prices."""
        if "direct_substances" in prices:
            for substance, values in prices["direct_substances"].items():
                if isinstance(values, dict):
                    self.prices[substance] = values.get("central", 0)
                else:
                    self.prices[substance] = values
        else:
            self.prices.update(prices)
    
    def get_price(self, substance: str) -> float:
        """Get shadow price for a substance (public method)."""
        return self._get_price(substance)


if __name__ == "__main__":
    # Example usage
    calc = ExternalCostCalculator()
    
    emissions = {
        "emissions_air": [
            {"name": "CO2", "quantity": 380, "unit": "kg"},
            {"name": "NH3", "quantity": 5, "unit": "kg"},
            {"name": "PM2.5", "quantity": 0.5, "unit": "kg"},
        ],
        "emissions_water": [
            {"name": "phosphorus", "quantity": 0.1, "unit": "kg"},
        ],
    }
    
    result = calc.calculate(emissions)
    print(f"Total external cost: ${result['total']:.2f}")
    print(f"Breakdown: {result['breakdown']}")
