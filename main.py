"""
NanoP-LCA-TEA Main Entry Point

Demonstrates the integrated assessment workflow:
1. Pathway initialization (NanoP synthesis)
2. LCA (Environmental Impact)
3. TEA (Economic Assessment)
4. Risk Assessment (Macro & Micro)
5. Decision Support (Ranking & Recommendation)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from nanop import (
    LCAEngine, 
    TEAEngine, 
    RiskAggregator, 
    PathwayRanker, 
    list_pathways, 
    get_pathway
)
from nanop.risk.aggregator import RiskScore, RiskLevel
from nanop.decision.scenario import Scenario, ScenarioAnalyzer, MARKET_SCENARIOS
from nanop.utils.currency import format_currency

def run_integrated_analysis():
    print("="*60)
    print("   PHOSPHORUS NANOFERTILIZER INTEGRATED ASSESSMENT (NANOP)   ")
    print("="*60)
    
    # 1. Initialize Engines
    lca_engine = LCAEngine()
    tea_engine = TEAEngine(country="China")
    risk_aggregator = RiskAggregator()
    pathway_ranker = PathwayRanker()
    
    # 2. Select Pathways
    # In this project, we primarily focus on NanoP synthesis
    pathway_codes = ["NanoP-Synth"]
    pathways = [get_pathway(code) for code in pathway_codes]
    
    print(f"\nAnalyzing {len(pathways)} pathways...")
    
    # Storage for decision metrics
    decision_data = {}
    
    for pathway in pathways:
        print(f"\n--- Processing: {pathway.name} [{pathway.code}] ---")
        
        # A. LCA Calculation
        lca_result = lca_engine.calculate(pathway, functional_unit_value=1.0)
        gwp = lca_result.impacts.get("climate_change", 0)
        print(f"  LCA: GWP = {gwp:.2f} kg CO2-eq/t")
        
        # B. TEA Calculation
        tea_result = tea_engine.calculate(pathway, functional_unit_value=1.0)
        npv_result = tea_engine.calculate_npv(pathway)
        npv = npv_result.get("npv", 0)
        payback = npv_result.get("payback_years", 20)
        
        print(f"  TEA: CLCC = {format_currency(tea_result.clcc)}/t")
        print(f"  TEA: NPV  = {format_currency(npv)}")
        
        # C. Risk Assessment (Sample Scores)
        sample_risks = [
            RiskScore.from_score("technical", "tech_maturity", 100 - (pathway.trl * 10), description="Based on TRL"),
            RiskScore.from_score("economic", "price_volatility", 35, description="Market risk"),
            RiskScore.from_score("policy", "regulatory_stringency", 25, description="Environmental law")
        ]
        aggregated_risk = risk_aggregator.aggregate(sample_risks)
        print(f"  Risk: Score = {aggregated_risk.overall_score:.2f} [{aggregated_risk.overall_level.name}]")
        
        # D. Collect metrics for ranking
        decision_data[pathway.name] = {
            "gwp": gwp,
            "resource_depletion": lca_result.impacts.get("resource_depletion", 0),
            "human_toxicity": lca_result.impacts.get("human_toxicity", 0),
            "npv": npv / 1000000, # normalized in Millions for scoring
            "irr": 0.18, # Sample IRR for NanoP
            "payback": payback,
            "trl": pathway.trl,
            "scalability": 0.7, # Assumed for nano processes
            "overall_risk": aggregated_risk.overall_score
        }
    
    # 3. Decision Support (Ranking)
    print("\n" + "="*60)
    print("   MULTI-CRITERIA DECISION ANALYSIS (MCDA) RESULTS   ")
    print("="*60)
    
    recommendations = pathway_ranker.rank(decision_data)
    
    for rec in recommendations:
        status = " [OPTIMAL]" if rec.is_pareto_optimal else ""
        print(f"\nRank {rec.rank}: {rec.pathway_name}{status}")
        print(f"  Score: {rec.score:.3f}")
        print(f"  Explanation: {rec.explanation}")
    
    # 4. Scenario Analysis
    print("\n" + "="*60)
    print("   SCENARIO ANALYSIS: MARKET ROBUSTNESS   ")
    print("="*60)
    
    analyzer = ScenarioAnalyzer(lca_engine, tea_engine)
    
    # We'll use the NanoP pathway for scenario testing
    nanop_pathway = get_pathway("NanoP-Synth")
    
    robustness = analyzer.quick_robustness_check(
        pathway=nanop_pathway,
        scenarios=list(MARKET_SCENARIOS.values())[:3], # Baseline, Optimistic, Pessimistic
        metric="clcc"
    )
    
    for scenario_name, value in robustness.items():
        if scenario_name != "robustness_stats":
            print(f"  {scenario_name:12}: {format_currency(value)}/t")
    
    print("\nFinished Integrated Analysis.")

if __name__ == "__main__":
    run_integrated_analysis()
