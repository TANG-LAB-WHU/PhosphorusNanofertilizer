"""
RAG (Retrieval-Augmented Generation) Engine Module

Provides document chunking, embedding, and retrieval for LCA-TEA knowledge.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
import hashlib


@dataclass
class DocumentChunk:
    """A chunk of text from a document."""
    
    id: str
    text: str
    source: str
    page: int = 0
    metadata: Dict = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(self.text[:100].encode()).hexdigest()[:12]


@dataclass
class RetrievalResult:
    """Result from retrieval query."""
    
    chunk: DocumentChunk
    score: float
    context: str = ""


class TextChunker:
    """
    Split text into chunks for embedding.
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separator: str = "\n"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    def chunk(self, text: str, source: str = "") -> List[DocumentChunk]:
        """Split text into overlapping chunks."""
        chunks = []
        
        # Split by separator first
        paragraphs = text.split(self.separator)
        
        current_chunk = ""
        chunk_idx = 0
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + self.separator
            else:
                if current_chunk:
                    chunks.append(DocumentChunk(
                        id=f"{source}_{chunk_idx}",
                        text=current_chunk.strip(),
                        source=source,
                        metadata={"chunk_idx": chunk_idx}
                    ))
                    chunk_idx += 1
                
                # Handle overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if self.chunk_overlap else ""
                current_chunk = overlap_text + para + self.separator
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(DocumentChunk(
                id=f"{source}_{chunk_idx}",
                text=current_chunk.strip(),
                source=source,
                metadata={"chunk_idx": chunk_idx}
            ))
        
        return chunks


class SimpleVectorStore:
    """
    Simple in-memory vector store.
    
    For production, use ChromaDB, Pinecone, or similar.
    """
    
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.embeddings: List[List[float]] = []
    
    def add(self, chunk: DocumentChunk) -> None:
        """Add a chunk to the store."""
        self.chunks.append(chunk)
        if chunk.embedding:
            self.embeddings.append(chunk.embedding)
    
    def add_batch(self, chunks: List[DocumentChunk]) -> None:
        """Add multiple chunks."""
        for chunk in chunks:
            self.add(chunk)
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Search for similar chunks."""
        if not self.embeddings:
            return []
        
        # Compute cosine similarities
        scores = []
        for i, emb in enumerate(self.embeddings):
            score = self._cosine_similarity(query_embedding, emb)
            scores.append((i, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in scores[:top_k]:
            results.append(RetrievalResult(
                chunk=self.chunks[idx],
                score=score
            ))
        
        return results
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0
        
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot / (norm_a * norm_b)
    
    def size(self) -> int:
        """Return number of stored chunks."""
        return len(self.chunks)


class RAGEngine:
    """
    RAG Engine for LCA-TEA knowledge retrieval.
    
    Components:
    - Text chunking
    - Embedding (placeholder - requires external model)
    - Vector storage
    - Retrieval
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_fn: Optional[Callable] = None
    ):
        self.chunker = TextChunker(chunk_size, chunk_overlap)
        self.vector_store = SimpleVectorStore()
        self.embedding_fn = embedding_fn or self._default_embedding
    
    def _default_embedding(self, text: str) -> List[float]:
        """
        Simple bag-of-words embedding (placeholder).
        
        For production, use sentence-transformers, OpenAI, etc.
        """
        # Simple character-based embedding for demo
        vocab_size = 128
        embedding = [0.0] * vocab_size
        
        for char in text.lower():
            idx = ord(char) % vocab_size
            embedding[idx] += 1
        
        # Normalize
        total = sum(embedding) or 1
        return [x / total for x in embedding]
    
    def add_document(self, text: str, source: str = "unknown") -> int:
        """
        Add a document to the knowledge base.
        
        Returns:
            Number of chunks added
        """
        chunks = self.chunker.chunk(text, source)
        
        for chunk in chunks:
            chunk.embedding = self.embedding_fn(chunk.text)
        
        self.vector_store.add_batch(chunks)
        return len(chunks)
    
    def query(
        self,
        query: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Query the knowledge base.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of retrieval results
        """
        query_embedding = self.embedding_fn(query)
        return self.vector_store.search(query_embedding, top_k)
    
    def get_context(
        self,
        query: str,
        max_chunks: int = 3
    ) -> str:
        """
        Get context string for LLM prompt.
        
        Args:
            query: Query text
            max_chunks: Maximum chunks to include
            
        Returns:
            Context string
        """
        results = self.query(query, top_k=max_chunks)
        
        context_parts = []
        for r in results:
            context_parts.append(f"[Source: {r.chunk.source}]\n{r.chunk.text}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def stats(self) -> Dict:
        """Get engine statistics."""
        return {
            "total_chunks": self.vector_store.size(),
            "chunk_size": self.chunker.chunk_size,
            "chunk_overlap": self.chunker.chunk_overlap
        }


if __name__ == "__main__":
    # Example usage
    engine = RAGEngine()
    
    # Add some sample documents
    sample_text = """
    Nano hydroxyapatite (nanoHAP) is a biocompatible calcium phosphate compound 
    with the chemical formula Ca10(PO4)6(OH)2. It is widely used in biomedical 
    applications and increasingly as a slow-release phosphorus fertilizer.
    
    The wet chemical precipitation method is the most common synthesis route.
    Calcium chloride and phosphoric acid are mixed under controlled pH conditions
    to produce nano-sized hydroxyapatite particles.
    
    Environmental benefits include reduced phosphorus runoff compared to 
    conventional fertilizers, leading to lower eutrophication potential.
    """
    
    n_chunks = engine.add_document(sample_text, source="sample_paper")
    print(f"Added {n_chunks} chunks to knowledge base")
    
    # Query
    results = engine.query("phosphorus fertilizer synthesis")
    print(f"\nQuery results ({len(results)} chunks):")
    for r in results:
        print(f"  Score: {r.score:.3f} | {r.chunk.text[:50]}...")
