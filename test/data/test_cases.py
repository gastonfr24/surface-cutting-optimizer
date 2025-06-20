"""
Test cases with known optimal solutions for Surface Cutting Optimizer
"""

from typing import Dict, List, Tuple, Any
from surface_optimizer.core.models import Stock, Order, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle


def get_all_test_cases() -> Dict[str, Tuple[List[Stock], List[Order], Dict[str, Any]]]:
    """Get all available test cases"""
    return {
        "simple_rectangular": generate_simple_rectangular_test(),
        "rotation_required": generate_rotation_test(),
        "mixed_materials": generate_mixed_materials_test()
    }


def generate_simple_rectangular_test() -> Tuple[List[Stock], List[Order], Dict[str, Any]]:
    """Simple rectangular test case"""
    
    stocks = [
        Stock("S1", 1000, 800, 6.0, MaterialType.GLASS, 100.0)
    ]
    
    orders = [
        Order("O1", Rectangle(400, 300), 1, Priority.HIGH, MaterialType.GLASS),
        Order("O2", Rectangle(300, 200), 1, Priority.MEDIUM, MaterialType.GLASS)
    ]
    
    optimal_solution = {
        "description": "Simple rectangular case",
        "total_stock_used": 1,
        "total_orders_fulfilled": 2,
        "efficiency_percentage": 75.0,  # Expected minimum efficiency
        "notes": "Should fit both rectangles efficiently"
    }
    
    return stocks, orders, optimal_solution


def generate_rotation_test() -> Tuple[List[Stock], List[Order], Dict[str, Any]]:
    """Test case where rotation improves efficiency"""
    
    stocks = [
        Stock("S1", 1000, 600, 6.0, MaterialType.METAL, 150.0)
    ]
    
    orders = [
        Order("O1", Rectangle(800, 400), 1, Priority.HIGH, MaterialType.METAL),
        Order("O2", Rectangle(400, 500), 1, Priority.MEDIUM, MaterialType.METAL)  # Needs rotation
    ]
    
    optimal_solution = {
        "description": "Rotation required case",
        "total_stock_used": 1,
        "total_orders_fulfilled": 2,
        "efficiency_percentage": 80.0,
        "notes": "Second rectangle should be rotated to fit"
    }
    
    return stocks, orders, optimal_solution


def generate_mixed_materials_test() -> Tuple[List[Stock], List[Order], Dict[str, Any]]:
    """Test case with multiple material types"""
    
    stocks = [
        Stock("Glass1", 2000, 1000, 6.0, MaterialType.GLASS, 100.0),
        Stock("Metal1", 1500, 1200, 3.0, MaterialType.METAL, 150.0)
    ]
    
    orders = [
        Order("G1", Rectangle(800, 600), 1, Priority.HIGH, MaterialType.GLASS),
        Order("M1", Rectangle(600, 400), 1, Priority.HIGH, MaterialType.METAL),
        Order("G2", Rectangle(400, 300), 2, Priority.MEDIUM, MaterialType.GLASS)
    ]
    
    optimal_solution = {
        "description": "Mixed materials case",
        "total_stock_used": 2,
        "total_orders_fulfilled": 3,
        "efficiency_percentage": 65.0,
        "notes": "Should use both material types appropriately"
    }
    
    return stocks, orders, optimal_solution


def validate_result_against_optimal(result, optimal_solution: Dict[str, Any], 
                                  tolerance: float = 5.0) -> Dict[str, bool]:
    """Validate optimization result against known optimal solution"""
    
    validation = {}
    
    # Check stock usage
    validation['stock_usage_ok'] = (
        result.total_stock_used <= optimal_solution.get('total_stock_used', float('inf'))
    )
    
    # Check order fulfillment
    validation['orders_fulfilled_ok'] = (
        result.total_orders_fulfilled >= optimal_solution.get('total_orders_fulfilled', 0)
    )
    
    # Check efficiency (with tolerance)
    expected_efficiency = optimal_solution.get('efficiency_percentage', 0)
    efficiency_diff = abs(result.efficiency_percentage - expected_efficiency)
    validation['efficiency_ok'] = efficiency_diff <= tolerance
    
    # Overall validation
    validation['overall_pass'] = all(validation.values())
    
    return validation 