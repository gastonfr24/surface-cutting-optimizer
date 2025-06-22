#!/usr/bin/env python3
"""
🚀 Hybrid Multi-Algorithm Optimizer
==================================

Advanced optimizer that runs multiple algorithms in parallel and 
selects the best result, significantly improving efficiency.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ...core.models import CuttingResult, OptimizationConfig, Stock, Order
from ...core.exceptions import OptimizationError
from ..base import BaseAlgorithm
from ..basic.best_fit import BestFitAlgorithm
from ..basic.first_fit import FirstFitAlgorithm
from ..basic.bottom_left import BottomLeftAlgorithm


@dataclass
class AlgorithmConfig:
    """Configuration for individual algorithm in hybrid optimization"""
    algorithm: BaseAlgorithm
    weight: float  # Weight in final score calculation
    timeout: float  # Maximum time allowed for this algorithm
    priority: int  # Execution priority (lower = higher priority)


class HybridOptimizer(BaseAlgorithm):
    """
    Hybrid Multi-Algorithm Optimizer
    
    Runs multiple algorithms concurrently and selects the best result
    based on a weighted scoring system that considers:
    - Material efficiency
    - Number of pieces placed
    - Execution time
    - Algorithm reliability
    """
    
    def __init__(self):
        super().__init__()
        self.name = "hybrid_optimizer"
        self.supports_rotation = True
        self.description = """
        Advanced hybrid optimizer that runs multiple algorithms concurrently
        and intelligently selects the best result based on multiple criteria.
        """
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """Execute hybrid multi-algorithm optimization"""
        
        start_time = time.time()
        
        # Input validation
        if not stocks or not orders:
            return self._create_empty_result(start_time)
        
        # Configure algorithms based on problem complexity
        algorithm_configs = self._configure_algorithms(stocks, orders, config)
        
        if not algorithm_configs:
            return self._create_empty_result(start_time)
        
        # Run algorithms concurrently
        results = self._run_parallel_optimization(
            algorithm_configs, stocks, orders, config
        )
        
        if not results:
            return self._create_empty_result(start_time)
        
        # Select best result
        best_result = self._select_best_result(results, algorithm_configs)
        
        # Add hybrid metadata
        computation_time = time.time() - start_time
        best_result.computation_time = computation_time
        best_result.algorithm_used = self.name
        
        if not hasattr(best_result, 'metadata') or best_result.metadata is None:
            best_result.metadata = {}
        
        best_result.metadata.update({
            'hybrid_analysis': {
                'algorithms_tested': len(results),
                'best_algorithm': results[0]['algorithm_name'] if results else 'none',
                'results_summary': [
                    {
                        'algorithm': r['algorithm_name'],
                        'efficiency': r['result'].efficiency_percentage,
                        'time': r['result'].computation_time,
                        'score': r['score']
                    }
                    for r in results[:3]  # Top 3 results
                ],
                'total_computation_time': computation_time
            }
        })
        
        return best_result
    
    def _configure_algorithms(self, stocks: List[Stock], orders: List[Order], 
                            config: OptimizationConfig) -> List[AlgorithmConfig]:
        """Configure algorithms based on problem characteristics"""
        
        # Analyze problem complexity
        total_pieces = sum(order.quantity for order in orders)
        total_area = sum(order.total_area for order in orders)
        stock_count = len(stocks)
        
        configs = []
        
        # Always include BestFit (most reliable)
        configs.append(AlgorithmConfig(
            algorithm=BestFitAlgorithm(),
            weight=1.0,
            timeout=min(5.0, config.max_computation_time * 0.3),
            priority=1
        ))
        
        # Include FirstFit for speed comparison
        configs.append(AlgorithmConfig(
            algorithm=FirstFitAlgorithm(),
            weight=0.8,  # Lower weight due to lower efficiency
            timeout=min(2.0, config.max_computation_time * 0.1),
            priority=2
        ))
        
        # Include BottomLeft for edge optimization
        configs.append(AlgorithmConfig(
            algorithm=BottomLeftAlgorithm(),
            weight=0.9,
            timeout=min(8.0, config.max_computation_time * 0.4),
            priority=3
        ))
        
        # For complex problems, consider advanced algorithms
        if total_pieces > 10 and config.max_computation_time > 10:
            try:
                from .genetic import GeneticAlgorithm
                configs.append(AlgorithmConfig(
                    algorithm=GeneticAlgorithm(),
                    weight=1.2,  # Higher weight for potentially better results
                    timeout=min(15.0, config.max_computation_time * 0.5),
                    priority=4
                ))
            except ImportError:
                pass  # Genetic algorithm not available
        
        return configs
    
    def _run_parallel_optimization(self, algorithm_configs: List[AlgorithmConfig],
                                 stocks: List[Stock], orders: List[Order],
                                 config: OptimizationConfig) -> List[Dict[str, Any]]:
        """Run algorithms in parallel and collect results"""
        
        results = []
        
        # Sort by priority
        algorithm_configs.sort(key=lambda c: c.priority)
        
        # Use thread pool for parallel execution
        with ThreadPoolExecutor(max_workers=min(4, len(algorithm_configs))) as executor:
            # Submit all algorithms
            futures = {}
            
            for algo_config in algorithm_configs:
                # Create algorithm-specific config with timeout
                algo_specific_config = OptimizationConfig(
                    allow_rotation=config.allow_rotation,
                    prioritize_orders=config.prioritize_orders,
                    cutting_width=config.cutting_width,
                    max_computation_time=algo_config.timeout
                )
                
                future = executor.submit(
                    self._run_single_algorithm,
                    algo_config.algorithm,
                    stocks,
                    orders,
                    algo_specific_config
                )
                futures[future] = algo_config
            
            # Collect results as they complete
            for future in as_completed(futures, timeout=config.max_computation_time):
                algo_config = futures[future]
                
                try:
                    result = future.result(timeout=1.0)  # Quick timeout for result retrieval
                    
                    if result and result.efficiency_percentage > 0:
                        score = self._calculate_algorithm_score(result, algo_config)
                        
                        results.append({
                            'algorithm_name': algo_config.algorithm.name,
                            'result': result,
                            'config': algo_config,
                            'score': score
                        })
                        
                except Exception as e:
                    # Algorithm failed, skip it
                    print(f"Algorithm {algo_config.algorithm.name} failed: {e}")
                    continue
        
        # Sort results by score (highest first)
        results.sort(key=lambda r: r['score'], reverse=True)
        
        return results
    
    def _run_single_algorithm(self, algorithm: BaseAlgorithm, stocks: List[Stock],
                            orders: List[Order], config: OptimizationConfig) -> Optional[CuttingResult]:
        """Run a single algorithm with error handling"""
        
        try:
            start_time = time.time()
            result = algorithm.optimize(stocks, orders, config)
            
            # Ensure computation time is set
            if not hasattr(result, 'computation_time') or result.computation_time == 0:
                result.computation_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            # Return empty result on failure
            return CuttingResult(
                placed_shapes=[],
                efficiency_percentage=0.0,
                total_stock_used=0,
                total_orders_fulfilled=0,
                algorithm_used=algorithm.name,
                computation_time=time.time() - start_time
            )
    
    def _calculate_algorithm_score(self, result: CuttingResult, 
                                 config: AlgorithmConfig) -> float:
        """Calculate weighted score for algorithm result"""
        
        # Base efficiency score (0-100)
        efficiency_score = result.efficiency_percentage
        
        # Time penalty (faster is better)
        time_penalty = min(result.computation_time * 2, 20)  # Max 20 point penalty
        
        # Placement success bonus
        total_pieces = getattr(result, 'total_pieces_attempted', len(result.placed_shapes))
        if total_pieces > 0:
            placement_ratio = len(result.placed_shapes) / total_pieces
            placement_bonus = placement_ratio * 10  # Up to 10 points
        else:
            placement_bonus = 0
        
        # Stock efficiency bonus (fewer stocks is better)
        if result.total_stock_used > 0:
            stock_bonus = max(0, 10 - result.total_stock_used)  # Bonus for using fewer stocks
        else:
            stock_bonus = 0
        
        # Calculate final score
        raw_score = (efficiency_score - time_penalty + placement_bonus + stock_bonus)
        weighted_score = raw_score * config.weight
        
        return max(0, weighted_score)
    
    def _select_best_result(self, results: List[Dict[str, Any]], 
                          algorithm_configs: List[AlgorithmConfig]) -> CuttingResult:
        """Select the best result from all algorithm results"""
        
        if not results:
            return self._create_empty_result(time.time())
        
        # Results are already sorted by score
        best_result_data = results[0]
        best_result = best_result_data['result']
        
        # Ensure required attributes
        if not hasattr(best_result, 'metadata'):
            best_result.metadata = {}
        
        return best_result
    
    def _create_empty_result(self, start_time: float) -> CuttingResult:
        """Create empty result for failed optimization"""
        
        return CuttingResult(
            placed_shapes=[],
            efficiency_percentage=0.0,
            total_stock_used=0,
            total_orders_fulfilled=0,
            algorithm_used=self.name,
            computation_time=time.time() - start_time,
            metadata={
                'hybrid_analysis': {
                    'algorithms_tested': 0,
                    'best_algorithm': 'none',
                    'results_summary': [],
                    'total_computation_time': time.time() - start_time
                }
            }
        ) 