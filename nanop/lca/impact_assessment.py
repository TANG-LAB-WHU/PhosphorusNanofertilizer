"""
Impact Assessment Module

Calculates environmental impacts from life cycle inventory data.
"""

from typing import Any, Dict, List, Optional
from nanop.lca.characterization import CharacterizationFactors


class ImpactAssessment:
    """
    Life Cycle Impact Assessment (LCIA) calculator.
    
    Converts inventory emissions to environmental impact scores
    using characterization factors.
    """
    
    # Normalization references (per capita annual, EU27 2010)
    NORMALIZATION_REFS = {
        "climate_change": 8100,  # kg CO2-eq/person/year
        "acidification": 47,  # mol H+-eq
        "eutrophication_fresh": 1.9,  # kg P-eq
        "eutrophication_marine": 17,  # kg N-eq
        "human_toxicity_cancer": 3.5e-5,  # CTUh
        "human_toxicity_noncancer": 4.3e-4,  # CTUh
        "ecotoxicity_freshwater": 8900,  # CTUe
        "particulate_matter": 6.8e-4,  # disease incidence
        "resource_depletion": 0.12,  # kg Sb-eq
        "water_use": 73,  # m3 water-eq
    }
    
    def __init__(self, characterization: CharacterizationFactors):
        """
        Initialize impact assessment.
        
        Args:
            characterization: CharacterizationFactors instance
        """
        self.characterization = characterization
    
    def calculate(self, inventory: Dict) -> Dict[str, float]:
        """
        Calculate environmental impacts from inventory.
        
        Args:
            inventory: Inventory dict with emissions_air, emissions_water, etc.
            
        Returns:
            Dict mapping impact category to impact value
        """
        impacts = {}
        
        categories = self.characterization.list_categories()
        
        for category in categories:
            total_impact = 0.0
            
            # Process emissions from all compartments
            for compartment in ["emissions_air", "emissions_water", "emissions_soil"]:
                emissions = inventory.get(compartment, [])
                for emission in emissions:
                    name = emission.get("name", "")
                    quantity = emission.get("quantity", 0)
                    
                    # Get characterization factor
                    cf = self.characterization.get_factor(category, name)
                    
                    if cf != 0:
                        total_impact += quantity * cf
            
            # Subtract avoided products (credits)
            for avoided in inventory.get("avoided_products", []):
                name = avoided.get("name", "")
                quantity = avoided.get("quantity", 0)
                cf = self.characterization.get_factor(category, name)
                
                if cf != 0:
                    total_impact -= quantity * cf
            
            impacts[category] = total_impact
        
        return impacts
    
    def normalize(self, impacts: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize impacts to per-capita reference.
        
        Args:
            impacts: Dict of impact category to impact value
            
        Returns:
            Normalized impacts (dimensionless)
        """
        normalized = {}
        
        for category, value in impacts.items():
            ref = self.NORMALIZATION_REFS.get(category, 1.0)
            normalized[category] = value / ref if ref != 0 else 0
        
        return normalized
    
    def weight(
        self,
        normalized_impacts: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate weighted single score.
        
        Args:
            normalized_impacts: Normalized impact values
            weights: Optional weights per category (default: equal)
            
        Returns:
            Weighted single score
        """
        if weights is None:
            # Equal weighting
            n_categories = len(normalized_impacts)
            weights = {cat: 1.0 / n_categories for cat in normalized_impacts}
        
        total = 0.0
        for category, value in normalized_impacts.items():
            weight = weights.get(category, 0)
            total += value * weight
        
        return total
    
    def get_contribution(
        self,
        inventory: Dict,
        impact_category: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze contribution of individual flows to an impact.
        
        Args:
            inventory: Inventory dict
            impact_category: Target impact category
            
        Returns:
            Nested dict: {compartment: {substance: contribution%}}
        """
        contributions = {}
        total_impact = 0.0
        
        # First pass: calculate total
        for compartment in ["emissions_air", "emissions_water", "emissions_soil"]:
            for emission in inventory.get(compartment, []):
                name = emission.get("name", "")
                quantity = emission.get("quantity", 0)
                cf = self.characterization.get_factor(impact_category, name)
                total_impact += quantity * cf
        
        if total_impact == 0:
            return contributions
        
        # Second pass: calculate contributions
        for compartment in ["emissions_air", "emissions_water", "emissions_soil"]:
            contributions[compartment] = {}
            for emission in inventory.get(compartment, []):
                name = emission.get("name", "")
                quantity = emission.get("quantity", 0)
                cf = self.characterization.get_factor(impact_category, name)
                
                if cf != 0:
                    contribution = (quantity * cf / total_impact) * 100
                    contributions[compartment][name] = contribution
        
        return contributions


if __name__ == "__main__":
    # Example usage
    from nanop.lca.characterization import CharacterizationFactors
    
    cf = CharacterizationFactors()
    ia = ImpactAssessment(cf)
    
    # Sample inventory
    inventory = {
        "emissions_air": [
            {"name": "CO2", "quantity": 380, "unit": "kg"},
            {"name": "NH3", "quantity": 5, "unit": "kg"},
        ],
        "emissions_water": [
            {"name": "phosphorus", "quantity": 0.5, "unit": "kg"},
        ],
    }
    
    impacts = ia.calculate(inventory)
    print("Impacts:", impacts)
    
    normalized = ia.normalize(impacts)
    print("Normalized:", normalized)
