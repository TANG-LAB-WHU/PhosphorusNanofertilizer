# Data Directory

This directory contains data sources for the NanoP LCA-TEA framework.

## Structure

```
data/
├── raw/                    # Raw unprocessed data
│   ├── papers/             # Research papers (PDF)
│   │   ├── unparsed/       # Original PDFs
│   │   └── parsed/         # Extracted text/data
│   └── lci/                # LCI data files
├── processed/              # Processed and standardized data
│   ├── flows/              # Standardized flow data
│   └── parameters/         # Process parameters
└── cache/                  # Cached API responses and embeddings
```

## Data Sources

- **Local Papers**: Research papers stored in `raw/papers/`
- **Open Access**: PubMed, arXiv, OpenAlex
- **LCI Databases**: ELCD, USLCI, Agribalyse
- **Regulatory**: EPA, EU Fertilizer Regulation
- **Industry**: IFA, FAO reports
