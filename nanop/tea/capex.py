"""
CAPEX Calculator Module

Calculates capital expenditure for nanoP production facilities.
"""

from typing import Any, Dict, List, Optional


class CAPEXCalculator:
    """
    Capital Expenditure Calculator.
    
    Calculates total and annualized CAPEX for nanoP production equipment.
    Uses Lang factors for installation costs.
    """
    
    # Lang factors for different equipment types
    LANG_FACTORS = {
        "reactor": 3.5,  # For fluid processing
        "heat_exchanger": 3.2,
        "filter": 2.8,
        "dryer": 3.0,
        "pump": 2.5,
        "tank": 2.0,
        "instrumentation": 1.5,
        "default": 3.0,
    }
    
    # Scale exponent for capacity scaling
    SCALE_EXPONENTS = {
        "reactor": 0.6,
        "filter": 0.65,
        "dryer": 0.7,
        "pump": 0.5,
        "tank": 0.7,
        "default": 0.6,
    }
    
    def __init__(self, params: Dict):
        """
        Initialize CAPEX calculator.
        
        Args:
            params: Economic parameters (discount_rate, lifetime_years, etc.)
        """
        self.params = params
    
    def calculate_total(self, capex_data: Dict) -> float:
        """
        Calculate total CAPEX from equipment data.
        
        Args:
            capex_data: Dict with equipment items and costs
            
        Returns:
            Total CAPEX in USD
        """
        total = 0.0
        
        equipment = capex_data.get("equipment", [])
        for item in equipment:
            name = item.get("name", "")
            base_cost = item.get("base_cost", 0)
            quantity = item.get("quantity", 1)
            equipment_type = item.get("type", "default")
            
            # Apply Lang factor for installation
            lang_factor = self.LANG_FACTORS.get(equipment_type, self.LANG_FACTORS["default"])
            installed_cost = base_cost * lang_factor * quantity
            
            total += installed_cost
        
        # Add additional CAPEX items
        working_capital = capex_data.get("working_capital", 0)
        total += working_capital
        
        contingency_pct = capex_data.get("contingency_pct", 0.15)
        total *= (1 + contingency_pct)
        
        return total
    
    def annualize(
        self,
        capex_total: float,
        discount_rate: float,
        lifetime: int
    ) -> float:
        """
        Calculate annualized CAPEX using capital recovery factor.
        
        Args:
            capex_total: Total capital expenditure
            discount_rate: Annual discount rate (e.g., 0.08 for 8%)
            lifetime: Project lifetime in years
            
        Returns:
            Annualized CAPEX in USD/year
        """
        if discount_rate == 0:
            return capex_total / lifetime
        
        # Capital Recovery Factor (CRF)
        crf = (discount_rate * (1 + discount_rate) ** lifetime) / \
              ((1 + discount_rate) ** lifetime - 1)
        
        return capex_total * crf
    
    def scale_equipment(
        self,
        base_cost: float,
        base_capacity: float,
        target_capacity: float,
        equipment_type: str = "default"
    ) -> float:
        """
        Scale equipment cost based on capacity using power law.
        
        Args:
            base_cost: Cost at base capacity
            base_capacity: Base capacity
            target_capacity: Target capacity
            equipment_type: Type for scale exponent lookup
            
        Returns:
            Scaled cost
        """
        exponent = self.SCALE_EXPONENTS.get(equipment_type, self.SCALE_EXPONENTS["default"])
        return base_cost * (target_capacity / base_capacity) ** exponent
    
    def get_breakdown(self, capex_data: Dict) -> Dict[str, float]:
        """
        Get detailed CAPEX breakdown.
        
        Args:
            capex_data: Dict with equipment items and costs
            
        Returns:
            Dict mapping item name to installed cost
        """
        breakdown = {}
        
        equipment = capex_data.get("equipment", [])
        for item in equipment:
            name = item.get("name", "Unknown")
            base_cost = item.get("base_cost", 0)
            quantity = item.get("quantity", 1)
            equipment_type = item.get("type", "default")
            
            lang_factor = self.LANG_FACTORS.get(equipment_type, self.LANG_FACTORS["default"])
            installed_cost = base_cost * lang_factor * quantity
            
            breakdown[name] = installed_cost
        
        if "working_capital" in capex_data:
            breakdown["working_capital"] = capex_data["working_capital"]
        
        return breakdown


if __name__ == "__main__":
    # Example usage
    calc = CAPEXCalculator({"discount_rate": 0.08, "lifetime_years": 15})
    
    capex_data = {
        "equipment": [
            {"name": "Reactor", "base_cost": 150000, "type": "reactor", "quantity": 2},
            {"name": "Filter Press", "base_cost": 80000, "type": "filter", "quantity": 1},
            {"name": "Spray Dryer", "base_cost": 200000, "type": "dryer", "quantity": 1},
        ],
        "working_capital": 100000,
        "contingency_pct": 0.15,
    }
    
    total = calc.calculate_total(capex_data)
    annualized = calc.annualize(total, 0.08, 15)
    
    print(f"Total CAPEX: ${total:,.0f}")
    print(f"Annualized CAPEX: ${annualized:,.0f}/year")
    print(f"Breakdown: {calc.get_breakdown(capex_data)}")
