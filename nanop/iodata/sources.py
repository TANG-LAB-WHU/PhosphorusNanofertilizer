"""
Data Sources Module

Defines data sources and LCI database connectors.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from pathlib import Path


class SourceType(Enum):
    """Types of data sources."""
    LOCAL_PAPER = "local_paper"
    OPEN_ACCESS = "open_access"
    LCI_DATABASE = "lci_database"
    REGULATORY = "regulatory"
    INDUSTRY_REPORT = "industry_report"
    EXPERIMENT = "experiment"


@dataclass
class DataSource:
    """
    Represents a data source for LCA-TEA.
    """
    
    name: str
    source_type: SourceType
    url: Optional[str] = None
    description: str = ""
    access_method: str = "direct"  # direct, api, scrape
    credentials_required: bool = False
    data_quality: str = "medium"
    year: int = 2024
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.source_type.value,
            "url": self.url,
            "description": self.description,
            "data_quality": self.data_quality,
            "year": self.year,
        }


@dataclass
class LCIDatabase:
    """
    LCI Database connector.
    """
    
    name: str
    version: str = "latest"
    base_url: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    
    def search(self, query: str) -> List[Dict]:
        """
        Search database for processes/flows.
        
        This is a placeholder - actual implementation would
        connect to real LCI databases (ELCD, USLCI, ecoinvent).
        """
        # Placeholder results
        return [
            {"name": query, "database": self.name, "available": False}
        ]
    
    def get_process(self, process_id: str) -> Optional[Dict]:
        """Get process data by ID."""
        return None


# Pre-defined data sources for nano-fertilizer domain
NANOP_DATA_SOURCES = {
    # Literature sources
    "local_papers": DataSource(
        name="Local Research Papers",
        source_type=SourceType.LOCAL_PAPER,
        description="Research papers stored locally in ./data/raw/papers/",
        access_method="direct"
    ),
    "pubmed": DataSource(
        name="PubMed Open Access",
        source_type=SourceType.OPEN_ACCESS,
        url="https://pubmed.ncbi.nlm.nih.gov/",
        description="Biomedical literature database",
        access_method="api"
    ),
    "scopus": DataSource(
        name="Scopus",
        source_type=SourceType.OPEN_ACCESS,
        url="https://www.scopus.com/",
        description="Abstract and citation database",
        credentials_required=True
    ),
    
    # LCI Databases
    "elcd": DataSource(
        name="ELCD",
        source_type=SourceType.LCI_DATABASE,
        url="https://eplca.jrc.ec.europa.eu/ELCD3/",
        description="European Life Cycle Database",
        data_quality="high"
    ),
    "uslci": DataSource(
        name="USLCI",
        source_type=SourceType.LCI_DATABASE,
        url="https://www.lcacommons.gov/lca-collaboration/",
        description="US Life Cycle Inventory Database",
        data_quality="high"
    ),
    "agribalyse": DataSource(
        name="Agribalyse",
        source_type=SourceType.LCI_DATABASE,
        url="https://agribalyse.ademe.fr/",
        description="French agricultural LCI database",
        data_quality="high"
    ),
    
    # Regulatory sources
    "epa": DataSource(
        name="US EPA",
        source_type=SourceType.REGULATORY,
        url="https://www.epa.gov/",
        description="US Environmental Protection Agency"
    ),
    "eu_fertilizer_reg": DataSource(
        name="EU Fertilizer Regulation",
        source_type=SourceType.REGULATORY,
        url="https://eur-lex.europa.eu/",
        description="EU Regulation 2019/1009 on fertilizing products"
    ),
    
    # Industry sources
    "ifa": DataSource(
        name="IFA",
        source_type=SourceType.INDUSTRY_REPORT,
        url="https://www.fertilizer.org/",
        description="International Fertilizer Association"
    ),
    "fao": DataSource(
        name="FAO",
        source_type=SourceType.INDUSTRY_REPORT,
        url="https://www.fao.org/",
        description="Food and Agriculture Organization"
    ),
}


# Pre-defined LCI databases
LCI_DATABASES = {
    "elcd": LCIDatabase(
        name="ELCD",
        version="3.2",
        base_url="https://eplca.jrc.ec.europa.eu/",
        categories=["energy", "materials", "transport", "waste"]
    ),
    "uslci": LCIDatabase(
        name="USLCI",
        version="2023",
        categories=["agriculture", "chemicals", "energy", "metals"]
    ),
    "agribalyse": LCIDatabase(
        name="Agribalyse",
        version="3.1",
        categories=["crops", "livestock", "processing", "packaging"]
    ),
}


def list_sources() -> List[str]:
    """List available data sources."""
    return list(NANOP_DATA_SOURCES.keys())


def get_source(name: str) -> Optional[DataSource]:
    """Get data source by name."""
    return NANOP_DATA_SOURCES.get(name)


def list_lci_databases() -> List[str]:
    """List available LCI databases."""
    return list(LCI_DATABASES.keys())


def get_lci_database(name: str) -> Optional[LCIDatabase]:
    """Get LCI database by name."""
    return LCI_DATABASES.get(name)


if __name__ == "__main__":
    print("Available data sources:")
    for name in list_sources():
        source = get_source(name)
        print(f"  - {name}: {source.description}")
