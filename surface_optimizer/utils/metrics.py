"""
Metrics calculation utilities for Surface Cutting Optimizer
"""

from typing import List, Dict, Any
from ..core.models import Stock, Order, CuttingResult


def calculate_efficiency(result: CuttingResult, stocks: List[Stock]) -> float:
    """Calculate material utilization efficiency"""
    if not result.placed_shapes:
        return 0.0
    
    used_stock_ids = set(ps.stock_id for ps in result.placed_shapes)
    total_placed_area = sum(ps.shape.area() for ps in result.placed_shapes)
    total_stock_area = sum(stock.area for stock in stocks if stock.id in used_stock_ids)
    
    return (total_placed_area / total_stock_area) * 100 if total_stock_area > 0 else 0.0


def calculate_waste(result: CuttingResult, stocks: List[Stock]) -> float:
    """Calculate total waste area"""
    if not result.placed_shapes:
        return 0.0
    
    used_stock_ids = set(ps.stock_id for ps in result.placed_shapes)
    total_placed_area = sum(ps.shape.area() for ps in result.placed_shapes)
    total_stock_area = sum(stock.area for stock in stocks if stock.id in used_stock_ids)
    
    return total_stock_area - total_placed_area


def generate_metrics_report(result: CuttingResult, stocks: List[Stock], orders: List[Order]) -> Dict[str, Any]:
    """Generate comprehensive metrics report"""
    
    used_stock_ids = set(ps.stock_id for ps in result.placed_shapes)
    
    # Basic metrics
    total_placed_area = sum(ps.shape.area() for ps in result.placed_shapes)
    total_stock_area = sum(stock.area for stock in stocks if stock.id in used_stock_ids)
    total_order_area = sum(order.total_area for order in orders)
    
    # Efficiency calculations
    material_efficiency = calculate_efficiency(result, stocks)
    waste_area = calculate_waste(result, stocks)
    
    # Order fulfillment metrics
    total_orders = len(orders)
    fulfilled_orders = result.total_orders_fulfilled
    fulfillment_rate = (fulfilled_orders / total_orders) * 100 if total_orders > 0 else 0.0
    
    # Cost calculations (if stock costs available)
    total_cost = sum(stock.cost_per_unit for stock in stocks if stock.id in used_stock_ids)
    cost_per_area = total_cost / total_placed_area if total_placed_area > 0 else 0.0
    
    return {
        "material_efficiency_percentage": material_efficiency,
        "waste_area": waste_area,
        "waste_percentage": (waste_area / total_stock_area) * 100 if total_stock_area > 0 else 0.0,
        "order_fulfillment_rate": fulfillment_rate,
        "total_placed_area": total_placed_area,
        "total_stock_area": total_stock_area,
        "total_order_area": total_order_area,
        "stocks_used": result.total_stock_used,
        "orders_fulfilled": fulfilled_orders,
        "orders_unfulfilled": len(result.unfulfilled_orders),
        "total_cost": total_cost,
        "cost_per_area": cost_per_area,
        "algorithm_used": result.algorithm_used,
        "computation_time": result.computation_time
    } 