"""
Simulated Annealing Algorithm for Surface Cutting Optimization
Advanced optimization using simulated annealing metaheuristic
"""

import random
import copy
import math
from typing import List, Tuple, Optional, Dict, Any

from ...core.models import Stock, Order, CuttingResult, OptimizationConfig, PlacedShape
from ...core.geometry import Rectangle, Circle, Shape
from ..base import BaseAlgorithm
from ...utils.logging import get_logger


class SimulatedAnnealingAlgorithm(BaseAlgorithm):
    """Simulated Annealing with auto-scaling for cutting optimization"""
    
    def __init__(self, 
                 initial_temperature: Optional[float] = None,
                 cooling_rate: float = 0.95,
                 min_temperature: Optional[float] = None,
                 max_iterations: Optional[int] = None,
                 iterations_per_temp: Optional[int] = None,
                 auto_scale: bool = True):
        super().__init__()
        self.name = "Simulated Annealing"
        self.base_initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.base_min_temperature = min_temperature
        self.base_max_iterations = max_iterations
        self.base_iterations_per_temp = iterations_per_temp
        self.auto_scale = auto_scale
        self.logger = get_logger()
        
        # Tracking
        self.temperature_history: List[float] = []
        self.cost_history: List[float] = []
        self.acceptance_history: List[float] = []
        
        # Performance optimizations
        self.early_stop_patience = 20
        self.convergence_threshold = 1e-6
    
    def _auto_scale_parameters(self, num_stocks: int, num_orders: int) -> Tuple[float, float, int, int]:
        """Auto-scale parameters based on problem size"""
        
        if not self.auto_scale:
            return (
                self.base_initial_temperature or 1000.0,
                self.base_min_temperature or 0.1,
                self.base_max_iterations or 1000,
                self.base_iterations_per_temp or 50
            )
        
        problem_size = num_stocks * num_orders
        
        # Scale parameters based on problem complexity
        if problem_size <= 50:  # Small problems
            initial_temp = 100.0
            min_temp = 0.01
            max_iter = max(100, problem_size * 10)
            iter_per_temp = max(10, problem_size // 2)
        elif problem_size <= 200:  # Medium problems
            initial_temp = 500.0
            min_temp = 0.05
            max_iter = max(300, problem_size * 5)
            iter_per_temp = max(20, problem_size // 5)
        else:  # Large problems
            initial_temp = 1000.0
            min_temp = 0.1
            max_iter = max(500, int(math.sqrt(problem_size) * 50))
            iter_per_temp = max(30, int(math.sqrt(problem_size) * 5))
        
        self.logger.logger.debug(f"Auto-scaled SA: temp={initial_temp}, max_iter={max_iter}")
        return initial_temp, min_temp, max_iter, iter_per_temp
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """Optimize using simulated annealing with auto-scaling"""
        
        # Auto-scale parameters
        (self.initial_temperature, self.min_temperature, 
         self.max_iterations, self.iterations_per_temp) = self._auto_scale_parameters(
            len(stocks), len(orders))
        
        self.logger.start_operation("simulated_annealing", {
            "stocks": len(stocks),
            "orders": len(orders),
            "initial_temp": self.initial_temperature,
            "cooling_rate": self.cooling_rate,
            "auto_scaled": self.auto_scale
        })
        
        try:
            # Expand orders
            expanded_orders = self._expand_orders(orders)
            
            # Generate initial solution
            current_solution = self._generate_initial_solution(stocks, expanded_orders, config)
            current_cost = self._evaluate_solution(current_solution, stocks, expanded_orders, config)
            
            # Best solution tracking
            best_solution = copy.deepcopy(current_solution)
            best_cost = current_cost
            
            # Annealing process
            temperature = self.initial_temperature
            iteration = 0
            
            while temperature > self.min_temperature and iteration < self.max_iterations:
                
                accepted_moves = 0
                
                for _ in range(self.iterations_per_temp):
                    iteration += 1
                    
                    # Generate neighbor solution
                    neighbor_solution = self._generate_neighbor(current_solution, stocks, 
                                                              expanded_orders, config)
                    neighbor_cost = self._evaluate_solution(neighbor_solution, stocks, 
                                                           expanded_orders, config)
                    
                    # Accept or reject
                    if self._accept_solution(current_cost, neighbor_cost, temperature):
                        current_solution = neighbor_solution
                        current_cost = neighbor_cost
                        accepted_moves += 1
                        
                        # Update best solution
                        if neighbor_cost < best_cost:
                            best_solution = copy.deepcopy(neighbor_solution)
                            best_cost = neighbor_cost
                
                # Track statistics
                acceptance_rate = accepted_moves / self.iterations_per_temp
                self.temperature_history.append(temperature)
                self.cost_history.append(current_cost)
                self.acceptance_history.append(acceptance_rate)
                
                # Cool down
                temperature *= self.cooling_rate
                
                if iteration % 100 == 0:
                    self.logger.logger.debug(f"Iteration {iteration}: T={temperature:.2f}, "
                                           f"Cost={current_cost:.3f}, Accept={acceptance_rate:.3f}")
            
            # Convert best solution to result
            result = self._solution_to_result(best_solution, stocks, expanded_orders, orders)
            
            # Set metadata
            result.metadata = {
                "algorithm": "simulated_annealing",
                "iterations_run": iteration,
                "final_temperature": temperature,
                "best_cost": best_cost,
                "cooling_schedule": {
                    "initial_temperature": self.initial_temperature,
                    "cooling_rate": self.cooling_rate,
                    "final_temperature": temperature
                },
                "annealing_stats": {
                    "temperature_history": self.temperature_history,
                    "cost_history": self.cost_history,
                    "acceptance_history": self.acceptance_history
                }
            }
            
            self.logger.end_operation("simulated_annealing", success=True, result={
                "efficiency": result.efficiency_percentage,
                "iterations": iteration,
                "final_temperature": temperature
            })
            
            return result
            
        except Exception as e:
            self.logger.end_operation("simulated_annealing", success=False, 
                                    result={"error": str(e)})
            raise
    
    def _expand_orders(self, orders: List[Order]) -> List[Order]:
        """Expand orders by quantity"""
        expanded = []
        for order in orders:
            for i in range(order.quantity):
                expanded_order = copy.deepcopy(order)
                expanded_order.id = f"{order.id}_{i+1}"
                expanded_order.quantity = 1
                expanded.append(expanded_order)
        return expanded
    
    def _generate_initial_solution(self, stocks: List[Stock], orders: List[Order], 
                                 config: OptimizationConfig) -> Dict[str, Any]:
        """Generate initial solution using greedy approach"""
        
        solution = {
            "placements": [],  # List of (order_idx, stock_idx, x, y, rotation)
            "stock_usage": {i: [] for i in range(len(stocks))},
            "unplaced_orders": list(range(len(orders)))
        }
        
        # Sort orders by area (largest first)
        order_indices = sorted(range(len(orders)), 
                             key=lambda i: orders[i].shape.area(), reverse=True)
        
        for order_idx in order_indices:
            order = orders[order_idx]
            placed = False
            
            # Try each stock
            for stock_idx, stock in enumerate(stocks):
                if order.material_type != stock.material_type:
                    continue
                
                # Find position using bottom-left heuristic
                position = self._find_position(order, stock, solution["stock_usage"][stock_idx], config)
                
                if position:
                    x, y, rotation = position
                    placement = (order_idx, stock_idx, x, y, rotation)
                    
                    solution["placements"].append(placement)
                    
                    # Update stock usage
                    shape = copy.deepcopy(order.shape)
                    shape.x = x
                    shape.y = y
                    shape.rotation = rotation
                    solution["stock_usage"][stock_idx].append(shape)
                    
                    solution["unplaced_orders"].remove(order_idx)
                    placed = True
                    break
        
        return solution
    
    def _find_position(self, order: Order, stock: Stock, occupied_shapes: List[Shape], 
                      config: OptimizationConfig) -> Optional[Tuple[float, float, float]]:
        """Find position for order in stock"""
        
        # Try different rotations
        rotations = [0]
        if config.allow_rotation and isinstance(order.shape, Rectangle):
            rotations = [0, 90]
        
        for rotation in rotations:
            shape = copy.deepcopy(order.shape)
            shape.rotation = rotation
            
            # Effective dimensions after rotation
            if isinstance(shape, Rectangle) and rotation == 90:
                width, height = shape.height, shape.width
            else:
                width = getattr(shape, 'width', 2 * getattr(shape, 'radius', 0))
                height = getattr(shape, 'height', 2 * getattr(shape, 'radius', 0))
            
            # Check if it fits at all
            if width > stock.width or height > stock.height:
                continue
            
            # Try positions
            for y in range(0, int(stock.height - height) + 1, 10):
                for x in range(0, int(stock.width - width) + 1, 10):
                    shape.x = x
                    shape.y = y
                    
                    # Check overlaps
                    valid = True
                    for occupied in occupied_shapes:
                        if shape.overlaps(occupied):
                            valid = False
                            break
                    
                    if valid:
                        return (x, y, rotation)
        
        return None
    
    def _generate_neighbor(self, solution: Dict[str, Any], stocks: List[Stock], 
                          orders: List[Order], config: OptimizationConfig) -> Dict[str, Any]:
        """Generate neighbor solution"""
        
        neighbor = copy.deepcopy(solution)
        
        if not neighbor["placements"]:
            return neighbor
        
        # Choose random move type
        move_type = random.choice(["relocate", "swap", "rotate", "reorder"])
        
        if move_type == "relocate" and neighbor["placements"]:
            self._relocate_order(neighbor, stocks, orders, config)
        elif move_type == "swap" and len(neighbor["placements"]) >= 2:
            self._swap_orders(neighbor, stocks, orders, config)
        elif move_type == "rotate" and config.allow_rotation:
            self._rotate_order(neighbor, stocks, orders, config)
        elif move_type == "reorder":
            self._reorder_placement(neighbor, stocks, orders, config)
        
        return neighbor
    
    def _relocate_order(self, solution: Dict[str, Any], stocks: List[Stock], 
                       orders: List[Order], config: OptimizationConfig):
        """Relocate a random order"""
        
        if not solution["placements"]:
            return
        
        # Choose random placement
        placement_idx = random.randint(0, len(solution["placements"]) - 1)
        order_idx, old_stock_idx, old_x, old_y, old_rotation = solution["placements"][placement_idx]
        
        # Remove from current position
        order = orders[order_idx]
        old_shape = copy.deepcopy(order.shape)
        old_shape.x = old_x
        old_shape.y = old_y
        old_shape.rotation = old_rotation
        
        if old_shape in solution["stock_usage"][old_stock_idx]:
            solution["stock_usage"][old_stock_idx].remove(old_shape)
        
        # Try new position
        for stock_idx, stock in enumerate(stocks):
            if order.material_type != stock.material_type:
                continue
            
            position = self._find_position(order, stock, solution["stock_usage"][stock_idx], config)
            
            if position:
                new_x, new_y, new_rotation = position
                
                # Update placement
                solution["placements"][placement_idx] = (order_idx, stock_idx, new_x, new_y, new_rotation)
                
                # Update stock usage
                new_shape = copy.deepcopy(order.shape)
                new_shape.x = new_x
                new_shape.y = new_y
                new_shape.rotation = new_rotation
                solution["stock_usage"][stock_idx].append(new_shape)
                return
        
        # If no new position found, restore old position
        solution["stock_usage"][old_stock_idx].append(old_shape)
    
    def _swap_orders(self, solution: Dict[str, Any], stocks: List[Stock], 
                    orders: List[Order], config: OptimizationConfig):
        """Swap positions of two orders"""
        
        if len(solution["placements"]) < 2:
            return
        
        # Choose two random placements
        idx1, idx2 = random.sample(range(len(solution["placements"])), 2)
        
        placement1 = solution["placements"][idx1]
        placement2 = solution["placements"][idx2]
        
        # Swap positions
        order1_idx, stock1_idx, x1, y1, rot1 = placement1
        order2_idx, stock2_idx, x2, y2, rot2 = placement2
        
        # Update placements
        solution["placements"][idx1] = (order1_idx, stock2_idx, x2, y2, rot2)
        solution["placements"][idx2] = (order2_idx, stock1_idx, x1, y1, rot1)
        
        # Update stock usage (simplified - assumes swap is valid)
        # In practice, should check feasibility
    
    def _rotate_order(self, solution: Dict[str, Any], stocks: List[Stock], 
                     orders: List[Order], config: OptimizationConfig):
        """Rotate a random order"""
        
        if not solution["placements"]:
            return
        
        # Choose random placement with rectangle
        rect_placements = [(i, p) for i, p in enumerate(solution["placements"]) 
                          if isinstance(orders[p[0]].shape, Rectangle)]
        
        if not rect_placements:
            return
        
        placement_idx, placement = random.choice(rect_placements)
        order_idx, stock_idx, x, y, rotation = placement
        
        # Toggle rotation
        new_rotation = 90 if rotation == 0 else 0
        
        # Update placement
        solution["placements"][placement_idx] = (order_idx, stock_idx, x, y, new_rotation)
    
    def _reorder_placement(self, solution: Dict[str, Any], stocks: List[Stock], 
                          orders: List[Order], config: OptimizationConfig):
        """Change order of placements"""
        
        if len(solution["placements"]) < 2:
            return
        
        # Shuffle placements
        random.shuffle(solution["placements"])
    
    def _evaluate_solution(self, solution: Dict[str, Any], stocks: List[Stock], 
                          orders: List[Order], config: OptimizationConfig) -> float:
        """Evaluate solution cost (lower is better)"""
        
        # Calculate efficiency
        total_used_area = 0
        total_stock_area = 0
        used_stocks = set()
        
        for placement in solution["placements"]:
            order_idx, stock_idx, x, y, rotation = placement
            total_used_area += orders[order_idx].shape.area()
            used_stocks.add(stock_idx)
        
        for stock_idx in used_stocks:
            total_stock_area += stocks[stock_idx].area
        
        efficiency = (total_used_area / total_stock_area * 100) if total_stock_area > 0 else 0
        
        # Cost function (minimize waste, unplaced orders, and used stocks)
        waste_penalty = (100 - efficiency) / 100.0
        unplaced_penalty = len(solution["unplaced_orders"]) * 0.5
        stock_penalty = len(used_stocks) * 0.1
        
        cost = waste_penalty + unplaced_penalty + stock_penalty
        
        return cost
    
    def _accept_solution(self, current_cost: float, neighbor_cost: float, 
                        temperature: float) -> bool:
        """Accept or reject neighbor solution"""
        
        if neighbor_cost < current_cost:
            return True
        
        # Acceptance probability
        delta = neighbor_cost - current_cost
        probability = math.exp(-delta / temperature)
        
        return random.random() < probability
    
    def _solution_to_result(self, solution: Dict[str, Any], stocks: List[Stock], 
                           expanded_orders: List[Order], original_orders: List[Order]) -> CuttingResult:
        """Convert solution to CuttingResult"""
        
        result = CuttingResult()
        result.algorithm_used = self.name
        
        placed_shapes = []
        used_stocks = set()
        
        for placement in solution["placements"]:
            order_idx, stock_idx, x, y, rotation = placement
            order = expanded_orders[order_idx]
            stock = stocks[stock_idx]
            
            # Create placed shape
            shape = copy.deepcopy(order.shape)
            shape.x = x
            shape.y = y
            shape.rotation = rotation
            
            placed_shape = PlacedShape(
                order_id=order.id,
                shape=shape,
                stock_id=stock.id,
                rotation_applied=rotation
            )
            
            placed_shapes.append(placed_shape)
            used_stocks.add(stock_idx)
        
        result.placed_shapes = placed_shapes
        result.total_stock_used = len(used_stocks)
        
        # Calculate fulfilled orders
        fulfilled_order_ids = set()
        for ps in placed_shapes:
            original_id = ps.order_id.rsplit('_', 1)[0]
            fulfilled_order_ids.add(original_id)
        
        result.total_orders_fulfilled = len(fulfilled_order_ids)
        
        # Calculate efficiency
        if placed_shapes:
            total_placed_area = sum(ps.shape.area() for ps in placed_shapes)
            total_stock_area = sum(stocks[i].area for i in used_stocks)
            result.efficiency_percentage = (total_placed_area / total_stock_area * 100) if total_stock_area > 0 else 0
        else:
            result.efficiency_percentage = 0
        
        # Find unfulfilled orders
        unfulfilled = []
        for order in original_orders:
            if order.id not in fulfilled_order_ids:
                unfulfilled.append(order)
        
        result.unfulfilled_orders = unfulfilled
        
        # Calculate cost
        result.total_cost = sum(stocks[i].total_cost for i in used_stocks)
        
        return result