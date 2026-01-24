"""
Tests for Pathways module.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nanop.pathways import (
    BasePathway,
    NanoPSynthesisPathway,
    get_pathway,
    list_pathways,
    PATHWAY_REGISTRY
)


class TestPathwayRegistry:
    """Test pathway registry functions."""
    
    def test_list_pathways(self):
        pathways = list_pathways()
        assert isinstance(pathways, list)
        assert "NanoP-Synth" in pathways
    
    def test_get_pathway(self):
        pathway = get_pathway("NanoP-Synth")
        assert pathway is not None
        assert pathway.code == "NanoP-Synth"
    
    def test_get_unknown_pathway(self):
        with pytest.raises(ValueError):
            get_pathway("Unknown-Pathway")


class TestNanoPSynthesisPathway:
    """Test NanoPSynthesisPathway class."""
    
    def test_initialization(self):
        pathway = NanoPSynthesisPathway()
        assert pathway.code == "NanoP-Synth"
        assert pathway.name == "NanoP Wet Chemical Synthesis"
    
    def test_trl(self):
        pathway = NanoPSynthesisPathway()
        assert pathway.trl == 7
    
    def test_capacity(self):
        pathway = NanoPSynthesisPathway(capacity_tonnes=5000)
        assert pathway.capacity == 5000
    
    def test_country(self):
        pathway = NanoPSynthesisPathway(country="China")
        assert pathway.country == "China"
    
    def test_inventory_has_inputs(self):
        pathway = NanoPSynthesisPathway()
        inv = pathway.inventory.to_dict()
        assert len(inv["inputs"]) > 0
    
    def test_inventory_has_outputs(self):
        pathway = NanoPSynthesisPathway()
        inv = pathway.inventory.to_dict()
        assert len(inv["outputs"]) > 0
    
    def test_inventory_has_emissions(self):
        pathway = NanoPSynthesisPathway()
        inv = pathway.inventory.to_dict()
        assert len(inv["emissions_air"]) > 0
    
    def test_capex_data(self):
        pathway = NanoPSynthesisPathway()
        capex = pathway.get_capex_data()
        assert "equipment" in capex
        assert len(capex["equipment"]) > 0
    
    def test_opex_data(self):
        pathway = NanoPSynthesisPathway()
        opex = pathway.get_opex_data()
        assert "materials" in opex
        assert "utilities" in opex
        assert "labor" in opex
    
    def test_products(self):
        pathway = NanoPSynthesisPathway()
        products = pathway.get_products()
        assert len(products) >= 1
        assert products[0]["name"] == "Nano Hydroxyapatite P Fertilizer"
    
    def test_to_dict(self):
        pathway = NanoPSynthesisPathway()
        data = pathway.to_dict()
        assert "code" in data
        assert "name" in data
        assert "parameters" in data
        assert "inventory" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
