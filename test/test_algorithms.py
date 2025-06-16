#!/usr/bin/env python3
"""
Unit tests for optimization algorithms
"""

import unittest
from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.utils.test_cases import (
    get_all_test_cases, 
    validate_result_against_optimal,
    generate_simple_rectangular_test
)


class TestBottomLeftAlgorithm(unittest.TestCase):
    """Test cases for Bottom-Left Fill algorithm"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = BottomLeftAlgorithm()
        self.config = OptimizationConfig(
            allow_rotation=True,
            cutting_width=3.0,
            prioritize_orders=True
        )
    
    def test_algorithm_name(self):
        """Test algorithm name"""
        self.assertEqual(self.algorithm.name, "Bottom-Left Fill")
    
    def test_empty_inputs(self):
        """Test algorithm with empty inputs"""
        result = self.algorithm.optimize([], [], self.config)
        
        self.assertEqual(result.total_stock_used, 0)
        self.assertEqual(result.total_orders_fulfilled, 0)
        self.assertEqual(len(result.placed_shapes), 0)
        self.assertEqual(len(result.unfulfilled_orders), 0)
    
    def test_no_stock_available(self):
        """Test algorithm with orders but no stock"""
        orders = [Order("O1", Rectangle(100, 50), 1, Priority.HIGH)]
        result = self.algorithm.optimize([], orders, self.config)
        
        self.assertEqual(result.total_stock_used, 0)
        self.assertEqual(result.total_orders_fulfilled, 0)
        self.assertEqual(len(result.unfulfilled_orders), 1)
    
    def test_simple_case(self):
        """Test algorithm with simple rectangular case"""
        stocks = [Stock("S1", 1000, 800, 6.0, MaterialType.GLASS, 100.0)]
        orders = [
            Order("O1", Rectangle(400, 300), 1, Priority.HIGH),
            Order("O2", Rectangle(300, 200), 1, Priority.MEDIUM)
        ]
        
        result = self.algorithm.optimize(stocks, orders, self.config)
        
        # Should use at least some stock
        self.assertGreater(result.total_stock_used, 0)
        self.assertLessEqual(result.total_stock_used, len(stocks))
        
        # Algorithm result should have proper structure
        self.assertIsInstance(result.computation_time, float)
        self.assertEqual(result.algorithm_used, "Bottom-Left Fill")
    
    def test_order_preprocessing(self):
        """Test order preprocessing (sorting by priority)"""
        orders = [
            Order("Low", Rectangle(100, 100), 1, Priority.LOW),
            Order("High", Rectangle(200, 200), 1, Priority.HIGH),
            Order("Urgent", Rectangle(150, 150), 1, Priority.URGENT),
            Order("Medium", Rectangle(120, 120), 1, Priority.MEDIUM)
        ]
        
        sorted_orders = self.algorithm.preprocess_orders(orders, self.config)
        
        # Should be sorted by priority (URGENT=4, HIGH=3, MEDIUM=2, LOW=1)
        priorities = [order.priority.value for order in sorted_orders]
        self.assertEqual(priorities, sorted(priorities, reverse=True))


class TestAlgorithmComparison(unittest.TestCase):
    """Test comparison between different algorithms"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = OptimizationConfig(allow_rotation=True)
        self.algorithms = [
            BottomLeftAlgorithm(),
            BestFitAlgorithm(),
            FirstFitAlgorithm()
        ]
    
    def test_all_algorithms_run(self):
        """Test that all algorithms can run without errors"""
        stocks = [Stock("S1", 1000, 800, 6.0)]
        orders = [Order("O1", Rectangle(400, 300), 1)]
        
        for algorithm in self.algorithms:
            with self.subTest(algorithm=algorithm.name):
                result = algorithm.optimize(stocks, orders, self.config)
                
                # Basic result structure checks
                self.assertIsNotNone(result)
                self.assertIsInstance(result.total_stock_used, int)
                self.assertIsInstance(result.total_orders_fulfilled, int)
                self.assertIsInstance(result.efficiency_percentage, float)
                self.assertEqual(result.algorithm_used, algorithm.name)


class TestKnownOptimalCases(unittest.TestCase):
    """Test algorithms against known optimal solutions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = BottomLeftAlgorithm()
        self.config = OptimizationConfig(allow_rotation=True, prioritize_orders=True)
    
    def test_simple_rectangular_case(self):
        """Test against simple rectangular case with known solution"""
        stocks, orders, optimal_solution = generate_simple_rectangular_test()
        
        result = self.algorithm.optimize(stocks, orders, self.config)
        validation = validate_result_against_optimal(result, optimal_solution, tolerance=10.0)
        
        # Basic checks
        self.assertIsNotNone(result)
        self.assertGreater(result.total_orders_fulfilled, 0)
        
        # Print validation results for debugging
        print(f"\nSimple rectangular test results:")
        print(f"Algorithm result: {result.efficiency_percentage:.1f}% efficiency")
        print(f"Expected optimal: {optimal_solution['efficiency_percentage']}% efficiency")
        print(f"Validation: {validation}")
    
    def test_all_known_cases(self):
        """Test algorithm against all known test cases"""
        test_cases = get_all_test_cases()
        
        for case_name, (stocks, orders, optimal_solution) in test_cases.items():
            with self.subTest(case=case_name):
                try:
                    result = self.algorithm.optimize(stocks, orders, self.config)
                    
                    # Basic sanity checks
                    self.assertIsNotNone(result)
                    self.assertGreaterEqual(result.total_stock_used, 0)
                    self.assertGreaterEqual(result.total_orders_fulfilled, 0)
                    self.assertGreaterEqual(result.efficiency_percentage, 0.0)
                    self.assertLessEqual(result.efficiency_percentage, 100.0)
                    
                    # Validate against optimal if possible
                    validation = validate_result_against_optimal(result, optimal_solution, tolerance=15.0)
                    
                    print(f"\nTest case '{case_name}':")
                    print(f"  Result: {result.efficiency_percentage:.1f}% efficiency, {result.total_orders_fulfilled} orders")
                    print(f"  Expected: {optimal_solution.get('efficiency_percentage', 'N/A')}% efficiency")
                    print(f"  Validation: {validation.get('overall_pass', 'N/A')}")
                    
                except Exception as e:
                    self.fail(f"Algorithm failed on test case '{case_name}': {e}")


class TestAlgorithmConfig(unittest.TestCase):
    """Test algorithm configuration effects"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = BottomLeftAlgorithm()
        self.stocks = [Stock("S1", 1000, 800, 6.0)]
        self.orders = [
            Order("O1", Rectangle(600, 400), 1, Priority.HIGH),
            Order("O2", Rectangle(300, 200), 1, Priority.LOW)
        ]
    
    def test_priority_configuration(self):
        """Test priority vs non-priority configuration"""
        # With priority
        config_priority = OptimizationConfig(prioritize_orders=True)
        result_priority = self.algorithm.optimize(self.stocks, self.orders, config_priority)
        
        # Without priority
        config_no_priority = OptimizationConfig(prioritize_orders=False)
        result_no_priority = self.algorithm.optimize(self.stocks, self.orders, config_no_priority)
        
        # Both should run successfully
        self.assertIsNotNone(result_priority)
        self.assertIsNotNone(result_no_priority)
    
    def test_rotation_configuration(self):
        """Test rotation vs no rotation configuration"""
        # With rotation
        config_rotation = OptimizationConfig(allow_rotation=True)
        result_rotation = self.algorithm.optimize(self.stocks, self.orders, config_rotation)
        
        # Without rotation
        config_no_rotation = OptimizationConfig(allow_rotation=False)
        result_no_rotation = self.algorithm.optimize(self.stocks, self.orders, config_no_rotation)
        
        # Both should run successfully
        self.assertIsNotNone(result_rotation)
        self.assertIsNotNone(result_no_rotation)


class TestPerformance(unittest.TestCase):
    """Test algorithm performance characteristics"""
    
    def test_computation_time_tracking(self):
        """Test that computation time is tracked"""
        algorithm = BottomLeftAlgorithm()
        config = OptimizationConfig()
        
        stocks = [Stock("S1", 1000, 800, 6.0)]
        orders = [Order("O1", Rectangle(400, 300), 1)]
        
        result = algorithm.optimize(stocks, orders, config)
        
        # Computation time should be tracked
        self.assertIsInstance(result.computation_time, float)
        self.assertGreaterEqual(result.computation_time, 0.0)
    
    def test_large_case_performance(self):
        """Test performance on larger case"""
        algorithm = BottomLeftAlgorithm()
        config = OptimizationConfig(max_computation_time=10.0)  # 10 second limit
        
        # Create larger test case
        stocks = [Stock(f"S{i}", 2000, 1000, 6.0) for i in range(5)]
        orders = [Order(f"O{i}", Rectangle(200 + i*50, 150 + i*30), 1) for i in range(20)]
        
        result = algorithm.optimize(stocks, orders, config)
        
        # Should complete within time limit
        self.assertLess(result.computation_time, config.max_computation_time)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2) 