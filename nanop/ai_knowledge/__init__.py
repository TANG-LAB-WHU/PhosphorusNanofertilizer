"""
AI and Knowledge Graph Module

Provides LightRAG-based knowledge graph and RAG capabilities.
"""

# LightRAG integration (primary)
from nanop.ai_knowledge.lightrag_integration import (
    NanoPRAG,
    NanoPRAGSync,
    RAGQueryResult,
    create_nanop_rag,
    LIGHTRAG_AVAILABLE,
)

# Legacy knowledge graph (for backward compatibility)
from nanop.ai_knowledge.knowledge_graph import (
    KnowledgeGraph,
    Entity,
    Relationship,
    EntityType,
    RelationType,
    create_nanop_base_graph,
)

# RAG components
from nanop.ai_knowledge.rag_engine import RAGEngine, DocumentChunk

# Gap filling
from nanop.ai_knowledge.gap_filling import GapFiller

# Paper parsing
from nanop.ai_knowledge.paper_parser import (
    AIFeatureDetector,
    AIPaperParser,
    ExtractedLCIData,
    ExtractedTEAData,
    RuleBasedExtractor,
)# Pipeline
from nanop.ai_knowledge.pipeline import (
    PaperToKnowledgeGraphPipeline,
    PaperToKGPipelineSync,
    PipelineResult,
)


__all__ = [
    # LightRAG (recommended)
    "NanoPRAG",
    "NanoPRAGSync",
    "RAGQueryResult",
    "create_nanop_rag",
    "LIGHTRAG_AVAILABLE",
    # Legacy knowledge graph
    "KnowledgeGraph",
    "Entity",
    "Relationship",
    "EntityType",
    "RelationType",
    "create_nanop_base_graph",
    # RAG
    "RAGEngine",
    "DocumentChunk",
    # Gap filling
    "GapFiller",
    # Paper parsing
    "AIFeatureDetector",
    "AIPaperParser",
    "ExtractedLCIData",
    "ExtractedTEAData",
    "RuleBasedExtractor",
    # Pipeline
    "PaperToKnowledgeGraphPipeline",
    "PaperToKGPipelineSync",
    "PipelineResult",
]
