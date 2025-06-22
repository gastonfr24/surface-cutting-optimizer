"""
Unit tests for Surface Cutting Optimizer main coordinator

Tests cover:
- Optimizer initialization and configuration
- Algorithm setting and management
- Input validation and error handling
- Optimization execution flow
- History tracking and performance summaries
- Algorithm comparison functionality
- Error conditions and edge cases
"""

import unittest
import pytest
from unittest.mock import Mock, MagicMock, patch
import tempfile
import json
from datetime import datetime

from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.core.models import (
    Stock, Order, CuttingResult, OptimizationConfig, 
    MaterialType, Priority, PlacedShape
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.exceptions import (
    OptimizationError, ValidationError, InvalidDimensionsError
)
from surface_optimizer.algorithms.base import BaseAlgorithm
from surface_optimizer.utils.logging import OptimizationLogger


class MockAlgorithm(BaseAlgorithm):
    """Mock algorithm for testing"""
    
    def __init__(self, name="MockAlgorithm", should_fail=False, efficiency=85.0):
        super().__init__()
        self.name = name
        self.should_fail = should_fail
        self.efficiency = efficiency
        self.call_count = 0
        
    def optimize(self, stocks, orders, config):
        self.call_count += 1
        
        if self.should_fail:
            raise Exception("Mock algorithm failure")
        
        # Create a mock result
        result = CuttingResult()
        result.algorithm_used = self.name
        result.total_stock_used = min(len(stocks), len(orders))
        result.total_orders_fulfilled = min(len(orders), 3)
        result.efficiency_percentage = self.efficiency
        result.computation_time = 0.1
        
        # Add some mock placed shapes with valid positions
        if stocks and orders:
            for i, order in enumerate(orders[:3]):
                if i < len(stocks):
                    # Create a copy of the shape with valid position
                    shape_copy = Rectangle(
                        width=min(order.shape.width, stocks[i].width),
                        height=min(order.shape.height, stocks[i].height),
                        x=0.0,
                        y=0.0
                    )
                    placed_shape = PlacedShape(
                        order_id=order.id,
                        shape=shape_copy,
                        stock_id=stocks[i].id
                    )
                    result.placed_shapes.append(placed_shape)
        
        # Add unfulfilled orders
        if len(orders) > 3:
            result.unfulfilled_orders = orders[3:]
            
        return result


class TestOptimizerInitialization(unittest.TestCase):
    """Tests for Optimizer initialization"""
    
    def test_default_initialization(self):
        """Test optimizer initialization with defaults"""
        optimizer = Optimizer()
        
        self.assertIsNotNone(optimizer.config)
        self.assertIsNone(optimizer.algorithm)
        self.assertIsNotNone(optimizer.logger)
        self.assertEqual(len(optimizer.optimization_history), 0)
        
    def test_initialization_with_config(self):
        """Test optimizer initialization with custom config"""
        custom_config = OptimizationConfig(
            allow_rotation=False,
            cutting_width=2.5,
            max_computation_time=30.0
        )
        
        optimizer = Optimizer(config=custom_config)
        
        self.assertEqual(optimizer.config.allow_rotation, False)
        self.assertEqual(optimizer.config.cutting_width, 2.5)
        self.assertEqual(optimizer.config.max_computation_time, 30.0)
        
    def test_initialization_with_logger(self):
        """Test optimizer initialization with custom logger"""
        custom_logger = OptimizationLogger("test_logger")
        optimizer = Optimizer(logger=custom_logger)
        
        self.assertEqual(optimizer.logger, custom_logger)


class TestAlgorithmManagement(unittest.TestCase):
    """Tests for algorithm setting and management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = Optimizer()
        self.mock_algorithm = MockAlgorithm("TestAlgorithm")
        
    def test_set_algorithm(self):
        """Test setting an algorithm"""
        self.optimizer.set_algorithm(self.mock_algorithm)
        self.assertEqual(self.optimizer.algorithm, self.mock_algorithm)
        
    def test_optimize_without_algorithm(self):
        """Test optimization fails without algorithm set"""
        stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        
        with self.assertRaises(OptimizationError) as context:
            self.optimizer.optimize(stocks, orders)
            
        self.assertIn("No algorithm set", str(context.exception))


class TestInputValidation(unittest.TestCase):
    """Tests for input validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = Optimizer()
        self.optimizer.set_algorithm(MockAlgorithm())
        
        self.valid_stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.GLASS),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.GLASS)
        ]
        
        self.valid_orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=1, material_type=MaterialType.GLASS),
            Order(id="O2", shape=Rectangle(150.0, 150.0), quantity=2, material_type=MaterialType.GLASS)
        ]
        
    def test_empty_stocks_validation(self):
        """Test validation with empty stocks list"""
        with self.assertRaises(OptimizationError):  # Optimizer wraps ValidationError
            self.optimizer.optimize([], self.valid_orders)
            
    def test_empty_orders_validation(self):
        """Test validation with empty orders list"""
        with self.assertRaises(OptimizationError):  # Optimizer wraps ValidationError
            self.optimizer.optimize(self.valid_stocks, [])
            
    def test_invalid_stock_dimensions(self):
        """Test validation with invalid stock dimensions"""
        # This should fail at Stock creation, not optimization
        with self.assertRaises(InvalidDimensionsError):
            Stock(id="S1", width=-100.0, height=500.0)
            
    def test_invalid_order_quantity(self):
        """Test validation with invalid order quantity"""
        with self.assertRaises(InvalidDimensionsError):
            # This should fail at Order creation
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=0)
            
    def test_material_compatibility_warning(self):
        """Test material compatibility warnings"""
        # Create stocks and orders with different materials
        metal_stocks = [Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.METAL)]
        glass_orders = [Order(id="O1", shape=Rectangle(100.0, 50.0), material_type=MaterialType.GLASS)]
        
        # This should raise an exception due to material incompatibility
        with self.assertRaises(OptimizationError) as context:
            self.optimizer.optimize(metal_stocks, glass_orders)
        
        self.assertIn("No stocks available for material type", str(context.exception))


class TestOptimizationExecution(unittest.TestCase):
    """Tests for optimization execution flow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = Optimizer()
        self.mock_algorithm = MockAlgorithm("TestAlgorithm", efficiency=78.5)
        self.optimizer.set_algorithm(self.mock_algorithm)
        
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, cost_per_unit=100.0),
            Stock(id="S2", width=800.0, height=600.0, cost_per_unit=80.0)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=1),
            Order(id="O2", shape=Rectangle(150.0, 150.0), quantity=2),
            Order(id="O3", shape=Circle(50.0), quantity=1),
            Order(id="O4", shape=Rectangle(300.0, 200.0), quantity=1)  # Large order
        ]
        
    def test_successful_optimization(self):
        """Test successful optimization execution"""
        result = self.optimizer.optimize(self.stocks, self.orders)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "TestAlgorithm")
        self.assertEqual(result.efficiency_percentage, 78.5)
        self.assertEqual(self.mock_algorithm.call_count, 1)
        self.assertGreaterEqual(result.computation_time, 0)  # Allow 0 for very fast operations
        
    def test_algorithm_failure_handling(self):
        """Test handling of algorithm failures"""
        failing_algorithm = MockAlgorithm("FailingAlgorithm", should_fail=True)
        self.optimizer.set_algorithm(failing_algorithm)
        
        with self.assertRaises(OptimizationError) as context:
            self.optimizer.optimize(self.stocks, self.orders)
            
        self.assertIn("Optimization failed", str(context.exception))
        
    def test_result_validation(self):
        """Test result validation"""
        result = self.optimizer.optimize(self.stocks, self.orders)
        
        # Check that result is properly validated
        self.assertGreaterEqual(result.total_stock_used, 0)
        self.assertGreaterEqual(result.total_orders_fulfilled, 0)
        self.assertGreaterEqual(result.efficiency_percentage, 0)
        self.assertLessEqual(result.efficiency_percentage, 100)
        
    def test_cost_calculation(self):
        """Test cost calculation in results"""
        result = self.optimizer.optimize(self.stocks, self.orders)
        
        # Cost should be calculated based on used stocks
        self.assertGreaterEqual(result.total_cost, 0)
        
    def test_computation_time_tracking(self):
        """Test computation time is tracked"""
        result = self.optimizer.optimize(self.stocks, self.orders)
        
        self.assertGreaterEqual(result.computation_time, 0)  # Allow 0 for very fast operations
        self.assertIsInstance(result.computation_time, float)


class TestHistoryTracking(unittest.TestCase):
    """Tests for optimization history tracking"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = Optimizer()
        self.optimizer.set_algorithm(MockAlgorithm("HistoryAlgorithm"))
        
        self.stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        self.orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        
    def test_history_recording(self):
        """Test that optimization history is recorded"""
        self.assertEqual(len(self.optimizer.optimization_history), 0)
        
        # Run optimization
        result1 = self.optimizer.optimize(self.stocks, self.orders)
        self.assertEqual(len(self.optimizer.optimization_history), 1)
        
        # Run another optimization
        result2 = self.optimizer.optimize(self.stocks, self.orders)
        self.assertEqual(len(self.optimizer.optimization_history), 2)
        
        # Check history contents
        history = self.optimizer.get_optimization_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], result1)
        self.assertEqual(history[1], result2)
        
    def test_performance_summary(self):
        """Test performance summary generation"""
        # Run multiple optimizations
        for i in range(3):
            self.optimizer.optimize(self.stocks, self.orders)
            
        summary = self.optimizer.get_performance_summary()
        
        self.assertIn("total_optimizations", summary)
        self.assertIn("average_efficiency", summary)
        self.assertIn("average_computation_time", summary)
        self.assertIn("best_efficiency", summary)
        self.assertIn("total_time", summary)
        
        self.assertEqual(summary["total_optimizations"], 3)
        self.assertGreater(summary["average_efficiency"], 0)
        
    def test_clear_history(self):
        """Test clearing optimization history"""
        # Add some history
        self.optimizer.optimize(self.stocks, self.orders)
        self.optimizer.optimize(self.stocks, self.orders)
        self.assertEqual(len(self.optimizer.optimization_history), 2)
        
        # Clear history
        self.optimizer.clear_history()
        self.assertEqual(len(self.optimizer.optimization_history), 0)


class TestAlgorithmComparison(unittest.TestCase):
    """Tests for algorithm comparison functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = Optimizer()
        
        self.algorithms = [
            MockAlgorithm("Algorithm1", efficiency=75.0),
            MockAlgorithm("Algorithm2", efficiency=85.0),
            MockAlgorithm("Algorithm3", efficiency=70.0)
        ]
        
        self.stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        self.orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        
    def test_algorithm_comparison(self):
        """Test comparing multiple algorithms"""
        results = self.optimizer.compare_algorithms(self.algorithms, self.stocks, self.orders)
        
        self.assertEqual(len(results), 3)
        
        # Check that each algorithm was called
        for algorithm in self.algorithms:
            self.assertEqual(algorithm.call_count, 1)
            
        # Check results are different (different algorithms)
        efficiencies = [r.efficiency_percentage for r in results]
        self.assertEqual(efficiencies, [75.0, 85.0, 70.0])
        
    def test_algorithm_comparison_with_failure(self):
        """Test algorithm comparison when one algorithm fails"""
        failing_algorithms = [
            MockAlgorithm("GoodAlgorithm", efficiency=80.0),
            MockAlgorithm("BadAlgorithm", should_fail=True),
            MockAlgorithm("AnotherGoodAlgorithm", efficiency=75.0)
        ]
        
        results = self.optimizer.compare_algorithms(failing_algorithms, self.stocks, self.orders)
        
        self.assertEqual(len(results), 3)
        
        # Check that failed algorithm returns a result with error metadata
        self.assertEqual(results[0].efficiency_percentage, 80.0)
        self.assertIn("error", results[1].metadata)
        self.assertEqual(results[2].efficiency_percentage, 75.0)
        
    def test_original_algorithm_restoration(self):
        """Test that original algorithm is restored after comparison"""
        original_algorithm = MockAlgorithm("OriginalAlgorithm")
        self.optimizer.set_algorithm(original_algorithm)
        
        # Run comparison
        self.optimizer.compare_algorithms(self.algorithms, self.stocks, self.orders)
        
        # Check original algorithm is restored
        self.assertEqual(self.optimizer.algorithm, original_algorithm)


class TestConfigurationValidation(unittest.TestCase):
    """Tests for configuration validation"""
    
    def test_invalid_configuration(self):
        """Test optimizer with invalid configuration"""
        invalid_config = OptimizationConfig(
            cutting_width=-1.0,  # Invalid
            max_computation_time=0.0  # Invalid
        )
        
        optimizer = Optimizer(config=invalid_config)
        optimizer.set_algorithm(MockAlgorithm())
        
        stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        
        with self.assertRaises(OptimizationError) as context:
            optimizer.optimize(stocks, orders)
            
        self.assertIn("Invalid configuration", str(context.exception))


class TestLogging(unittest.TestCase):
    """Tests for logging functionality"""
    
    def setUp(self):
        """Set up test fixtures with mock logger"""
        self.mock_logger = Mock(spec=OptimizationLogger)
        self.optimizer = Optimizer(logger=self.mock_logger)
        self.optimizer.set_algorithm(MockAlgorithm("LoggingAlgorithm"))
        
        self.stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        self.orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        
    def test_logging_operations(self):
        """Test that logging operations are called"""
        self.optimizer.optimize(self.stocks, self.orders)
        
        # Check that logging methods were called
        self.mock_logger.start_operation.assert_called()
        self.mock_logger.end_operation.assert_called()
        self.mock_logger.log_validation.assert_called()
        self.mock_logger.log_algorithm_start.assert_called()
        self.mock_logger.log_algorithm_result.assert_called()
        
    def test_export_logs(self):
        """Test log export functionality"""
        # Run some optimizations
        self.optimizer.optimize(self.stocks, self.orders)
        
        # Test export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            self.optimizer.export_logs(f.name)
            self.mock_logger.export_logs.assert_called_with(f.name)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = Optimizer()
        self.optimizer.set_algorithm(MockAlgorithm())
        
    def test_empty_result_handling(self):
        """Test handling of empty optimization results"""
        # Use algorithm that returns minimal result with no placed shapes
        class EmptyAlgorithm(BaseAlgorithm):
            def __init__(self):
                super().__init__()
                self.name = "EmptyAlgorithm"
            
            def optimize(self, stocks, orders, config):
                result = CuttingResult()
                result.algorithm_used = self.name
                result.total_stock_used = 0
                result.total_orders_fulfilled = 0
                result.efficiency_percentage = 0.0
                result.unfulfilled_orders = orders.copy()
                return result
        
        empty_algorithm = EmptyAlgorithm()
        self.optimizer.set_algorithm(empty_algorithm)
        
        stocks = [Stock(id="S1", width=10.0, height=10.0)]  # Very small stock
        orders = [Order(id="O1", shape=Rectangle(1000.0, 1000.0))]  # Very large order
        
        result = self.optimizer.optimize(stocks, orders)
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.efficiency_percentage, 0.0)
        
    def test_single_stock_single_order(self):
        """Test optimization with minimal input"""
        stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        
        result = self.optimizer.optimize(stocks, orders)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertGreaterEqual(result.total_orders_fulfilled, 0)
        
    def test_many_stocks_few_orders(self):
        """Test optimization with many stocks, few orders"""
        stocks = [Stock(id=f"S{i}", width=1000.0, height=500.0) for i in range(100)]
        orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        
        result = self.optimizer.optimize(stocks, orders)
        self.assertIsInstance(result, CuttingResult)
        
    def test_few_stocks_many_orders(self):
        """Test optimization with few stocks, many orders"""
        stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        orders = [Order(id=f"O{i}", shape=Rectangle(50.0, 50.0)) for i in range(100)]
        
        result = self.optimizer.optimize(stocks, orders)
        self.assertIsInstance(result, CuttingResult)
        
    def test_zero_area_shapes(self):
        """Test optimization with very small shapes"""
        stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        orders = [Order(id="O1", shape=Rectangle(0.1, 0.1))]  # Very small
        
        result = self.optimizer.optimize(stocks, orders)
        self.assertIsInstance(result, CuttingResult)


class TestStringRepresentation(unittest.TestCase):
    """Tests for string representations"""
    
    def test_optimizer_string(self):
        """Test optimizer string representation"""
        optimizer = Optimizer()
        optimizer_str = str(optimizer)
        
        self.assertIsInstance(optimizer_str, str)
        self.assertIn("Optimizer", optimizer_str)


if __name__ == '__main__':
    unittest.main() 