"""
Characterization Factors Module

Loads and provides access to characterization factors for LCIA.
"""

from typing import Any, Dict, Optional
from pathlib import Path
import yaml


class CharacterizationFactors:
    """
    Manages characterization factors for Life Cycle Impact Assessment.
    
    Loads factors from YAML configuration and provides lookup methods
    for calculating impacts from inventory flows.
    """
    
    # Default characterization factors (fallback)
    DEFAULT_FACTORS = {
        "climate_change": {
            "CO2": 1.0,
            "CH4": 29.8,
            "N2O": 273.0,
        },
        "acidification": {
            "SO2": 1.31,
            "NOx": 0.74,
            "NH3": 1.96,
        },
        "eutrophication_fresh": {
            "PO4": 0.33,
            "P": 1.0,
            "phosphorus": 1.0,
        },
        "eutrophication_marine": {
            "NOx": 0.039,
            "NH3": 0.092,
            "N": 1.0,
            "nitrogen": 1.0,
        },
        "human_toxicity_cancer": {
            "chromium_vi": 1.46e-5,
            "arsenic": 1.30e-5,
        },
        "human_toxicity_noncancer": {
            "lead": 4.91e-7,
            "mercury": 3.17e-5,
        },
        "ecotoxicity_freshwater": {
            "copper": 5.15e+3,
            "zinc": 1.45e+3,
        },
        "particulate_matter": {
            "PM2.5": 6.51e-4,
            "PM10": 2.45e-4,
        },
        "resource_depletion": {
            "phosphorus": 2.3e-2,
        },
        "water_use": {
            "water": 1.0,
        },
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize characterization factors.
        
        Args:
            config_path: Path to config directory containing impact_factors.yaml
        """
        self.factors = {}
        self._load_factors(config_path)
    
    def _load_factors(self, config_path: Optional[Path]) -> None:
        """Load characterization factors from YAML file."""
        factors_file = None
        
        if config_path:
            factors_file = Path(config_path) / "impact_factors.yaml"
        else:
            # Try default locations
            default_paths = [
                Path("./config/impact_factors.yaml"),
                Path(__file__).parent.parent.parent / "config" / "impact_factors.yaml",
            ]
            for path in default_paths:
                if path.exists():
                    factors_file = path
                    break
        
        if factors_file and factors_file.exists():
            try:
                with open(factors_file, "r", encoding="utf-8") as f:
                    self.factors = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load impact factors from {factors_file}: {e}")
                self.factors = self.DEFAULT_FACTORS.copy()
        else:
            self.factors = self.DEFAULT_FACTORS.copy()
    
    def get_factors(self, impact_category: str) -> Dict[str, float]:
        """
        Get characterization factors for an impact category.
        
        Args:
            impact_category: Name of impact category
            
        Returns:
            Dict mapping substance names to characterization factors
        """
        return self.factors.get(impact_category, {})
    
    def get_factor(
        self,
        impact_category: str,
        substance: str,
        default: float = 0.0
    ) -> float:
        """
        Get characterization factor for a specific substance.
        
        Args:
            impact_category: Name of impact category
            substance: Name of substance
            default: Default value if not found
            
        Returns:
            Characterization factor value
        """
        category_factors = self.factors.get(impact_category, {})
        
        # Try exact match first
        if substance in category_factors:
            return category_factors[substance]
        
        # Try case-insensitive match
        substance_lower = substance.lower()
        for key, value in category_factors.items():
            if key.lower() == substance_lower:
                return value
        
        return default
    
    def list_categories(self) -> list:
        """List all available impact categories."""
        return list(self.factors.keys())
    
    def list_substances(self, impact_category: str) -> list:
        """List substances with factors for an impact category."""
        return list(self.factors.get(impact_category, {}).keys())


if __name__ == "__main__":
    # Example usage
    cf = CharacterizationFactors()
    
    print("Available categories:", cf.list_categories())
    print("\nClimate change factors:", cf.get_factors("climate_change"))
    print("\nCO2 GWP:", cf.get_factor("climate_change", "CO2"))
