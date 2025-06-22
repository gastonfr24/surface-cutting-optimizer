"""
Best Fit Algorithm - Advanced implementation with intelligent placement
"""

import time
import copy
from typing import List, Tuple, Optional
from ...core.models import Stock, Order, CuttingResult, OptimizationConfig, PlacedShape
from ...core.geometry import Rectangle
from ..base import BaseAlgorithm


class BestFitAlgorithm(BaseAlgorithm):
    """Advanced Best Fit algorithm with intelligent placement"""
    
    def __init__(self):
        super().__init__()
        self.name = "best_fit"
        self.description = """
        Advanced Best Fit algorithm that:
        - Chooses stock with smallest waste for each piece
        - Uses intelligent bottom-left placement
        - Handles rotations optimally
        - Minimizes material waste through smart positioning
        """
        self.supports_rotation = True
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """Advanced Best Fit optimization with intelligent placement"""
        
        start_time = time.time()
        
        result = CuttingResult()
        result.algorithm_used = self.name
        
        if not stocks or not orders:
            result.computation_time = time.time() - start_time
            return result
        
        # Preprocess orders and stocks
        processed_orders = self.preprocess_orders(orders, config)
        processed_stocks = self.preprocess_stocks(stocks, config)
        
        # Track occupied areas for each stock
        stock_occupied = {stock.id: [] for stock in processed_stocks}
        placed_shapes = []
        unfulfilled_orders = []
        
        # Expand orders by quantity and sort by area (largest first)
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
        
        # Sort by area (largest first) for better packing efficiency
        expanded_orders.sort(key=lambda o: o.shape.area(), reverse=True)
        
        # Place each piece using advanced best fit strategy
        for order in expanded_orders:
            best_placement = None
            best_waste = float('inf')
            
            # Try each compatible stock
            for stock in processed_stocks:
                # Check material compatibility
                if stock.material_type != order.material_type:
                    continue
                
                # Find best placement in this stock
                placement = self._find_best_placement(
                    stock, order.shape, stock_occupied[stock.id], config
                )
                
                if placement:
                    # Calculate waste for this placement
                    waste = self._calculate_placement_waste(
                        stock, placement, stock_occupied[stock.id]
                    )
                    
                    if waste < best_waste:
                        best_waste = waste
                        best_placement = {
                            'stock': stock,
                            'position': placement['position'],
                            'rotated': placement['rotated'],
                            'shape': placement['shape']
                        }
            
            # Place piece in best location if found
            if best_placement:
                # Create properly positioned shape
                placed_shape = PlacedShape(
                    order_id=order.id,
                    shape=best_placement['shape'],
                    stock_id=best_placement['stock'].id
                )
                
                placed_shapes.append(placed_shape)
                stock_occupied[best_placement['stock'].id].append(best_placement['shape'])
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
    
    def _find_best_placement(self, stock: Stock, shape: Rectangle, 
                           occupied_shapes: List[Rectangle], 
                           config: OptimizationConfig) -> Optional[dict]:
        """Find the best placement position for a shape in a stock"""
        
        orientations = [shape]
        
        # Add rotated version if rotation is allowed
        if config.allow_rotation and shape.width != shape.height:
            rotated = Rectangle(
                x=shape.x, y=shape.y,
                width=shape.height, height=shape.width
            )
            orientations.append(rotated)
        
        best_placement = None
        best_y = float('inf')
        best_x = float('inf')
        
        for i, oriented_shape in enumerate(orientations):
            # Check if shape fits in stock at all
            if (oriented_shape.width > stock.width or 
                oriented_shape.height > stock.height):
                continue
            
            # Try bottom-left placement
            position = self._find_bottom_left_position(
                stock, oriented_shape, occupied_shapes
            )
            
            if position:
                x, y = position
                
                # Prefer lower positions, then leftmost
                if y < best_y or (y == best_y and x < best_x):
                    placed_shape = Rectangle(
                        x=x, y=y,
                        width=oriented_shape.width,
                        height=oriented_shape.height
                    )
                    
                    best_placement = {
                        'position': (x, y),
                        'rotated': i > 0,
                        'shape': placed_shape
                    }
                    best_y = y
                    best_x = x
        
        return best_placement
    
    def _find_bottom_left_position(self, stock: Stock, shape: Rectangle,
                                 occupied_shapes: List[Rectangle]) -> Optional[Tuple[float, float]]:
        """Find bottom-left position for a shape"""
        
        # Generate candidate positions
        candidate_positions = [(0, 0)]  # Start with bottom-left corner
        
        # Add positions based on existing shapes
        for occupied in occupied_shapes:
            # Right edge of existing shape
            candidate_positions.append((occupied.x + occupied.width, occupied.y))
            # Top edge of existing shape
            candidate_positions.append((occupied.x, occupied.y + occupied.height))
            # Top-right corner
            candidate_positions.append((occupied.x + occupied.width, occupied.y + occupied.height))
        
        # Sort by Y first (bottom), then X (left)
        candidate_positions.sort(key=lambda pos: (pos[1], pos[0]))
        
        # Try each position
        for x, y in candidate_positions:
            # Check if shape fits within stock bounds
            if (x + shape.width <= stock.width and 
                y + shape.height <= stock.height):
                
                # Check for overlaps with existing shapes
                test_shape = Rectangle(x=x, y=y, width=shape.width, height=shape.height)
                
                if not self._has_overlap(test_shape, occupied_shapes):
                    return (x, y)
        
        return None
    
    def _has_overlap(self, test_shape: Rectangle, occupied_shapes: List[Rectangle]) -> bool:
        """Check if test shape overlaps with any occupied shape"""
        
        for occupied in occupied_shapes:
            if self._rectangles_overlap(test_shape, occupied):
                return True
        return False
    
    def _rectangles_overlap(self, rect1: Rectangle, rect2: Rectangle) -> bool:
        """Check if two rectangles overlap"""
        
        return not (rect1.x + rect1.width <= rect2.x or
                   rect2.x + rect2.width <= rect1.x or
                   rect1.y + rect1.height <= rect2.y or
                   rect2.y + rect2.height <= rect1.y)
    
    def _calculate_placement_waste(self, stock: Stock, placement: dict,
                                 occupied_shapes: List[Rectangle]) -> float:
        """Calculate waste introduced by a placement"""
        
        # Simple waste calculation: remaining area in stock
        used_area = placement['shape'].area()
        for occupied in occupied_shapes:
            used_area += occupied.area()
        
        return stock.area - used_area 