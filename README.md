# NanoP LCA-TEA: Nano Hydroxyapatite Phosphorus Fertilizer Assessment Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive framework for Life Cycle Assessment (LCA) and Techno-Economic Analysis (TEA) of nano hydroxyapatite phosphorus fertilizer (nanoP) production.

## Features

- **LCA Module**: ISO 14040/14044 compliant life cycle assessment
  - 10 impact categories (climate change, acidification, eutrophication, toxicity, etc.)
  - Characterization factors based on ILCD 2011 methodology
  - Monte Carlo uncertainty analysis
  - Sensitivity analysis

- **TEA Module**: Complete techno-economic analysis
  - CAPEX calculation with Lang factors
  - OPEX calculation (materials, utilities, labor)
  - CLCC (Conventional Life Cycle Cost)
  - SLCC (Societal Life Cycle Cost with external costs)
  - NPV, payback period calculation

- **NanoP Synthesis Pathway**: Wet chemical precipitation process
  - Complete life cycle inventory
  - Stoichiometric material balances
  - Energy consumption modeling
  - Emission calculations

## Installation

```bash
# Clone the repository
git clone https://github.com/TANG-LAB-WHU/PhosphorusNanofertilizer.git
cd PhosphorusNanofertilizer

# Create virtual environment (optional)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Quick Start

```python
from nanop import LCAEngine, TEAEngine, get_pathway

# Initialize engines
lca = LCAEngine()
tea = TEAEngine(country="China")

# Get pathway
pathway = get_pathway("NanoP-Synth", capacity_tonnes=10000)

# Run LCA
lca_result = lca.calculate(pathway, functional_unit_value=1.0)
print(f"GWP: {lca_result.impacts['climate_change']:.1f} kg CO2-eq/t")

# Run TEA
tea_result = tea.calculate(pathway)
print(f"CLCC: ${tea_result.clcc:.2f}/t")
print(f"SLCC: ${tea_result.slcc:.2f}/t")

# NPV Analysis
npv_result = tea.calculate_npv(pathway, project_lifetime=15)
print(f"NPV: ${npv_result['npv']:,.0f}")
```

## Run Demo

```bash
python main.py
```

## Project Structure

```
PhosphorusNanofertilizer/
├── nanop/                    # Main package
│   ├── lca/                  # LCA module
│   │   ├── engine.py         # LCA calculation engine
│   │   ├── inventory.py      # Life cycle inventory
│   │   ├── characterization.py
│   │   └── impact_assessment.py
│   ├── tea/                  # TEA module
│   │   ├── engine.py         # TEA calculation engine
│   │   ├── capex.py          # Capital costs
│   │   ├── opex.py           # Operating costs
│   │   └── external_cost.py  # External cost monetization
│   ├── pathways/             # Production pathways
│   │   ├── base_pathway.py
│   │   └── nanop_synthesis.py
│   └── utils/                # Utilities
├── config/                   # Configuration files
│   ├── settings.yaml
│   ├── impact_factors.yaml
│   └── shadow_prices.yaml
├── main.py                   # Demo script
├── requirements.txt
└── README.md
```

## NanoP Synthesis Process

The framework models wet chemical precipitation of nano hydroxyapatite:

```
10 CaCl₂ + 6 (NH₄)₂HPO₄ + 8 NH₄OH → Ca₁₀(PO₄)₆(OH)₂ + 20 NH₄Cl + 6 H₂O
```

**Key Parameters:**
- Functional unit: 1 tonne nanoP produced
- Ca/P molar ratio: 1.67
- Particle size: ~50 nm
- Product purity: 98%

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

```bibtex
@software{nanop_lca_tea_2024,
  title = {NanoP LCA-TEA: Nano Hydroxyapatite Phosphorus Fertilizer Assessment Framework},
  year = {2024},
  url = {https://github.com/TANG-LAB-WHU/PhosphorusNanofertilizer}
}
```
