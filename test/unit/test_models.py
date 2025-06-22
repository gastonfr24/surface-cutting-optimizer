"""
Unit tests for Surface Cutting Optimizer core models

Tests cover:
- Stock creation and validation
- Order creation and validation  
- CuttingResult metrics calculation
- MaterialType and Priority enums
- OptimizationConfig validation
- Serialization/deserialization
"""

import unittest
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from surface_optimizer.core.models import (
    Stock, Order, CuttingResult, PlacedShape, OptimizationConfig,
    MaterialType, Priority, OrderStatus, StockStatus, OrderSortCriteria,
    MaterialProperties, Surface, Piece, CuttingPattern
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.exceptions import (
    InvalidDimensionsError, ValidationError
)


class TestMaterialType(unittest.TestCase):
    """Tests for MaterialType enum"""
    
    def test_material_type_values(self):
        """Test MaterialType enum values"""
        self.assertEqual(MaterialType.GLASS.value, "glass")
        self.assertEqual(MaterialType.METAL.value, "metal")
        self.assertEqual(MaterialType.WOOD.value, "wood")
        self.assertEqual(MaterialType.PLASTIC.value, "plastic")
        
    def test_from_string_valid(self):
        """Test creating MaterialType from valid strings"""
        self.assertEqual(MaterialType.from_string("glass"), MaterialType.GLASS)
        self.assertEqual(MaterialType.from_string("METAL"), MaterialType.METAL)
        self.assertEqual(MaterialType.from_string("WooD"), MaterialType.WOOD)
        
    def test_from_string_invalid(self):
        """Test creating MaterialType from invalid strings"""
        with self.assertRaises(ValueError):
            MaterialType.from_string("invalid_material")
        with self.assertRaises(ValueError):
            MaterialType.from_string("")


class TestPriority(unittest.TestCase):
    """Tests for Priority enum"""
    
    def test_priority_weights(self):
        """Test priority weights are correct"""
        self.assertEqual(Priority.LOW.weight, 1)
        self.assertEqual(Priority.MEDIUM.weight, 2)
        self.assertEqual(Priority.HIGH.weight, 3)
        self.assertEqual(Priority.URGENT.weight, 4)
        
    def test_priority_descriptions(self):
        """Test priority descriptions"""
        self.assertEqual(Priority.LOW.description, "Low Priority")
        self.assertEqual(Priority.URGENT.description, "Urgent")
        
    def test_from_weight_valid(self):
        """Test creating Priority from valid weights"""
        self.assertEqual(Priority.from_weight(1), Priority.LOW)
        self.assertEqual(Priority.from_weight(4), Priority.URGENT)
        
    def test_from_weight_invalid(self):
        """Test creating Priority from invalid weights"""
        with self.assertRaises(ValueError):
            Priority.from_weight(0)
        with self.assertRaises(ValueError):
            Priority.from_weight(5)


class TestMaterialProperties(unittest.TestCase):
    """Tests for MaterialProperties class"""
    
    def test_default_properties(self):
        """Test default material properties"""
        props = MaterialProperties()
        self.assertEqual(props.density, 1.0)
        self.assertEqual(props.cost_per_area, 0.0)
        self.assertEqual(props.cutting_speed, 1.0)
        
    def test_glass_properties(self):
        """Test glass-specific properties"""
        props = MaterialProperties.get_default_properties(MaterialType.GLASS)
        self.assertEqual(props.density, 2.5)
        self.assertEqual(props.cost_per_area, 15.0)
        self.assertEqual(props.cutting_speed, 0.8)
        self.assertEqual(props.waste_factor, 0.08)
        
    def test_metal_properties(self):
        """Test metal-specific properties"""
        props = MaterialProperties.get_default_properties(MaterialType.METAL)
        self.assertEqual(props.density, 7.8)
        self.assertEqual(props.cost_per_area, 25.0)
        self.assertEqual(props.cutting_speed, 0.6)
        
    def test_unknown_material_properties(self):
        """Test properties for unknown materials default to base values"""
        props = MaterialProperties.get_default_properties(MaterialType.CERAMIC)
        self.assertEqual(props.density, 1.0)
        self.assertEqual(props.cost_per_area, 0.0)


class TestStock(unittest.TestCase):
    """Tests for Stock class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_stock = Stock(
            id="S001",
            width=2000.0,
            height=1000.0,
            thickness=6.0,
            material_type=MaterialType.GLASS
        )
    
    def test_valid_stock_creation(self):
        """Test creating valid stock"""
        stock = Stock(id="S001", width=1000.0, height=500.0)
        self.assertEqual(stock.id, "S001")
        self.assertEqual(stock.width, 1000.0)
        self.assertEqual(stock.height, 500.0)
        self.assertEqual(stock.thickness, 6.0)  # default
        self.assertEqual(stock.material_type, MaterialType.GLASS)  # default
        
    def test_invalid_dimensions(self):
        """Test stock creation with invalid dimensions"""
        with self.assertRaises(InvalidDimensionsError):
            Stock(id="S001", width=-100.0, height=500.0)
        with self.assertRaises(InvalidDimensionsError):
            Stock(id="S001", width=1000.0, height=0.0)
        with self.assertRaises(InvalidDimensionsError):
            Stock(id="S001", width=1000.0, height=500.0, thickness=-1.0)
    
    def test_area_calculation(self):
        """Test area calculations"""
        self.assertEqual(self.valid_stock.area, 2000000.0)  # 2000 * 1000
        self.assertAlmostEqual(self.valid_stock.area_m2, 2.0)  # 2 m²
        
    def test_volume_calculation(self):
        """Test volume calculation"""
        expected_volume = 2000.0 * 1000.0 * 6.0
        self.assertEqual(self.valid_stock.volume, expected_volume)
        
    def test_weight_calculation(self):
        """Test weight calculation using material properties"""
        # Glass density = 2.5 kg/m³
        expected_weight = 2.0 * 6.0 * 2.5 / 1000  # area_m2 * thickness * density / 1000
        self.assertAlmostEqual(self.valid_stock.weight_kg, expected_weight)
        
    def test_cost_calculation(self):
        """Test cost calculations"""
        # Test with cost_per_unit
        stock_with_cost = Stock(id="S001", width=1000.0, height=500.0, cost_per_unit=100.0)
        self.assertEqual(stock_with_cost.total_cost, 100.0)
        
        # Test with material properties cost
        stock_material_cost = Stock(id="S002", width=1000.0, height=500.0, material_type=MaterialType.GLASS)
        expected_cost = stock_material_cost.area_m2 * 15.0  # Glass cost per area
        self.assertAlmostEqual(stock_material_cost.total_cost, expected_cost)
        
    def test_availability_checks(self):
        """Test stock availability checks"""
        self.assertTrue(self.valid_stock.is_available)
        self.assertFalse(self.valid_stock.is_expired)
        
        # Test reservation
        self.assertTrue(self.valid_stock.reserve())
        self.assertFalse(self.valid_stock.is_available)
        self.assertFalse(self.valid_stock.reserve())  # Already reserved
        
        # Test release
        self.assertTrue(self.valid_stock.release())
        self.assertTrue(self.valid_stock.is_available)
        
    def test_expiry_checks(self):
        """Test stock expiry functionality"""
        expired_stock = Stock(
            id="S002", width=1000.0, height=500.0,
            expiry_date=datetime.now() - timedelta(days=1)
        )
        self.assertTrue(expired_stock.is_expired)
        
        future_stock = Stock(
            id="S003", width=1000.0, height=500.0,
            expiry_date=datetime.now() + timedelta(days=30)
        )
        self.assertFalse(future_stock.is_expired)
        
    def test_shape_fitting(self):
        """Test can_fit_shape method"""
        rect_small = Rectangle(500.0, 300.0)
        rect_large = Rectangle(3000.0, 1500.0)
        circle_small = Circle(250.0)  # radius 250, diameter 500
        circle_large = Circle(600.0)  # radius 600, diameter 1200
        
        self.assertTrue(self.valid_stock.can_fit_shape(rect_small))
        self.assertFalse(self.valid_stock.can_fit_shape(rect_large))
        self.assertTrue(self.valid_stock.can_fit_shape(circle_small))
        self.assertFalse(self.valid_stock.can_fit_shape(circle_large))
        
    def test_validation(self):
        """Test stock validation"""
        issues = self.valid_stock.validate()
        self.assertEqual(len(issues), 0)
        
        # Test expired stock
        expired_stock = Stock(
            id="S002", width=1000.0, height=500.0,
            expiry_date=datetime.now() - timedelta(days=1)
        )
        issues = expired_stock.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("expired" in issue.lower() for issue in issues))
        
    def test_serialization(self):
        """Test to_dict serialization"""
        stock_dict = self.valid_stock.to_dict()
        self.assertEqual(stock_dict["id"], "S001")
        self.assertEqual(stock_dict["width"], 2000.0)
        self.assertEqual(stock_dict["height"], 1000.0)
        self.assertEqual(stock_dict["material_type"], "glass")
        self.assertEqual(stock_dict["area"], 2000000.0)


class TestOrder(unittest.TestCase):
    """Tests for Order class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_order = Order(
            id="O001",
            shape=Rectangle(800.0, 600.0),
            quantity=5,
            priority=Priority.HIGH,
            material_type=MaterialType.GLASS
        )
    
    def test_valid_order_creation(self):
        """Test creating valid order"""
        rect = Rectangle(500.0, 300.0)
        order = Order(id="O001", shape=rect, quantity=3)
        self.assertEqual(order.id, "O001")
        self.assertEqual(order.quantity, 3)
        self.assertEqual(order.priority, Priority.MEDIUM)  # default
        self.assertEqual(order.material_type, MaterialType.GLASS)  # default
        
    def test_invalid_quantity(self):
        """Test order creation with invalid quantity"""
        rect = Rectangle(500.0, 300.0)
        with self.assertRaises(InvalidDimensionsError):
            Order(id="O001", shape=rect, quantity=0)
        with self.assertRaises(InvalidDimensionsError):
            Order(id="O001", shape=rect, quantity=-1)
            
    def test_invalid_tolerance(self):
        """Test order creation with invalid tolerance"""
        rect = Rectangle(500.0, 300.0)
        with self.assertRaises(InvalidDimensionsError):
            Order(id="O001", shape=rect, tolerance=-1.0)
    
    def test_area_calculations(self):
        """Test area calculations"""
        expected_area = 800.0 * 600.0 * 5  # width * height * quantity
        self.assertEqual(self.valid_order.total_area, expected_area)
        
    def test_value_calculations(self):
        """Test value calculations"""
        order_with_price = Order(
            id="O002", shape=Rectangle(100.0, 100.0),
            quantity=2, unit_price=50.0
        )
        self.assertEqual(order_with_price.total_value, 100.0)  # 2 * 50
        
    def test_priority_checks(self):
        """Test priority-related properties"""
        urgent_order = Order(
            id="O002", shape=Rectangle(100.0, 100.0),
            priority=Priority.URGENT
        )
        self.assertTrue(urgent_order.is_urgent)
        self.assertFalse(self.valid_order.is_urgent)
        
    def test_due_date_calculations(self):
        """Test due date calculations"""
        future_date = datetime.now() + timedelta(days=7)
        past_date = datetime.now() - timedelta(days=1)
        
        future_order = Order(
            id="O002", shape=Rectangle(100.0, 100.0),
            due_date=future_date
        )
        past_order = Order(
            id="O003", shape=Rectangle(100.0, 100.0),
            due_date=past_date
        )
        
        self.assertFalse(future_order.is_overdue)
        self.assertTrue(past_order.is_overdue)
        self.assertAlmostEqual(future_order.days_until_due, 7, delta=1)
        
    def test_stock_compatibility(self):
        """Test can_be_fulfilled_by_stock method"""
        compatible_stock = Stock(
            id="S001", width=1000.0, height=800.0,
            material_type=MaterialType.GLASS, thickness=6.0
        )
        incompatible_material = Stock(
            id="S002", width=1000.0, height=800.0,
            material_type=MaterialType.METAL, thickness=6.0
        )
        incompatible_thickness = Stock(
            id="S003", width=1000.0, height=800.0,
            material_type=MaterialType.GLASS, thickness=12.0
        )
        
        self.assertTrue(self.valid_order.can_be_fulfilled_by_stock(compatible_stock))
        self.assertFalse(self.valid_order.can_be_fulfilled_by_stock(incompatible_material))
        # Thickness difference > tolerance (default 1.0mm)
        self.assertFalse(self.valid_order.can_be_fulfilled_by_stock(incompatible_thickness))
        
    def test_fulfillment_tracking(self):
        """Test order fulfillment tracking"""
        self.assertEqual(self.valid_order.status, OrderStatus.PENDING)
        
        # Mark as fulfilled
        self.valid_order.mark_fulfilled()
        self.assertEqual(self.valid_order.status, OrderStatus.FULFILLED)
        
        # Test partial fulfillment
        partial_order = Order(id="O002", shape=Rectangle(100.0, 100.0), quantity=10)
        partial_order.mark_fulfilled(5)
        self.assertEqual(partial_order.status, OrderStatus.PARTIALLY_FULFILLED)
        
    def test_validation(self):
        """Test order validation"""
        issues = self.valid_order.validate()
        self.assertEqual(len(issues), 0)
        
        # Test overdue order
        overdue_order = Order(
            id="O002", shape=Rectangle(100.0, 100.0),
            due_date=datetime.now() - timedelta(days=1)
        )
        issues = overdue_order.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("overdue" in issue.lower() for issue in issues))
        
    def test_serialization(self):
        """Test to_dict serialization"""
        order_dict = self.valid_order.to_dict()
        self.assertEqual(order_dict["id"], "O001")
        self.assertEqual(order_dict["quantity"], 5)
        self.assertEqual(order_dict["priority"], "HIGH")
        self.assertEqual(order_dict["material_type"], "glass")


class TestPlacedShape(unittest.TestCase):
    """Tests for PlacedShape class"""
    
    def test_placed_shape_creation(self):
        """Test creating placed shape"""
        rect = Rectangle(100.0, 50.0, x=10.0, y=20.0)
        placed = PlacedShape(
            order_id="O001_1",
            shape=rect,
            stock_id="S001",
            rotation_applied=90.0
        )
        
        self.assertEqual(placed.order_id, "O001_1")
        self.assertEqual(placed.stock_id, "S001")
        self.assertEqual(placed.rotation_applied, 90.0)
        self.assertEqual(placed.position, (10.0, 20.0))
        
    def test_serialization(self):
        """Test placed shape serialization"""
        rect = Rectangle(100.0, 50.0, x=5.0, y=15.0)
        placed = PlacedShape(order_id="O001", shape=rect, stock_id="S001")
        
        placed_dict = placed.to_dict()
        self.assertEqual(placed_dict["order_id"], "O001")
        self.assertEqual(placed_dict["stock_id"], "S001")
        self.assertEqual(placed_dict["position"], (5.0, 15.0))
        self.assertEqual(placed_dict["area"], 5000.0)  # 100 * 50


class TestCuttingResult(unittest.TestCase):
    """Tests for CuttingResult class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.result = CuttingResult()
        self.result.total_stock_used = 3
        self.result.total_orders_fulfilled = 15
        self.result.efficiency_percentage = 78.5
        self.result.algorithm_used = "test_algorithm"
        self.result.computation_time = 1.234
        
        # Add some placed shapes
        rect1 = Rectangle(100.0, 50.0)
        rect2 = Rectangle(200.0, 100.0)
        self.result.placed_shapes = [
            PlacedShape("O001", rect1, "S001"),
            PlacedShape("O002", rect2, "S002")
        ]
        
    def test_basic_properties(self):
        """Test basic result properties"""
        self.assertEqual(self.result.total_stock_used, 3)
        self.assertEqual(self.result.total_orders_fulfilled, 15)
        self.assertAlmostEqual(self.result.efficiency_percentage, 78.5)
        
    def test_calculated_properties(self):
        """Test calculated properties"""
        self.assertAlmostEqual(self.result.waste_percentage, 21.5)  # 100 - 78.5
        
        expected_area = 100.0 * 50.0 + 200.0 * 100.0  # 5000 + 20000 = 25000
        self.assertEqual(self.result.total_area_used, expected_area)
        
    def test_fulfillment_rate(self):
        """Test fulfillment rate calculation"""
        # Add unfulfilled orders
        unfulfilled = Order("U001", Rectangle(50.0, 50.0))
        self.result.unfulfilled_orders = [unfulfilled]
        
        # 15 fulfilled, 1 unfulfilled = 15/16 * 100 = 93.75%
        expected_rate = (15 / 16) * 100
        self.assertAlmostEqual(self.result.fulfillment_rate, expected_rate)
        
    def test_shapes_by_stock(self):
        """Test filtering shapes by stock"""
        shapes_s001 = self.result.get_shapes_by_stock("S001")
        shapes_s002 = self.result.get_shapes_by_stock("S002")
        shapes_s999 = self.result.get_shapes_by_stock("S999")
        
        self.assertEqual(len(shapes_s001), 1)
        self.assertEqual(len(shapes_s002), 1)
        self.assertEqual(len(shapes_s999), 0)
        self.assertEqual(shapes_s001[0].order_id, "O001")
        
    def test_stock_efficiency(self):
        """Test stock-specific efficiency calculation"""
        stock_area = 10000.0
        efficiency = self.result.get_stock_efficiency("S001", stock_area)
        expected_efficiency = (5000.0 / stock_area) * 100  # 50%
        self.assertAlmostEqual(efficiency, expected_efficiency)
        
    def test_export_summary(self):
        """Test exporting result summary"""
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            self.result.export_summary(f.name)
            
            # Read back and verify
            with open(f.name, 'r') as read_f:
                data = json.load(read_f)
                
            self.assertEqual(data["algorithm_used"], "test_algorithm")
            self.assertEqual(data["stocks_used"], 3)
            self.assertEqual(data["orders_fulfilled"], 15)
            self.assertAlmostEqual(data["efficiency_percentage"], 78.5)


class TestOptimizationConfig(unittest.TestCase):
    """Tests for OptimizationConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = OptimizationConfig()
        self.assertTrue(config.allow_rotation)
        self.assertEqual(config.cutting_width, 3.0)
        self.assertEqual(config.algorithm_name, "bottom_left")
        self.assertEqual(config.order_sort_criteria, OrderSortCriteria.AREA_DESC)
        
    def test_custom_config(self):
        """Test custom configuration"""
        config = OptimizationConfig(
            allow_rotation=False,
            cutting_width=2.5,
            max_computation_time=120.0,
            prioritize_orders=False
        )
        self.assertFalse(config.allow_rotation)
        self.assertEqual(config.cutting_width, 2.5)
        self.assertEqual(config.max_computation_time, 120.0)
        self.assertFalse(config.prioritize_orders)
        
    def test_config_validation(self):
        """Test configuration validation"""
        valid_config = OptimizationConfig()
        issues = valid_config.validate()
        self.assertEqual(len(issues), 0)
        
        # Test invalid configurations
        invalid_config = OptimizationConfig(
            cutting_width=-1.0,
            max_computation_time=0.0,
            placement_precision=-0.1,
            waste_penalty_factor=15.0
        )
        issues = invalid_config.validate()
        self.assertGreater(len(issues), 0)
        
    def test_config_serialization(self):
        """Test configuration serialization"""
        config = OptimizationConfig(
            allow_rotation=False,
            cutting_width=2.0
        )
        config_dict = config.to_dict()
        self.assertFalse(config_dict["allow_rotation"])
        self.assertEqual(config_dict["cutting_width"], 2.0)


class TestSimpleClasses(unittest.TestCase):
    """Tests for simpler classes like Surface, Piece, CuttingPattern"""
    
    def test_surface_creation(self):
        """Test Surface creation and properties"""
        surface = Surface(1000.0, 500.0)
        self.assertEqual(surface.width, 1000.0)
        self.assertEqual(surface.height, 500.0)
        self.assertEqual(surface.area, 500000.0)
        
        with self.assertRaises(InvalidDimensionsError):
            Surface(-100.0, 500.0)
            
    def test_piece_creation(self):
        """Test Piece creation and properties"""
        piece = Piece(100.0, 50.0, piece_id=42)
        self.assertEqual(piece.width, 100.0)
        self.assertEqual(piece.height, 50.0)
        self.assertEqual(piece.piece_id, 42)
        self.assertEqual(piece.area, 5000.0)
        
        with self.assertRaises(InvalidDimensionsError):
            Piece(0.0, 50.0)
            
    def test_cutting_pattern(self):
        """Test CuttingPattern functionality"""
        piece1 = Piece(100.0, 50.0)
        piece2 = Piece(200.0, 100.0)
        pattern = CuttingPattern(surface_id=1, pieces=[piece1, piece2])
        
        self.assertEqual(pattern.surface_id, 1)
        self.assertEqual(len(pattern.pieces), 2)
        self.assertEqual(pattern.total_area, 25000.0)  # 5000 + 20000


if __name__ == '__main__':
    unittest.main() 