"""
Genetic Algorithm for Surface Cutting Optimization
Advanced optimization using evolutionary computation with auto-scaling
"""

import random
import copy
import math
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field

from ...core.models import Stock, Order, CuttingResult, OptimizationConfig, PlacedShape
from ...core.geometry import Rectangle, Circle, Shape
from ..base import BaseAlgorithm
from ...utils.logging import get_logger


@dataclass
class Individual:
    """Individual in genetic algorithm population"""
    genes: List[Tuple[int, int, float, float, float]]  # (order_idx, stock_idx, x, y, rotation)
    fitness: float = 0.0
    efficiency: float = 0.0
    waste: float = 0.0
    cost: float = 0.0
    feasible: bool = True
    
    def copy(self) -> 'Individual':
        """Create a copy of this individual"""
        return Individual(
            genes=self.genes.copy(),
            fitness=self.fitness,
            efficiency=self.efficiency,
            waste=self.waste,
            cost=self.cost,
            feasible=self.feasible
        )


class GeneticAlgorithm(BaseAlgorithm):
    """Genetic Algorithm with auto-scaling for cutting optimization"""
    
    def __init__(self, 
                 population_size: Optional[int] = None,
                 generations: Optional[int] = None,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elite_size: Optional[int] = None,
                 tournament_size: int = 3,
                 auto_scale: bool = True):
        super().__init__()
        self.name = "Genetic Algorithm"
        self.base_population_size = population_size
        self.base_generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.base_elite_size = elite_size
        self.tournament_size = tournament_size
        self.auto_scale = auto_scale
        self.logger = get_logger()
        
        # Evolution tracking
        self.best_fitness_history: List[float] = []
        self.average_fitness_history: List[float] = []
        self.diversity_history: List[float] = []
        
        # Performance optimizations
        self.early_stop_patience = 15
        self.convergence_threshold = 1e-6
    
    def _auto_scale_parameters(self, num_stocks: int, num_orders: int) -> Tuple[int, int, int]:
        """Auto-scale parameters based on problem size"""
        
        if not self.auto_scale:
            return (
                self.base_population_size or 50,
                self.base_generations or 100,
                self.base_elite_size or 5
            )
        
        problem_size = num_stocks * num_orders
        
        # Scale parameters based on problem complexity
        if problem_size <= 50:  # Small problems
            population_size = max(10, min(20, problem_size))
            generations = max(20, min(50, problem_size * 2))
            elite_size = max(2, population_size // 10)
        elif problem_size <= 200:  # Medium problems
            population_size = max(20, min(40, problem_size // 3))
            generations = max(30, min(100, problem_size))
            elite_size = max(3, population_size // 8)
        else:  # Large problems
            population_size = max(30, min(100, int(math.sqrt(problem_size) * 5)))
            generations = max(50, min(200, int(math.sqrt(problem_size) * 10)))
            elite_size = max(5, population_size // 6)
        
        self.logger.logger.debug(f"Auto-scaled: pop={population_size}, gen={generations}, elite={elite_size}")
        return population_size, generations, elite_size
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """Optimize using genetic algorithm with auto-scaling"""
        
        # Auto-scale parameters
        self.population_size, self.generations, self.elite_size = self._auto_scale_parameters(
            len(stocks), len(orders))
        
        self.logger.start_operation("genetic_optimization", {
            "stocks": len(stocks),
            "orders": len(orders),
            "population_size": self.population_size,
            "generations": self.generations,
            "auto_scaled": self.auto_scale
        })
        
        try:
            # Expand orders by quantity (with optimization for large quantities)
            expanded_orders = self._expand_orders_optimized(orders)
            
            # For very small problems, use simplified approach
            if len(expanded_orders) <= 5 and len(stocks) <= 3:
                return self._solve_small_problem(stocks, expanded_orders, orders, config)
            
            # Initialize population
            population = self._initialize_population(stocks, expanded_orders, config)
            
            # Evolution loop with early stopping
            best_fitness_unchanged = 0
            last_best_fitness = 0
            
            for generation in range(self.generations):
                # Evaluate fitness
                self._evaluate_population(population, stocks, expanded_orders, config)
                
                # Track statistics
                current_best_fitness = self._track_generation_stats(population, generation)
                
                # Early stopping check
                if abs(current_best_fitness - last_best_fitness) < self.convergence_threshold:
                    best_fitness_unchanged += 1
                    if best_fitness_unchanged >= self.early_stop_patience:
                        self.logger.logger.info(f"Early stopping at generation {generation}")
                        break
                else:
                    best_fitness_unchanged = 0
                
                last_best_fitness = current_best_fitness
                
                # Create next generation
                population = self._evolve_population(population, stocks, expanded_orders, config)
            
            # Get best solution
            best_individual = max(population, key=lambda x: x.fitness)
            result = self._individual_to_result(best_individual, stocks, expanded_orders, orders)
            
            # Set metadata
            result.metadata = {
                "algorithm": "genetic",
                "generations_run": generation + 1,
                "final_population_size": len(population),
                "best_fitness": best_individual.fitness,
                "convergence_generation": generation,
                "auto_scaled": self.auto_scale,
                "problem_size": len(stocks) * len(orders),
                "early_stopped": best_fitness_unchanged >= self.early_stop_patience
            }
            
            self.logger.end_operation("genetic_optimization", success=True, result={
                "efficiency": result.efficiency_percentage,
                "generations": generation + 1,
                "best_fitness": best_individual.fitness
            })
            
            return result
            
        except Exception as e:
            self.logger.end_operation("genetic_optimization", success=False, 
                                    result={"error": str(e)})
            raise
    
    def _expand_orders_optimized(self, orders: List[Order]) -> List[Order]:
        """Expand orders with optimization for large quantities"""
        expanded = []
        for order in orders:
            # For very large quantities, limit expansion to prevent memory issues
            actual_quantity = min(order.quantity, 50)  # Cap at 50 per order
            for i in range(actual_quantity):
                expanded_order = copy.deepcopy(order)
                expanded_order.id = f"{order.id}_{i+1}"
                expanded_order.quantity = 1
                expanded.append(expanded_order)
        return expanded
    
    def _solve_small_problem(self, stocks: List[Stock], expanded_orders: List[Order], 
                           original_orders: List[Order], config: OptimizationConfig) -> CuttingResult:
        """Optimized solver for very small problems"""
        
        self.logger.logger.debug("Using small problem solver")
        
        # Use simple greedy approach for small problems
        result = CuttingResult()
        result.algorithm_used = f"{self.name} (Small Problem)"
        
        placed_shapes = []
        used_stocks = set()
        
        # Sort orders by priority and area
        sorted_orders = sorted(expanded_orders, 
                             key=lambda o: (o.priority.weight, -o.shape.area()), 
                             reverse=True)
        
        for order in sorted_orders:
            # Find best fitting stock
            best_stock = None
            best_position = None
            
            for stock in stocks:
                if stock.material_type != order.material_type:
                    continue
                
                # Simple position finding
                if isinstance(order.shape, Rectangle):
                    if order.shape.width <= stock.width and order.shape.height <= stock.height:
                        best_stock = stock
                        best_position = (0, 0, 0)
                        break
                elif isinstance(order.shape, Circle):
                    if 2 * order.shape.radius <= min(stock.width, stock.height):
                        best_stock = stock
                        best_position = (0, 0, 0)
                        break
            
            if best_stock and best_position:
                shape = copy.deepcopy(order.shape)
                shape.x, shape.y, shape.rotation = best_position
                
                placed_shape = PlacedShape(
                    order_id=order.id,
                    shape=shape,
                    stock_id=best_stock.id,
                    rotation_applied=best_position[2]
                )
                
                placed_shapes.append(placed_shape)
                used_stocks.add(best_stock.id)
        
        result.placed_shapes = placed_shapes
        result.total_stock_used = len(used_stocks)
        
        # Calculate metrics
        self._calculate_result_metrics(result, stocks, original_orders)
        
        return result
    
    def _calculate_result_metrics(self, result: CuttingResult, stocks: List[Stock], 
                                 original_orders: List[Order]):
        """Calculate metrics for the result"""
        
        if not result.placed_shapes:
            result.efficiency_percentage = 0
            result.total_orders_fulfilled = 0
            result.unfulfilled_orders = original_orders.copy()
            result.total_cost = 0
            return
        
        # Calculate fulfilled orders
        fulfilled_order_ids = set()
        for ps in result.placed_shapes:
            original_id = ps.order_id.rsplit('_', 1)[0] if '_' in ps.order_id else ps.order_id
            fulfilled_order_ids.add(original_id)
        
        result.total_orders_fulfilled = len(fulfilled_order_ids)
        
        # Calculate efficiency
        used_stock_ids = {ps.stock_id for ps in result.placed_shapes}
        total_used_area = sum(ps.shape.area() for ps in result.placed_shapes)
        total_stock_area = sum(s.area for s in stocks if s.id in used_stock_ids)
        
        if total_stock_area > 0:
            efficiency = (total_used_area / total_stock_area * 100)
            result.efficiency_percentage = min(efficiency, 100.0)  # Cap at 100%
        else:
            result.efficiency_percentage = 0
        
        # Calculate cost
        result.total_cost = sum(s.total_cost for s in stocks if s.id in used_stock_ids)
        
        # Find unfulfilled orders
        unfulfilled = []
        for order in original_orders:
            if order.id not in fulfilled_order_ids:
                unfulfilled.append(order)
        result.unfulfilled_orders = unfulfilled
    
    def _initialize_population(self, stocks: List[Stock], orders: List[Order], 
                             config: OptimizationConfig) -> List[Individual]:
        """Initialize population with improved diversity"""
        population = []
        
        for i in range(self.population_size):
            if i < self.population_size // 3:
                # Greedy individuals
                individual = self._create_greedy_individual(stocks, orders, config)
            elif i < 2 * self.population_size // 3:
                # Semi-random individuals
                individual = self._create_semi_random_individual(stocks, orders, config)
            else:
                # Random individuals
                individual = self._create_random_individual(stocks, orders, config)
            
            population.append(individual)
        
        return population
    
    def _create_greedy_individual(self, stocks: List[Stock], orders: List[Order], 
                                config: OptimizationConfig) -> Individual:
        """Create greedy individual using priority-based placement"""
        genes = []
        
        # Sort orders by priority and area
        sorted_orders = sorted(enumerate(orders), 
                             key=lambda x: (x[1].priority.weight, -x[1].shape.area()), 
                             reverse=True)
        
        for order_idx, order in sorted_orders:
            # Find best stock for this order
            best_stock_idx = 0
            best_score = float('-inf')
            
            for stock_idx, stock in enumerate(stocks):
                if stock.material_type != order.material_type:
                    continue
                
                # Score based on fit and cost
                if isinstance(order.shape, Rectangle):
                    if order.shape.width <= stock.width and order.shape.height <= stock.height:
                        score = -(stock.total_cost / stock.area)  # Prefer cheaper per area
                        if score > best_score:
                            best_score = score
                            best_stock_idx = stock_idx
            
            # Simple positioning
            x, y, rotation = 0, 0, 0
            genes.append((order_idx, best_stock_idx, x, y, rotation))
        
        return Individual(genes=genes)
    
    def _create_semi_random_individual(self, stocks: List[Stock], orders: List[Order], 
                                     config: OptimizationConfig) -> Individual:
        """Create semi-random individual with some heuristics"""
        genes = []
        
        for order_idx, order in enumerate(orders):
            # Filter compatible stocks
            compatible_stocks = [i for i, s in enumerate(stocks) 
                               if s.material_type == order.material_type]
            
            if compatible_stocks:
                stock_idx = random.choice(compatible_stocks)
            else:
                stock_idx = random.randint(0, len(stocks) - 1)
            
            stock = stocks[stock_idx]
            
            # Random but constrained position
            x = random.uniform(0, max(0, stock.width - getattr(order.shape, 'width', 100)))
            y = random.uniform(0, max(0, stock.height - getattr(order.shape, 'height', 100)))
            
            rotation = 0
            if config.allow_rotation and isinstance(order.shape, Rectangle):
                rotation = random.choice([0, 90])
            
            genes.append((order_idx, stock_idx, x, y, rotation))
        
        return Individual(genes=genes)
    
    def _create_random_individual(self, stocks: List[Stock], orders: List[Order], 
                                config: OptimizationConfig) -> Individual:
        """Create completely random individual"""
        genes = []
        
        for order_idx, order in enumerate(orders):
            stock_idx = random.randint(0, len(stocks) - 1)
            stock = stocks[stock_idx]
            
            x = random.uniform(0, stock.width * 0.8)
            y = random.uniform(0, stock.height * 0.8)
            
            rotation = 0
            if config.allow_rotation and isinstance(order.shape, Rectangle):
                rotation = random.choice([0, 90, 180, 270])
            
            genes.append((order_idx, stock_idx, x, y, rotation))
        
        return Individual(genes=genes)
    
    def _track_generation_stats(self, population: List[Individual], generation: int) -> float:
        """Track evolution statistics and return best fitness"""
        fitnesses = [ind.fitness for ind in population if ind.feasible]
        
        if not fitnesses:
            return 0.0
        
        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        
        self.best_fitness_history.append(best_fitness)
        self.average_fitness_history.append(avg_fitness)
        
        # Calculate diversity
        if len(fitnesses) > 1:
            variance = sum((f - avg_fitness) ** 2 for f in fitnesses) / len(fitnesses)
            diversity = math.sqrt(variance)
        else:
            diversity = 0.0
        
        self.diversity_history.append(diversity)
        
        if generation % 20 == 0 or generation < 10:
            self.logger.logger.debug(f"Gen {generation}: Best={best_fitness:.3f}, "
                                   f"Avg={avg_fitness:.3f}, Diversity={diversity:.3f}")
        
        return best_fitness
    
    def _evaluate_population(self, population: List[Individual], stocks: List[Stock], 
                           orders: List[Order], config: OptimizationConfig):
        """Evaluate fitness for entire population"""
        for individual in population:
            self._evaluate_individual(individual, stocks, orders, config)
    
    def _evaluate_individual(self, individual: Individual, stocks: List[Stock], 
                           orders: List[Order], config: OptimizationConfig):
        """Fast individual evaluation with caching"""
        
        # Quick feasibility check
        individual.feasible = self._fast_feasibility_check(individual, stocks, orders)
        
        if not individual.feasible:
            individual.fitness = 0.0
            return
        
        # Calculate metrics efficiently
        total_used_area = sum(orders[gene[0]].shape.area() for gene in individual.genes)
        used_stocks = set(gene[1] for gene in individual.genes)
        total_stock_area = sum(stocks[i].area for i in used_stocks)
        
        individual.efficiency = (total_used_area / total_stock_area * 100) if total_stock_area > 0 else 0
        individual.waste = 100 - individual.efficiency
        individual.cost = sum(stocks[i].total_cost for i in used_stocks)
        
        # Simplified fitness function
        efficiency_score = individual.efficiency / 100.0
        waste_penalty = individual.waste / 100.0
        
        individual.fitness = 0.8 * efficiency_score + 0.2 * (1 - waste_penalty)
    
    def _fast_feasibility_check(self, individual: Individual, stocks: List[Stock], 
                               orders: List[Order]) -> bool:
        """Fast feasibility check without detailed overlap detection"""
        
        # Group by stock for basic checks
        stock_usage = {}
        for gene in individual.genes:
            order_idx, stock_idx, x, y, rotation = gene
            if stock_idx not in stock_usage:
                stock_usage[stock_idx] = []
            stock_usage[stock_idx].append((order_idx, x, y, rotation))
        
        # Basic bounds checking
        for stock_idx, placements in stock_usage.items():
            stock = stocks[stock_idx]
            
            for order_idx, x, y, rotation in placements:
                order = orders[order_idx]
                
                # Simple bounds check
                if isinstance(order.shape, Rectangle):
                    width = order.shape.width if rotation in [0, 180] else order.shape.height
                    height = order.shape.height if rotation in [0, 180] else order.shape.width
                    
                    if x + width > stock.width or y + height > stock.height:
                        return False
                elif isinstance(order.shape, Circle):
                    if x + 2 * order.shape.radius > stock.width or y + 2 * order.shape.radius > stock.height:
                        return False
        
        return True
    
    def _check_feasibility(self, individual: Individual, stocks: List[Stock], 
                          orders: List[Order], config: OptimizationConfig) -> bool:
        """Check if individual represents a feasible solution"""
        
        # Group by stock
        stock_placements = {}
        for gene in individual.genes:
            order_idx, stock_idx, x, y, rotation = gene
            if stock_idx not in stock_placements:
                stock_placements[stock_idx] = []
            stock_placements[stock_idx].append(gene)
        
        # Check each stock
        for stock_idx, placements in stock_placements.items():
            stock = stocks[stock_idx]
            placed_shapes = []
            
            for gene in placements:
                order_idx, _, x, y, rotation = gene
                order = orders[order_idx]
                
                # Create placed shape
                shape = copy.deepcopy(order.shape)
                shape.x = x
                shape.y = y
                if rotation != 0:
                    shape.rotation = rotation
                
                # Check bounds
                if not self._shape_fits_in_stock(shape, stock):
                    return False
                
                # Check overlaps
                for placed_shape in placed_shapes:
                    if shape.overlaps(placed_shape):
                        return False
                
                placed_shapes.append(shape)
        
        return True
    
    def _shape_fits_in_stock(self, shape: Shape, stock: Stock) -> bool:
        """Check if shape fits within stock bounds"""
        if isinstance(shape, Rectangle):
            if shape.rotation in [90, 270]:
                return (shape.x + shape.height <= stock.width and 
                       shape.y + shape.width <= stock.height)
            else:
                return (shape.x + shape.width <= stock.width and 
                       shape.y + shape.height <= stock.height)
        elif isinstance(shape, Circle):
            return (shape.x + 2 * shape.radius <= stock.width and 
                   shape.y + 2 * shape.radius <= stock.height)
        return True
    
    def _evolve_population(self, population: List[Individual], stocks: List[Stock], 
                          orders: List[Order], config: OptimizationConfig) -> List[Individual]:
        """Create next generation"""
        
        # Sort by fitness
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        new_population = []
        
        # Elitism: keep best individuals
        for i in range(self.elite_size):
            new_population.append(population[i].copy())
        
        # Generate offspring
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self._tournament_selection(population)
            parent2 = self._tournament_selection(population)
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if random.random() < self.mutation_rate:
                self._mutate(child1, stocks, orders, config)
            if random.random() < self.mutation_rate:
                self._mutate(child2, stocks, orders, config)
            
            new_population.extend([child1, child2])
        
        return new_population[:self.population_size]
    
    def _tournament_selection(self, population: List[Individual]) -> Individual:
        """Tournament selection"""
        tournament = random.sample(population, min(self.tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness).copy()
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Single-point crossover"""
        point = random.randint(1, len(parent1.genes) - 1)
        
        child1_genes = parent1.genes[:point] + parent2.genes[point:]
        child2_genes = parent2.genes[:point] + parent1.genes[point:]
        
        return Individual(genes=child1_genes), Individual(genes=child2_genes)
    
    def _mutate(self, individual: Individual, stocks: List[Stock], 
               orders: List[Order], config: OptimizationConfig):
        """Mutate individual"""
        
        for i in range(len(individual.genes)):
            if random.random() < 0.1:  # Gene mutation rate
                order_idx, stock_idx, x, y, rotation = individual.genes[i]
                order = orders[order_idx]
                
                # Mutate position
                if random.random() < 0.5:
                    stock = stocks[stock_idx]
                    if isinstance(order.shape, Rectangle):
                        max_x = max(0, stock.width - order.shape.width)
                        max_y = max(0, stock.height - order.shape.height)
                    elif isinstance(order.shape, Circle):
                        max_x = max(0, stock.width - 2 * order.shape.radius)
                        max_y = max(0, stock.height - 2 * order.shape.radius)
                    else:
                        max_x = stock.width * 0.8
                        max_y = stock.height * 0.8
                    
                    x = random.uniform(0, max_x) if max_x > 0 else 0
                    y = random.uniform(0, max_y) if max_y > 0 else 0
                
                # Mutate stock assignment
                elif random.random() < 0.3:
                    stock_idx = random.randint(0, len(stocks) - 1)
                
                # Mutate rotation
                elif config.allow_rotation and isinstance(order.shape, Rectangle):
                    rotation = random.choice([0, 90, 180, 270])
                
                individual.genes[i] = (order_idx, stock_idx, x, y, rotation)
    
    def _individual_to_result(self, individual: Individual, stocks: List[Stock], 
                            expanded_orders: List[Order], original_orders: List[Order]) -> CuttingResult:
        """Convert individual to CuttingResult"""
        
        result = CuttingResult()
        result.algorithm_used = self.name
        
        placed_shapes = []
        used_stocks = set()
        
        for gene in individual.genes:
            order_idx, stock_idx, x, y, rotation = gene
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
        
        # Find unfulfilled orders
        unfulfilled = []
        for order in original_orders:
            if order.id not in fulfilled_order_ids:
                unfulfilled.append(order)
        
        result.unfulfilled_orders = unfulfilled
        result.efficiency_percentage = individual.efficiency
        result.total_cost = individual.cost
        
        return result