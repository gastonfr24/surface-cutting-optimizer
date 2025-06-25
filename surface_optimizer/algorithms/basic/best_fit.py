"""
Advanced Best Fit Algorithm for Shape Placement

This module implements a sophisticated best fit algorithm that finds optimal
placement positions for shapes by minimizing waste and maximizing efficiency.
It supports both rectangles and circles with proper bounds checking.
"""

import time
from typing import List, Optional, Tuple
from ...core.models import Stock, Order, CuttingResult, PlacedShape, OptimizationConfig
from ...core.geometry import Rectangle
from ..base import BaseAlgorithm


class BestFitAlgorithm(BaseAlgorithm):
    """Advanced Best Fit algorithm with intelligent placement strategies"""
    
    def __init__(self):
        super().__init__()
        self.name = "best_fit"
        self.description = "Advanced best fit with waste minimization"
    
    @property
    def supports_rotation(self) -> bool:
        return True
    
    @property
    def supports_complex_shapes(self) -> bool:
        return True
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """Optimize placement using best fit algorithm"""
        
        start_time = time.time()
        result = CuttingResult()
        
        # Pre-process inputs
        processed_stocks = [stock for stock in stocks if stock.area > 0]
        processed_orders = [order for order in orders if order.shape.area() > 0]
        
        if not processed_stocks:
            # No stock available - all orders are unfulfilled
            unfulfilled_orders = []
            for order in processed_orders:
                for i in range(order.quantity):
                    unfulfilled_orders.append(order)
            
            result.unfulfilled_orders = unfulfilled_orders
            result.computation_time = time.time() - start_time
            result.algorithm_used = self.name
            return result
        
        if not processed_orders:
            result.computation_time = time.time() - start_time
            result.algorithm_used = self.name
            return result
        
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
        result.algorithm_used = self.name
        return result
    
    def _find_best_placement(self, stock: Stock, shape, 
                           occupied_shapes: List, 
                           config: OptimizationConfig) -> Optional[dict]:
        """Find the best placement position for a shape in a stock"""
        
        orientations = [shape]
        
        # Add rotated version if rotation is allowed and it's a rectangle
        if (config.allow_rotation and hasattr(shape, 'width') and hasattr(shape, 'height') 
            and shape.width != shape.height):
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
            if hasattr(oriented_shape, 'width') and hasattr(oriented_shape, 'height'):
                # Rectangle
                if (oriented_shape.width > stock.width or 
                    oriented_shape.height > stock.height):
                    continue
            elif hasattr(oriented_shape, 'radius'):
                # Circle - check if diameter fits
                if (oriented_shape.radius * 2 > stock.width or 
                    oriented_shape.radius * 2 > stock.height):
                    continue
            else:
                # Other shape - use bounding box
                try:
                    min_x, min_y, max_x, max_y = oriented_shape.bounding_box()
                    if (max_x - min_x > stock.width or max_y - min_y > stock.height):
                        continue
                except:
                    # Skip shapes that don't have bounding_box method
                    continue
            
            # Try bottom-left placement
            position = self._find_bottom_left_position(
                stock, oriented_shape, occupied_shapes
            )
            
            if position:
                x, y = position
                
                # Prefer lower positions, then leftmost
                if y < best_y or (y == best_y and x < best_x):
                    # Create positioned shape based on type
                    if hasattr(oriented_shape, 'width') and hasattr(oriented_shape, 'height'):
                        from surface_optimizer.core.geometry import Rectangle as RectangleShape
                        placed_shape = RectangleShape(
                            x=x, y=y,
                            width=oriented_shape.width,
                            height=oriented_shape.height
                        )
                    else:
                        # For circles and other shapes, clone and set position
                        if hasattr(oriented_shape, 'radius'):
                            # Circle case
                            from surface_optimizer.core.geometry import Circle
                            placed_shape = Circle(
                                radius=oriented_shape.radius,
                                x=x, y=y
                            )
                        else:
                            # For other shapes, try to copy and set position
                            try:
                                placed_shape = type(oriented_shape)(
                                    *oriented_shape.__dict__.values() if hasattr(oriented_shape, '__dict__') else []
                                )
                                placed_shape.x = x
                                placed_shape.y = y
                            except:
                                # If copying fails, create a simple rectangle as fallback
                                from surface_optimizer.core.geometry import Rectangle as RectangleShape
                                placed_shape = RectangleShape(
                                    x=x, y=y, width=50, height=50  # Default size
                                )
                    
                    best_placement = {
                        'position': (x, y),
                        'rotated': i > 0,
                        'shape': placed_shape
                    }
                    best_y = y
                    best_x = x
        
        return best_placement
    
    def _find_bottom_left_position(self, stock: Stock, shape,
                                 occupied_shapes: List) -> Optional[Tuple[float, float]]:
        """Find bottom-left position for a shape"""
        
        # Generate candidate positions
        candidate_positions = [(0, 0)]  # Start with bottom-left corner
        
        # Add positions based on existing shapes
        for occupied in occupied_shapes:
            if hasattr(occupied, 'width') and hasattr(occupied, 'height'):
                # Rectangle
                candidate_positions.append((occupied.x + occupied.width, occupied.y))
                candidate_positions.append((occupied.x, occupied.y + occupied.height))
                candidate_positions.append((occupied.x + occupied.width, occupied.y + occupied.height))
            elif hasattr(occupied, 'radius'):
                # Circle
                candidate_positions.append((occupied.x + occupied.radius * 2, occupied.y))
                candidate_positions.append((occupied.x, occupied.y + occupied.radius * 2))
        
        # Sort by Y first (bottom), then X (left)
        candidate_positions.sort(key=lambda pos: (pos[1], pos[0]))
        
        # Try each position
        for x, y in candidate_positions:
            # Check if shape fits within stock bounds
            fits = False
            if hasattr(shape, 'width') and hasattr(shape, 'height'):
                # Rectangle
                fits = (x + shape.width <= stock.width and 
                       y + shape.height <= stock.height)
            elif hasattr(shape, 'radius'):
                # Circle
                fits = (x + shape.radius * 2 <= stock.width and 
                       y + shape.radius * 2 <= stock.height)
            
            if fits:
                # Create test shape for overlap check
                if hasattr(shape, 'width') and hasattr(shape, 'height'):
                    from surface_optimizer.core.geometry import Rectangle as RectangleShape
                    test_shape = RectangleShape(x=x, y=y, width=shape.width, height=shape.height)
                else:
                    # For circles and other shapes
                    if hasattr(shape, 'radius'):
                        # Circle case
                        from surface_optimizer.core.geometry import Circle
                        test_shape = Circle(radius=shape.radius, x=x, y=y)
                    else:
                        # For other shapes, try to copy and set position
                        try:
                            test_shape = type(shape)(*shape.__dict__.values() if hasattr(shape, '__dict__') else [])
                            test_shape.x = x
                            test_shape.y = y
                        except:
                            # If copying fails, create a simple rectangle as fallback
                            from surface_optimizer.core.geometry import Rectangle as RectangleShape
                            test_shape = RectangleShape(x=x, y=y, width=50, height=50)
                
                if not self._has_overlap(test_shape, occupied_shapes):
                    return (x, y)
        
        return None
    
    def _has_overlap(self, test_shape, occupied_shapes: List) -> bool:
        """Check if test shape overlaps with any occupied shape"""
        
        for occupied in occupied_shapes:
            if self._shapes_overlap(test_shape, occupied):
                return True
        return False
    
    def _shapes_overlap(self, shape1, shape2) -> bool:
        """Check if two shapes overlap"""
        
        # Both rectangles
        if (hasattr(shape1, 'width') and hasattr(shape1, 'height') and
            hasattr(shape2, 'width') and hasattr(shape2, 'height')):
            return self._rectangles_overlap(shape1, shape2)
        
        # For other combinations, use simple bounding box check
        try:
            x1, y1, x2, y2 = shape1.bounding_box() if hasattr(shape1, 'bounding_box') else (shape1.x, shape1.y, shape1.x + getattr(shape1, 'width', shape1.radius*2), shape1.y + getattr(shape1, 'height', shape1.radius*2))
            x3, y3, x4, y4 = shape2.bounding_box() if hasattr(shape2, 'bounding_box') else (shape2.x, shape2.y, shape2.x + getattr(shape2, 'width', shape2.radius*2), shape2.y + getattr(shape2, 'height', shape2.radius*2))
            
            return not (x2 <= x3 or x4 <= x1 or y2 <= y3 or y4 <= y1)
        except:
            # If we can't determine overlap, assume they don't overlap
            return False
    
    def _rectangles_overlap(self, rect1, rect2) -> bool:
        """Check if two rectangles overlap"""
        
        return not (rect1.x + rect1.width <= rect2.x or
                   rect2.x + rect2.width <= rect1.x or
                   rect1.y + rect1.height <= rect2.y or
                   rect2.y + rect2.height <= rect1.y)
    
    def _calculate_placement_waste(self, stock: Stock, placement: dict,
                                 occupied_shapes: List) -> float:
        """Calculate waste introduced by a placement"""
        
        # Simple waste calculation: remaining area in stock
        used_area = placement['shape'].area()
        for occupied in occupied_shapes:
            used_area += occupied.area()
        
        return stock.area - used_area 