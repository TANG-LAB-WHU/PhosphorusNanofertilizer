"""
AI Paper Parser Module

Uses LLM to extract structured LCA-TEA data from research papers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import json
import re


@dataclass
class ExtractedLCIData:
    """Extracted LCI data from a paper."""
    
    process_name: str
    functional_unit: str = ""
    inputs: List[Dict] = field(default_factory=list)
    outputs: List[Dict] = field(default_factory=list)
    emissions: List[Dict] = field(default_factory=list)
    energy_consumption: Dict = field(default_factory=dict)
    source: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "process_name": self.process_name,
            "functional_unit": self.functional_unit,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "emissions": self.emissions,
            "energy_consumption": self.energy_consumption,
            "source": self.source,
            "confidence": self.confidence
        }


@dataclass
class ExtractedTEAData:
    """Extracted TEA data from a paper."""
    
    process_name: str
    capital_cost: Optional[float] = None
    operating_cost: Optional[float] = None
    product_price: Optional[float] = None
    production_capacity: Optional[float] = None
    currency: str = "USD"
    year: int = 2024
    source: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "process_name": self.process_name,
            "capital_cost": self.capital_cost,
            "operating_cost": self.operating_cost,
            "product_price": self.product_price,
            "production_capacity": self.production_capacity,
            "currency": self.currency,
            "year": self.year,
            "source": self.source,
            "confidence": self.confidence
        }


@dataclass 
class PaperMetadata:
    """Metadata extracted from a paper."""
    
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: int = 0
    doi: str = ""
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)


class AIFeatureDetector:
    """
    Detect available AI features and LLM backends.
    """
    
    SUPPORTED_BACKENDS = [
        "google_genai",   # Google Generative AI (Gemini)
        "openai",         # OpenAI API
        "anthropic",      # Anthropic Claude
        "ollama",         # Local Ollama
        "transformers",   # HuggingFace Transformers
    ]
    
    def __init__(self):
        self._available_backends = {}
        self._detect_backends()
    
    def _detect_backends(self) -> None:
        """Detect available LLM backends."""
        
        # Check Google Generative AI
        try:
            import google.generativeai as genai
            self._available_backends["google_genai"] = {
                "available": True,
                "version": getattr(genai, "__version__", "unknown"),
                "module": genai
            }
        except ImportError:
            self._available_backends["google_genai"] = {"available": False}
        
        # Check OpenAI
        try:
            import openai
            self._available_backends["openai"] = {
                "available": True,
                "version": openai.__version__,
                "module": openai
            }
        except ImportError:
            self._available_backends["openai"] = {"available": False}
        
        # Check Anthropic
        try:
            import anthropic
            self._available_backends["anthropic"] = {
                "available": True,
                "version": getattr(anthropic, "__version__", "unknown"),
                "module": anthropic
            }
        except ImportError:
            self._available_backends["anthropic"] = {"available": False}
        
        # Check Ollama
        try:
            import ollama
            self._available_backends["ollama"] = {
                "available": True,
                "version": getattr(ollama, "__version__", "unknown"),
                "module": ollama
            }
        except ImportError:
            self._available_backends["ollama"] = {"available": False}
        
        # Check Transformers
        try:
            import transformers
            self._available_backends["transformers"] = {
                "available": True,
                "version": transformers.__version__,
                "module": transformers
            }
        except ImportError:
            self._available_backends["transformers"] = {"available": False}
    
    def list_available(self) -> List[str]:
        """List available backends."""
        return [k for k, v in self._available_backends.items() if v.get("available")]
    
    def is_available(self, backend: str) -> bool:
        """Check if a backend is available."""
        return self._available_backends.get(backend, {}).get("available", False)
    
    def get_best_backend(self) -> Optional[str]:
        """Get the best available backend."""
        priority = ["google_genai", "openai", "anthropic", "ollama", "transformers"]
        for backend in priority:
            if self.is_available(backend):
                return backend
        return None
    
    def get_status(self) -> Dict:
        """Get status of all backends."""
        return {
            name: {
                "available": info.get("available", False),
                "version": info.get("version", "N/A")
            }
            for name, info in self._available_backends.items()
        }


class AIPaperParser:
    """
    AI-powered paper parser for extracting LCA-TEA data.
    
    Supports multiple LLM backends:
    - Google Generative AI (Gemini)
    - OpenAI
    - Anthropic Claude
    - Local Ollama
    - HuggingFace Transformers
    """
    
    # Extraction prompts
    LCI_EXTRACTION_PROMPT = """
You are an expert in Life Cycle Assessment (LCA). Extract LCI (Life Cycle Inventory) data from the following research paper text.

Focus on:
1. Process name and functional unit
2. Input materials (name, quantity, unit)
3. Output products (name, quantity, unit)
4. Emissions to air, water, soil
5. Energy consumption (electricity, heat, fuel)

Return the data as JSON with this structure:
{
    "process_name": "...",
    "functional_unit": "...",
    "inputs": [{"name": "...", "quantity": ..., "unit": "..."}],
    "outputs": [{"name": "...", "quantity": ..., "unit": "..."}],
    "emissions": [{"name": "...", "quantity": ..., "unit": "...", "compartment": "air/water/soil"}],
    "energy_consumption": {"electricity_kwh": ..., "heat_mj": ...}
}

Paper text:
{text}
"""

    TEA_EXTRACTION_PROMPT = """
You are an expert in Techno-Economic Analysis (TEA). Extract economic data from the following research paper text.

Focus on:
1. Capital costs (CAPEX)
2. Operating costs (OPEX)
3. Product prices
4. Production capacity
5. Currency and reference year

Return the data as JSON with this structure:
{
    "process_name": "...",
    "capital_cost": ...,
    "operating_cost": ...,
    "product_price": ...,
    "production_capacity": ...,
    "currency": "USD/EUR/CNY",
    "year": 2024
}

Paper text:
{text}
"""
    
    def __init__(self, backend: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the AI paper parser.
        
        Args:
            backend: LLM backend to use (auto-detect if None)
            api_key: API key for the backend (uses env var if None)
        """
        self.detector = AIFeatureDetector()
        self.backend = backend or self.detector.get_best_backend()
        self.api_key = api_key
        self._client = None
        
        if self.backend:
            self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the LLM client."""
        if self.backend == "google_genai":
            import google.generativeai as genai
            import os
            key = self.api_key or os.environ.get("GOOGLE_API_KEY")
            if key:
                genai.configure(api_key=key)
            self._client = genai.GenerativeModel("gemini-1.5-flash")
        
        elif self.backend == "openai":
            import openai
            import os
            key = self.api_key or os.environ.get("OPENAI_API_KEY")
            self._client = openai.OpenAI(api_key=key)
        
        elif self.backend == "anthropic":
            import anthropic
            import os
            key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
            self._client = anthropic.Anthropic(api_key=key)
        
        elif self.backend == "ollama":
            import ollama
            self._client = ollama
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with a prompt."""
        if not self._client:
            raise RuntimeError("No LLM backend available")
        
        if self.backend == "google_genai":
            response = self._client.generate_content(prompt)
            return response.text
        
        elif self.backend == "openai":
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        elif self.backend == "anthropic":
            response = self._client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif self.backend == "ollama":
            response = self._client.generate(
                model="llama3.2",
                prompt=prompt
            )
            return response["response"]
        
        return ""
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response."""
        # Try to find JSON block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            text = json_match.group(1)
        
        # Try to find JSON object
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return {}
    
    def extract_lci(self, text: str, source: str = "") -> ExtractedLCIData:
        """
        Extract LCI data from paper text.
        
        Args:
            text: Paper text content
            source: Source identifier (e.g., filename, DOI)
            
        Returns:
            ExtractedLCIData object
        """
        prompt = self.LCI_EXTRACTION_PROMPT.format(text=text[:10000])  # Limit text length
        
        try:
            response = self._call_llm(prompt)
            data = self._extract_json(response)
            
            return ExtractedLCIData(
                process_name=data.get("process_name", "Unknown"),
                functional_unit=data.get("functional_unit", ""),
                inputs=data.get("inputs", []),
                outputs=data.get("outputs", []),
                emissions=data.get("emissions", []),
                energy_consumption=data.get("energy_consumption", {}),
                source=source,
                confidence=0.8 if data else 0.0
            )
        except Exception as e:
            return ExtractedLCIData(
                process_name="Error",
                source=source,
                confidence=0.0
            )
    
    def extract_tea(self, text: str, source: str = "") -> ExtractedTEAData:
        """
        Extract TEA data from paper text.
        
        Args:
            text: Paper text content
            source: Source identifier
            
        Returns:
            ExtractedTEAData object
        """
        prompt = self.TEA_EXTRACTION_PROMPT.format(text=text[:10000])
        
        try:
            response = self._call_llm(prompt)
            data = self._extract_json(response)
            
            return ExtractedTEAData(
                process_name=data.get("process_name", "Unknown"),
                capital_cost=data.get("capital_cost"),
                operating_cost=data.get("operating_cost"),
                product_price=data.get("product_price"),
                production_capacity=data.get("production_capacity"),
                currency=data.get("currency", "USD"),
                year=data.get("year", 2024),
                source=source,
                confidence=0.8 if data else 0.0
            )
        except Exception as e:
            return ExtractedTEAData(
                process_name="Error",
                source=source,
                confidence=0.0
            )
    
    def parse_paper(self, filepath: str) -> Dict:
        """
        Parse a research paper and extract all LCA-TEA data.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Dict with extracted LCI, TEA, and metadata
        """
        from nanop.data import PDFParser
        
        parser = PDFParser()
        doc = parser.parse_pdf(filepath)
        
        text = doc.text
        source = Path(filepath).name
        
        return {
            "source": source,
            "lci_data": self.extract_lci(text, source).to_dict(),
            "tea_data": self.extract_tea(text, source).to_dict(),
            "word_count": parsed.get("word_count", 0),
            "backend_used": self.backend
        }
    
    def get_status(self) -> Dict:
        """Get parser status."""
        return {
            "active_backend": self.backend,
            "client_initialized": self._client is not None,
            "available_backends": self.detector.get_status()
        }


# Rule-based fallback for when no LLM is available
class RuleBasedExtractor:
    """
    Rule-based extraction when no LLM backend is available.
    Uses regex patterns to extract common LCA-TEA values.
    """
    
    # Common patterns
    PATTERNS = {
        "electricity": r"electricity[:\s]+(\d+(?:\.\d+)?)\s*(kWh|MWh|GJ)",
        "co2_emission": r"CO2[:\s]+(\d+(?:\.\d+)?)\s*(kg|g|t)",
        "capex": r"(?:CAPEX|capital cost)[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(M|K|million|thousand)?",
        "opex": r"(?:OPEX|operating cost)[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(M|K|million|thousand)?",
        "capacity": r"(?:capacity|production)[:\s]+(\d+(?:,\d{3})*(?:\.\d+)?)\s*(t|kg|tonne)/(?:year|y|a)",
    }
    
    def extract(self, text: str) -> Dict:
        """Extract data using regex patterns."""
        results = {}
        
        for key, pattern in self.PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1).replace(",", ""))
                unit = match.group(2) if len(match.groups()) > 1 else ""
                results[key] = {"value": value, "unit": unit}
        
        return results


if __name__ == "__main__":
    # Check available backends
    detector = AIFeatureDetector()
    print("AI Feature Detection:")
    print(f"  Available backends: {detector.list_available()}")
    print(f"  Best backend: {detector.get_best_backend()}")
    print("\nStatus:")
    for name, status in detector.get_status().items():
        available = "✓" if status["available"] else "✗"
        print(f"  {available} {name}: {status['version']}")
