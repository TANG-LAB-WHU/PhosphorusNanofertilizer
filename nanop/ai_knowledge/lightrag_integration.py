"""
LightRAG Integration Module

Provides a wrapper around LightRAG for knowledge graph construction and RAG.
https://github.com/HKUDS/LightRAG
"""

import os
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field


# Check LightRAG availability
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.utils import setup_logger
    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False
    LightRAG = None
    QueryParam = None


@dataclass
class RAGQueryResult:
    """Result from a RAG query."""
    
    answer: str
    mode: str
    sources: List[str] = field(default_factory=list)
    entities: List[Dict] = field(default_factory=list)
    relations: List[Dict] = field(default_factory=list)


class NanoPRAG:
    """
    LightRAG wrapper for NanoP LCA-TEA domain.
    
    Provides:
    - Document ingestion with automatic entity extraction
    - Knowledge graph construction
    - Hybrid search (local + global + hybrid modes)
    - Integration with Gemini/OpenAI/Ollama LLMs
    
    Usage:
        rag = NanoPRAG(working_dir="./rag_storage", llm_provider="gemini")
        await rag.initialize()
        await rag.insert_documents(["paper1.txt", "paper2.txt"])
        result = await rag.query("What is the carbon footprint of nanoP?")
    """
    
    def __init__(
        self,
        working_dir: Union[str, Path] = "./data/rag_storage",
        llm_provider: str = "gemini",  # gemini, openai, ollama
        model_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        chunk_size: int = 1200,
        chunk_overlap: int = 100,
    ):
        """
        Initialize NanoPRAG.
        
        Args:
            working_dir: Directory to store RAG data
            llm_provider: LLM provider (gemini, openai, ollama)
            model_name: Model name (default: auto-select based on provider)
            embedding_model: Embedding model name
            chunk_size: Text chunk size for processing
            chunk_overlap: Overlap between chunks
        """
        if not LIGHTRAG_AVAILABLE:
            raise ImportError(
                "LightRAG not installed. Run: pip install lightrag-hku"
            )
        
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self._rag: Optional[LightRAG] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the RAG system."""
        if self._initialized:
            return
        
        # Setup logging
        setup_logger("lightrag", level="INFO")
        
        # Configure LLM and embedding based on provider
        llm_func, embed_func = self._get_llm_functions()
        
        self._rag = LightRAG(
            working_dir=str(self.working_dir),
            llm_model_func=llm_func,
            embedding_func=embed_func,
            chunk_token_size=self.chunk_size,
            chunk_overlap_token_size=self.chunk_overlap,
        )
        
        await self._rag.initialize_storages()
        self._initialized = True
    
    def _get_llm_functions(self):
        """Get LLM and embedding functions based on provider."""
        if self.llm_provider == "gemini":
            from lightrag.llm.gemini import gemini_complete, gemini_embed
            from nanop.utils.api_mgmt import get_default_model
            model = self.model_name or get_default_model()
            return (
                lambda *args, **kwargs: gemini_complete(model, *args, **kwargs),
                gemini_embed
            )
        
        elif self.llm_provider == "openai":
            from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
            return gpt_4o_mini_complete, openai_embed
        
        elif self.llm_provider == "ollama":
            from lightrag.llm.ollama import ollama_model_complete, ollama_embed
            model = self.model_name or "llama3.2"
            return (
                lambda *args, **kwargs: ollama_model_complete(model, *args, **kwargs),
                ollama_embed
            )
        
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
    
    async def insert_text(self, text: str) -> None:
        """
        Insert text into the knowledge base.
        
        Args:
            text: Text content to insert
        """
        if not self._initialized:
            await self.initialize()
        
        await self._rag.ainsert(text)
    
    async def insert_documents(self, filepaths: List[Union[str, Path]]) -> int:
        """
        Insert documents into the knowledge base.
        
        Args:
            filepaths: List of file paths to insert
            
        Returns:
            Number of documents processed
        """
        if not self._initialized:
            await self.initialize()
        
        count = 0
        for filepath in filepaths:
            path = Path(filepath)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                await self._rag.ainsert(text)
                count += 1
                print(f"✓ Inserted: {path.name}")
            else:
                print(f"✗ Not found: {path}")
        
        return count
    
    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        only_need_context: bool = False
    ) -> RAGQueryResult:
        """
        Query the knowledge base.
        
        Args:
            question: Question to ask
            mode: Query mode (local, global, hybrid, naive)
                - local: Search in entity neighborhoods
                - global: Search across communities
                - hybrid: Combine local and global
                - naive: Simple vector search
            only_need_context: Return only context without LLM answer
            
        Returns:
            RAGQueryResult with answer and sources
        """
        if not self._initialized:
            await self.initialize()
        
        param = QueryParam(
            mode=mode,
            only_need_context=only_need_context
        )
        
        answer = await self._rag.aquery(question, param=param)
        
        return RAGQueryResult(
            answer=answer,
            mode=mode,
            sources=[],
            entities=[],
            relations=[]
        )
    
    async def get_knowledge_graph(self) -> Dict:
        """
        Export the knowledge graph.
        
        Returns:
            Dict with entities and relations
        """
        if not self._initialized:
            await self.initialize()
        
        # Export graph data
        try:
            entities, relations = await self._rag.aexport_data()
            return {
                "entities": entities,
                "relations": relations,
                "stats": {
                    "entity_count": len(entities),
                    "relation_count": len(relations)
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self) -> None:
        """Clean up resources."""
        if self._rag and self._initialized:
            await self._rag.finalize_storages()
            self._initialized = False
    
    @staticmethod
    def is_available() -> bool:
        """Check if LightRAG is available."""
        return LIGHTRAG_AVAILABLE


# Synchronous wrapper for convenience
class NanoPRAGSync:
    """
    Synchronous wrapper for NanoPRAG.
    
    Usage:
        rag = NanoPRAGSync(llm_provider="gemini")
        rag.insert_text("Your document text...")
        result = rag.query("Your question?")
    """
    
    def __init__(self, **kwargs):
        self._async_rag = NanoPRAG(**kwargs)
        self._loop = None
    
    def _get_loop(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop
    
    def _run(self, coro):
        loop = self._get_loop()
        return loop.run_until_complete(coro)
    
    def initialize(self) -> None:
        self._run(self._async_rag.initialize())
    
    def insert_text(self, text: str) -> None:
        self._run(self._async_rag.insert_text(text))
    
    def insert_documents(self, filepaths: List[Union[str, Path]]) -> int:
        return self._run(self._async_rag.insert_documents(filepaths))
    
    def query(self, question: str, mode: str = "hybrid") -> RAGQueryResult:
        return self._run(self._async_rag.query(question, mode=mode))
    
    def get_knowledge_graph(self) -> Dict:
        return self._run(self._async_rag.get_knowledge_graph())
    
    def close(self) -> None:
        self._run(self._async_rag.close())


# Keep backward compatibility
def create_nanop_rag(
    working_dir: str = "./data/rag_storage",
    llm_provider: str = "gemini"
) -> NanoPRAGSync:
    """
    Create a NanoPRAG instance for the NanoP domain.
    
    Args:
        working_dir: Storage directory
        llm_provider: LLM provider (gemini, openai, ollama)
        
    Returns:
        Initialized NanoPRAGSync instance
    """
    rag = NanoPRAGSync(
        working_dir=working_dir,
        llm_provider=llm_provider
    )
    rag.initialize()
    return rag


if __name__ == "__main__":
    print("LightRAG Integration Module")
    print("-" * 40)
    print(f"LightRAG available: {LIGHTRAG_AVAILABLE}")
    
    if LIGHTRAG_AVAILABLE:
        print("\nUsage:")
        print("  rag = NanoPRAGSync(llm_provider='gemini')")
        print("  rag.insert_text('Your text...')")
        print("  result = rag.query('Your question?')")
    else:
        print("\nInstall LightRAG:")
        print("  pip install lightrag-hku")
