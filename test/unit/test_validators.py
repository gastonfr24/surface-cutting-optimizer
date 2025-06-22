"""
Unit tests for Surface Cutting Optimizer validation system

Tests cover:
- Stock validation (dimensions, materials, properties)
- Order validation (quantities, shapes, requirements)
- Configuration validation (parameters, constraints)
- Stock-order compatibility validation
- Result validation (placement, efficiency, bounds)
- Data consistency validation
- Edge cases and error conditions
"""

import unittest
import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from surface_optimizer.core.validators import (
    validate_stocks, validate_orders, validate_configuration,
    validate_stock_order_compatibility, validate_cutting_result,
    validate_placement_bounds, validate_material_compatibility,
    validate_order_quantities, validate_stock_dimensions
)
from surface_optimizer.core.models import (
    Stock, Order, CuttingResult, OptimizationConfig, PlacedShape,
    MaterialType, Priority, OrderStatus
)
from surface_optimizer.core.geometry import Rectangle, Circle, Polygon
from surface_optimizer.core.exceptions import (
    ValidationError, InvalidDimensionsError
)


class TestStockValidation(unittest.TestCase):
    """Tests for stock validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_stock = Stock(
            id="S1",
            width=1000.0,
            height=500.0,
            thickness=6.0,
            material_type=MaterialType.GLASS,
            cost_per_unit=10.0,
            supplier="TestSupplier",
            quality_grade="A"
        )
        
    def test_valid_stock_validation(self):
        """Test validation of valid stock"""
        # Should not raise any exception
        validate_stocks([self.valid_stock])
        
        # Individual validation should also pass
        issues = self.valid_stock.validate()
        self.assertEqual(len(issues), 0)
        
    def test_stock_dimension_validation(self):
        """Test stock dimension validation"""
        # Test zero width
        with self.assertRaises(InvalidDimensionsError):
            Stock(id="S1", width=0.0, height=500.0)
            
        # Test negative height
        with self.assertRaises(InvalidDimensionsError):
            Stock(id="S1", width=1000.0, height=-500.0)
            
        # Test negative thickness
        with self.assertRaises(InvalidDimensionsError):
            Stock(id="S1", width=1000.0, height=500.0, thickness=-1.0)
            
    def test_stock_area_validation(self):
        """Test stock area validation"""
        # Very small stock should trigger warning
        small_stock = Stock(id="S1", width=10.0, height=10.0)
        issues = small_stock.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("very small" in issue.lower() for issue in issues))
        
        # Very large stock should trigger warning
        large_stock = Stock(id="S1", width=50000.0, height=50000.0)
        issues = large_stock.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("very large" in issue.lower() for issue in issues))
        
    def test_stock_cost_validation(self):
        """Test stock cost validation"""
        # Negative cost should trigger warning
        negative_cost_stock = Stock(
            id="S1", width=1000.0, height=500.0, cost_per_unit=-10.0
        )
        issues = negative_cost_stock.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("negative cost" in issue.lower() for issue in issues))
        
    def test_stock_id_validation(self):
        """Test stock ID validation"""
        # Empty ID is allowed by the model but should be caught by validators
        empty_stock = Stock(id="", width=1000.0, height=500.0)
        with self.assertRaises(ValidationError):
            validate_stocks([empty_stock])
            
        # Whitespace only ID should also be caught
        whitespace_stock = Stock(id="   ", width=1000.0, height=500.0)
        with self.assertRaises(ValidationError):
            validate_stocks([whitespace_stock])
            
    def test_multiple_stocks_validation(self):
        """Test validation of multiple stocks"""
        stocks = [
            Stock(id="S1", width=1000.0, height=500.0),
            Stock(id="S2", width=800.0, height=600.0),
            Stock(id="S3", width=1200.0, height=400.0)
        ]
        
        # Should not raise exception
        validate_stocks(stocks)
        
    def test_duplicate_stock_ids(self):
        """Test validation with duplicate stock IDs"""
        stocks = [
            Stock(id="S1", width=1000.0, height=500.0),
            Stock(id="S1", width=800.0, height=600.0)  # Duplicate ID
        ]
        
        with self.assertRaises(ValidationError) as context:
            validate_stocks(stocks)
        self.assertIn("duplicate", str(context.exception).lower())
        
    def test_empty_stocks_list(self):
        """Test validation with empty stocks list"""
        with self.assertRaises(ValidationError):
            validate_stocks([])
            
    def test_stock_expiry_date_validation(self):
        """Test stock expiry date validation"""
        # Past expiry date should trigger warning
        past_expiry = Stock(
            id="S1", width=1000.0, height=500.0,
            expiry_date=datetime.now() - timedelta(days=30)
        )
        issues = past_expiry.validate()
        self.assertGreater(len(issues), 0)
        
        # Near expiry should trigger warning
        near_expiry = Stock(
            id="S1", width=1000.0, height=500.0,
            expiry_date=datetime.now() + timedelta(days=5)
        )
        issues = near_expiry.validate()
        self.assertGreater(len(issues), 0)


class TestOrderValidation(unittest.TestCase):
    """Tests for order validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_order = Order(
            id="O1",
            shape=Rectangle(200.0, 100.0),
            quantity=1,
            priority=Priority.MEDIUM,
            material_type=MaterialType.GLASS
        )
        
    def test_valid_order_validation(self):
        """Test validation of valid order"""
        # Should not raise any exception
        validate_orders([self.valid_order])
        
        # Individual validation should also pass
        issues = self.valid_order.validate()
        self.assertEqual(len(issues), 0)
        
    def test_order_quantity_validation(self):
        """Test order quantity validation"""
        # Zero quantity should fail
        with self.assertRaises(InvalidDimensionsError):
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=0)
            
        # Negative quantity should fail
        with self.assertRaises(InvalidDimensionsError):
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=-1)
            
        # Very large quantity should trigger warning
        large_qty_order = Order(
            id="O1", shape=Rectangle(100.0, 50.0), quantity=10000
        )
        issues = large_qty_order.validate()
        self.assertGreater(len(issues), 0)
        
    def test_order_shape_validation(self):
        """Test order shape validation"""
        # Valid shapes should pass
        rect_order = Order(id="O1", shape=Rectangle(100.0, 50.0))
        self.assertEqual(len(rect_order.validate()), 0)
        
        circle_order = Order(id="O2", shape=Circle(25.0))
        self.assertEqual(len(circle_order.validate()), 0)
        
        # Very small shapes should trigger warning
        tiny_order = Order(id="O3", shape=Rectangle(0.1, 0.1))
        issues = tiny_order.validate()
        self.assertGreater(len(issues), 0)
        
        # Very large shapes should trigger warning
        huge_order = Order(id="O4", shape=Rectangle(10000.0, 10000.0))
        issues = huge_order.validate()
        self.assertGreater(len(issues), 0)
        
    def test_order_id_validation(self):
        """Test order ID validation"""
        # Empty ID is allowed by the model but should be caught by validators
        empty_order = Order(id="", shape=Rectangle(100.0, 50.0))
        with self.assertRaises(ValidationError):
            validate_orders([empty_order])
            
        # Whitespace only ID should also be caught
        whitespace_order = Order(id="   ", shape=Rectangle(100.0, 50.0))
        with self.assertRaises(ValidationError):
            validate_orders([whitespace_order])
            
    def test_multiple_orders_validation(self):
        """Test validation of multiple orders"""
        orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0)),
            Order(id="O2", shape=Circle(50.0)),
            Order(id="O3", shape=Rectangle(150.0, 150.0))
        ]
        
        # Should not raise exception
        validate_orders(orders)
        
    def test_duplicate_order_ids(self):
        """Test validation with duplicate order IDs"""
        orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0)),
            Order(id="O1", shape=Circle(50.0))  # Duplicate ID
        ]
        
        with self.assertRaises(ValidationError) as context:
            validate_orders(orders)
        self.assertIn("duplicate", str(context.exception).lower())
        
    def test_empty_orders_list(self):
        """Test validation with empty orders list"""
        with self.assertRaises(ValidationError):
            validate_orders([])
            
    def test_order_due_date_validation(self):
        """Test order due date validation"""
        # Past due date should trigger warning
        past_due = Order(
            id="O1", shape=Rectangle(100.0, 50.0),
            due_date=datetime.now() - timedelta(days=5)
        )
        issues = past_due.validate()
        self.assertGreater(len(issues), 0)
        
        # Near due date should trigger warning
        near_due = Order(
            id="O1", shape=Rectangle(100.0, 50.0),
            due_date=datetime.now() + timedelta(hours=12)
        )
        issues = near_due.validate()
        self.assertGreater(len(issues), 0)
        
    def test_order_priority_validation(self):
        """Test order priority validation"""
        # All priority levels should be valid
        for priority in Priority:
            order = Order(id="O1", shape=Rectangle(100.0, 50.0), priority=priority)
            self.assertEqual(len(order.validate()), 0)


class TestConfigurationValidation(unittest.TestCase):
    """Tests for configuration validation"""
    
    def test_valid_configuration(self):
        """Test validation of valid configuration"""
        config = OptimizationConfig(
            allow_rotation=True,
            cutting_width=2.0,
            max_computation_time=60.0,
            prioritize_orders=True
        )
        
        issues = config.validate()
        self.assertEqual(len(issues), 0)
        
    def test_invalid_cutting_width(self):
        """Test invalid cutting width validation"""
        # Negative cutting width
        config = OptimizationConfig(cutting_width=-1.0)
        issues = config.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("cutting width" in issue.lower() for issue in issues))
        
        # Zero cutting width should be allowed
        config = OptimizationConfig(cutting_width=0.0)
        issues = config.validate()
        self.assertEqual(len(issues), 0)
        
    def test_invalid_computation_time(self):
        """Test invalid computation time validation"""
        # Negative computation time
        config = OptimizationConfig(max_computation_time=-10.0)
        issues = config.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("computation time" in issue.lower() for issue in issues))
        
        # Zero computation time
        config = OptimizationConfig(max_computation_time=0.0)
        issues = config.validate()
        self.assertGreater(len(issues), 0)
        
    def test_invalid_placement_precision(self):
        """Test invalid placement precision validation"""
        # Negative precision
        config = OptimizationConfig(placement_precision=-1.0)
        issues = config.validate()
        self.assertGreater(len(issues), 0)
        
        # Zero precision
        config = OptimizationConfig(placement_precision=0.0)
        issues = config.validate()
        self.assertGreater(len(issues), 0)
        
        # Valid precision
        config = OptimizationConfig(placement_precision=0.1)
        issues = config.validate()
        self.assertEqual(len(issues), 0)


class TestStockOrderCompatibility(unittest.TestCase):
    """Tests for stock-order compatibility validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.glass_stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.GLASS),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.GLASS)
        ]
        
        self.metal_stocks = [
            Stock(id="S3", width=1200.0, height=400.0, material_type=MaterialType.METAL)
        ]
        
        self.glass_orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), material_type=MaterialType.GLASS),
            Order(id="O2", shape=Circle(50.0), material_type=MaterialType.GLASS)
        ]
        
        self.metal_orders = [
            Order(id="O3", shape=Rectangle(150.0, 150.0), material_type=MaterialType.METAL)
        ]
        
    def test_compatible_materials(self):
        """Test compatible material validation"""
        # Same materials should be compatible
        validate_stock_order_compatibility(self.glass_stocks, self.glass_orders)
        validate_stock_order_compatibility(self.metal_stocks, self.metal_orders)
        
    def test_incompatible_materials(self):
        """Test incompatible material validation"""
        # Different materials should fail
        with self.assertRaises(ValidationError) as context:
            validate_stock_order_compatibility(self.glass_stocks, self.metal_orders)
        self.assertIn("No stocks available for material type", str(context.exception))
        
        with self.assertRaises(ValidationError) as context:
            validate_stock_order_compatibility(self.metal_stocks, self.glass_orders)
        self.assertIn("No stocks available for material type", str(context.exception))
        
    def test_mixed_materials_success(self):
        """Test mixed materials when all are covered"""
        mixed_stocks = self.glass_stocks + self.metal_stocks
        mixed_orders = self.glass_orders + self.metal_orders
        
        # Should not raise exception
        validate_stock_order_compatibility(mixed_stocks, mixed_orders)
        
    def test_insufficient_stock_area(self):
        """Test insufficient stock area validation"""
        # Small stock, large orders
        small_stock = [Stock(id="S1", width=100.0, height=100.0, material_type=MaterialType.GLASS)]
        large_orders = [
            Order(id="O1", shape=Rectangle(500.0, 500.0), material_type=MaterialType.GLASS),
            Order(id="O2", shape=Rectangle(600.0, 600.0), material_type=MaterialType.GLASS)
        ]
        
        # Should still pass validation (algorithm will handle optimization)
        validate_stock_order_compatibility(small_stock, large_orders)
        
    def test_size_compatibility_warnings(self):
        """Test size compatibility warnings"""
        # Very small stock with large orders should log warnings
        tiny_stock = [Stock(id="S1", width=50.0, height=50.0, material_type=MaterialType.GLASS)]
        big_orders = [Order(id="O1", shape=Rectangle(1000.0, 1000.0), material_type=MaterialType.GLASS)]
        
        # Should not raise exception but may log warnings
        validate_stock_order_compatibility(tiny_stock, big_orders)


class TestMaterialCompatibility(unittest.TestCase):
    """Tests for material compatibility validation"""
    
    def test_exact_material_match(self):
        """Test exact material type matching"""
        glass_stock = Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.GLASS)
        glass_order = Order(id="O1", shape=Rectangle(100.0, 50.0), material_type=MaterialType.GLASS)
        
        # Should return True for exact match
        self.assertTrue(validate_material_compatibility(glass_stock, glass_order))
        
    def test_material_mismatch(self):
        """Test material type mismatch"""
        glass_stock = Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.GLASS)
        metal_order = Order(id="O1", shape=Rectangle(100.0, 50.0), material_type=MaterialType.METAL)
        
        # Should return False for mismatch
        self.assertFalse(validate_material_compatibility(glass_stock, metal_order))
        
    def test_thickness_compatibility(self):
        """Test thickness compatibility"""
        thin_stock = Stock(id="S1", width=1000.0, height=500.0, thickness=3.0)
        thick_requirement = Order(
            id="O1", shape=Rectangle(100.0, 50.0),
            special_requirements={"min_thickness": 6.0}
        )
        
        # Thin stock should not meet thick requirement
        self.assertFalse(validate_material_compatibility(thin_stock, thick_requirement))
        
        thick_stock = Stock(id="S2", width=1000.0, height=500.0, thickness=10.0)
        # Thick stock should meet thick requirement
        self.assertTrue(validate_material_compatibility(thick_stock, thick_requirement))


class TestPlacementBoundsValidation(unittest.TestCase):
    """Tests for placement bounds validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stock = Stock(id="S1", width=1000.0, height=500.0)
        
    def test_valid_placement(self):
        """Test valid shape placement"""
        shape = Rectangle(width=200.0, height=100.0, x=100.0, y=50.0)
        placed_shape = PlacedShape(order_id="O1", shape=shape, stock_id="S1")
        
        # Should not raise exception
        validate_placement_bounds(placed_shape, self.stock)
        
    def test_placement_exceeds_width(self):
        """Test placement exceeding stock width"""
        shape = Rectangle(width=200.0, height=100.0, x=900.0, y=50.0)  # x + width = 1100 > 1000
        placed_shape = PlacedShape(order_id="O1", shape=shape, stock_id="S1")
        
        with self.assertRaises(ValidationError):
            validate_placement_bounds(placed_shape, self.stock)
            
    def test_placement_exceeds_height(self):
        """Test placement exceeding stock height"""
        shape = Rectangle(width=200.0, height=100.0, x=100.0, y=450.0)  # y + height = 550 > 500
        placed_shape = PlacedShape(order_id="O1", shape=shape, stock_id="S1")
        
        with self.assertRaises(ValidationError):
            validate_placement_bounds(placed_shape, self.stock)
            
    def test_negative_position(self):
        """Test negative position placement"""
        shape = Rectangle(width=200.0, height=100.0, x=-10.0, y=50.0)
        placed_shape = PlacedShape(order_id="O1", shape=shape, stock_id="S1")
        
        with self.assertRaises(ValidationError):
            validate_placement_bounds(placed_shape, self.stock)
            
        shape = Rectangle(width=200.0, height=100.0, x=100.0, y=-10.0)
        placed_shape = PlacedShape(order_id="O1", shape=shape, stock_id="S1")
        
        with self.assertRaises(ValidationError):
            validate_placement_bounds(placed_shape, self.stock)
            
    def test_circle_placement(self):
        """Test circle placement validation"""
        # Valid circle placement
        circle = Circle(radius=50.0, x=100.0, y=100.0)
        placed_shape = PlacedShape(order_id="O1", shape=circle, stock_id="S1")
        
        validate_placement_bounds(placed_shape, self.stock)
        
        # Circle exceeding bounds
        circle = Circle(radius=50.0, x=980.0, y=100.0)  # x + radius = 1030 > 1000
        placed_shape = PlacedShape(order_id="O1", shape=circle, stock_id="S1")
        
        with self.assertRaises(ValidationError):
            validate_placement_bounds(placed_shape, self.stock)
            
    def test_polygon_placement(self):
        """Test polygon placement validation"""
        # Valid triangle placement
        triangle_points = [(100.0, 100.0), (200.0, 100.0), (150.0, 200.0)]
        triangle = Polygon(triangle_points)
        placed_shape = PlacedShape(order_id="O1", shape=triangle, stock_id="S1")
        
        validate_placement_bounds(placed_shape, self.stock)
        
        # Triangle exceeding bounds
        large_triangle_points = [(900.0, 400.0), (1100.0, 400.0), (1000.0, 600.0)]
        large_triangle = Polygon(large_triangle_points)
        placed_shape = PlacedShape(order_id="O1", shape=large_triangle, stock_id="S1")
        
        with self.assertRaises(ValidationError):
            validate_placement_bounds(placed_shape, self.stock)


class TestCuttingResultValidation(unittest.TestCase):
    """Tests for cutting result validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0),
            Stock(id="S2", width=800.0, height=600.0)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0)),
            Order(id="O2", shape=Circle(50.0)),
            Order(id="O3", shape=Rectangle(150.0, 150.0))
        ]
        
    def test_valid_cutting_result(self):
        """Test validation of valid cutting result"""
        result = CuttingResult()
        result.total_stock_used = 2
        result.total_orders_fulfilled = 2
        result.efficiency_percentage = 75.5
        result.computation_time = 1.5
        result.placed_shapes = [
            PlacedShape(
                order_id="O1",
                shape=Rectangle(width=200.0, height=100.0, x=0.0, y=0.0),
                stock_id="S1"
            ),
            PlacedShape(
                order_id="O2", 
                shape=Rectangle(width=100.0, height=100.0, x=0.0, y=0.0),  # Simplified circle as rectangle
                stock_id="S2"
            )
        ]
        result.unfulfilled_orders = [self.orders[2]]  # O3 not fulfilled
        
        # Should not raise exception
        validate_cutting_result(result, self.stocks, self.orders)
        
    def test_invalid_efficiency_percentage(self):
        """Test invalid efficiency percentage"""
        result = CuttingResult()
        result.efficiency_percentage = -10.0  # Invalid
        
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
        result.efficiency_percentage = 150.0  # Invalid
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
    def test_invalid_stock_usage(self):
        """Test invalid stock usage"""
        result = CuttingResult()
        result.total_stock_used = -1  # Invalid
        
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
        result.total_stock_used = len(self.stocks) + 1  # More than available
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
    def test_invalid_orders_fulfilled(self):
        """Test invalid orders fulfilled count"""
        result = CuttingResult()
        result.total_orders_fulfilled = -1  # Invalid
        
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
        result.total_orders_fulfilled = len(self.orders) + 1  # More than available
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
    def test_placed_shapes_validation(self):
        """Test placed shapes validation"""
        result = CuttingResult()
        result.placed_shapes = [
            PlacedShape(
                order_id="INVALID_ID",  # Non-existent order
                shape=Rectangle(width=100.0, height=100.0, x=0.0, y=0.0),
                stock_id="S1"
            )
        ]
        
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
        # Invalid stock ID
        result.placed_shapes = [
            PlacedShape(
                order_id="O1",
                shape=Rectangle(width=100.0, height=100.0, x=0.0, y=0.0),
                stock_id="INVALID_STOCK"  # Non-existent stock
            )
        ]
        
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)
            
    def test_computation_time_validation(self):
        """Test computation time validation"""
        result = CuttingResult()
        result.computation_time = -1.0  # Invalid
        
        with self.assertRaises(ValidationError):
            validate_cutting_result(result, self.stocks, self.orders)


class TestQuantityValidation(unittest.TestCase):
    """Tests for order quantity validation"""
    
    def test_valid_quantities(self):
        """Test valid quantity validation"""
        orders = [
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=1),
            Order(id="O2", shape=Rectangle(100.0, 50.0), quantity=5),
            Order(id="O3", shape=Rectangle(100.0, 50.0), quantity=100)
        ]
        
        # Should not raise exception
        validate_order_quantities(orders)
        
    def test_invalid_quantities(self):
        """Test invalid quantity validation"""
        with self.assertRaises(InvalidDimensionsError):
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=0)
            
        with self.assertRaises(InvalidDimensionsError):
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=-5)
            
    def test_quantity_warnings(self):
        """Test quantity warning thresholds"""
        # Very large quantity should trigger warnings
        large_qty_order = Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=10000)
        issues = large_qty_order.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("large quantity" in issue.lower() for issue in issues))


class TestDimensionValidation(unittest.TestCase):
    """Tests for dimension validation"""
    
    def test_valid_stock_dimensions(self):
        """Test valid stock dimension validation"""
        dimensions = [
            (100.0, 100.0, 6.0),
            (1000.0, 500.0, 3.0),
            (2000.0, 1000.0, 12.0)
        ]
        
        for width, height, thickness in dimensions:
            # Should not raise exception
            validate_stock_dimensions(width, height, thickness)
            
    def test_invalid_stock_dimensions(self):
        """Test invalid stock dimension validation"""
        invalid_dimensions = [
            (-100.0, 500.0, 6.0),  # Negative width
            (100.0, -500.0, 6.0),  # Negative height
            (100.0, 500.0, -6.0),  # Negative thickness
            (0.0, 500.0, 6.0),     # Zero width
            (100.0, 0.0, 6.0),     # Zero height
            (100.0, 500.0, 0.0)    # Zero thickness
        ]
        
        for width, height, thickness in invalid_dimensions:
            with self.assertRaises(InvalidDimensionsError):
                validate_stock_dimensions(width, height, thickness)
                
    def test_dimension_warnings(self):
        """Test dimension warning thresholds"""
        # Very small dimensions
        with self.assertWarns(UserWarning):
            validate_stock_dimensions(1.0, 1.0, 0.1)
            
        # Very large dimensions  
        with self.assertWarns(UserWarning):
            validate_stock_dimensions(100000.0, 100000.0, 100.0)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions"""
    
    def test_minimum_valid_values(self):
        """Test minimum valid values"""
        # Minimum valid stock
        min_stock = Stock(id="S1", width=0.1, height=0.1, thickness=0.1)
        issues = min_stock.validate()
        # Should have warnings but not fail
        self.assertGreater(len(issues), 0)
        
        # Minimum valid order
        min_order = Order(id="O1", shape=Rectangle(0.1, 0.1), quantity=1)
        issues = min_order.validate()
        # Should have warnings but not fail
        self.assertGreater(len(issues), 0)
        
    def test_maximum_reasonable_values(self):
        """Test maximum reasonable values"""
        # Large stock that exceeds our warning threshold (50 m²)
        large_stock = Stock(id="S1", width=10000.0, height=6000.0, thickness=50.0)  # 60 m²
        issues = large_stock.validate()
        # Should have warnings but not fail
        self.assertGreater(len(issues), 0)
        
        # Large order with high quantity
        large_order = Order(id="O1", shape=Rectangle(500.0, 250.0), quantity=2000)  # Exceeds 1000 qty
        issues = large_order.validate()
        # Should have warnings but not fail
        self.assertGreater(len(issues), 0)
        
    def test_float_precision_edge_cases(self):
        """Test floating point precision edge cases"""
        # Very precise dimensions
        precise_stock = Stock(id="S1", width=1000.123456789, height=500.987654321)
        self.assertEqual(len(precise_stock.validate()), 0)
        
        # Scientific notation
        scientific_stock = Stock(id="S1", width=1e3, height=5e2)
        self.assertEqual(len(scientific_stock.validate()), 0)
        
    def test_unicode_ids(self):
        """Test Unicode characters in IDs"""
        # Unicode stock ID
        unicode_stock = Stock(id="S1_测试_🔧", width=1000.0, height=500.0)
        self.assertEqual(len(unicode_stock.validate()), 0)
        
        # Unicode order ID
        unicode_order = Order(id="O1_订单_📦", shape=Rectangle(100.0, 50.0))
        self.assertEqual(len(unicode_order.validate()), 0)
        
    def test_special_characters_in_ids(self):
        """Test special characters in IDs"""
        # Special characters that should be allowed
        special_stock = Stock(id="S1-ABC_123.v2", width=1000.0, height=500.0)
        self.assertEqual(len(special_stock.validate()), 0)
        
        special_order = Order(id="O1-XYZ_456.v1", shape=Rectangle(100.0, 50.0))
        self.assertEqual(len(special_order.validate()), 0)


class TestPerformanceValidation(unittest.TestCase):
    """Tests for validation performance with large datasets"""
    
    def test_large_stock_list_validation(self):
        """Test validation performance with many stocks"""
        import time
        
        # Create 1000 stocks
        stocks = []
        for i in range(1000):
            stocks.append(Stock(
                id=f"S{i}",
                width=1000.0 + i,
                height=500.0 + i,
                material_type=MaterialType.GLASS if i % 2 == 0 else MaterialType.METAL
            ))
        
        start_time = time.time()
        validate_stocks(stocks)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 1 second)
        self.assertLess(end_time - start_time, 1.0)
        
    def test_large_order_list_validation(self):
        """Test validation performance with many orders"""
        import time
        
        # Create 1000 orders
        orders = []
        for i in range(1000):
            orders.append(Order(
                id=f"O{i}",
                shape=Rectangle(100.0 + i % 100, 50.0 + i % 50),
                quantity=1 + i % 10,
                material_type=MaterialType.GLASS if i % 2 == 0 else MaterialType.METAL
            ))
        
        start_time = time.time()
        validate_orders(orders)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 1 second)
        self.assertLess(end_time - start_time, 1.0)


if __name__ == '__main__':
    unittest.main() 