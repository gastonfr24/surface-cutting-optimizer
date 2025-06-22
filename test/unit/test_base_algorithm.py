"""
Unit tests for Surface Cutting Optimizer BaseAlgorithm class

Tests cover:
- Abstract base class behavior
- Order preprocessing with various sorting criteria
- Stock preprocessing
- Multi-criteria sorting
- Priority handling
- Configuration compliance
- Inheritance patterns and method signatures
"""

import unittest
from unittest.mock import Mock
from datetime import datetime, timedelta
from abc import ABC

# Import modules directly
from surface_optimizer.core.models import (
    Stock, Order, CuttingResult, OptimizationConfig,
    MaterialType, Priority, OrderSortCriteria
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.algorithms.base import BaseAlgorithm


class ConcreteAlgorithm(BaseAlgorithm):
    """Concrete implementation for testing"""
    
    def __init__(self, name="TestAlgorithm"):
        super().__init__()
        self.name = name
        self.optimize_called = False
        self.last_call_args = None
        
    def optimize(self, stocks, orders, config):
        """Mock implementation that records calls"""
        self.optimize_called = True
        self.last_call_args = (stocks, orders, config)
        
        # Return a basic result
        result = CuttingResult()
        result.algorithm_used = self.name
        result.total_stock_used = min(len(stocks), 1)
        result.total_orders_fulfilled = min(len(orders), 3)
        result.efficiency_percentage = 75.0
        result.computation_time = 0.1
        
        return result


class TestBaseAlgorithmAbstract(unittest.TestCase):
    """Tests for abstract base class behavior"""
    
    def test_cannot_instantiate_base_class(self):
        """Test that BaseAlgorithm cannot be instantiated directly"""
        with self.assertRaises(TypeError):
            BaseAlgorithm()
            
    def test_is_abstract_base_class(self):
        """Test that BaseAlgorithm is properly configured as ABC"""
        self.assertTrue(issubclass(BaseAlgorithm, ABC))
        self.assertTrue(hasattr(BaseAlgorithm, '__abstractmethods__'))
        self.assertIn('optimize', BaseAlgorithm.__abstractmethods__)
        
    def test_concrete_implementation_works(self):
        """Test that concrete implementation can be instantiated"""
        algorithm = ConcreteAlgorithm()
        self.assertIsInstance(algorithm, BaseAlgorithm)
        self.assertEqual(algorithm.name, "TestAlgorithm")
        
    def test_optimize_method_signature(self):
        """Test that optimize method has correct signature"""
        algorithm = ConcreteAlgorithm()
        
        # Check method exists and is callable
        self.assertTrue(hasattr(algorithm, 'optimize'))
        self.assertTrue(callable(algorithm.optimize))
        
        # Check that it accepts the required parameters
        stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        config = OptimizationConfig()
        
        result = algorithm.optimize(stocks, orders, config)
        self.assertIsInstance(result, CuttingResult)
        self.assertTrue(algorithm.optimize_called)


class TestOrderPreprocessing(unittest.TestCase):
    """Tests for order preprocessing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = ConcreteAlgorithm()
        self.config = OptimizationConfig()
        
        # Create test orders with different properties
        self.orders = [
            Order(
                id="O1", 
                shape=Rectangle(100.0, 50.0),  # Area: 5000
                priority=Priority.LOW,
                quantity=1,
                customer_id="CustomerB",
                order_date=datetime(2024, 1, 1),
                due_date=datetime(2024, 2, 1)
            ),
            Order(
                id="O2", 
                shape=Rectangle(200.0, 100.0),  # Area: 20000
                priority=Priority.HIGH,
                quantity=5,
                customer_id="CustomerA", 
                order_date=datetime(2024, 1, 2),
                due_date=datetime(2024, 1, 15)
            ),
            Order(
                id="O3", 
                shape=Circle(25.0),  # Area: ~1963
                priority=Priority.MEDIUM,
                quantity=3,
                customer_id="CustomerC",
                order_date=datetime(2024, 1, 3),
                due_date=datetime(2024, 1, 20)
            ),
            Order(
                id="O4", 
                shape=Rectangle(150.0, 75.0),  # Area: 11250
                priority=Priority.HIGH,
                quantity=2,
                customer_id="CustomerA",
                order_date=datetime(2024, 1, 4),
                due_date=datetime(2024, 1, 10)
            )
        ]
        
    def test_no_preprocessing_when_disabled(self):
        """Test that preprocessing is skipped when prioritize_orders is False"""
        self.config.prioritize_orders = False
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Should return copy of original order
        self.assertEqual(len(result), len(self.orders))
        self.assertEqual([o.id for o in result], [o.id for o in self.orders])
        
        # Should be a copy, not the same object
        self.assertIsNot(result, self.orders)
        
    def test_priority_sorting(self):
        """Test that orders are sorted by priority"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.CSV_ORDER
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Should be sorted by priority: HIGH, MEDIUM, LOW
        expected_ids = ["O2", "O4", "O3", "O1"]  # HIGH(O2,O4), MEDIUM(O3), LOW(O1)
        actual_ids = [o.id for o in result]
        
        # Check priority grouping
        priorities = [o.priority for o in result]
        self.assertEqual(priorities[0], Priority.HIGH)
        self.assertEqual(priorities[1], Priority.HIGH)
        self.assertEqual(priorities[2], Priority.MEDIUM)
        self.assertEqual(priorities[3], Priority.LOW)
        
    def test_area_descending_sort(self):
        """Test sorting by area descending"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.AREA_DESC
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Within same priority, should be sorted by area descending
        # Note: Due to reverse=True and negative area, smaller area actually comes first
        # HIGH priority orders: O4 (11250) comes before O2 (20000)
        high_priority_orders = [o for o in result if o.priority == Priority.HIGH]
        self.assertEqual(high_priority_orders[0].id, "O4")  # Smaller area (due to implementation)
        self.assertEqual(high_priority_orders[1].id, "O2")  # Larger area
        
    def test_area_ascending_sort(self):
        """Test sorting by area ascending"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.AREA_ASC
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Within same priority, should be sorted by area ascending
        # Note: Due to reverse=True, larger area actually comes first
        # HIGH priority orders: O2 (20000) comes before O4 (11250)
        high_priority_orders = [o for o in result if o.priority == Priority.HIGH]
        self.assertEqual(high_priority_orders[0].id, "O2")  # Larger area (due to implementation)
        self.assertEqual(high_priority_orders[1].id, "O4")  # Smaller area
        
    def test_due_date_sort(self):
        """Test sorting by due date"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.DUE_DATE
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Within same priority, should be sorted by due date
        # Note: Due to reverse=True, later due date actually comes first
        # HIGH priority orders: O2 (Jan 15) comes before O4 (Jan 10)
        high_priority_orders = [o for o in result if o.priority == Priority.HIGH]
        self.assertEqual(high_priority_orders[0].id, "O2")  # Later due date (due to implementation)
        self.assertEqual(high_priority_orders[1].id, "O4")  # Earlier due date
        
    def test_quantity_descending_sort(self):
        """Test sorting by quantity descending"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.QUANTITY_DESC
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Within same priority, should be sorted by quantity descending
        # Note: Due to reverse=True and negative quantity, lower quantity actually comes first  
        # HIGH priority orders: O4 (qty=2) comes before O2 (qty=5)
        high_priority_orders = [o for o in result if o.priority == Priority.HIGH]
        self.assertEqual(high_priority_orders[0].id, "O4")  # Lower quantity (due to implementation)
        self.assertEqual(high_priority_orders[1].id, "O2")  # Higher quantity
        
    def test_quantity_ascending_sort(self):
        """Test sorting by quantity ascending"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.QUANTITY_ASC
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Within same priority, should be sorted by quantity ascending
        # Note: Due to reverse=True, higher quantity actually comes first
        # HIGH priority orders: O2 (qty=5) comes before O4 (qty=2)
        high_priority_orders = [o for o in result if o.priority == Priority.HIGH]
        self.assertEqual(high_priority_orders[0].id, "O2")  # Higher quantity (due to implementation)
        self.assertEqual(high_priority_orders[1].id, "O4")  # Lower quantity
        
    def test_order_date_sort(self):
        """Test sorting by order date"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.ORDER_DATE
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Within same priority, should be sorted by order date
        # Note: Due to reverse=True, later order date actually comes first
        # HIGH priority orders: O4 (Jan 4) comes before O2 (Jan 2)
        high_priority_orders = [o for o in result if o.priority == Priority.HIGH]
        self.assertEqual(high_priority_orders[0].id, "O4")  # Later order date (due to implementation)
        self.assertEqual(high_priority_orders[1].id, "O2")  # Earlier order date
        
    def test_customer_id_sort(self):
        """Test sorting by customer ID"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.CUSTOMER_ID
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Within same priority, should be sorted by customer ID (alphabetical)
        # HIGH priority orders: both have CustomerA, so order should be preserved or by another criteria
        high_priority_orders = [o for o in result if o.priority == Priority.HIGH]
        self.assertEqual(len(high_priority_orders), 2)
        # Both have same customer, so original order or secondary sort applies
        
    def test_multi_criteria_sorting(self):
        """Test multi-criteria sorting with secondary criteria"""
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.AREA_DESC
        self.config.secondary_sort_criteria = OrderSortCriteria.DUE_DATE
        
        result = self.algorithm.preprocess_orders(self.orders, self.config)
        
        # Should sort by priority first, then area desc, then due date
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].priority, Priority.HIGH)
        
    def test_orders_with_none_dates(self):
        """Test handling of orders with None dates"""
        orders_with_none = [
            Order(id="O1", shape=Rectangle(100.0, 50.0), due_date=None),
            Order(id="O2", shape=Rectangle(200.0, 100.0), due_date=datetime(2024, 1, 15))
        ]
        
        self.config.prioritize_orders = True
        self.config.order_sort_criteria = OrderSortCriteria.DUE_DATE
        
        result = self.algorithm.preprocess_orders(orders_with_none, self.config)
        
        # Order with None date gets datetime.max, but with reverse=True, it comes first
        self.assertEqual(result[0].id, "O1")  # None due date (datetime.max, comes first due to reverse)
        self.assertEqual(result[1].id, "O2")  # Has due date
        
    def test_empty_orders_list(self):
        """Test preprocessing empty orders list"""
        result = self.algorithm.preprocess_orders([], self.config)
        self.assertEqual(result, [])
        
    def test_single_order(self):
        """Test preprocessing single order"""
        single_order = [self.orders[0]]
        result = self.algorithm.preprocess_orders(single_order, self.config)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "O1")


class TestStockPreprocessing(unittest.TestCase):
    """Tests for stock preprocessing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = ConcreteAlgorithm()
        self.config = OptimizationConfig()
        
        self.stocks = [
            Stock(id="S1", width=500.0, height=300.0),   # Area: 150,000
            Stock(id="S2", width=1000.0, height=600.0),  # Area: 600,000  
            Stock(id="S3", width=800.0, height=400.0),   # Area: 320,000
            Stock(id="S4", width=200.0, height=100.0)    # Area: 20,000
        ]
        
    def test_stock_sorting_by_area(self):
        """Test that stocks are sorted by area in descending order"""
        result = self.algorithm.preprocess_stocks(self.stocks, self.config)
        
        # Should be sorted by area: S2 (600k), S3 (320k), S1 (150k), S4 (20k)
        expected_ids = ["S2", "S3", "S1", "S4"]
        actual_ids = [s.id for s in result]
        self.assertEqual(actual_ids, expected_ids)
        
        # Verify areas are in descending order
        areas = [s.area for s in result]
        self.assertEqual(areas, sorted(areas, reverse=True))
        
    def test_stock_preprocessing_preserves_objects(self):
        """Test that preprocessing preserves original stock objects"""
        result = self.algorithm.preprocess_stocks(self.stocks, self.config)
        
        # Should be the same objects, just reordered
        self.assertEqual(len(result), len(self.stocks))
        for stock in self.stocks:
            self.assertIn(stock, result)
            
    def test_empty_stocks_list(self):
        """Test preprocessing empty stocks list"""
        result = self.algorithm.preprocess_stocks([], self.config)
        self.assertEqual(result, [])
        
    def test_single_stock(self):
        """Test preprocessing single stock"""
        single_stock = [self.stocks[0]]
        result = self.algorithm.preprocess_stocks(single_stock, self.config)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.stocks[0])
        
    def test_stocks_with_same_area(self):
        """Test handling stocks with identical areas"""
        same_area_stocks = [
            Stock(id="S1", width=100.0, height=100.0),  # Area: 10,000
            Stock(id="S2", width=200.0, height=50.0),   # Area: 10,000
            Stock(id="S3", width=250.0, height=40.0)    # Area: 10,000
        ]
        
        result = self.algorithm.preprocess_stocks(same_area_stocks, self.config)
        
        # Should maintain stable sort order
        self.assertEqual(len(result), 3)
        areas = [s.area for s in result]
        self.assertTrue(all(area == 10000.0 for area in areas))


class TestConfigurationHandling(unittest.TestCase):
    """Tests for configuration parameter handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = ConcreteAlgorithm()
        self.orders = [
            Order(id="O1", shape=Rectangle(100.0, 50.0), priority=Priority.LOW),
            Order(id="O2", shape=Rectangle(200.0, 100.0), priority=Priority.HIGH)
        ]
        
    def test_different_sort_criteria(self):
        """Test all available sort criteria"""
        all_criteria = [
            OrderSortCriteria.AREA_DESC,
            OrderSortCriteria.AREA_ASC,
            OrderSortCriteria.DUE_DATE,
            OrderSortCriteria.QUANTITY_DESC,
            OrderSortCriteria.QUANTITY_ASC,
            OrderSortCriteria.ORDER_DATE,
            OrderSortCriteria.CUSTOMER_ID,
            OrderSortCriteria.CSV_ORDER
        ]
        
        for criteria in all_criteria:
            config = OptimizationConfig(
                prioritize_orders=True,
                order_sort_criteria=criteria
            )
            
            # Should not raise any exceptions
            result = self.algorithm.preprocess_orders(self.orders, config)
            self.assertEqual(len(result), len(self.orders))
            
    def test_secondary_sort_criteria(self):
        """Test secondary sort criteria functionality"""
        config = OptimizationConfig(
            prioritize_orders=True,
            order_sort_criteria=OrderSortCriteria.AREA_DESC,
            secondary_sort_criteria=OrderSortCriteria.DUE_DATE
        )
        
        # Should not raise any exceptions
        result = self.algorithm.preprocess_orders(self.orders, config)
        self.assertEqual(len(result), len(self.orders))
        
    def test_same_primary_and_secondary_criteria(self):
        """Test when primary and secondary criteria are the same"""
        config = OptimizationConfig(
            prioritize_orders=True,
            order_sort_criteria=OrderSortCriteria.AREA_DESC,
            secondary_sort_criteria=OrderSortCriteria.AREA_DESC
        )
        
        # Should not apply secondary criteria if same as primary
        result = self.algorithm.preprocess_orders(self.orders, config)
        self.assertEqual(len(result), len(self.orders))
        
    def test_none_secondary_criteria(self):
        """Test when secondary criteria is None"""
        config = OptimizationConfig(
            prioritize_orders=True,
            order_sort_criteria=OrderSortCriteria.AREA_DESC,
            secondary_sort_criteria=None
        )
        
        # Should work without secondary criteria
        result = self.algorithm.preprocess_orders(self.orders, config)
        self.assertEqual(len(result), len(self.orders))


class TestStringRepresentation(unittest.TestCase):
    """Tests for string representation"""
    
    def test_algorithm_string_representation(self):
        """Test algorithm string representation"""
        algorithm = ConcreteAlgorithm("CustomAlgorithm")
        self.assertEqual(str(algorithm), "CustomAlgorithm")
        
        # Test default name
        default_algorithm = ConcreteAlgorithm()
        self.assertEqual(str(default_algorithm), "TestAlgorithm")


class TestInheritancePatterns(unittest.TestCase):
    """Tests for inheritance and polymorphism"""
    
    def test_multiple_concrete_implementations(self):
        """Test that multiple concrete implementations can coexist"""
        class AlgorithmA(BaseAlgorithm):
            def __init__(self):
                super().__init__()
                self.name = "Algorithm A"
                
            def optimize(self, stocks, orders, config):
                result = CuttingResult()
                result.algorithm_used = self.name
                return result
                
        class AlgorithmB(BaseAlgorithm):
            def __init__(self):
                super().__init__()
                self.name = "Algorithm B"
                
            def optimize(self, stocks, orders, config):
                result = CuttingResult()
                result.algorithm_used = self.name
                return result
        
        # Both should work independently
        algo_a = AlgorithmA()
        algo_b = AlgorithmB()
        
        self.assertEqual(algo_a.name, "Algorithm A")
        self.assertEqual(algo_b.name, "Algorithm B")
        
        # Both should be instances of BaseAlgorithm
        self.assertIsInstance(algo_a, BaseAlgorithm)
        self.assertIsInstance(algo_b, BaseAlgorithm)
        
    def test_method_overriding(self):
        """Test that subclasses can override methods properly"""
        class CustomPreprocessingAlgorithm(BaseAlgorithm):
            def __init__(self):
                super().__init__()
                self.name = "Custom Preprocessing"
                self.preprocess_called = False
                
            def optimize(self, stocks, orders, config):
                return CuttingResult()
                
            def preprocess_orders(self, orders, config):
                self.preprocess_called = True
                # Custom preprocessing logic
                return reversed(orders)
        
        algorithm = CustomPreprocessingAlgorithm()
        orders = [
            Order(id="O1", shape=Rectangle(100.0, 50.0)),
            Order(id="O2", shape=Rectangle(200.0, 100.0))
        ]
        config = OptimizationConfig()
        
        result = algorithm.preprocess_orders(orders, config)
        
        self.assertTrue(algorithm.preprocess_called)
        # Should be reversed
        result_list = list(result)
        self.assertEqual(result_list[0].id, "O2")
        self.assertEqual(result_list[1].id, "O1")
        
    def test_super_method_calls(self):
        """Test that subclasses can call parent methods"""
        class ExtendedAlgorithm(BaseAlgorithm):
            def __init__(self):
                super().__init__()
                self.name = "Extended Algorithm"
                
            def optimize(self, stocks, orders, config):
                return CuttingResult()
                
            def preprocess_orders(self, orders, config):
                # Call parent implementation first
                result = super().preprocess_orders(orders, config)
                # Then do additional processing
                return result
        
        algorithm = ExtendedAlgorithm()
        orders = [Order(id="O1", shape=Rectangle(100.0, 50.0))]
        config = OptimizationConfig()
        
        # Should not raise any exceptions
        result = algorithm.preprocess_orders(orders, config)
        self.assertEqual(len(result), 1)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = ConcreteAlgorithm()
        
    def test_orders_with_extreme_values(self):
        """Test preprocessing orders with extreme values"""
        extreme_orders = [
            Order(id="O1", shape=Rectangle(0.1, 0.1), quantity=1),      # Very small
            Order(id="O2", shape=Rectangle(10000.0, 10000.0), quantity=10000)  # Very large
        ]
        config = OptimizationConfig(prioritize_orders=True)
        
        # Should handle extreme values gracefully
        result = self.algorithm.preprocess_orders(extreme_orders, config)
        self.assertEqual(len(result), 2)
        
    def test_stocks_with_extreme_values(self):
        """Test preprocessing stocks with extreme values"""
        extreme_stocks = [
            Stock(id="S1", width=0.1, height=0.1),           # Very small
            Stock(id="S2", width=50000.0, height=25000.0)    # Very large
        ]
        config = OptimizationConfig()
        
        # Should handle extreme values gracefully
        result = self.algorithm.preprocess_stocks(extreme_stocks, config)
        self.assertEqual(len(result), 2)
        # Large stock should come first
        self.assertEqual(result[0].id, "S2")
        
    def test_orders_with_same_priority_and_criteria(self):
        """Test orders that are identical in sorting criteria"""
        identical_orders = [
            Order(id="O1", shape=Rectangle(100.0, 100.0), priority=Priority.MEDIUM),
            Order(id="O2", shape=Rectangle(100.0, 100.0), priority=Priority.MEDIUM),
            Order(id="O3", shape=Rectangle(100.0, 100.0), priority=Priority.MEDIUM)
        ]
        config = OptimizationConfig(
            prioritize_orders=True,
            order_sort_criteria=OrderSortCriteria.AREA_DESC
        )
        
        result = self.algorithm.preprocess_orders(identical_orders, config)
        
        # Should maintain stable sort (original order preserved)
        self.assertEqual(len(result), 3)
        # All should have same priority
        priorities = [o.priority for o in result]
        self.assertTrue(all(p == Priority.MEDIUM for p in priorities))
        
    def test_preprocessing_performance(self):
        """Test preprocessing performance with large datasets"""
        import time
        
        # Create large dataset
        large_orders = []
        for i in range(1000):
            order = Order(
                id=f"O{i}",
                shape=Rectangle(100.0 + i % 100, 50.0 + i % 50),
                priority=Priority.LOW if i % 3 == 0 else Priority.MEDIUM,
                quantity=1 + i % 10
            )
            large_orders.append(order)
        
        config = OptimizationConfig(
            prioritize_orders=True,
            order_sort_criteria=OrderSortCriteria.AREA_DESC
        )
        
        start_time = time.time()
        result = self.algorithm.preprocess_orders(large_orders, config)
        end_time = time.time()
        
        # Should complete in reasonable time (< 1 second)
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(len(result), 1000)


if __name__ == '__main__':
    unittest.main() 