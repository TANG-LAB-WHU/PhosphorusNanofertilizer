"""
NanoP AI Knowledge Module Demonstration

This script demonstrates the end-to-end pipeline:
1. Parsing a research paper (PDF) via MinerU/PyMuPDF
2. Extracting structured LCA/TEA data via Gemini API
3. Ingesting both full text and structured facts into LightRAG
4. Querying the knowledge graph for high-precision answers
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from nanop.ai_knowledge import PaperToKGPipelineSync, LIGHTRAG_AVAILABLE
from nanop.data import PDFParser

async def run_ai_demo():
    print("=" * 70)
    print("   NANO HYDROXYAPATITE PHOSPHORUS FERTILIZER (NanoP) AI KNOWLEDGE DEMO")
    print("=" * 70)

    if not LIGHTRAG_AVAILABLE:
        print("\n❌ LightRAG is not installed. Please run: pip install lightrag-hku")
        return

    # Prepare directories
    rag_dir = PROJECT_ROOT / "data" / "rag_storage"
    papers_dir = PROJECT_ROOT / "data" / "raw" / "papers"

    # 1. Initialize the Pipeline
    print("\n[1] Initializing AI Pipeline (Gemini + MinerU + LightRAG)...")
    # Setting extract_structured=True tells the pipeline to convert data to JSON 
    # before passing it to LightRAG for maximum precision.
    pipeline = PaperToKGPipelineSync(
        working_dir=str(rag_dir),
        llm_provider="gemini",
        pdf_parser_type="mineru",  # or "pymupdf"
        extract_structured=True
    )
    pipeline.initialize()

    # 2. Check for sample papers
    if not papers_dir.exists() or not list(papers_dir.glob("*.pdf")):
        print(f"\n[!] Please place some PDF papers in {papers_dir} to process.")
        print("    (Creating a mock analysis for demonstration purposes...)")
        
        # Injecting direct text for demonstration since we might not have a PDF
        mock_text = """
        Research Note: Synthesis of Nano Hydroxyapatite (NanoP) via Wet Chemical Route.
        The synthesis requires 100 kg of Calcium Chloride and 80 kg of Phosphoric Acid 
        per tonne of final product. The electricity consumption is 450 kWh/t.
        Capital expenditure (CAPEX) is estimated at $2.5 million for a 5000 t/year plant.
        Global Warming Potential (GWP) is calculated at 350 kg CO2-eq/tonne.
        """
        print("\n[2] Injecting mock document into LightRAG...")
        # We simulate the pipeline's internal fact-injection logic
        # In a real run, pipeline.process_paper("file.pdf") handles this automatically.
        from nanop.ai_knowledge import NanoPRAGSync
        rag = NanoPRAGSync(llm_provider="gemini")
        rag.initialize()
        rag.insert_text(mock_text)
    else:
        print(f"\n[2] Processing papers in {papers_dir}...")
        results = pipeline.process_directory(str(papers_dir), batch_size=2)
        print(f"    Processed {len(results)} papers.")

    # 3. Querying
    print("\n[3] Querying the Knowledge Graph...")
    
    questions = [
        "What are the main raw materials for NanoP synthesis?",
        "What is the energy consumption and carbon footprint mentioned in the reports?",
        "Compare the CAPEX across different production capacities."
    ]

    for q in questions:
        print(f"\nQ: {q}")
        # Using hybrid mode for comprehensive graph + vector search
        answer = pipeline.query(q, mode="hybrid")
        print(f"A: {answer}")

    # 4. View Graph Stats
    print("\n[4] Knowledge Graph Statistics:")
    kg_data = pipeline.get_knowledge_graph()
    if "stats" in kg_data:
        stats = kg_data["stats"]
        print(f"    Entities identified: {stats.get('entity_count', 0)}")
        print(f"    Relationships mapped: {stats.get('relationship_count', 0)}")

    print("\n" + "=" * 70)
    print("   AI Knowledge analysis completed.")
    print("=" * 70)
    
    pipeline.close()

if __name__ == "__main__":
    # Note: Requires GOOGLE_API_KEY environment variable for Gemini
    if "GOOGLE_API_KEY" not in os.environ:
        print("⚠️  Warning: GOOGLE_API_KEY not found in environment.")
    
    try:
        asyncio.run(run_ai_demo())
    except KeyboardInterrupt:
        pass
