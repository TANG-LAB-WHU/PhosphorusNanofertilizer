"""
Integration tests for the complete LCA-TEA workflow.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nanop import (
    LCAEngine,
    TEAEngine,
    get_pathway,
    list_pathways,
    UncertaintyEngine,
    ResultsExporter,
    AnalysisReport
)


class TestIntegration:
    """Integration tests for LCA-TEA workflow."""
    
    def test_complete_workflow(self):
        """Test the complete LCA-TEA analysis workflow."""
        # Initialize engines
        lca_engine = LCAEngine()
        tea_engine = TEAEngine(country="China")
        
        # Get pathway
        pathway = get_pathway("NanoP-Synth", capacity_tonnes=10000)
        
        # Run LCA
        lca_result = lca_engine.calculate(pathway)
        assert lca_result.impacts["climate_change"] > 0
        
        # Run TEA
        tea_result = tea_engine.calculate(pathway)
        assert tea_result.capex_total > 0
        assert tea_result.opex_total > 0
        
        # Calculate NPV
        npv_result = tea_engine.calculate_npv(pathway, project_lifetime=15)
        assert "npv" in npv_result
        assert "payback_years" in npv_result
    
    def test_results_export(self, tmp_path):
        """Test results export functionality."""
        lca_engine = LCAEngine()
        tea_engine = TEAEngine(country="China")
        pathway = get_pathway("NanoP-Synth")
        
        lca_result = lca_engine.calculate(pathway)
        tea_result = tea_engine.calculate(pathway)
        npv_result = tea_engine.calculate_npv(pathway)
        
        # Create exporter
        exporter = ResultsExporter(output_dir=tmp_path)
        
        # Create report
        report = exporter.create_report(pathway, lca_result, tea_result, npv_result)
        assert isinstance(report, AnalysisReport)
        
        # Export JSON
        json_path = exporter.export_json(report)
        assert json_path.exists()
        
        # Export summary
        txt_path = exporter.export_summary_txt(report)
        assert txt_path.exists()
    
    def test_uncertainty_analysis(self):
        """Test uncertainty analysis functionality."""
        engine = UncertaintyEngine(seed=42)
        
        # Simple model function
        def simple_model(params):
            return {"result": params.get("a", 1) * params.get("b", 2)}
        
        # Define distributions
        distributions = {
            "a": {"type": "triangular", "min": 0.8, "mode": 1.0, "max": 1.2},
            "b": {"type": "triangular", "min": 1.8, "mode": 2.0, "max": 2.2},
        }
        
        # Run Monte Carlo
        results = engine.monte_carlo(
            simple_model,
            distributions,
            n_iterations=100
        )
        
        assert "result" in results
        assert results["result"].mean > 0
        assert results["result"].std > 0
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis functionality."""
        engine = UncertaintyEngine(seed=42)
        
        def simple_model(params):
            return params.get("a", 1) + 2 * params.get("b", 1)
        
        base_params = {"a": 1.0, "b": 1.0}
        
        results = engine.sensitivity_analysis(
            simple_model,
            base_params,
            ["a", "b"],
            variation_pct=0.1
        )
        
        assert len(results) == 2
        # b should be more sensitive (coefficient of 2)
        assert results[0].parameter == "b"


class TestPackageImports:
    """Test that all package imports work correctly."""
    
    def test_main_imports(self):
        from nanop import LCAEngine, TEAEngine, get_pathway
        assert LCAEngine is not None
        assert TEAEngine is not None
        assert get_pathway is not None
    
    def test_lca_imports(self):
        from nanop.lca import LCAEngine, LCAResult, LifeCycleInventory
        assert LCAEngine is not None
    
    def test_tea_imports(self):
        from nanop.tea import TEAEngine, TEAResult, CAPEXCalculator
        assert TEAEngine is not None
    
    def test_pathways_imports(self):
        from nanop.pathways import BasePathway, NanoPSynthesisPathway
        assert BasePathway is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
