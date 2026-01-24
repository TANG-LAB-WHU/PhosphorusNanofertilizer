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

## Core Modules

| Module | Description | Key Classes |
|--------|-------------|-------------|
| `nanop/lca` | Life Cycle Assessment | `LCAEngine`, `LifeCycleInventory`, `ImpactAssessment` |
| `nanop/tea` | Techno-Economic Analysis | `TEAEngine`, `CAPEXCalculator`, `OPEXCalculator` |
| `nanop/pathways` | Production Pathways | `BasePathway`, `NanoPSynthesisPathway` |
| `nanop/utils` | Utilities | `format_currency`, `convert_currency` |
| `nanop/data` | Data Ingestion | `DataLoader`, `DataStandardizer`, `DataSource` |
| `nanop/ai` | AI & Knowledge Graph | `KnowledgeGraph`, `RAGEngine`, `GapFiller` |

## System Architecture

```text
┌─══════════════════════════════════════════════════════════════════════════════┐
│                      NANOP LCA-TEA FRAMEWORK ARCHITECTURE                      │
└─══════════════════════════════════════════════════════════════════════════════┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              INPUT DATA SOURCES                                 │
├───────────────┬───────────────┬───────────────┬───────────────┬─────────────────┤
│ Local Papers  │ Open Access   │ Open LCI      │ Regulatory    │ Industry        │
│               │ Literature    │ Databases     │ Databases     │ Reports         │
│               │               │               │               │                 │
│ ./data/raw/   │ • PubMed OA   │ • ELCD        │ • EPA         │ • IFA           │
│   papers/     │ • arXiv       │ • USLCI       │ • EU Fertil.  │ • FAO           │
│ • unparsed/   │ • OpenAlex    │ • Agribalyse  │   Regulation  │ • World Bank    │
│ • parsed/     │ • Scopus      │ • Idemat      │               │                 │
└───────┬───────┴───────┬───────┴───────┬───────┴───────┬───────┴────────┬────────┘
        │               │               │               │                │
        ▼               ▼               ▼               ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA INGESTION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐              │
│  │  PDF Parser      │  │  CSV/Excel       │  │  API Connector   │              │
│  │  (PyMuPDF)       │  │  Loader          │  │  (REST)          │              │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘              │
│           └─────────────────────┼─────────────────────┘                         │
│                                 ▼                                               │
│                    ┌────────────────────────┐                                   │
│                    │  Data Standardizer     │                                   │
│                    │  • Unit conversion     │                                   │
│                    │  • Schema mapping      │                                   │
│                    │  • Quality tagging     │                                   │
│                    └───────────┬────────────┘                                   │
└────────────────────────────────┼────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AI + KNOWLEDGE GRAPH LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     LLM-RAG EXTRACTION ENGINE                           │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │   │
│  │  │ Text Chunking  │─▶│ Embedding      │─▶│ Vector Store   │            │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘            │   │
│  │                                                  │                      │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────▼─────────┐            │   │
│  │  │ Query Engine   │◀─│ RAG Retriever  │◀─│ LLM Extractor  │            │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                     │                                          │
│  ┌──────────────────────────────────▼──────────────────────────────────────┐   │
│  │                    KNOWLEDGE GRAPH DATABASE                             │   │
│  │                        (NetworkX / Neo4j)                               │   │
│  │                                                                         │   │
│  │    [Material]──requires──▶[Process]──produces──▶[Product]              │   │
│  │        │                      │                      │                  │   │
│  │        ▼                      ▼                      ▼                  │   │
│  │    [CaCl₂]               [Synthesis]            [NanoP]                │   │
│  │    [H₃PO₄]                    │                  [NH₄Cl]               │   │
│  │    [NH₄OH]                    ▼                                        │   │
│  │                          [Emission]──impacts──▶[Impact]                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        ML GAP-FILLING MODULE                            │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │   │
│  │  │ Similarity     │  │ Regression     │  │ Uncertainty    │            │   │
│  │  │ Matching       │  │ Prediction     │  │ Estimation     │            │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION LAYER                                │
├───────────────────────┬───────────────────────┬─────────────────────────────────┤
│   settings.yaml       │  impact_factors.yaml  │     shadow_prices.yaml          │
│   • Functional unit   │  • GWP factors        │     • CO2 price ($/kg)          │
│   • Economic params   │  • Acidification      │     • NOx, SO2, PM prices       │
│   • Impact categories │  • Eutrophication     │     • External cost rates       │
└───────────┬───────────┴───────────┬───────────┴─────────────┬───────────────────┘
            │                       │                         │
            ▼                       ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         LCA-TEA CALCULATION ENGINE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         LCA MODULE (nanop/lca/)                         │   │
│  │  Functional Unit: 1 tonne nano hydroxyapatite phosphorus fertilizer     │   │
│  │                                                                         │   │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │   │
│  │  │ Inventory    │──▶│ Character-   │──▶│ Impact       │                │   │
│  │  │ (LCI)        │   │ ization      │   │ Assessment   │                │   │
│  │  └──────────────┘   └──────────────┘   └──────────────┘                │   │
│  │                                                                         │   │
│  │  Impact Categories: Climate Change, Acidification, Eutrophication,     │   │
│  │                     Human Toxicity, Ecotoxicity, PM, Resources         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         TEA MODULE (nanop/tea/)                         │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│  │  │ CLCC = CAPEX_annualized + OPEX - Product_Revenue                 │  │   │
│  │  │ SLCC = Internal_Cost + External_Cost(emissions)                  │  │   │
│  │  └──────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                         │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │   │
│  │  │ CAPEX      │  │ OPEX       │  │ External   │  │ NPV        │       │   │
│  │  │ Calculator │  │ Calculator │  │ Cost Calc  │  │ Analysis   │       │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    UNCERTAINTY ENGINE                                   │   │
│  │  Monte Carlo Simulation  │  Sensitivity Analysis  │  Parameter Sampling │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION PATHWAY (nanop/pathways/)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    NanoP-Synth: Wet Chemical Precipitation              │   │
│  │                                                                         │   │
│  │   INPUTS                    PROCESS                      OUTPUTS        │   │
│  │  ┌──────────┐            ┌───────────┐               ┌──────────┐      │   │
│  │  │ CaCl₂    │──┐         │ Reactor   │               │ NanoP    │      │   │
│  │  │ H₃PO₄   │──┼────────▶│ (80°C)    │──────────────▶│ Product  │      │   │
│  │  │ NH₄OH   │──┘         │ pH=10     │               │ (1000kg) │      │   │
│  │  └──────────┘            └─────┬─────┘               └──────────┘      │   │
│  │  ┌──────────┐                  │                     ┌──────────┐      │   │
│  │  │Electricity│                  ├────────────────────▶│ NH₄Cl    │      │   │
│  │  │ 450 kWh  │                  │                     │ Byproduct│      │   │
│  │  └──────────┘                  │                     └──────────┘      │   │
│  │  ┌──────────┐                  │ EMISSIONS           ┌──────────┐      │   │
│  │  │ Thermal  │                  └────────────────────▶│ CO₂, NH₃ │      │   │
│  │  │ 800 kWh  │                                        │ PM, NOx  │      │   │
│  │  └──────────┘                                        └──────────┘      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  10 CaCl₂ + 6 (NH₄)₂HPO₄ + 8 NH₄OH → Ca₁₀(PO₄)₆(OH)₂ + 20 NH₄Cl + 6 H₂O       │
│                                                                                 │
│                    [Extensible: New pathways can be added]                      │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           OUTPUT & RESULTS                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ LCA Results     │  │ TEA Results     │  │ NPV Analysis    │                 │
│  │ • GWP           │  │ • CLCC          │  │ • Net Present   │                 │
│  │ • Acidification │  │ • SLCC          │  │   Value         │                 │
│  │ • Eutrophication│  │ • Cost Breakdown│  │ • Payback       │                 │
│  │ • Toxicity      │  │ • External Cost │  │ • IRR           │                 │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

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
