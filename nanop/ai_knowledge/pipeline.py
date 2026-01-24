"""
Integrated Paper to Knowledge Graph Pipeline

Combines PDFParser (MinerU/PyMuPDF) + NanoPRAG (LightRAG) for 
end-to-end paper parsing and knowledge graph construction.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Union, Dict
from dataclasses import dataclass


@dataclass
class PipelineResult:
    """Result from the paper processing pipeline."""
    
    source: str
    status: str
    entities_extracted: int = 0
    relations_extracted: int = 0
    query_ready: bool = False
    error: Optional[str] = None


class PaperToKnowledgeGraphPipeline:
    """
    End-to-end pipeline: PDF → Text → Knowledge Graph → RAG Query
    
    Combines:
    - PDFParser (PyMuPDF/MinerU) for document parsing
    - NanoPRAG (LightRAG) for knowledge graph construction and RAG
    
    Usage:
        pipeline = PaperToKnowledgeGraphPipeline(llm_provider="gemini")
        await pipeline.initialize()
        
        # Process papers
        await pipeline.process_paper("paper.pdf")
        
        # Query
        result = await pipeline.query("What is the carbon footprint?")
    """
    
    def __init__(
        self,
        working_dir: str = "./data/rag_storage",
        llm_provider: str = "gemini",
        pdf_parser_type: str = "pymupdf",  # pymupdf or mineru
    ):
        self.working_dir = Path(working_dir)
        self.llm_provider = llm_provider
        self.pdf_parser_type = pdf_parser_type
        
        self._pdf_parser = None
        self._rag = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all components."""
        if self._initialized:
            return
        
        # Initialize PDF Parser
        from nanop.data import PDFParser
        self._pdf_parser = PDFParser(parser_type=self.pdf_parser_type)
        
        # Initialize LightRAG
        from nanop.ai_knowledge import NanoPRAG, LIGHTRAG_AVAILABLE
        
        if LIGHTRAG_AVAILABLE:
            self._rag = NanoPRAG(
                working_dir=str(self.working_dir),
                llm_provider=self.llm_provider
            )
            await self._rag.initialize()
        else:
            print("⚠️ LightRAG not available. Install: pip install lightrag-hku")
            self._rag = None
        
        self._initialized = True
        print(f"✓ Pipeline initialized")
        print(f"  PDF Parser: {self.pdf_parser_type}")
        print(f"  LLM Provider: {self.llm_provider}")
        print(f"  LightRAG: {'Available' if self._rag else 'Not Available'}")
    
    async def process_paper(self, filepath: Union[str, Path]) -> PipelineResult:
        """
        Process a single paper: parse PDF and insert into knowledge graph.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            PipelineResult with processing status
        """
        if not self._initialized:
            await self.initialize()
        
        path = Path(filepath)
        
        # Step 1: Parse PDF
        try:
            doc = self._pdf_parser.parse_pdf(path)
            print(f"✓ Parsed: {path.name} ({doc.pages} pages)")
        except Exception as e:
            return PipelineResult(
                source=str(path),
                status="failed",
                error=f"PDF parsing failed: {e}"
            )
        
        # Step 2: Insert into LightRAG
        if self._rag:
            try:
                await self._rag.insert_text(doc.text)
                print(f"✓ Inserted into knowledge graph")
                
                return PipelineResult(
                    source=str(path),
                    status="success",
                    query_ready=True
                )
            except Exception as e:
                return PipelineResult(
                    source=str(path),
                    status="partial",
                    error=f"KG insertion failed: {e}"
                )
        else:
            return PipelineResult(
                source=str(path),
                status="partial",
                error="LightRAG not available"
            )
    
    async def process_directory(
        self, 
        directory: Union[str, Path],
        pattern: str = "*.pdf"
    ) -> List[PipelineResult]:
        """Process all PDFs in a directory."""
        if not self._initialized:
            await self.initialize()
        
        directory = Path(directory)
        results = []
        
        for pdf_path in directory.glob(pattern):
            result = await self.process_paper(pdf_path)
            results.append(result)
        
        success = sum(1 for r in results if r.status == "success")
        print(f"\n✓ Processed {success}/{len(results)} papers")
        
        return results
    
    async def query(
        self, 
        question: str, 
        mode: str = "hybrid"
    ) -> str:
        """
        Query the knowledge graph.
        
        Args:
            question: Question to ask
            mode: Query mode (local, global, hybrid)
            
        Returns:
            Answer string
        """
        if not self._rag:
            return "Error: LightRAG not available"
        
        result = await self._rag.query(question, mode=mode)
        return result.answer
    
    async def get_knowledge_graph(self) -> Dict:
        """Export the constructed knowledge graph."""
        if not self._rag:
            return {"error": "LightRAG not available"}
        
        return await self._rag.get_knowledge_graph()
    
    async def close(self) -> None:
        """Clean up resources."""
        if self._rag:
            await self._rag.close()


# Synchronous convenience wrapper
class PaperToKGPipelineSync:
    """Synchronous wrapper for the pipeline."""
    
    def __init__(self, **kwargs):
        self._async_pipeline = PaperToKnowledgeGraphPipeline(**kwargs)
        self._loop = None
    
    def _run(self, coro):
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        return self._loop.run_until_complete(coro)
    
    def initialize(self):
        self._run(self._async_pipeline.initialize())
    
    def process_paper(self, filepath) -> PipelineResult:
        return self._run(self._async_pipeline.process_paper(filepath))
    
    def process_directory(self, directory, pattern="*.pdf") -> List[PipelineResult]:
        return self._run(self._async_pipeline.process_directory(directory, pattern))
    
    def query(self, question: str, mode: str = "hybrid") -> str:
        return self._run(self._async_pipeline.query(question, mode))
    
    def get_knowledge_graph(self) -> Dict:
        return self._run(self._async_pipeline.get_knowledge_graph())
    
    def close(self):
        self._run(self._async_pipeline.close())


if __name__ == "__main__":
    print("Paper to Knowledge Graph Pipeline")
    print("=" * 50)
    print()
    print("Usage:")
    print("  pipeline = PaperToKGPipelineSync(llm_provider='gemini')")
    print("  pipeline.initialize()")
    print("  pipeline.process_paper('paper.pdf')")
    print("  answer = pipeline.query('What is the carbon footprint?')")
