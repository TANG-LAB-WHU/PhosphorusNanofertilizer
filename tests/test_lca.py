"""
Tests for LCA module.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nanop.lca import LCAEngine, LCAResult, LifeCycleInventory, Flow
from nanop.lca.characterization import CharacterizationFactors
from nanop.lca.impact_assessment import ImpactAssessment
from nanop.pathways import get_pathway


class TestFlow:
    """Test Flow dataclass."""
    
    def test_flow_creation(self):
        flow = Flow(name="CO2", quantity=100.0, unit="kg")
        assert flow.name == "CO2"
        assert flow.quantity == 100.0
        assert flow.unit == "kg"
    
    def test_flow_with_uncertainty(self):
        flow = Flow(
            name="electricity",
            quantity=500.0,
            unit="kWh",
            uncertainty=0.1
        )
        assert flow.uncertainty == 0.1


class TestLifeCycleInventory:
    """Test LifeCycleInventory class."""
    
    def test_inventory_creation(self):
        lci = LifeCycleInventory(
            process_name="Test Process",
            functional_unit="1 kg product"
        )
        assert lci.process_name == "Test Process"
        assert len(lci.inputs) == 0
    
    def test_add_input(self):
        lci = LifeCycleInventory(process_name="Test")
        lci.add_input("Material A", 10.0, "kg")
        assert len(lci.inputs) == 1
        assert lci.inputs[0].name == "Material A"
    
    def test_add_emission(self):
        lci = LifeCycleInventory(process_name="Test")
        lci.add_emission("CO2", 50.0, "kg", "air")
        assert len(lci.emissions_air) == 1
    
    def test_scale_inventory(self):
        lci = LifeCycleInventory(
            process_name="Test",
            functional_unit_value=100  # base: 100 kg
        )
        lci.add_input("Material", 10.0, "kg")
        
        scaled = lci.scale_to(1000)  # scale to 1000 kg
        assert scaled.inputs[0].quantity == 100.0  # 10 * (1000/100)
    
    def test_to_dict(self):
        lci = LifeCycleInventory(process_name="Test")
        lci.add_input("A", 1.0, "kg")
        lci.add_output("B", 2.0, "kg")
        
        result = lci.to_dict()
        assert "inputs" in result
        assert "outputs" in result


class TestLCAEngine:
    """Test LCAEngine class."""
    
    def test_engine_initialization(self):
        engine = LCAEngine()
        assert engine is not None
        assert len(engine.IMPACT_CATEGORIES) > 0
    
    def test_calculate_with_pathway(self):
        engine = LCAEngine()
        pathway = get_pathway("NanoP-Synth")
        
        result = engine.calculate(pathway)
        
        assert isinstance(result, LCAResult)
        assert "climate_change" in result.impacts
        assert result.impacts["climate_change"] > 0
    
    def test_calculate_functional_unit_scaling(self):
        engine = LCAEngine()
        pathway = get_pathway("NanoP-Synth")
        
        result_1 = engine.calculate(pathway, functional_unit_value=1.0)
        result_2 = engine.calculate(pathway, functional_unit_value=2.0)
        
        # Impacts should scale linearly
        assert abs(result_2.impacts["climate_change"] - 
                   2 * result_1.impacts["climate_change"]) < 0.01


class TestCharacterizationFactors:
    """Test CharacterizationFactors class."""
    
    def test_load_factors(self):
        cf = CharacterizationFactors()
        assert cf is not None
    
    def test_get_factor(self):
        cf = CharacterizationFactors()
        factor = cf.get_factor("CO2", "climate_change")
        assert factor == 1.0  # CO2 has GWP of 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
