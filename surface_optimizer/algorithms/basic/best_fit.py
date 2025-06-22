"""
Best Fit Algorithm - Basic implementation using First Fit with best stock selection
"""

import time
from typing import List
from ...core.models import Stock, Order, CuttingResult, OptimizationConfig, PlacedShape
from ...core.geometry import Rectangle
from ..base import BaseAlgorithm


class BestFitAlgorithm(BaseAlgorithm):
    """Best Fit algorithm - chooses stock with smallest remaining area that fits the piece"""
    
    def __init__(self):
        super().__init__()
        self.name = "best_fit"
        self.description = """
        Best Fit algorithm that places each piece in the stock with the
        smallest remaining area that can accommodate it. Minimizes waste.
        """
        self.supports_rotation = True
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """Best Fit optimization - basic implementation"""
        
        start_time = time.time()
        
        result = CuttingResult()
        result.algorithm_used = self.name
        
        if not stocks or not orders:
            result.computation_time = time.time() - start_time
            return result
        
        # Preprocess orders and stocks
        processed_orders = self.preprocess_orders(orders, config)
        processed_stocks = self.preprocess_stocks(stocks, config)
        
        # Track used area for each stock
        stock_used_area = {stock.id: 0.0 for stock in processed_stocks}
        placed_shapes = []
        unfulfilled_orders = []
        
        # Expand orders by quantity
        expanded_orders = []
        for order in processed_orders:
            for i in range(order.quantity):
                expanded_order = type(order)(
                    id=f"{order.id}_{i+1}",
                    shape=order.shape,
                    quantity=1,
                    material_type=order.material_type,
                    priority=order.priority
                )
                expanded_orders.append(expanded_order)
        
        # Place each piece using best fit strategy
        for order in expanded_orders:
            best_stock = None
            best_remaining_area = float('inf')
            
            # Find the stock with smallest remaining area that fits this piece
            for stock in processed_stocks:
                # Check material compatibility
                if stock.material_type != order.material_type:
                    continue
                
                # Check if piece fits
                if isinstance(order.shape, Rectangle):
                    piece_area = order.shape.area()
                    
                    # Try without rotation
                    if (order.shape.width <= stock.width and 
                        order.shape.height <= stock.height):
                        
                        remaining_area = stock.area - stock_used_area[stock.id] - piece_area
                        if remaining_area >= 0 and remaining_area < best_remaining_area:
                            best_stock = stock
                            best_remaining_area = remaining_area
                    
                    # Try with rotation if enabled
                    if (config.allow_rotation and 
                        order.shape.width != order.shape.height and
                        order.shape.height <= stock.width and 
                        order.shape.width <= stock.height):
                        
                        remaining_area = stock.area - stock_used_area[stock.id] - piece_area
                        if remaining_area >= 0 and remaining_area < best_remaining_area:
                            best_stock = stock
                            best_remaining_area = remaining_area
            
            # Place piece in best stock if found
            if best_stock:
                # Create placed shape (simplified placement at origin)
                placed_shape = PlacedShape(
                    order_id=order.id,
                    shape=Rectangle(
                        x=0.0, y=0.0,  # Simplified placement
                        width=order.shape.width, 
                        height=order.shape.height
                    ),
                    stock_id=best_stock.id
                )
                
                placed_shapes.append(placed_shape)
                stock_used_area[best_stock.id] += order.shape.area()
            else:
                unfulfilled_orders.append(order)
        
        # Calculate metrics
        result.placed_shapes = placed_shapes
        result.unfulfilled_orders = unfulfilled_orders
        result.total_stock_used = len(set(ps.stock_id for ps in placed_shapes))
        
        # Count fulfilled orders (by original order ID)
        fulfilled_order_ids = set()
        for placed_shape in placed_shapes:
            original_id = placed_shape.order_id.rsplit('_', 1)[0]
            fulfilled_order_ids.add(original_id)
        result.total_orders_fulfilled = len(fulfilled_order_ids)
        
        # Calculate efficiency
        if placed_shapes:
            total_placed_area = sum(ps.shape.area() for ps in placed_shapes)
            used_stock_ids = set(ps.stock_id for ps in placed_shapes)
            total_stock_area = sum(stock.area for stock in stocks if stock.id in used_stock_ids)
            result.efficiency_percentage = (total_placed_area / total_stock_area) * 100 if total_stock_area > 0 else 0
        else:
            result.efficiency_percentage = 0.0
        
        result.computation_time = time.time() - start_time
        return result 