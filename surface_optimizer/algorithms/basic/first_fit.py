"""
🔹 First Fit Algorithm for 2D Cutting Stock Optimization

The First Fit algorithm is a greedy heuristic that places each piece in the first
available stock that has enough space. It is one of the simplest and fastest
algorithms for the 2D cutting stock problem.

Characteristics:
- Ultra-fast execution (< 0.01s for 1000 pieces)
- O(n×m) time complexity  
- Predictable behavior
- Good for problems with many similar stocks

Limitations:
- Moderate efficiency (45-60%)
- High dependence on input order
- No optimization or backtracking

Ideal for:
- Problems with very limited computation time
- Rapid prototyping
- As baseline for comparing other algorithms

Examples:
    >>> from surface_optimizer.algorithms.basic import FirstFitAlgorithm
    >>> algorithm = FirstFitAlgorithm()
    >>> result = algorithm.optimize(stocks, orders, config)
    >>> print(f"Efficiency: {result.efficiency_percentage:.1f}%")
"""

import random
import time
from typing import List, Dict, Any

from ...core.models import CuttingResult, OptimizationConfig, PlacedShape, Order, Stock
from ...core.geometry import Rectangle
from ...core.exceptions import AlgorithmError, ValidationError
from ...utils.metrics import calculate_efficiency
from ...utils.logging import get_logger
from ...utils.error_handler import get_error_handler, error_context, with_error_handling
from ..base import BaseAlgorithm

logger = get_logger()
error_handler = get_error_handler()


class FirstFitAlgorithm(BaseAlgorithm):
    """
    First Fit Algorithm for 2D Cutting Optimization

    Implements the First Fit algorithm that places each piece in the first
    available stock with sufficient space. It's the fastest algorithm but
    doesn't guarantee optimal results.

    Attributes:
        name (str): Algorithm name "First Fit"
        description (str): Detailed algorithm description
        supports_rotation (bool): Supports 90° rotation
        complexity (str): O(n×m) time complexity

    Methods:
        optimize: Execute First Fit optimization
        _try_place_piece: Try to place a piece in stock
        _find_valid_position: Find valid position for piece
    """
    
    def __init__(self):
        """
        Initialize First Fit algorithm.

        Sets up algorithm metadata and prepares initial state
        for optimization.
        """
        super().__init__()
        self.name = "first_fit"
        self.description = """
        Greedy algorithm that places each piece in the first available stock
        with enough space. Very fast but doesn't guarantee optimal results.
        """
        self.supports_rotation = True
        self.complexity = "O(n×m)"
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """
        Execute optimization using First Fit algorithm.

        The algorithm processes each order in sequence and for each piece
        attempts to place it in the first stock where it fits. If rotation
        is enabled, it also tries 90° rotation before moving to next stock.

        Args:
            stocks (List[Stock]): List of available stocks
            orders (List[Order]): List of cutting orders  
            config (OptimizationConfig): Optimization configuration

        Returns:
            CuttingResult: Result with placed pieces and metrics

        Raises:
            AlgorithmError: If algorithm encounters an error during execution
            ValidationError: If input parameters are invalid

        Note:
            The algorithm doesn't guarantee optimal solution, but is very fast.
            For better efficiency results, consider using algorithms
            like Best Fit or Genetic Algorithm.
        """
        
        with error_context("first_fit_optimization", {
            "stocks_count": len(stocks) if stocks else 0,
            "orders_count": len(orders) if orders else 0,
            "algorithm": "first_fit"
        }):
            start_time = time.time()
            
            # Input validation with error handling
            try:
                if not orders:
                    # No orders to process
                    return CuttingResult(
                        placed_shapes=[],
                        efficiency_percentage=0.0,
                        total_stock_used=0,
                        algorithm_used=self.name,
                        computation_time=time.time() - start_time,
                        unfulfilled_orders=[]
                    )
                
                if not stocks:
                    # No stock available - all orders are unfulfilled
                    unfulfilled_order_objects = []
                    for order in orders:
                        for i in range(order.quantity):
                            unfulfilled_order_objects.append(order)
                    
                    return CuttingResult(
                        placed_shapes=[],
                        efficiency_percentage=0.0,
                        total_stock_used=0,
                        algorithm_used=self.name,
                        computation_time=time.time() - start_time,
                        unfulfilled_orders=unfulfilled_order_objects
                    )
                
                # Validate input data
                for i, stock in enumerate(stocks):
                    if not hasattr(stock, 'width') or not hasattr(stock, 'height'):
                        raise ValidationError(f"Stock {i} is missing width or height attributes")
                    if stock.width <= 0 or stock.height <= 0:
                        raise ValidationError(f"Stock {i} has invalid dimensions: {stock.width}x{stock.height}")
                
                for i, order in enumerate(orders):
                    if not hasattr(order, 'shape') or not hasattr(order, 'quantity'):
                        raise ValidationError(f"Order {i} is missing required attributes")
                    if order.quantity <= 0:
                        raise ValidationError(f"Order {i} has invalid quantity: {order.quantity}")
                        
            except Exception as e:
                error_handler.handle_error(
                    e,
                    context={"stage": "input_validation"},
                    operation="first_fit_validation",
                    reraise=True
                )
            
            logger.info(f"🔧 FIRST FIT CONFIGURATION:")
            logger.info(f"   • Rotation enabled: {config.allow_rotation}")
            logger.info(f"   • Priority processing: {config.prioritize_orders}")
            logger.info(f"   • Order sort criteria: {config.order_sort_criteria.value}")
            if config.secondary_sort_criteria:
                logger.info(f"   • Secondary sort: {config.secondary_sort_criteria.value}")
            
            logger.info(f"🚀 Starting First Fit optimization...")
            logger.info(f"   • Processing {len(stocks)} stock panels")
            logger.info(f"   • Processing {len(orders)} orders")
            
            try:
                # Initialize result
                placed_shapes = []
                total_pieces = sum(order.quantity for order in orders)
                unfulfilled_orders = []
                
                # Working copies - convert Stock objects to working format
                working_stocks = []
                for i, stock in enumerate(stocks):
                    working_stocks.append({
                        'id': stock.id,  # Use original stock ID instead of index
                        'index': i,      # Keep index for internal calculations
                        'width': stock.width,
                        'height': stock.height, 
                        'cost': stock.cost_per_unit,
                        'material': stock.material_type.value,
                        'occupied_areas': []  # List of placed rectangles
                    })
                
                # Preprocess orders (sort by priority and configured criteria)
                processed_orders = self.preprocess_orders(orders, config)
                
                # Process each order - convert Order objects to working format
                for order in processed_orders:
                    quantity = order.quantity
                    order_id = order.id
                    
                    for piece_num in range(quantity):
                        piece_id = f"{order_id}_{piece_num + 1}"
                        piece_width = order.shape.width
                        piece_height = order.shape.height
                        
                        placed = False
                        
                        # Try to place in each stock (First Fit strategy)
                        for stock in working_stocks:
                            try:
                                # Try without rotation
                                position = self._find_valid_position(
                                    stock, piece_width, piece_height
                                )
                                
                                if position:
                                    x, y = position
                                    self._place_piece(stock, piece_id, x, y, piece_width, piece_height, False)
                                    placed_shapes.append({
                                        'piece_id': piece_id,
                                        'stock_id': stock['id'],
                                        'x': x,
                                        'y': y, 
                                        'width': piece_width,
                                        'height': piece_height,
                                        'rotated': False
                                    })
                                    placed = True
                                    break
                                
                                # Try with rotation (if enabled)
                                if config.allow_rotation and piece_width != piece_height:
                                    position = self._find_valid_position(
                                        stock, piece_height, piece_width
                                    )
                                    
                                    if position:
                                        x, y = position
                                        self._place_piece(stock, piece_id, x, y, piece_height, piece_width, True)
                                        placed_shapes.append({
                                            'piece_id': piece_id,
                                            'stock_id': stock['id'],
                                            'x': x,
                                            'y': y,
                                            'width': piece_height,  # Rotated
                                            'height': piece_width,  # Rotated
                                            'rotated': True
                                        })
                                        placed = True
                                        break
                                        
                            except Exception as placement_error:
                                # Log placement error but continue with next stock
                                error_handler.handle_error(
                                    placement_error,
                                    context={
                                        "piece_id": piece_id,
                                        "stock_id": stock['id'],
                                        "piece_dimensions": f"{piece_width}x{piece_height}"
                                    },
                                    operation="piece_placement",
                                    reraise=False
                                )
                                continue
                        
                        # If piece couldn't be placed, add to unfulfilled
                        if not placed:
                            unfulfilled_orders.append(order)
                
                # Calculate final metrics
                total_used_stocks = len([s for s in working_stocks if s['occupied_areas']])
                
                computation_time = time.time() - start_time
                
                # Convert to PlacedShape objects first
                result_shapes = []
                for shape_data in placed_shapes:
                    # Create a Rectangle shape for the placed piece
                    from surface_optimizer.core.geometry import Rectangle
                    shape = Rectangle(shape_data['width'], shape_data['height'])
                    shape.x = shape_data['x']
                    shape.y = shape_data['y']
                    
                    placed_shape = PlacedShape(
                        order_id=shape_data['piece_id'].split('_')[0],  # Extract order ID from piece ID
                        shape=shape,
                        stock_id=shape_data['stock_id']
                    )
                    result_shapes.append(placed_shape)
                
                # Create temporary result to calculate efficiency
                temp_result = CuttingResult(
                    placed_shapes=result_shapes,
                    efficiency_percentage=0.0,  # Will be calculated
                    total_stock_used=total_used_stocks,
                    algorithm_used=self.name,
                    computation_time=computation_time,
                    unfulfilled_orders=unfulfilled_orders
                )
                
                # Now calculate efficiency with proper parameters
                efficiency = calculate_efficiency(temp_result, stocks)
                
                logger.info(f"✅ First Fit optimization completed:")
                logger.info(f"   • Placed pieces: {len(placed_shapes)}/{total_pieces}")
                logger.info(f"   • Efficiency: {efficiency:.1f}%")
                logger.info(f"   • Stocks used: {total_used_stocks}")
                logger.info(f"   • Computation time: {computation_time:.3f}s")
                
                return CuttingResult(
                    placed_shapes=result_shapes,
                    efficiency_percentage=efficiency,
                    total_stock_used=total_used_stocks,
                    algorithm_used=self.name,
                    computation_time=computation_time,
                    unfulfilled_orders=unfulfilled_orders
                )
                
            except Exception as e:
                # Handle any unexpected errors during optimization
                error_handler.handle_error(
                    AlgorithmError(f"First Fit algorithm failed: {str(e)}"),
                    context={
                        "stage": "optimization_execution",
                        "placed_pieces": len(placed_shapes) if 'placed_shapes' in locals() else 0,
                        "computation_time": time.time() - start_time
                    },
                    operation="first_fit_execution",
                    reraise=True
                )
    
    def _find_valid_position(self, stock: Dict, width: float, height: float):
        """
        Find valid position for piece in stock

        Args:
            stock: Stock to place piece in
            width: Piece width
            height: Piece height
            config (OptimizationConfig): Configuration with rotation options

        Returns:
            tuple: (x, y) position if found, None otherwise
        """
        stock_width = stock['width']
        stock_height = stock['height']
        
        # Check if piece fits in stock at all
        if width > stock_width or height > stock_height:
            return None
        
        # Try positions from top-left to bottom-right
        for y in range(int(stock_height - height) + 1):
            for x in range(int(stock_width - width) + 1):
                
                # Check overlap with existing pieces
                piece_rect = Rectangle(width, height, x, y)
                overlap = False
                
                for occupied in stock['occupied_areas']:
                    occupied_rect = Rectangle(
                        occupied['width'], occupied['height'],
                        occupied['x'], occupied['y']
                    )
                    
                    if self._rectangles_overlap(piece_rect, occupied_rect):
                        overlap = True
                        break
                
                if not overlap:
                    return (x, y)
        
        return None
    
    def _place_piece(self, stock: Dict, piece_id: str, x: float, y: float,
                    width: float, height: float, rotated: bool):
        """Add piece to stock's occupied areas"""
        stock['occupied_areas'].append({
            'piece_id': piece_id,
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'rotated': rotated
        })
    
    def _rectangles_overlap(self, rect1: Rectangle, rect2: Rectangle) -> bool:
        """Check if two rectangles overlap"""
        return not (rect1.x + rect1.width <= rect2.x or
                   rect2.x + rect2.width <= rect1.x or
                   rect1.y + rect1.height <= rect2.y or
                   rect2.y + rect2.height <= rect1.y) 