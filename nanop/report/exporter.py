"""
Results and Reporting Module

Export and format analysis results.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class AnalysisReport:
    """Complete analysis report for a pathway."""
    
    pathway_code: str
    pathway_name: str
    functional_unit: str
    analysis_date: str
    
    # LCA Results
    lca_impacts: Dict[str, float]
    lca_total_gwp: float
    
    # TEA Results
    tea_capex: float
    tea_opex: float
    tea_clcc: float
    tea_slcc: float
    tea_external_cost: float
    tea_revenue: float
    
    # NPV Results
    npv: float
    payback_years: float
    
    # Metadata
    country: str = "global"
    capacity_tonnes: float = 10000
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class ResultsExporter:
    """
    Export analysis results to various formats.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize exporter.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir) if output_dir else Path("./results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_report(
        self,
        pathway,
        lca_result,
        tea_result,
        npv_result: Dict
    ) -> AnalysisReport:
        """
        Create analysis report from results.
        
        Args:
            pathway: Pathway instance
            lca_result: LCAResult from engine
            tea_result: TEAResult from engine
            npv_result: NPV result dict
            
        Returns:
            AnalysisReport instance
        """
        return AnalysisReport(
            pathway_code=pathway.code,
            pathway_name=pathway.name,
            functional_unit=lca_result.functional_unit,
            analysis_date=datetime.now().isoformat(),
            lca_impacts=lca_result.impacts,
            lca_total_gwp=lca_result.impacts.get("climate_change", 0),
            tea_capex=tea_result.capex_total,
            tea_opex=tea_result.opex_total,
            tea_clcc=tea_result.clcc,
            tea_slcc=tea_result.slcc,
            tea_external_cost=tea_result.external_cost,
            tea_revenue=tea_result.revenue,
            npv=npv_result.get("npv", 0),
            payback_years=npv_result.get("payback_years", 0),
            country=pathway.country,
            capacity_tonnes=pathway.capacity
        )
    
    def export_json(
        self,
        report: AnalysisReport,
        filename: Optional[str] = None
    ) -> Path:
        """Export report to JSON file."""
        if filename is None:
            filename = f"{report.pathway_code}_{report.analysis_date[:10]}.json"
        
        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            f.write(report.to_json())
        
        return filepath
    
    def export_csv(
        self,
        reports: List[AnalysisReport],
        filename: str = "comparison.csv"
    ) -> Path:
        """Export multiple reports to CSV for comparison."""
        filepath = self.output_dir / filename
        
        if not reports:
            return filepath
        
        # Get headers from first report
        headers = list(reports[0].to_dict().keys())
        
        with open(filepath, "w") as f:
            # Header row
            f.write(",".join(headers) + "\n")
            
            # Data rows
            for report in reports:
                data = report.to_dict()
                row = []
                for h in headers:
                    val = data.get(h, "")
                    if isinstance(val, dict):
                        val = str(val)
                    row.append(str(val))
                f.write(",".join(row) + "\n")
        
        return filepath
    
    def export_summary_txt(
        self,
        report: AnalysisReport,
        filename: Optional[str] = None
    ) -> Path:
        """Export human-readable summary."""
        if filename is None:
            filename = f"{report.pathway_code}_summary.txt"
        
        filepath = self.output_dir / filename
        
        lines = [
            "=" * 70,
            f"ANALYSIS REPORT: {report.pathway_name}",
            "=" * 70,
            f"Pathway Code: {report.pathway_code}",
            f"Functional Unit: {report.functional_unit}",
            f"Country: {report.country}",
            f"Capacity: {report.capacity_tonnes:,.0f} tonnes/year",
            f"Analysis Date: {report.analysis_date}",
            "",
            "-" * 70,
            "ENVIRONMENTAL IMPACTS (LCA)",
            "-" * 70,
        ]
        
        for category, value in report.lca_impacts.items():
            lines.append(f"  {category}: {value:.4f}")
        
        lines.extend([
            "",
            "-" * 70,
            "ECONOMIC ANALYSIS (TEA)",
            "-" * 70,
            f"  CAPEX Total: ${report.tea_capex:,.2f}",
            f"  OPEX per FU: ${report.tea_opex:,.2f}",
            f"  Revenue per FU: ${report.tea_revenue:,.2f}",
            f"  CLCC: ${report.tea_clcc:,.2f}",
            f"  External Cost: ${report.tea_external_cost:,.2f}",
            f"  SLCC: ${report.tea_slcc:,.2f}",
            "",
            "-" * 70,
            "FINANCIAL METRICS",
            "-" * 70,
            f"  Net Present Value: ${report.npv:,.2f}",
            f"  Payback Period: {report.payback_years:.1f} years",
            "",
            "=" * 70,
        ])
        
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        
        return filepath


def format_results_table(
    lca_result,
    tea_result,
    npv_result: Dict
) -> str:
    """
    Format results as a text table.
    """
    lines = [
        "",
        "┌" + "─" * 50 + "┐",
        "│" + " RESULTS SUMMARY".center(50) + "│",
        "├" + "─" * 50 + "┤",
    ]
    
    # LCA
    gwp = lca_result.impacts.get("climate_change", 0)
    lines.extend([
        "│ LCA Results:" + " " * 37 + "│",
        f"│   GWP: {gwp:>12.2f} kg CO2-eq/t" + " " * 17 + "│",
    ])
    
    # TEA
    lines.extend([
        "│ TEA Results:" + " " * 37 + "│",
        f"│   CLCC: ${tea_result.clcc:>12,.2f}/t" + " " * 19 + "│",
        f"│   SLCC: ${tea_result.slcc:>12,.2f}/t" + " " * 19 + "│",
    ])
    
    # NPV
    lines.extend([
        "│ Financial:" + " " * 39 + "│",
        f"│   NPV: ${npv_result['npv']:>14,.0f}" + " " * 19 + "│",
        f"│   Payback: {npv_result['payback_years']:>8.1f} years" + " " * 19 + "│",
    ])
    
    lines.append("└" + "─" * 50 + "┘")
    
    return "\n".join(lines)
