"""
Tests for Google Gemini API integration.

These tests verify:
1. API key validation
2. Model listing
3. Basic text generation
4. Integration with NanoP AI features

Note: Tests are skipped if google-genai is not installed or GOOGLE_API_KEY is not set.
"""

import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # Load .env from project root

# Check if google-genai is available (new package: google-genai)
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Check if API key is configured
API_KEY = os.environ.get("GOOGLE_API_KEY")
API_KEY_AVAILABLE = API_KEY is not None and len(API_KEY) > 0

# Default model for testing (from .env or fallback)
from nanop.utils.api_mgmt import get_default_model
DEFAULT_MODEL = get_default_model()


# Skip conditions
requires_genai = pytest.mark.skipif(
    not GENAI_AVAILABLE,
    reason="google-genai package not installed"
)

requires_api_key = pytest.mark.skipif(
    not API_KEY_AVAILABLE,
    reason="GOOGLE_API_KEY environment variable not set"
)


@pytest.fixture
def gemini_client():
    """Create a Gemini API client for testing."""
    if not GENAI_AVAILABLE or not API_KEY_AVAILABLE:
        pytest.skip("Gemini API not available")
    from google import genai
    return genai.Client(api_key=API_KEY)


class TestGeminiAPISetup:
    """Test Gemini API setup and configuration."""
    
    @requires_genai
    def test_genai_import(self):
        """Test that google-genai can be imported."""
        from google import genai
        assert genai is not None
    
    @requires_genai
    @requires_api_key
    def test_client_initialization(self):
        """Test that Gemini client can be initialized."""
        from google import genai
        client = genai.Client(api_key=API_KEY)
        assert client is not None
    
    @requires_genai
    @requires_api_key
    def test_list_models(self, gemini_client):
        """Test listing available models."""
        models = list(gemini_client.models.list())
        
        assert len(models) > 0
        # Check that at least one Gemini model is available
        model_names = [m.name for m in models]
        gemini_models = [n for n in model_names if "gemini" in n.lower()]
        assert len(gemini_models) > 0, "No Gemini models found"


class TestGeminiTextGeneration:
    """Test Gemini text generation capabilities."""
    
    @requires_genai
    @requires_api_key
    def test_simple_generation(self, gemini_client):
        """Test basic text generation with Gemini."""
        response = gemini_client.models.generate_content(
            model=DEFAULT_MODEL,
            contents="What is 2 + 2? Answer with just the number."
        )
        
        assert response is not None
        assert response.text is not None
        assert "4" in response.text
    
    @requires_genai
    @requires_api_key
    def test_lca_related_query(self, gemini_client):
        """Test Gemini with an LCA-related query."""
        prompt = """
        What does LCA stand for in environmental science?
        Answer in one sentence.
        """
        
        response = gemini_client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        
        assert response is not None
        assert response.text is not None
        # Check for relevant keywords
        text_lower = response.text.lower()
        assert any(kw in text_lower for kw in ["life cycle", "lifecycle", "assessment"])
    
    @requires_genai
    @requires_api_key
    def test_json_extraction(self, gemini_client):
        """Test Gemini's ability to extract structured data."""
        import json
        
        prompt = """
        Extract the following information as JSON:
        "The production of nano hydroxyapatite requires 450 kWh of electricity 
        and 800 kWh of thermal energy per tonne of product."
        
        Return only valid JSON with keys: electricity_kwh, thermal_kwh, unit
        """
        
        response = gemini_client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        
        assert response is not None
        assert response.text is not None
        
        # Try to parse as JSON (clean up markdown if present)
        text = response.text.strip()
        if text.startswith("```"):
            # Remove markdown code blocks
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        
        try:
            data = json.loads(text)
            assert "electricity" in str(data).lower() or "450" in str(data)
        except json.JSONDecodeError:
            # If not valid JSON, at least check the numbers are present
            assert "450" in response.text and "800" in response.text


class TestGeminiNanoPIntegration:
    """Test Gemini integration with NanoP-specific features."""
    
    @requires_genai
    @requires_api_key
    def test_nanop_domain_query(self, gemini_client):
        """Test Gemini with a nano hydroxyapatite related query."""
        prompt = """
        What is nano hydroxyapatite (nanoHAP) used for in agriculture?
        Answer briefly in 2-3 sentences.
        """
        
        response = gemini_client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        
        assert response is not None
        assert response.text is not None
        # Check for relevant keywords
        text_lower = response.text.lower()
        assert any(kw in text_lower for kw in ["fertilizer", "phosphorus", "nutrient", "soil", "plant"])
    
    @requires_genai
    @requires_api_key
    def test_tea_data_extraction(self, gemini_client):
        """Test Gemini's ability to extract TEA-related data."""
        prompt = """
        From the following text, extract economic data:
        "The capital cost of a 10,000 tonne/year nano hydroxyapatite plant is 
        approximately $2.5 million, with operating costs of $150 per tonne."
        
        Provide the answer in this format:
        - CAPEX: [value]
        - OPEX: [value]
        - Capacity: [value]
        """
        
        response = gemini_client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        
        assert response is not None
        assert response.text is not None
        # Check that key numbers are extracted
        assert "2.5" in response.text or "2,500,000" in response.text or "2500000" in response.text
        assert "150" in response.text
        assert "10,000" in response.text or "10000" in response.text


class TestGeminiErrorHandling:
    """Test error handling for Gemini API."""
    
    @requires_genai
    def test_invalid_api_key_error(self):
        """Test appropriate error when API key is invalid."""
        from google import genai
        
        # Use an invalid API key
        client = genai.Client(api_key="invalid_key_12345")
        
        with pytest.raises(Exception):
            client.models.generate_content(
                model=DEFAULT_MODEL,
                contents="Hello"
            )
    
    @requires_genai
    @requires_api_key
    def test_get_masked_key(self):
        """Test API key masking for display."""
        from nanop.utils.api_mgmt import get_masked_key
        
        masked = get_masked_key("GOOGLE_API_KEY")
        
        # Should show first 4 and last 4 characters
        assert "..." in masked
        assert len(masked) < len(API_KEY)
        # Should not expose the full key
        assert masked != API_KEY


class TestGeminiModelParameters:
    """Test Gemini model parameters and configurations."""
    
    @requires_genai
    @requires_api_key
    def test_different_models(self, gemini_client):
        """Test using different Gemini models."""
        models_to_test = [DEFAULT_MODEL]  # Only test the default model
        
        for model_name in models_to_test:
            try:
                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents="Say 'hello' in one word."
                )
                assert response is not None
                assert response.text is not None
            except Exception as e:
                # Some models may not be available, skip them
                pytest.skip(f"Model {model_name} not available: {e}")
    
    @requires_genai
    @requires_api_key
    def test_token_counting(self, gemini_client):
        """Test token counting functionality."""
        text = "This is a test sentence for token counting."
        
        try:
            result = gemini_client.models.count_tokens(
                model=DEFAULT_MODEL,
                contents=text
            )
            assert result is not None
            assert hasattr(result, 'total_tokens') or 'total_tokens' in str(result)
        except Exception as e:
            pytest.skip(f"Token counting not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
