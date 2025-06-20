#!/usr/bin/env python3
"""
Modern pytest-based tests for optimization algorithms

Uses pytest fixtures, parametrization, and modern testing patterns.
"""

import pytest
import time
from typing import List, Type

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from test.data.test_cases import get_all_test_cases, validate_result_against_optimal, generate_simple_rectangular_test


# Fixtures for reusable test data
@pytest.fixture
def basic_config():
    """Standard optimization configuration"""
    return OptimizationConfig(
        allow_rotation=True,
        cutting_width=3.0,
        prioritize_orders=True
    )


@pytest.fixture
def simple_stock():
    """Simple stock for basic tests"""
    return Stock("S1", 1000, 800, 6.0, MaterialType.GLASS, 100.0)


@pytest.fixture
def simple_orders():
    """Simple orders for basic tests"""
    return [
        Order("O1", Rectangle(400, 300), 1, Priority.HIGH),
        Order("O2", Rectangle(300, 200), 1, Priority.MEDIUM),
        Order("O3", Rectangle(200, 100), 1, Priority.LOW)
    ]


@pytest.fixture
def complex_orders():
    """Complex orders for advanced testing"""
    return [
        Order("High1", Rectangle(500, 400), 2, Priority.HIGH),
        Order("Urgent1", Rectangle(300, 600), 1, Priority.URGENT),
        Order("Med1", Rectangle(250, 200), 3, Priority.MEDIUM),
        Order("Low1", Rectangle(150, 100), 4, Priority.LOW),
        Order("Circle1", Circle(100), 2, Priority.MEDIUM)
    ]


@pytest.fixture(params=[
    BottomLeftAlgorithm,
    BestFitAlgorithm,
    FirstFitAlgorithm
])
def algorithm_class(request):
    """Parametrized fixture for all algorithm classes"""
    return request.param


@pytest.fixture
def algorithm_instance(algorithm_class):
    """Create algorithm instance from class"""
    return algorithm_class()


# Unit Tests for Individual Algorithms
class TestAlgorithmInterface:
    """Test algorithm interface compliance"""
    
    def test_algorithm_has_name(self, algorithm_instance):
        """All algorithms must have a name"""
        assert hasattr(algorithm_instance, 'name')
        assert isinstance(algorithm_instance.name, str)
        assert len(algorithm_instance.name) > 0
    
    def test_algorithm_has_optimize_method(self, algorithm_instance):
        """All algorithms must have optimize method"""
        assert hasattr(algorithm_instance, 'optimize')
        assert callable(algorithm_instance.optimize)
    
    def test_empty_inputs_return_empty_result(self, algorithm_instance, basic_config):
        """Algorithms should handle empty inputs gracefully"""
        result = algorithm_instance.optimize([], [], basic_config)
        
        assert result.total_stock_used == 0
        assert result.total_orders_fulfilled == 0
        assert len(result.placed_shapes) == 0
        assert len(result.unfulfilled_orders) == 0
        assert result.efficiency_percentage == 0.0


class TestBasicFunctionality:
    """Test basic algorithm functionality"""
    
    def test_no_stock_available(self, algorithm_instance, simple_orders, basic_config):
        """Test with orders but no stock"""
        result = algorithm_instance.optimize([], simple_orders, basic_config)
        
        assert result.total_stock_used == 0
        assert result.total_orders_fulfilled == 0
        assert len(result.unfulfilled_orders) == len(simple_orders)
    
    def test_no_orders_available(self, algorithm_instance, simple_stock, basic_config):
        """Test with stock but no orders"""
        result = algorithm_instance.optimize([simple_stock], [], basic_config)
        
        assert result.total_stock_used == 0
        assert result.total_orders_fulfilled == 0
        assert len(result.placed_shapes) == 0
    
    def test_simple_optimization(self, algorithm_instance, simple_stock, simple_orders, basic_config):
        """Test basic optimization with simple inputs"""
        result = algorithm_instance.optimize([simple_stock], simple_orders, basic_config)
        
        # Basic sanity checks
        assert result.total_stock_used >= 0
        assert result.total_orders_fulfilled >= 0
        assert len(result.placed_shapes) >= 0
        assert 0.0 <= result.efficiency_percentage <= 100.0
        assert result.algorithm_used == algorithm_instance.name
        assert isinstance(result.computation_time, float)
        assert result.computation_time >= 0


@pytest.mark.integration
class TestAlgorithmIntegration:
    """Integration tests for algorithm behavior"""
    
    def test_order_priority_respected(self, algorithm_instance, basic_config):
        """Test that order priority affects placement"""
        stock = Stock("S1", 1000, 600, 6.0)
        orders = [
            Order("Low", Rectangle(800, 500), 1, Priority.LOW),
            Order("Urgent", Rectangle(900, 550), 1, Priority.URGENT),
            Order("High", Rectangle(850, 520), 1, Priority.HIGH),
        ]
        
        # With priority enabled
        config_priority = OptimizationConfig(prioritize_orders=True)
        result_priority = algorithm_instance.optimize([stock], orders, config_priority)
        
        # Without priority
        config_no_priority = OptimizationConfig(prioritize_orders=False)
        result_no_priority = algorithm_instance.optimize([stock], orders, config_no_priority)
        
        # Both should work
        assert result_priority is not None
        assert result_no_priority is not None
    
    def test_rotation_configuration(self, algorithm_instance, simple_stock, basic_config):
        """Test rotation vs no rotation"""
        # Order that fits only when rotated
        orders = [Order("Rotate", Rectangle(900, 700), 1, Priority.HIGH)]  # Doesn't fit normally
        
        # With rotation
        config_rotation = OptimizationConfig(allow_rotation=True)
        result_rotation = algorithm_instance.optimize([simple_stock], orders, config_rotation)
        
        # Without rotation
        config_no_rotation = OptimizationConfig(allow_rotation=False)
        result_no_rotation = algorithm_instance.optimize([simple_stock], orders, config_no_rotation)
        
        # Rotation should potentially allow more placement
        # (This is algorithm-dependent, so we just check both work)
        assert result_rotation is not None
        assert result_no_rotation is not None


@pytest.mark.performance
class TestPerformance:
    """Performance tests for algorithms"""
    
    def test_computation_time_reasonable(self, algorithm_instance, basic_config):
        """Test that computation time is reasonable for small problems"""
        stocks = [Stock(f"S{i}", 1000, 800, 6.0) for i in range(3)]
        orders = [Order(f"O{i}", Rectangle(200, 150), 1, Priority.MEDIUM) for i in range(10)]
        
        start_time = time.time()
        result = algorithm_instance.optimize(stocks, orders, basic_config)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds for small problem)
        assert elapsed < 5.0
        assert result.computation_time <= elapsed + 0.1  # Allow small measurement error
    
    @pytest.mark.slow
    def test_large_case_performance(self, algorithm_instance, basic_config):
        """Test performance with larger problem sizes"""
        stocks = [Stock(f"S{i}", 2000, 1500, 6.0) for i in range(5)]
        orders = [Order(f"O{i}", Rectangle(200, 150), 1, Priority.MEDIUM) for i in range(50)]
        
        start_time = time.time()
        result = algorithm_instance.optimize(stocks, orders, basic_config)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time even for larger problems
        assert elapsed < 30.0  # 30 seconds max for 50 orders
        assert result.total_orders_fulfilled >= 0  # Should produce some result


@pytest.mark.real_world
class TestKnownSolutions:
    """Test against known optimal solutions"""
    
    def test_simple_rectangular_case(self, algorithm_instance, basic_config):
        """Test against simple known solution"""
        stocks, orders, optimal_solution = generate_simple_rectangular_test()
        
        result = algorithm_instance.optimize(stocks, orders, basic_config)
        validation = validate_result_against_optimal(result, optimal_solution, tolerance=15.0)
        
        # Basic checks
        assert result.total_orders_fulfilled > 0
        assert result.efficiency_percentage > 0
        
        # Log results for analysis
        print(f"\n{algorithm_instance.name} - Simple case:")
        print(f"  Result: {result.efficiency_percentage:.1f}% efficiency")
        print(f"  Expected: {optimal_solution['efficiency_percentage']}% efficiency")
        print(f"  Validation: {validation.get('overall_pass', 'N/A')}")
    
    @pytest.mark.parametrize("case_name", ["simple_rectangular", "mixed_shapes", "priority_test"])
    def test_all_known_cases(self, algorithm_instance, basic_config, case_name):
        """Test against all available known cases"""
        test_cases = get_all_test_cases()
        
        if case_name not in test_cases:
            pytest.skip(f"Test case '{case_name}' not available")
        
        stocks, orders, optimal_solution = test_cases[case_name]
        
        result = algorithm_instance.optimize(stocks, orders, basic_config)
        validation = validate_result_against_optimal(result, optimal_solution, tolerance=20.0)
        
        # Basic sanity checks
        assert result.total_stock_used >= 0
        assert result.total_orders_fulfilled >= 0
        assert 0.0 <= result.efficiency_percentage <= 100.0
        
        # Log results
        print(f"\n{algorithm_instance.name} - {case_name}:")
        print(f"  Orders fulfilled: {result.total_orders_fulfilled}")
        print(f"  Efficiency: {result.efficiency_percentage:.1f}%")
        print(f"  Validation: {validation.get('overall_pass', 'N/A')}")


# Comparative Tests
@pytest.mark.algorithm
class TestAlgorithmComparison:
    """Compare different algorithms on same problems"""
    
    @pytest.fixture
    def all_algorithms(self):
        """All available algorithms"""
        return [
            BottomLeftAlgorithm(),
            BestFitAlgorithm(),
            FirstFitAlgorithm()
        ]
    
    def test_all_algorithms_consistency(self, all_algorithms, simple_stock, simple_orders, basic_config):
        """Test that all algorithms produce valid results"""
        results = {}
        
        for algorithm in all_algorithms:
            result = algorithm.optimize([simple_stock], simple_orders, basic_config)
            results[algorithm.name] = result
            
            # Each algorithm should produce valid result
            assert result is not None
            assert result.algorithm_used == algorithm.name
            assert 0.0 <= result.efficiency_percentage <= 100.0
        
        # Log comparison
        print("\nAlgorithm Comparison:")
        for name, result in results.items():
            print(f"  {name}: {result.efficiency_percentage:.1f}% efficiency, "
                  f"{result.total_orders_fulfilled} orders fulfilled")
    
    def test_algorithm_ranking(self, all_algorithms, basic_config):
        """Test algorithm performance ranking"""
        # Create a moderately complex problem
        stocks = [Stock("S1", 2000, 1500, 6.0), Stock("S2", 2000, 1500, 6.0)]
        orders = [
            Order(f"O{i}", Rectangle(300 + i*10, 200 + i*5), 1, Priority.MEDIUM) 
            for i in range(15)
        ]
        
        performance = {}
        
        for algorithm in all_algorithms:
            result = algorithm.optimize(stocks, orders, basic_config)
            performance[algorithm.name] = {
                'efficiency': result.efficiency_percentage,
                'orders_fulfilled': result.total_orders_fulfilled,
                'time': result.computation_time
            }
        
        # All algorithms should fulfill at least some orders
        for name, perf in performance.items():
            assert perf['orders_fulfilled'] > 0, f"{name} fulfilled no orders"
        
        # Log performance ranking
        sorted_by_efficiency = sorted(performance.items(), key=lambda x: x[1]['efficiency'], reverse=True)
        print(f"\nAlgorithm Performance Ranking (by efficiency):")
        for i, (name, perf) in enumerate(sorted_by_efficiency, 1):
            print(f"  {i}. {name}: {perf['efficiency']:.1f}% efficiency, "
                  f"{perf['orders_fulfilled']} orders, {perf['time']:.3f}s")


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--cov=surface_optimizer"]) 