"""
Data Ingestion Layer

This module handles data collection from various sources:
- PDF parsing (local papers)
- Web scraping (open access databases)
- API connectors (regulatory databases)
- Data standardization
"""

from nanop.iodata.pdf_parser import PDFParser
from nanop.iodata.web_scraper import WebScraper
from nanop.iodata.data_standardizer import DataStandardizer
from nanop.iodata.api_connector import APIConnector

__all__ = ["PDFParser", "WebScraper", "DataStandardizer", "APIConnector"]
