"""
Data Ingestion Module

Provides data loading, parsing, and standardization for LCA-TEA data.
"""

from nanop.data.loader import DataLoader, CSVLoader
from nanop.data.standardizer import DataStandardizer, UnitConverter
from nanop.data.sources import DataSource, LCIDatabase
from nanop.data.pdf_parser import PDFParser, ParsedDocument

__all__ = [
    "DataLoader",
    "PDFParser",
    "ParsedDocument",
    "CSVLoader",
    "DataStandardizer",
    "UnitConverter",
    "DataSource",
    "LCIDatabase",
]

