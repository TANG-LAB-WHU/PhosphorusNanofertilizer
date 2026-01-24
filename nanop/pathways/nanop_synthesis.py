"""
NanoP Synthesis Pathway Module

Wet chemical synthesis of nano hydroxyapatite phosphorus fertilizer.
"""

from typing import Dict, List

from nanop.pathways.base_pathway import BasePathway
from nanop.lca.inventory import LifeCycleInventory


class NanoPSynthesisPathway(BasePathway):
    """
    Nano Hydroxyapatite Phosphorus Fertilizer Synthesis Pathway.
    
    Process: Wet chemical precipitation method
    Reaction: 10 Ca(OH)2 + 6 H3PO4 → Ca10(PO4)6(OH)2 + 18 H2O
    Alternative: 10 CaCl2 + 6 (NH4)2HPO4 + 8 NH4OH → Ca10(PO4)6(OH)2 + 20 NH4Cl
    
    The nano-sized hydroxyapatite (HAP) particles are produced through
    controlled precipitation, aging, washing, and drying processes.
    """
    
    @property
    def code(self) -> str:
        return "NanoP-Synth"
    
    @property
    def name(self) -> str:
        return "NanoP Wet Chemical Synthesis"
    
    @property
    def trl(self) -> int:
        return 7  # Demonstration in operational environment
    
    def _default_parameters(self) -> Dict[str, float]:
        """
        Default process parameters for nanoP synthesis.
        
        All values are per 1000 kg (1 tonne) of nanoP product.
        """
        return {
            # Stoichiometry (based on Ca10(PO4)6(OH)2, MW = 1004 g/mol)
            # Ca: 10 mol × 40 g/mol = 400 g per 1004 g HAP
            # P: 6 mol × 31 g/mol = 186 g per 1004 g HAP
            
            # Raw materials (kg per tonne nanoP)
            "cacl2_consumption": 1110,  # CaCl2 (10 mol × 111 g/mol per mol HAP)
            "h3po4_consumption": 587,   # H3PO4 (6 mol × 98 g/mol per mol HAP)
            "nh4oh_consumption": 340,   # NH4OH for pH control
            "water_consumption": 8000,  # Process water (kg)
            
            # Energy (per tonne nanoP)
            "electricity_kwh": 450,     # Mixing, pumping, filtration
            "thermal_energy_kwh": 800,  # Heating for reaction and drying
            
            # Process efficiency
            "calcium_conversion": 0.95,
            "phosphorus_recovery": 0.92,
            "product_purity": 0.98,
            
            # Emissions factors
            "co2_electricity": 0.475,   # kg CO2/kWh (global average grid)
            "co2_thermal": 0.185,       # kg CO2/kWh (natural gas)
            
            # Product yield
            "product_yield": 1000,      # kg nanoP per FU
        }
    
    def _build_inventory(self) -> LifeCycleInventory:
        """Build the life cycle inventory for nanoP synthesis."""
        p = self.parameters
        
        lci = LifeCycleInventory(
            process_name="NanoP Wet Chemical Synthesis",
            functional_unit="1 tonne NanoP",
            functional_unit_value=1000  # kg
        )
        
        # === INPUTS ===
        
        # Raw materials
        lci.add_input("Calcium chloride (CaCl2)", p["cacl2_consumption"], "kg",
                     source="Chemical supplier")
        lci.add_input("Phosphoric acid (H3PO4, 85%)", p["h3po4_consumption"], "kg",
                     source="Chemical supplier")
        lci.add_input("Ammonium hydroxide (NH4OH, 25%)", p["nh4oh_consumption"], "kg",
                     source="Chemical supplier")
        lci.add_input("Deionized water", p["water_consumption"], "kg",
                     source="On-site production")
        
        # Energy
        lci.add_input("Electricity", p["electricity_kwh"], "kWh",
                     source="Grid electricity")
        lci.add_input("Natural gas (thermal)", p["thermal_energy_kwh"], "kWh",
                     source="Natural gas network")
        
        # === OUTPUTS ===
        
        lci.add_output("Nano hydroxyapatite (NanoP)", p["product_yield"], "kg")
        
        # Byproducts
        # NH4Cl is a byproduct from the reaction
        nh4cl_produced = p["cacl2_consumption"] * 0.48  # Stoichiometric ratio
        lci.add_output("Ammonium chloride (NH4Cl)", nh4cl_produced, "kg")
        
        # === EMISSIONS ===
        
        # Air emissions
        # CO2 from electricity
        co2_electricity = p["electricity_kwh"] * p["co2_electricity"]
        lci.add_emission("CO2", co2_electricity, "kg", "air",
                        source="Electricity generation")
        
        # CO2 from thermal energy
        co2_thermal = p["thermal_energy_kwh"] * p["co2_thermal"]
        lci.add_emission("CO2", co2_thermal, "kg", "air",
                        source="Natural gas combustion")
        
        # NOx from natural gas combustion
        nox = p["thermal_energy_kwh"] * 0.00005  # 50 mg/kWh
        lci.add_emission("NOx", nox, "kg", "air",
                        source="Natural gas combustion")
        
        # Ammonia slip from process
        nh3_slip = p["nh4oh_consumption"] * 0.01  # 1% ammonia loss
        lci.add_emission("NH3", nh3_slip, "kg", "air",
                        source="Process losses")
        
        # Particulate matter from drying
        pm_drying = p["product_yield"] * 0.0001  # 0.01% product loss as PM
        lci.add_emission("PM2.5", pm_drying * 0.5, "kg", "air",
                        source="Drying process")
        lci.add_emission("PM10", pm_drying * 0.5, "kg", "air",
                        source="Drying process")
        
        # Water emissions
        # Phosphorus in wastewater (from incomplete reaction)
        p_loss = p["h3po4_consumption"] * 0.31 * (1 - p["phosphorus_recovery"])
        lci.add_emission("phosphorus", p_loss, "kg", "water",
                        source="Wastewater")
        
        # Chloride in wastewater
        cl_wastewater = p["cacl2_consumption"] * 0.01  # 1% not recovered
        lci.add_emission("chloride", cl_wastewater, "kg", "water",
                        source="Wastewater")
        
        # === AVOIDED PRODUCTS ===
        # NH4Cl byproduct can replace synthetic ammonium chloride
        # Credit for avoided production
        lci.add_avoided_product("Ammonium chloride production", nh4cl_produced * 0.5, "kg")
        
        return lci
    
    def get_capex_data(self) -> Dict:
        """Return CAPEX data for TEA."""
        # Scale based on capacity (base: 10,000 tonnes/year)
        scale_factor = (self.capacity / 10000) ** 0.6
        
        return {
            "equipment": [
                {
                    "name": "Precipitation Reactor (stirred tank)",
                    "base_cost": 250000 * scale_factor,
                    "type": "reactor",
                    "quantity": 2
                },
                {
                    "name": "Aging Tank",
                    "base_cost": 80000 * scale_factor,
                    "type": "tank",
                    "quantity": 3
                },
                {
                    "name": "Filter Press",
                    "base_cost": 150000 * scale_factor,
                    "type": "filter",
                    "quantity": 2
                },
                {
                    "name": "Spray Dryer",
                    "base_cost": 400000 * scale_factor,
                    "type": "dryer",
                    "quantity": 1
                },
                {
                    "name": "Ball Mill (particle sizing)",
                    "base_cost": 120000 * scale_factor,
                    "type": "default",
                    "quantity": 1
                },
                {
                    "name": "Heat Exchanger",
                    "base_cost": 60000 * scale_factor,
                    "type": "heat_exchanger",
                    "quantity": 2
                },
                {
                    "name": "DI Water System",
                    "base_cost": 100000 * scale_factor,
                    "type": "default",
                    "quantity": 1
                },
                {
                    "name": "Pumps and Piping",
                    "base_cost": 80000 * scale_factor,
                    "type": "pump",
                    "quantity": 1
                },
                {
                    "name": "Instrumentation & Control",
                    "base_cost": 150000 * scale_factor,
                    "type": "instrumentation",
                    "quantity": 1
                },
            ],
            "working_capital": 500000 * scale_factor,
            "contingency_pct": 0.15,
        }
    
    def get_opex_data(self) -> Dict:
        """Return OPEX data for TEA."""
        p = self.parameters
        
        return {
            "materials": [
                {"name": "CaCl2", "quantity": p["cacl2_consumption"], "price": 0.18},  # USD/kg
                {"name": "H3PO4 (85%)", "quantity": p["h3po4_consumption"], "price": 0.75},
                {"name": "NH4OH (25%)", "quantity": p["nh4oh_consumption"], "price": 0.25},
            ],
            "utilities": [
                {"name": "electricity", "quantity": p["electricity_kwh"], "price": 0.10},
                {"name": "natural_gas", "quantity": p["thermal_energy_kwh"], "price": 0.04},
                {"name": "deionized_water", "quantity": p["water_consumption"], "price": 0.01},
            ],
            "labor": {
                "operators": 6,
                "annual_cost": 45000,  # USD/operator/year (global average)
            },
            "maintenance": 25,  # USD per tonne (from CAPEX percentage)
            "other": 10,  # USD per tonne (waste disposal, quality control)
        }
    
    def get_products(self) -> List[Dict]:
        """Return product outputs with prices."""
        p = self.parameters
        
        # NH4Cl byproduct quantity
        nh4cl_produced = p["cacl2_consumption"] * 0.48 * 0.5  # 50% recovery
        
        return [
            {
                "name": "Nano Hydroxyapatite P Fertilizer",
                "quantity": p["product_yield"],
                "price": 1.50,  # USD/kg (premium price for nano fertilizer)
                "unit": "kg"
            },
            {
                "name": "Ammonium Chloride (byproduct)",
                "quantity": nh4cl_produced,
                "price": 0.15,  # USD/kg
                "unit": "kg"
            },
        ]


# Convenience function for pathway creation
def create_nanop_pathway(
    country: str = "global",
    year: int = 2024,
    capacity_tonnes: float = 10000
) -> NanoPSynthesisPathway:
    """Create a NanoP synthesis pathway with specified parameters."""
    return NanoPSynthesisPathway(
        country=country,
        year=year,
        capacity_tonnes=capacity_tonnes
    )


if __name__ == "__main__":
    # Example usage
    pathway = NanoPSynthesisPathway(country="China", capacity_tonnes=10000)
    
    print(f"Pathway: {pathway.name} [{pathway.code}]")
    print(f"TRL: {pathway.trl}")
    print(f"Capacity: {pathway.capacity} tonnes/year")
    print(f"\nParameters: {pathway.parameters}")
    
    inv = pathway.inventory.to_dict()
    print(f"\nInputs: {len(inv['inputs'])}")
    print(f"Outputs: {len(inv['outputs'])}")
    print(f"Air emissions: {len(inv['emissions_air'])}")
