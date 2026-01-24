"""
Pathways Module

Provides production pathway definitions for nanoP LCA-TEA analysis.
"""

from typing import Dict, List, Optional

from nanop.pathways.base_pathway import BasePathway
from nanop.pathways.nanop_synthesis import NanoPSynthesisPathway, create_nanop_pathway


# Pathway Registry
PATHWAY_REGISTRY: Dict[str, type] = {
    "NanoP-Synth": NanoPSynthesisPathway,
}


def list_pathways() -> List[str]:
    """
    List all available pathway codes.
    
    Returns:
        List of pathway code strings
    """
    return list(PATHWAY_REGISTRY.keys())


def get_pathway(
    code: str,
    country: str = "global",
    year: int = 2024,
    capacity_tonnes: float = 10000
) -> BasePathway:
    """
    Get a pathway instance by code.
    
    Args:
        code: Pathway code (e.g., 'NanoP-Synth')
        country: Country context
        year: Reference year
        capacity_tonnes: Annual capacity
        
    Returns:
        Pathway instance
        
    Raises:
        ValueError: If pathway code is not found
    """
    if code not in PATHWAY_REGISTRY:
        available = ", ".join(PATHWAY_REGISTRY.keys())
        raise ValueError(f"Unknown pathway code: {code}. Available: {available}")
    
    pathway_class = PATHWAY_REGISTRY[code]
    return pathway_class(
        country=country,
        year=year,
        capacity_tonnes=capacity_tonnes
    )


__all__ = [
    "BasePathway",
    "NanoPSynthesisPathway",
    "create_nanop_pathway",
    "list_pathways",
    "get_pathway",
    "PATHWAY_REGISTRY",
]
