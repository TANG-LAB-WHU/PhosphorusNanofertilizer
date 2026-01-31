"""
Provides knowledge graph construction, LLM extraction, and RAG capabilities for Phosphorus Nanofertilizer.
"""

from nanop.knowledge.knowledge_graph import PhosphorusNanofertilizerKG
from nanop.knowledge.llm_extractor import LLMExtractor
from nanop.knowledge.gap_filler import GapFiller
from nanop.knowledge.embeddings import EmbeddingModel

try:
    from nanop.knowledge.lightrag_engine import (
        LightRAGEngine, 
        LIGHTRAG_AVAILABLE
    )
except ImportError:
    LightRAGEngine = None
    LIGHTRAG_AVAILABLE = False

# RAGAnything support
try:
    from nanop.knowledge.raganything_engine import (
        RAGAnythingEngine,
        RAGANYTHING_AVAILABLE
    )
except ImportError:
    RAGAnythingEngine = None
    RAGANYTHING_AVAILABLE = False

# Optional Neo4j support
try:
    from nanop.knowledge.neo4j_adapter import Neo4jAdapter, Neo4jConfig
    NEO4J_AVAILABLE = True
except ImportError:
    Neo4jAdapter = None
    Neo4jConfig = None
    NEO4J_AVAILABLE = False

__all__ = [
    "PhosphorusNanofertilizerKG",
    "LLMExtractor",
    "LightRAGEngine",
    "RAGAnythingEngine",
    "GapFiller",
    "EmbeddingModel",
    "Neo4jAdapter",
    "Neo4jConfig",
    "NEO4J_AVAILABLE",
    "LIGHTRAG_AVAILABLE",
    "RAGANYTHING_AVAILABLE",
]
