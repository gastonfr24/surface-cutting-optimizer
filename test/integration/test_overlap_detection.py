#!/usr/bin/env python3
"""
Modern pytest-based tests for overlap detection

Tests the critical overlap detection functionality that ensures
shapes don't overlap in optimization results.
"""

import pytest
from typing import List, Tuple

from surface_optimizer.core.models import Stock, Order, MaterialType, Priority, PlacedShape
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


# Fixtures
@pytest.fixture
def standard_stock():
    """Standard stock for overlap testing"""
    return Stock('S1', 1000, 1000, 5.0, MaterialType.METAL, 50.0)


@pytest.fixture
def two_squares_orders():
    """Two 500x500 squares that should fit without overlap"""
    return [
        Order('Square1', Rectangle(500, 500), 1, Priority.HIGH, MaterialType.METAL, 5.0),
        Order('Square2', Rectangle(500, 500), 1, Priority.HIGH, MaterialType.METAL, 5.0)
    ]


@pytest.fixture
def multiple_rectangles_orders():
    """Multiple rectangles for complex overlap testing"""
    return [
        Order('Rect1', Rectangle(400, 300), 1, Priority.HIGH),
        Order('Rect2', Rectangle(300, 400), 1, Priority.HIGH),
        Order('Rect3', Rectangle(250, 200), 1, Priority.MEDIUM),
        Order('Rect4', Rectangle(200, 250), 1, Priority.MEDIUM),
    ]


# Utility functions
def check_shapes_overlap(shape1: Rectangle, shape2: Rectangle) -> bool:
    """Check if two rectangles overlap"""
    return not (
        shape1.x + shape1.width <= shape2.x or 
        shape2.x + shape2.width <= shape1.x or 
        shape1.y + shape1.height <= shape2.y or 
        shape2.y + shape2.height <= shape1.y
    )


def check_all_placements_non_overlapping(placed_shapes: List[PlacedShape]) -> Tuple[bool, List[str]]:
    """
    Check that no placed shapes overlap.
    Returns (is_valid, list_of_overlapping_pairs)
    """
    overlaps = []
    
    for i in range(len(placed_shapes)):
        for j in range(i + 1, len(placed_shapes)):
            shape1 = placed_shapes[i].shape
            shape2 = placed_shapes[j].shape
            
            if isinstance(shape1, Rectangle) and isinstance(shape2, Rectangle):
                if check_shapes_overlap(shape1, shape2):
                    overlaps.append(f"{placed_shapes[i].order_id} overlaps with {placed_shapes[j].order_id}")
    
    return len(overlaps) == 0, overlaps


def get_shape_bounds(shape: Rectangle) -> Tuple[float, float, float, float]:
    """Get shape boundaries as (x1, y1, x2, y2)"""
    return (
        shape.x,
        shape.y,
        shape.x + shape.width,
        shape.y + shape.height
    )


# Basic Overlap Tests
class TestBasicOverlapDetection:
    """Test basic overlap detection functionality"""
    
    def test_no_overlap_simple_case(self):
        """Test two rectangles that don't overlap"""
        rect1 = Rectangle(100, 100, x=0, y=0)
        rect2 = Rectangle(100, 100, x=200, y=0)
        
        assert not check_shapes_overlap(rect1, rect2)
    
    def test_overlap_simple_case(self):
        """Test two rectangles that do overlap"""
        rect1 = Rectangle(100, 100, x=0, y=0)
        rect2 = Rectangle(100, 100, x=50, y=50)
        
        assert check_shapes_overlap(rect1, rect2)
    
    def test_touching_edges_not_overlap(self):
        """Test that touching edges don't count as overlap"""
        rect1 = Rectangle(100, 100, x=0, y=0)
        rect2 = Rectangle(100, 100, x=100, y=0)  # Touching right edge
        
        assert not check_shapes_overlap(rect1, rect2)
    
    @pytest.mark.parametrize("x2,y2,should_overlap", [
        (200, 0, False),    # No overlap (far right)
        (0, 200, False),    # No overlap (far up)
        (-200, 0, False),   # No overlap (far left)
        (0, -200, False),   # No overlap (far down)
        (50, 50, True),     # Overlap (center)
        (90, 0, True),      # Overlap (slight)
        (100, 0, False),    # Touching (no overlap)
        (99, 0, True),      # Just overlapping
    ])
    def test_overlap_scenarios(self, x2, y2, should_overlap):
        """Test various overlap scenarios"""
        rect1 = Rectangle(100, 100, x=0, y=0)
        rect2 = Rectangle(100, 100, x=x2, y=y2)
        
        assert check_shapes_overlap(rect1, rect2) == should_overlap


# Algorithm Overlap Tests
@pytest.mark.algorithm
class TestAlgorithmOverlapPrevention:
    """Test that algorithms prevent overlaps in their solutions"""
    
    def test_first_fit_no_overlap(self, standard_stock, two_squares_orders):
        """Test FirstFit algorithm doesn't create overlaps"""
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize([standard_stock], two_squares_orders)
        
        # Check basic result validity
        assert result.total_orders_fulfilled >= 0
        assert result.total_stock_used >= 0
        
        # Check for overlaps
        if len(result.placed_shapes) > 1:
            is_valid, overlaps = check_all_placements_non_overlapping(result.placed_shapes)
            assert is_valid, f"Overlaps detected: {overlaps}"
    
    def test_genetic_algorithm_no_overlap(self, standard_stock, two_squares_orders):
        """Test Genetic algorithm doesn't create overlaps"""
        algorithm = GeneticAlgorithm(population_size=10, generations=5)
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize([standard_stock], two_squares_orders)
        
        # Check for overlaps
        if len(result.placed_shapes) > 1:
            is_valid, overlaps = check_all_placements_non_overlapping(result.placed_shapes)
            assert is_valid, f"Overlaps detected: {overlaps}"
            
            # Log placement details for debugging
            print(f"\nGenetic Algorithm - Placement Details:")
            for ps in result.placed_shapes:
                x1, y1, x2, y2 = get_shape_bounds(ps.shape)
                print(f"  {ps.order_id}: ({x1}, {y1}) - ({x2}, {y2})")
    
    @pytest.mark.parametrize("algorithm_class", [
        FirstFitAlgorithm,
        # Add more algorithms as they become available
    ])
    def test_multiple_algorithms_no_overlap(self, algorithm_class, standard_stock, multiple_rectangles_orders):
        """Test multiple algorithms for overlap prevention"""
        algorithm = algorithm_class()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize([standard_stock], multiple_rectangles_orders)
        
        # Check for overlaps
        if len(result.placed_shapes) > 1:
            is_valid, overlaps = check_all_placements_non_overlapping(result.placed_shapes)
            assert is_valid, f"{algorithm.name} created overlaps: {overlaps}"


# Specific Problem Cases
@pytest.mark.real_world
class TestSpecificOverlapScenarios:
    """Test specific scenarios that commonly cause overlap issues"""
    
    def test_optimal_two_square_placement(self, standard_stock, two_squares_orders):
        """
        Test the classic two 500x500 squares in 1000x1000 stock case.
        This should achieve 50% efficiency with no overlaps.
        """
        algorithm = GeneticAlgorithm(population_size=20, generations=10)
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize([standard_stock], two_squares_orders)
        
        print(f"\nTwo Squares Test Results:")
        print(f"  Efficiency: {result.efficiency_percentage:.1f}%")
        print(f"  Orders fulfilled: {result.total_orders_fulfilled}")
        print(f"  Shapes placed: {len(result.placed_shapes)}")
        
        # Check basic expectations
        assert result.total_orders_fulfilled >= 1, "Should fulfill at least one order"
        
        # If both squares were placed, check they don't overlap
        if len(result.placed_shapes) == 2:
            is_valid, overlaps = check_all_placements_non_overlapping(result.placed_shapes)
            assert is_valid, f"Two squares overlap: {overlaps}"
            
            # Check efficiency is reasonable (should be close to 50%)
            assert result.efficiency_percentage >= 40, f"Low efficiency: {result.efficiency_percentage}%"
            
            # Log optimal placement
            print(f"  Optimal placement achieved!")
            for ps in result.placed_shapes:
                x1, y1, x2, y2 = get_shape_bounds(ps.shape)
                print(f"    {ps.order_id}: ({x1}, {y1}) - ({x2}, {y2})")
    
    def test_tight_fit_rectangles(self):
        """Test rectangles that fit tightly without overlap"""
        stock = Stock('Tight', 600, 400, 5.0)
        orders = [
            Order('R1', Rectangle(300, 400), 1, Priority.HIGH),  # Left half
            Order('R2', Rectangle(300, 400), 1, Priority.HIGH),  # Right half
        ]
        
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize([stock], orders)
        
        if len(result.placed_shapes) == 2:
            is_valid, overlaps = check_all_placements_non_overlapping(result.placed_shapes)
            assert is_valid, f"Tight fit rectangles overlap: {overlaps}"
            
            # Should achieve 100% efficiency
            assert result.efficiency_percentage >= 95, f"Should be near 100% efficiency: {result.efficiency_percentage}%"
    
    def test_mixed_size_rectangles(self):
        """Test various sized rectangles for complex overlap scenarios"""
        stock = Stock('Mixed', 1200, 800, 5.0)
        orders = [
            Order('Large', Rectangle(600, 400), 1, Priority.HIGH),
            Order('Medium1', Rectangle(400, 300), 1, Priority.MEDIUM),
            Order('Medium2', Rectangle(300, 400), 1, Priority.MEDIUM),
            Order('Small1', Rectangle(200, 200), 1, Priority.LOW),
            Order('Small2', Rectangle(200, 100), 2, Priority.LOW),
        ]
        
        algorithm = GeneticAlgorithm(population_size=15, generations=8)
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize([stock], orders)
        
        # Check for overlaps regardless of how many were placed
        if len(result.placed_shapes) > 1:
            is_valid, overlaps = check_all_placements_non_overlapping(result.placed_shapes)
            assert is_valid, f"Mixed rectangles have overlaps: {overlaps}"
            
            print(f"\nMixed Rectangles Test:")
            print(f"  Placed {len(result.placed_shapes)} shapes")
            print(f"  Efficiency: {result.efficiency_percentage:.1f}%")


# Integration Tests
@pytest.mark.integration
class TestOverlapIntegration:
    """Integration tests for overlap detection across the system"""
    
    def test_overlap_detection_with_rotation(self):
        """Test overlap detection when rotation is enabled"""
        stock = Stock('Rotate', 1000, 600, 5.0)
        orders = [
            Order('Wide', Rectangle(800, 300), 1, Priority.HIGH),  # Fits normally
            Order('Tall', Rectangle(300, 500), 1, Priority.HIGH),  # Needs rotation to fit alongside
        ]
        
        from surface_optimizer.core.models import OptimizationConfig
        config = OptimizationConfig(allow_rotation=True)
        
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize(stock, orders, config)
        
        if len(result.placed_shapes) > 1:
            is_valid, overlaps = check_all_placements_non_overlapping(result.placed_shapes)
            assert is_valid, f"Rotated shapes overlap: {overlaps}"
    
    def test_overlap_detection_multiple_stocks(self):
        """Test overlap detection across multiple stocks"""
        stocks = [
            Stock('S1', 800, 600, 5.0),
            Stock('S2', 800, 600, 5.0),
        ]
        
        orders = [
            Order('Big1', Rectangle(700, 500), 1, Priority.HIGH),
            Order('Big2', Rectangle(700, 500), 1, Priority.HIGH),
            Order('Small', Rectangle(200, 200), 2, Priority.LOW),
        ]
        
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = optimizer.optimize(stocks, orders)
        
        # Group placed shapes by stock
        shapes_by_stock = {}
        for ps in result.placed_shapes:
            stock_id = ps.stock_id
            if stock_id not in shapes_by_stock:
                shapes_by_stock[stock_id] = []
            shapes_by_stock[stock_id].append(ps)
        
        # Check overlaps within each stock
        for stock_id, shapes in shapes_by_stock.items():
            if len(shapes) > 1:
                is_valid, overlaps = check_all_placements_non_overlapping(shapes)
                assert is_valid, f"Overlaps in stock {stock_id}: {overlaps}"


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "-s", "--tb=short"]) 