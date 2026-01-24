"""
Data Loader Module

Provides data loading from various sources: PDF, CSV, Excel, JSON.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class LoadedData:
    """Container for loaded data."""
    
    source: str
    source_type: str
    content: Any
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DataLoader:
    """
    Universal data loader for LCA-TEA data sources.
    
    Supports: PDF, CSV, Excel, JSON, YAML
    """
    
    SUPPORTED_FORMATS = [".pdf", ".csv", ".xlsx", ".xls", ".json", ".yaml", ".yml"]
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize data loader.
        
        Args:
            data_dir: Base directory for data files
        """
        self.data_dir = Path(data_dir) if data_dir else Path("./data")
    
    def load(self, filepath: Union[str, Path]) -> LoadedData:
        """
        Load data from file.
        
        Args:
            filepath: Path to data file
            
        Returns:
            LoadedData object
        """
        path = Path(filepath)
        suffix = path.suffix.lower()
        
        if suffix == ".pdf":
            return self._load_pdf(path)
        elif suffix == ".csv":
            return self._load_csv(path)
        elif suffix in [".xlsx", ".xls"]:
            return self._load_excel(path)
        elif suffix == ".json":
            return self._load_json(path)
        elif suffix in [".yaml", ".yml"]:
            return self._load_yaml(path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")
    
    def _load_csv(self, path: Path) -> LoadedData:
        """Load CSV file."""
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            import csv
            reader = csv.DictReader(f)
            rows = list(reader)
        
        return LoadedData(
            source=str(path),
            source_type="csv",
            content=rows,
            metadata={"rows": len(rows)}
        )
    
    def _load_json(self, path: Path) -> LoadedData:
        """Load JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        return LoadedData(
            source=str(path),
            source_type="json",
            content=content
        )
    
    def _load_yaml(self, path: Path) -> LoadedData:
        """Load YAML file."""
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
        
        return LoadedData(
            source=str(path),
            source_type="yaml",
            content=content
        )
    
    def _load_pdf(self, path: Path) -> LoadedData:
        """Load PDF file (requires PyMuPDF or pdfplumber)."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            return LoadedData(
                source=str(path),
                source_type="pdf",
                content=text,
                metadata={"pages": len(doc)}
            )
        except ImportError:
            # Fallback: return path for external processing
            return LoadedData(
                source=str(path),
                source_type="pdf",
                content=None,
                metadata={"error": "PyMuPDF not installed"}
            )
    
    def _load_excel(self, path: Path) -> LoadedData:
        """Load Excel file."""
        try:
            import pandas as pd
            df = pd.read_excel(path)
            return LoadedData(
                source=str(path),
                source_type="excel",
                content=df.to_dict("records"),
                metadata={"rows": len(df), "columns": list(df.columns)}
            )
        except ImportError:
            return LoadedData(
                source=str(path),
                source_type="excel",
                content=None,
                metadata={"error": "pandas not installed"}
            )
    
    def list_files(self, pattern: str = "*") -> List[Path]:
        """List data files matching pattern."""
        return list(self.data_dir.glob(pattern))



# PDFParser is now imported from .pdf_parser in __init__.py to avoid duplication
# and provide advanced features (MinerU).

class CSVLoader:
    """
    CSV loader with LCI-specific functionality.
    """
    
    def __init__(self):
        self.loader = DataLoader()
    
    def load_lci(self, filepath: Union[str, Path]) -> Dict:
        """
        Load LCI data from CSV.
        
        Expected columns: name, quantity, unit, category, source
        """
        data = self.loader.load(filepath)
        
        if data.source_type != "csv":
            raise ValueError("Expected CSV file")
        
        return {
            "source": data.source,
            "flows": data.content,
            "count": len(data.content)
        }


if __name__ == "__main__":
    loader = DataLoader()
    print(f"Data loader initialized. Supported formats: {loader.SUPPORTED_FORMATS}")
