"""
Validation utilities for Surface Cutting Optimizer
"""

from typing import List
from .models import Stock, Order
from .exceptions import ValidationError


def validate_stocks(stocks: List[Stock]) -> bool:
    """Validate a list of stocks"""
    if not stocks:
        raise ValidationError("At least one stock must be provided")
    
    for stock in stocks:
        if stock.width <= 0 or stock.height <= 0:
            raise ValidationError(f"Stock {stock.id} has invalid dimensions: {stock.width}x{stock.height}")
        
        if stock.thickness <= 0:
            raise ValidationError(f"Stock {stock.id} has invalid thickness: {stock.thickness}")
    
    return True


def validate_orders(orders: List[Order]) -> bool:
    """Validate a list of orders"""
    if not orders:
        raise ValidationError("At least one order must be provided")
    
    for order in orders:
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
            raise ValidationError(
                f"Insufficient {material_type.value} stock area: {total_stock_area} < {total_order_area}"
            )
    
    return True 