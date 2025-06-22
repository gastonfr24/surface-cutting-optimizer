"""
Validation utilities for Surface Cutting Optimizer
"""

from typing import List, Dict, Any
import warnings
from .models import Stock, Order, CuttingResult, OptimizationConfig, PlacedShape
from .exceptions import ValidationError, InvalidDimensionsError


def validate_stocks(stocks: List[Stock]) -> bool:
    """Validate a list of stocks"""
    if not stocks:
        raise ValidationError("At least one stock must be provided")
    
    # Check for duplicate IDs
    stock_ids = [stock.id for stock in stocks]
    if len(stock_ids) != len(set(stock_ids)):
        raise ValidationError("Duplicate stock IDs found")
    
    for stock in stocks:
        # Validate stock ID
        if not stock.id or stock.id.strip() == "":
            raise ValidationError("Stock ID cannot be empty or whitespace only")
            
        if stock.width <= 0 or stock.height <= 0:
            raise ValidationError(f"Stock {stock.id} has invalid dimensions: {stock.width}x{stock.height}")
        
        if stock.thickness <= 0:
            raise ValidationError(f"Stock {stock.id} has invalid thickness: {stock.thickness}")
    
    return True


def validate_orders(orders: List[Order]) -> bool:
    """Validate a list of orders"""
    if not orders:
        raise ValidationError("At least one order must be provided")
    
    # Check for duplicate IDs
    order_ids = [order.id for order in orders]
    if len(order_ids) != len(set(order_ids)):
        raise ValidationError("Duplicate order IDs found")
    
    for order in orders:
        # Validate order ID
        if not order.id or order.id.strip() == "":
            raise ValidationError("Order ID cannot be empty or whitespace only")
            
        if order.quantity <= 0:
            raise ValidationError(f"Order {order.id} has invalid quantity: {order.quantity}")
        
        if order.shape.area() <= 0:
            raise ValidationError(f"Order {order.id} has invalid shape area: {order.shape.area()}")
    
    return True


def validate_stock_order_compatibility(stocks: List[Stock], orders: List[Order]) -> bool:
    """Check if orders can potentially be fulfilled by stocks"""
    material_stocks = {}
    material_orders = {}
    
    # Group by material type
    for stock in stocks:
        material_type = stock.material_type
        if material_type not in material_stocks:
            material_stocks[material_type] = []
        material_stocks[material_type].append(stock)
    
    for order in orders:
        material_type = order.material_type
        if material_type not in material_orders:
            material_orders[material_type] = []
        material_orders[material_type].append(order)
    
    # Check each material type
    for material_type, orders_list in material_orders.items():
        if material_type not in material_stocks:
            raise ValidationError(f"No stocks available for material type: {material_type}")
        
        stocks_list = material_stocks[material_type]
        total_stock_area = sum(stock.area for stock in stocks_list)
        total_order_area = sum(order.total_area for order in orders_list)
        
        if total_order_area > total_stock_area:
            # Allow overflow for demo purposes - just log a warning
            print(f"⚠️  WARNING: Overflow detected - {material_type.value} demand ({total_order_area:,}) > stock ({total_stock_area:,})")
            print(f"   Some orders will be discarded during optimization.")
    
    return True


def validate_configuration(config: OptimizationConfig) -> bool:
    """Validate optimization configuration"""
    issues = config.validate()
    if issues:
        raise ValidationError(f"Configuration validation failed: {'; '.join(issues)}")
    return True


def validate_cutting_result(result: CuttingResult, stocks: List[Stock], orders: List[Order]) -> bool:
    """Validate cutting result consistency"""
    if result.efficiency_percentage < 0 or result.efficiency_percentage > 100:
        raise ValidationError(f"Invalid efficiency percentage: {result.efficiency_percentage}%")
    
    if result.total_stock_used < 0:
        raise ValidationError("Invalid stock usage: cannot be negative")
    
    if result.total_stock_used > len(stocks):
        raise ValidationError(f"Invalid stock usage: {result.total_stock_used} > {len(stocks)} available")
    
    if result.total_orders_fulfilled < 0:
        raise ValidationError("Invalid orders fulfilled: cannot be negative")
    
    if result.total_orders_fulfilled > len(orders):
        raise ValidationError(f"Invalid orders fulfilled: {result.total_orders_fulfilled} > {len(orders)} available")
    
    if result.computation_time < 0:
        raise ValidationError("Invalid computation time: cannot be negative")
    
    # Validate placed shapes reference existing stocks and orders
    stock_ids = {stock.id for stock in stocks}
    order_ids = {order.id for order in orders}
    
    for placed_shape in result.placed_shapes:
        if placed_shape.stock_id not in stock_ids:
            raise ValidationError(f"Placed shape references unknown stock: {placed_shape.stock_id}")
        if placed_shape.order_id not in order_ids:
            raise ValidationError(f"Placed shape references unknown order: {placed_shape.order_id}")
    
    return True


def validate_placement_bounds(placed_shape: PlacedShape, stock: Stock) -> bool:
    """Validate that placed shape fits within stock bounds"""
    shape = placed_shape.shape
    
    # Check negative positions
    if shape.x < 0 or shape.y < 0:
        raise ValidationError(f"Shape placed at negative position: ({shape.x}, {shape.y})")
    
    # Check bounds based on shape type
    if hasattr(shape, 'width') and hasattr(shape, 'height'):
        # Rectangle
        if shape.x + shape.width > stock.width:
            raise ValidationError(f"Shape exceeds stock width: {shape.x + shape.width} > {stock.width}")
        if shape.y + shape.height > stock.height:
            raise ValidationError(f"Shape exceeds stock height: {shape.y + shape.height} > {stock.height}")
    elif hasattr(shape, 'radius'):
        # Circle
        if shape.x + shape.radius > stock.width:
            raise ValidationError(f"Circle exceeds stock width: {shape.x + shape.radius} > {stock.width}")
        if shape.y + shape.radius > stock.height:
            raise ValidationError(f"Circle exceeds stock height: {shape.y + shape.radius} > {stock.height}")
    else:
        # Polygon - check bounding box
        min_x, min_y, max_x, max_y = shape.bounding_box()
        if max_x > stock.width:
            raise ValidationError(f"Polygon exceeds stock width: {max_x} > {stock.width}")
        if max_y > stock.height:
            raise ValidationError(f"Polygon exceeds stock height: {max_y} > {stock.height}")
    
    return True


def validate_material_compatibility(stock: Stock, order: Order) -> bool:
    """Check if stock and order materials are compatible"""
    if stock.material_type != order.material_type:
        return False
    
    # Check thickness requirements
    if 'min_thickness' in order.special_requirements:
        min_thickness = order.special_requirements['min_thickness']
        if stock.thickness < min_thickness:
            return False
    
    return True


def validate_order_quantities(orders: List[Order]) -> bool:
    """Validate order quantities"""
    for order in orders:
        if order.quantity <= 0:
            raise InvalidDimensionsError(f"Order {order.id} has invalid quantity: {order.quantity}")
    return True


def validate_stock_dimensions(width: float, height: float, thickness: float) -> bool:
    """Validate stock dimensions"""
    if width <= 0 or height <= 0 or thickness <= 0:
        raise InvalidDimensionsError(f"Stock dimensions must be positive: {width}x{height}x{thickness}")
    
    # Warning for very small dimensions
    if width < 10 or height < 10 or thickness < 0.5:
        warnings.warn("Very small stock dimensions detected", UserWarning)
    
    # Warning for very large dimensions
    if width > 50000 or height > 50000 or thickness > 200:
        warnings.warn("Very large stock dimensions detected", UserWarning)
    
    return True 