"""
Tests for TEA module.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nanop.tea import TEAEngine, TEAResult, CAPEXCalculator, OPEXCalculator
from nanop.tea.external_cost import ExternalCostCalculator
from nanop.tea.revenue import calculate_revenue
from nanop.pathways import get_pathway


class TestCAPEXCalculator:
    """Test CAPEXCalculator class."""
    
    def test_initialization(self):
        calc = CAPEXCalculator({})
        assert calc is not None
    
    def test_calculate_capex(self):
        calc = CAPEXCalculator({
            "discount_rate": 0.05,
            "lifetime_years": 20
        })
        
        capex_data = {
            "equipment": [
                {"name": "Reactor", "base_cost": 100000, "type": "reactor", "quantity": 1}
            ],
            "working_capital": 50000,
            "contingency_pct": 0.1
        }
        
        result = calc.calculate(capex_data)
        assert result["total"] > 0
        assert result["annualized"] > 0


class TestOPEXCalculator:
    """Test OPEXCalculator class."""
    
    def test_initialization(self):
        calc = OPEXCalculator({}, country="global")
        assert calc is not None
    
    def test_regional_labor_factor(self):
        calc_global = OPEXCalculator({}, country="global")
        calc_china = OPEXCalculator({}, country="china")
        
        assert calc_china.LABOR_FACTORS["china"] < calc_global.LABOR_FACTORS["global"]
    
    def test_calculate_opex(self):
        calc = OPEXCalculator({}, country="china")
        
        opex_data = {
            "materials": [
                {"name": "CaCl2", "quantity": 100, "price": 0.2}
            ],
            "utilities": [
                {"name": "electricity", "quantity": 500, "price": 0.1}
            ],
            "labor": {"per_tonne_cost": 27.0},
            "maintenance": 10,
            "other": 5
        }
        
        result = calc.calculate(opex_data, 1000)
        assert result["total"] > 0
        assert "breakdown" in result


class TestExternalCostCalculator:
    """Test ExternalCostCalculator class."""
    
    def test_initialization(self):
        calc = ExternalCostCalculator()
        assert calc is not None
    
    def test_calculate_external_cost(self):
        calc = ExternalCostCalculator()
        
        emissions = {
            "emissions_air": [
                {"name": "CO2", "quantity": 100}
            ]
        }
        
        result = calc.calculate(emissions)
        assert result["total"] > 0


class TestRevenue:
    """Test revenue calculation."""
    
    def test_calculate_revenue(self):
        products = [
            {"name": "Product A", "quantity": 1000, "price": 1.5}
        ]
        
        result = calculate_revenue(products)
        assert result["total"] == 1500
        assert "breakdown" in result


class TestTEAEngine:
    """Test TEAEngine class."""
    
    def test_engine_initialization(self):
        engine = TEAEngine()
        assert engine is not None
    
    def test_calculate_with_pathway(self):
        engine = TEAEngine(country="China")
        pathway = get_pathway("NanoP-Synth")
        
        result = engine.calculate(pathway)
        
        assert isinstance(result, TEAResult)
        assert result.capex_total > 0
        assert result.opex_total > 0
    
    def test_calculate_npv(self):
        engine = TEAEngine(country="China")
        pathway = get_pathway("NanoP-Synth")
        
        result = engine.calculate_npv(pathway, project_lifetime=15)
        
        assert "npv" in result
        assert "payback_years" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
