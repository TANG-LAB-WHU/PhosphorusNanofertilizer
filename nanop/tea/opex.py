"""
OPEX Calculator Module

Calculates operating expenditure for nanoP production.
"""

from typing import Any, Dict, List, Optional


class OPEXCalculator:
    """
    Operating Expenditure Calculator.
    
    Calculates OPEX components: materials, utilities, labor, maintenance.
    """
    
    # Default utility prices (USD)
    DEFAULT_UTILITY_PRICES = {
        "electricity": 0.10,  # USD/kWh
        "natural_gas": 0.04,  # USD/kWh thermal
        "steam": 0.025,  # USD/kg
        "water": 0.002,  # USD/kg
        "deionized_water": 0.01,  # USD/kg
        "cooling_water": 0.0005,  # USD/kg
        "compressed_air": 0.02,  # USD/Nm3
    }
    
    # Regional labor cost factors
    LABOR_FACTORS = {
        "global": 1.0,
        "china": 0.35,
        "usa": 1.5,
        "eu": 1.2,
        "india": 0.25,
    }
    
    def __init__(self, params: Dict, country: str = "global"):
        """
        Initialize OPEX calculator.
        
        Args:
            params: Economic parameters
            country: Country for labor cost adjustment
        """
        self.params = params
        self.country = country.lower()
        self.utility_prices = self.DEFAULT_UTILITY_PRICES.copy()
    
    def calculate(self, opex_data: Dict, functional_unit_kg: float) -> Dict:
        """
        Calculate total OPEX per functional unit.
        
        Args:
            opex_data: Dict with materials, utilities, labor data
            functional_unit_kg: Functional unit in kg
            
        Returns:
            Dict with total OPEX and breakdown
        """
        breakdown = {}
        total = 0.0
        
        # Materials cost
        materials_cost = self._calculate_materials(opex_data.get("materials", []))
        breakdown["materials"] = materials_cost
        total += materials_cost
        
        # Utilities cost
        utilities_cost = self._calculate_utilities(opex_data.get("utilities", []))
        breakdown["utilities"] = utilities_cost
        total += utilities_cost
        
        # Labor cost
        labor_cost = self._calculate_labor(opex_data.get("labor", {}))
        breakdown["labor"] = labor_cost
        total += labor_cost
        
        # Maintenance (typically % of CAPEX per year)
        maintenance_cost = opex_data.get("maintenance", 0)
        breakdown["maintenance"] = maintenance_cost
        total += maintenance_cost
        
        # Other costs
        other_cost = opex_data.get("other", 0)
        breakdown["other"] = other_cost
        total += other_cost
        
        return {
            "total": total,
            "breakdown": breakdown
        }
    
    def _calculate_materials(self, materials: List[Dict]) -> float:
        """Calculate materials cost."""
        total = 0.0
        
        for material in materials:
            quantity = material.get("quantity", 0)
            price = material.get("price", 0)
            total += quantity * price
        
        return total
    
    def _calculate_utilities(self, utilities: List[Dict]) -> float:
        """Calculate utilities cost."""
        total = 0.0
        
        for utility in utilities:
            name = utility.get("name", "").lower()
            quantity = utility.get("quantity", 0)
            
            # Use provided price or default
            price = utility.get("price")
            if price is None:
                # Try to find in default prices
                price = self.utility_prices.get(name, 0)
                if price == 0:
                    # Try partial match
                    for key, val in self.utility_prices.items():
                        if key in name or name in key:
                            price = val
                            break
            
            total += quantity * price
        
        return total
    
    def _calculate_labor(self, labor_data: Dict) -> float:
        """Calculate labor cost with regional adjustment."""
        base_cost = labor_data.get("annual_cost", 0)
        n_operators = labor_data.get("operators", 0)
        
        # Apply regional factor
        factor = self.LABOR_FACTORS.get(self.country, 1.0)
        
        return base_cost * n_operators * factor
    
    def update_utility_prices(self, prices: Dict) -> None:
        """Update utility prices."""
        self.utility_prices.update(prices)


if __name__ == "__main__":
    # Example usage
    calc = OPEXCalculator({}, country="china")
    
    opex_data = {
        "materials": [
            {"name": "CaCl2", "quantity": 650, "price": 0.15},  # kg, USD/kg
            {"name": "H3PO4", "quantity": 580, "price": 0.80},
            {"name": "NH4OH", "quantity": 120, "price": 0.30},
        ],
        "utilities": [
            {"name": "electricity", "quantity": 800},  # kWh
            {"name": "deionized_water", "quantity": 5000},  # kg
        ],
        "labor": {
            "operators": 3,
            "annual_cost": 40000,  # USD/operator/year, will be adjusted
        },
        "maintenance": 10,  # USD per tonne (from annual maintenance / throughput)
    }
    
    result = calc.calculate(opex_data, 1000)
    print(f"Total OPEX: ${result['total']:.2f}/tonne")
    print(f"Breakdown: {result['breakdown']}")
