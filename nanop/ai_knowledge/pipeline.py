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
    pages: int = 0
    structured_data_extracted: bool = False
    query_ready: bool = False
    error: Optional[str] = None


class PaperToKnowledgeGraphPipeline:
    """
    Enhanced End-to-end pipeline for large-scale processing.
    PDF → Text (MinerU) → Structured Extraction (AI) → Knowledge Graph (LightRAG)
    """
    
    def __init__(
        self,
        working_dir: str = "./data/rag_storage",
        llm_provider: str = "gemini",
        pdf_parser_type: str = "mineru",
        extract_structured: bool = True,
    ):
        self.working_dir = Path(working_dir)
        self.llm_provider = llm_provider
        self.pdf_parser_type = pdf_parser_type
        self.extract_structured = extract_structured
        
        self._pdf_parser = None
        self._ai_extractor = None
        self._rag = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all components."""
        if self._initialized:
            return
        
        # Initialize PDF Parser
        from nanop.iodata import PDFParser
        self._pdf_parser = PDFParser(parser_type=self.pdf_parser_type)
        
        # Initialize AI Extractor for structured data
        from nanop.ai_knowledge import AIPaperParser
        self._ai_extractor = AIPaperParser(backend=self.llm_provider)
        
        # Initialize LightRAG
        from nanop.ai_knowledge import NanoPRAG, LIGHTRAG_AVAILABLE
        
        if LIGHTRAG_AVAILABLE:
            self._rag = NanoPRAG(
                working_dir=str(self.working_dir),
                llm_provider=self.llm_provider
            )
            await self._rag.initialize()
        else:
            print("⚠️ LightRAG not available.")
            self._rag = None
        
        self._initialized = True
        print(f"✓ Pipeline initialized for large-scale processing")
    
    async def process_paper(self, filepath: Union[str, Path]) -> PipelineResult:
        """
        Process a single paper with dual-track ingestion:
        1. Markdown text for context
        2. Structured JSON fact blocks for precision
        """
        if not self._initialized:
            await self.initialize()
        
        path = Path(filepath)
        result = PipelineResult(source=str(path), status="processing")
        
        # Step 1: High-quality PDF Parsing
        try:
            doc = self._pdf_parser.parse_pdf(path)
            result.pages = doc.pages
        except Exception as e:
            result.status = "failed"
            result.error = f"Parsing error: {e}"
            return result
        
        # Step 2: Structured Fact Extraction (Optional but recommended)
        json_facts = ""
        if self.extract_structured and self._ai_extractor:
            try:
                # Extract LCI and TEA data
                lci = self._ai_extractor.extract_lci(doc.text, source=path.name)
                tea = self._ai_extractor.extract_tea(doc.text, source=path.name)
                
                # Combine into high-density facts
                facts = {
                    "lca_inventory": lci.to_dict(),
                    "tea_metrics": tea.to_dict(),
                    "tables_found": len(doc.tables)
                }
                json_facts = (
                    f"\n\n### HIGH-PRECISION STRUCTURED DATA FOR {path.name} ###\n"
                    f"```json\n{json.dumps(facts, indent=2, ensure_ascii=False)}\n```\n"
                )
                result.structured_data_extracted = True
            except Exception as e:
                print(f"⚠️ Structured extraction failed for {path.name}: {e}")
        
        # Step 3: Dual-Track Ingestion into LightRAG
        if self._rag:
            try:
                # Track 1: Full text for context and semantic graph
                await self._rag.insert_text(doc.text)
                
                # Track 2: Structured facts for precision queries (LCA/TEA values)
                if json_facts:
                    await self._rag.insert_text(json_facts)
                
                result.status = "success"
                result.query_ready = True
            except Exception as e:
                result.status = "failed"
                result.error = f"Ingestion error: {e}"
        
        return result
    
    async def process_directory(
        self, 
        directory: Union[str, Path],
        pattern: str = "*.pdf",
        batch_size: int = 10
    ) -> List[PipelineResult]:
        """
        Process directory in batches for scalability.
        """
        if not self._initialized:
            await self.initialize()
        
        directory = Path(directory)
        pdf_files = list(directory.glob(pattern))
        all_results = []
        
        print(f"🚀 Starting batch processing of {len(pdf_files)} papers...")
        
        for i in range(0, len(pdf_files), batch_size):
            batch = pdf_files[i:i+batch_size]
            tasks = [self.process_paper(f) for f in batch]
            batch_results = await asyncio.gather(*tasks)
            all_results.extend(batch_results)
            
            success = sum(1 for r in batch_results if r.status == "success")
            print(f"  Batch {i//batch_size + 1}: {success}/{len(batch)} successful")
        
        return all_results
    
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
    
    def process_directory(self, directory, pattern="*.pdf", batch_size=10) -> List[PipelineResult]:
        return self._run(self._async_pipeline.process_directory(directory, pattern, batch_size))
    
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
