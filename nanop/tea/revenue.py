"""
Revenue Calculator Module

Calculates revenue from product sales.
"""

from typing import Any, Dict, List


def calculate_revenue(products: List[Dict], functional_unit_kg: float = 1000) -> Dict:
    """
    Calculate revenue from products.
    
    Args:
        products: List of product dicts with name, quantity, price, unit
        functional_unit_kg: Functional unit in kg for scaling
        
    Returns:
        Dict with total revenue and breakdown
    """
    total = 0.0
    breakdown = {}
    
    for product in products:
        name = product.get("name", "Unknown")
        quantity = product.get("quantity", 0)  # per FU
        price = product.get("price", 0)  # per unit
        unit = product.get("unit", "kg")
        
        # Scale to functional unit if needed
        if unit == "kg":
            scaled_quantity = quantity * (functional_unit_kg / 1000)
        elif unit == "tonne":
            scaled_quantity = quantity * (functional_unit_kg / 1000)
        else:
            scaled_quantity = quantity
        
        revenue = scaled_quantity * price
        total += revenue
        breakdown[name] = revenue
    
    return {
        "total": total,
        "breakdown": breakdown
    }


if __name__ == "__main__":
    # Example usage
    products = [
        {"name": "NanoP Fertilizer", "quantity": 1000, "price": 1.2, "unit": "kg"},
        {"name": "CaCl2 Byproduct", "quantity": 50, "price": 0.1, "unit": "kg"},  
    ]
    
    result = calculate_revenue(products, 1000)
    print(f"Total revenue: ${result['total']:.2f}")
    print(f"Breakdown: {result['breakdown']}")
