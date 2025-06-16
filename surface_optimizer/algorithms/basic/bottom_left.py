"""
Bottom-Left Fill Algorithm for Surface Cutting Optimizer
"""

import copy
from typing import List, Tuple, Optional
from ...core.models import Stock, Order, CuttingResult, PlacedShape, OptimizationConfig
from ...core.geometry import Rectangle, Circle
from ..base import BaseAlgorithm


class BottomLeftAlgorithm(BaseAlgorithm):
    """Bottom-Left Fill algorithm implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Bottom-Left Fill"
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """Execute Bottom-Left Fill optimization"""
        
        result = CuttingResult()
        result.algorithm_used = self.name
        
        # Preprocess
        processed_orders = self.preprocess_orders(orders, config)
        processed_stocks = self.preprocess_stocks(stocks, config)
        
        # Group orders by material type
        orders_by_material = {}
        for order in processed_orders:
            material = order.material_type
            if material not in orders_by_material:
                orders_by_material[material] = []
            orders_by_material[material].append(order)
        
        # Process each material type separately
        used_stocks = set()
        
        for material_type, material_orders in orders_by_material.items():
            # Get stocks for this material
            material_stocks = [s for s in processed_stocks if s.material_type == material_type]
            
            if not material_stocks:
                # No stocks for this material, add to unfulfilled
                result.unfulfilled_orders.extend(material_orders)
                continue
            
            # Optimize for this material
            material_result = self._optimize_material(material_stocks, material_orders, config)
            
            # Merge results
            result.placed_shapes.extend(material_result.placed_shapes)
            result.unfulfilled_orders.extend(material_result.unfulfilled_orders)
            used_stocks.update([ps.stock_id for ps in material_result.placed_shapes])
        
        # Calculate final metrics
        result.total_stock_used = len(used_stocks)
        
        # Count fulfilled orders (by original order ID, not expanded)
        fulfilled_order_ids = set()
        for placed_shape in result.placed_shapes:
            # Extract original order ID (remove the _1, _2 suffix)
            original_id = placed_shape.order_id.rsplit('_', 1)[0]
            fulfilled_order_ids.add(original_id)
        
        result.total_orders_fulfilled = len(fulfilled_order_ids)
        
        if result.placed_shapes:
            total_placed_area = sum(ps.shape.area() for ps in result.placed_shapes)
            total_stock_area = sum(stock.area for stock in stocks if stock.id in used_stocks)
            result.efficiency_percentage = (total_placed_area / total_stock_area) * 100 if total_stock_area > 0 else 0
        else:
            result.efficiency_percentage = 0
        
        return result
    
    def _optimize_material(self, stocks: List[Stock], orders: List[Order], 
                          config: OptimizationConfig) -> CuttingResult:
        """Optimize orders for a specific material type"""
        
        result = CuttingResult()
        remaining_orders = []
        
        # Expand orders by quantity
        expanded_orders = []
        for order in orders:
            for i in range(order.quantity):
                expanded_order = copy.deepcopy(order)
                expanded_order.id = f"{order.id}_{i+1}"
                expanded_order.quantity = 1
                expanded_orders.append(expanded_order)
        
        # Track occupied areas for each stock
        stock_occupied = {stock.id: [] for stock in stocks}
        
        # Try to place each order
        for order in expanded_orders:
            placed = False
            
            # Try each stock
            for stock in stocks:
                # Check material compatibility
                if stock.material_type != order.material_type:
                    continue
                
                # Try to place shape
                position = self._find_bottom_left_position(
                    stock, order.shape, stock_occupied[stock.id], config
                )
                
                if position:
                    # Place the shape
                    placed_shape = copy.deepcopy(order.shape)
                    placed_shape.x = position[0]
                    placed_shape.y = position[1]
                    
                    placed = PlacedShape(
                        order_id=order.id,
                        shape=placed_shape,
                        stock_id=stock.id
                    )
                    
                    result.placed_shapes.append(placed)
                    stock_occupied[stock.id].append(placed_shape)
                    placed = True
                    break
            
            if not placed:
                remaining_orders.append(order)
        
        result.unfulfilled_orders = remaining_orders
        return result
    
    def _find_bottom_left_position(self, stock: Stock, shape, 
                                  occupied_shapes: List, config: OptimizationConfig) -> Optional[Tuple[float, float]]:
        """Find bottom-left position for a shape in stock"""
        
        if not isinstance(shape, (Rectangle, Circle)):
            return None
        
        # Try different orientations if rotation is allowed
        orientations = [shape]
        
        if config.allow_rotation and isinstance(shape, Rectangle):
            rotated = copy.deepcopy(shape)
            rotated.width, rotated.height = rotated.height, rotated.width
            orientations.append(rotated)
        
        best_position = None
        best_y = float('inf')
        
        for oriented_shape in orientations:
            # Check if shape fits in stock at all
            if isinstance(oriented_shape, Rectangle):
                if (oriented_shape.width > stock.width or 
                    oriented_shape.height > stock.height):
                    continue
            elif isinstance(oriented_shape, Circle):
                if (oriented_shape.radius * 2 > stock.width or 
                    oriented_shape.radius * 2 > stock.height):
                    continue
            
            # Try positions from bottom-left
            for y in self._get_y_positions(stock, occupied_shapes, oriented_shape):
                for x in self._get_x_positions(stock, occupied_shapes, oriented_shape, y):
                    
                    # Check if position is valid
                    if self._is_valid_position(stock, oriented_shape, x, y, occupied_shapes, config):
                        if y < best_y or (y == best_y and x < best_position[0] if best_position else True):
                            best_position = (x, y)
                            best_y = y
        
        return best_position
    
    def _get_y_positions(self, stock: Stock, occupied_shapes: List, shape) -> List[float]:
        """Get candidate Y positions (bottom-up)"""
        positions = [0]  # Start from bottom
        
        for occupied in occupied_shapes:
            # Add position above each occupied shape
            if isinstance(occupied, Rectangle):
                positions.append(occupied.y + occupied.height)
            elif isinstance(occupied, Circle):
                positions.append(occupied.y + occupied.radius)
        
        # Filter valid positions
        if isinstance(shape, Rectangle):
            max_y = stock.height - shape.height
        elif isinstance(shape, Circle):
            max_y = stock.height - shape.radius * 2
        else:
            max_y = stock.height
        
        return [y for y in sorted(set(positions)) if y <= max_y]
    
    def _get_x_positions(self, stock: Stock, occupied_shapes: List, shape, y: float) -> List[float]:
        """Get candidate X positions for given Y"""
        positions = [0]  # Start from left
        
        for occupied in occupied_shapes:
            # Add position to the right of each occupied shape
            if isinstance(occupied, Rectangle):
                positions.append(occupied.x + occupied.width)
            elif isinstance(occupied, Circle):
                positions.append(occupied.x + occupied.radius)
        
        # Filter valid positions
        if isinstance(shape, Rectangle):
            max_x = stock.width - shape.width
        elif isinstance(shape, Circle):
            max_x = stock.width - shape.radius * 2
        else:
            max_x = stock.width
        
        return [x for x in sorted(set(positions)) if x <= max_x]
    
    def _is_valid_position(self, stock: Stock, shape, x: float, y: float, 
                          occupied_shapes: List, config: OptimizationConfig) -> bool:
        """Check if position is valid (no overlaps, within bounds)"""
        
        # Create temporary shape at position
        temp_shape = copy.deepcopy(shape)
        temp_shape.x = x
        temp_shape.y = y
        
        # Check bounds
        if isinstance(temp_shape, Rectangle):
            if (x + temp_shape.width > stock.width or 
                y + temp_shape.height > stock.height):
                return False
        elif isinstance(temp_shape, Circle):
            if (x + temp_shape.radius * 2 > stock.width or 
                y + temp_shape.radius * 2 > stock.height):
                return False
        
        # Check overlaps with occupied shapes
        for occupied in occupied_shapes:
            if temp_shape.overlaps(occupied):
                return False
        
        return True 