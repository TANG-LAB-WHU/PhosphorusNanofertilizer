"""
NanoP LCA-TEA Main Entry Point

Demonstrates the integrated assessment workflow:
1. Pathway initialization
2. LCA (Environmental Impact)
3. TEA (Economic Assessment)
4. Results interpretation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from nanop import LCAEngine, TEAEngine, get_pathway, list_pathways
from nanop.utils.currency import format_currency


def run_integrated_analysis():
    """Run integrated LCA-TEA analysis for NanoP production."""
    
    print("=" * 70)
    print("   NANO HYDROXYAPATITE PHOSPHORUS FERTILIZER (NanoP) LCA-TEA ANALYSIS")
    print("=" * 70)
    
    # 1. Initialize Engines
    print("\n[1] Initializing analysis engines...")
    lca_engine = LCAEngine()
    tea_engine = TEAEngine(country="China")
    
    # 2. List Available Pathways
    print("\n[2] Available pathways:")
    for code in list_pathways():
        print(f"    - {code}")
    
    # 3. Select and Configure Pathway
    print("\n[3] Configuring NanoP synthesis pathway...")
    pathway = get_pathway(
        "NanoP-Synth",
        country="China",
        year=2024,
        capacity_tonnes=10000  # 10,000 tonnes/year
    )
    
    print(f"    Pathway: {pathway.name}")
    print(f"    Code: {pathway.code}")
    print(f"    TRL: {pathway.trl}")
    print(f"    Annual capacity: {pathway.capacity:,} tonnes/year")
    
    # 4. Run LCA
    print("\n[4] Running Life Cycle Assessment...")
    lca_result = lca_engine.calculate(
        pathway,
        functional_unit_value=1.0,  # 1 tonne
        include_uncertainty=False
    )
    
    print(f"\n    Functional Unit: {lca_result.functional_unit}")
    print(f"\n    Environmental Impacts (per tonne NanoP):")
    print("    " + "-" * 50)
    
    # Format and display key impacts
    impact_units = {
        "climate_change": "kg CO2-eq",
        "acidification": "mol H+-eq",
        "eutrophication_fresh": "kg P-eq",
        "eutrophication_marine": "kg N-eq",
        "particulate_matter": "disease incidence",
        "resource_depletion": "kg Sb-eq",
    }
    
    for category, value in lca_result.impacts.items():
        if value != 0:
            unit = impact_units.get(category, "")
            print(f"    {category:30}: {value:>12.4f} {unit}")
    
    # 5. Run TEA
    print("\n[5] Running Techno-Economic Analysis...")
    tea_result = tea_engine.calculate(
        pathway,
        functional_unit_value=1.0,
        include_external=True
    )
    
    print(f"\n    Capital & Operating Costs:")
    print("    " + "-" * 50)
    print(f"    Total CAPEX:           {format_currency(tea_result.capex_total)}")
    print(f"    Annualized CAPEX:      {format_currency(tea_result.capex_annualized)}/year")
    print(f"    OPEX per tonne:        {format_currency(tea_result.opex_total)}/t")
    print(f"    Revenue per tonne:     {format_currency(tea_result.revenue)}/t")
    
    print(f"\n    Life Cycle Costs (per tonne NanoP):")
    print("    " + "-" * 50)
    print(f"    CLCC (Conventional):   {format_currency(tea_result.clcc)}/t")
    print(f"    External Cost:         {format_currency(tea_result.external_cost)}/t")
    print(f"    SLCC (Societal):       {format_currency(tea_result.slcc)}/t")
    
    # 6. Cost Breakdown
    print(f"\n    OPEX Breakdown:")
    print("    " + "-" * 50)
    for item, cost in tea_result.cost_breakdown.items():
        if cost > 0:
            print(f"    {item:25}: {format_currency(cost)}")
    
    # 7. NPV Calculation
    print("\n[6] Calculating Net Present Value...")
    npv_result = tea_engine.calculate_npv(
        pathway,
        project_lifetime=15,
    )
    
    print(f"\n    Financial Metrics (15-year project):")
    print("    " + "-" * 50)
    print(f"    Total Investment:      {format_currency(npv_result['total_investment'])}")
    print(f"    Annual Profit:         {format_currency(npv_result['annual_profit'])}/year")
    print(f"    Net Present Value:     {format_currency(npv_result['npv'])}")
    print(f"    Payback Period:        {npv_result['payback_years']} years")
    
    # 8. Summary
    print("\n" + "=" * 70)
    print("   ANALYSIS SUMMARY")
    print("=" * 70)
    
    gwp = lca_result.impacts.get("climate_change", 0)
    print(f"\n    Carbon Footprint:      {gwp:.1f} kg CO2-eq/tonne NanoP")
    print(f"    Production Cost:       {format_currency(tea_result.clcc)}/tonne (CLCC)")
    print(f"    Societal Cost:         {format_currency(tea_result.slcc)}/tonne (SLCC)")
    print(f"    Profitability:         NPV = {format_currency(npv_result['npv'])}")
    
    if npv_result['npv'] > 0:
        print("\n    Status: ECONOMICALLY VIABLE ✓")
    else:
        print("\n    Status: REQUIRES OPTIMIZATION")
    
    print("\n" + "=" * 70)
    print("   Analysis completed successfully.")
    print("=" * 70)
    
    return {
        "lca_result": lca_result,
        "tea_result": tea_result,
        "npv_result": npv_result
    }


if __name__ == "__main__":
    results = run_integrated_analysis()
