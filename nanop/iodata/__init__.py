"""
Data Ingestion Module

Provides data loading, parsing, and standardization for LCA-TEA data.
"""

from nanop.iodata.loader import DataLoader, CSVLoader
from nanop.iodata.standardizer import DataStandardizer, UnitConverter
from nanop.iodata.sources import DataSource, LCIDatabase
from nanop.iodata.pdf_parser import PDFParser, ParsedDocument

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

