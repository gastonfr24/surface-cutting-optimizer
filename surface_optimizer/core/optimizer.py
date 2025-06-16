"""
Main optimizer class for Surface Cutting Optimizer
Enhanced with logging and advanced features
"""

import time
from typing import List, Optional, Dict, Any
from .models import Stock, Order, CuttingResult, OptimizationConfig
from .validators import validate_stocks, validate_orders, validate_stock_order_compatibility
from .exceptions import OptimizationError, ValidationError
from ..algorithms.base import BaseAlgorithm
from ..utils.logging import get_logger, OptimizationLogger


class Optimizer:
    """Main optimizer class that coordinates algorithms and validation"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None, logger: Optional[OptimizationLogger] = None):
        self.config = config or OptimizationConfig()
        self.algorithm: Optional[BaseAlgorithm] = None
        self.logger = logger or get_logger()
        self.optimization_history: List[CuttingResult] = []
    
    def set_algorithm(self, algorithm: BaseAlgorithm):
        """Set the optimization algorithm to use"""
        self.algorithm = algorithm
    
    def optimize(self, stocks: List[Stock], orders: List[Order]) -> CuttingResult:
        """
        Optimize cutting plan for given stocks and orders
        
        Args:
            stocks: List of available stock materials
            orders: List of cutting orders to fulfill
            
        Returns:
            CuttingResult with optimization results
            
        Raises:
            OptimizationError: If optimization fails
            ValidationError: If inputs are invalid
        """
        self.logger.start_operation("optimize", {
            "stocks_count": len(stocks),
            "orders_count": len(orders),
            "algorithm": self.algorithm.name if self.algorithm else "None"
        })
        
        try:
            # Validate configuration
            config_issues = self.config.validate()
            if config_issues:
                self.logger.log_validation("configuration", 1, config_issues)
                raise OptimizationError(f"Invalid configuration: {'; '.join(config_issues)}")
            
            # Validate inputs
            try:
                stock_issues = []
                order_issues = []
                
                for stock in stocks:
                    stock_issues.extend(stock.validate())
                
                for order in orders:
                    order_issues.extend(order.validate())
                
                self.logger.log_validation("stocks", len(stocks), stock_issues)
                self.logger.log_validation("orders", len(orders), order_issues)
                
                validate_stocks(stocks)
                validate_orders(orders)
                validate_stock_order_compatibility(stocks, orders)
                
            except ValidationError as e:
                self.logger.end_operation("optimize", success=False, 
                                        result={"error": f"Validation failed: {e}"})
                raise OptimizationError(f"Validation failed: {e}")
            
            # Check algorithm is set
            if self.algorithm is None:
                self.logger.end_operation("optimize", success=False, 
                                        result={"error": "No algorithm set"})
                raise OptimizationError("No algorithm set. Use set_algorithm() first.")
            
            # Log algorithm start
            self.logger.log_algorithm_start(self.algorithm.name, len(stocks), len(orders))
            
            # Track computation time
            start_time = time.time()
            
            # Run optimization
            result = self.algorithm.optimize(stocks, orders, self.config)
            
            # Set computation time
            result.computation_time = time.time() - start_time
            
            # Calculate costs
            result.total_cost = sum(stock.total_cost for stock in stocks 
                                  if any(ps.stock_id == stock.id for ps in result.placed_shapes))
            
            # Validate result
            self._validate_result(result, stocks, orders)
            
            # Log results
            result_summary = {
                "stocks_used": result.total_stock_used,
                "orders_fulfilled": result.total_orders_fulfilled,
                "efficiency": result.efficiency_percentage,
                "computation_time": result.computation_time,
                "total_cost": result.total_cost
            }
            
            self.logger.log_algorithm_result(result_summary)
            self.logger.end_operation("optimize", success=True, result=result_summary)
            
            # Store in history
            self.optimization_history.append(result)
            
            return result
            
        except Exception as e:
            self.logger.end_operation("optimize", success=False, 
                                    result={"error": str(e)})
            raise OptimizationError(f"Optimization failed: {e}")
    
    def compare_algorithms(self, algorithms: List[BaseAlgorithm], 
                          stocks: List[Stock], orders: List[Order]) -> List[CuttingResult]:
        """
        Compare multiple algorithms on the same problem
        
        Args:
            algorithms: List of algorithms to compare
            stocks: Stock materials
            orders: Orders to fulfill
            
        Returns:
            List of CuttingResult, one per algorithm
        """
        results = []
        
        for algorithm in algorithms:
            original_algorithm = self.algorithm
            self.set_algorithm(algorithm)
            
            try:
                result = self.optimize(stocks, orders)
                results.append(result)
            except Exception as e:
                # Create failed result
                failed_result = CuttingResult()
                failed_result.algorithm_used = algorithm.name
                failed_result.metadata = {"error": str(e)}
                results.append(failed_result)
            
            # Restore original algorithm
            self.algorithm = original_algorithm
        
        return results
    
    def _validate_result(self, result: CuttingResult, 
                        stocks: List[Stock], orders: List[Order]):
        """Validate optimization result"""
        # Basic sanity checks
        if result.total_stock_used < 0:
            raise OptimizationError("Invalid result: negative stock usage")
        
        if result.total_orders_fulfilled < 0:
            raise OptimizationError("Invalid result: negative orders fulfilled")
        
        if result.efficiency_percentage < 0 or result.efficiency_percentage > 100:
            raise OptimizationError(f"Invalid efficiency: {result.efficiency_percentage}%")
        
        # Check placed shapes don't exceed stock bounds
        stock_dict = {stock.id: stock for stock in stocks}
        
        for placed_shape in result.placed_shapes:
            stock = stock_dict.get(placed_shape.stock_id)
            if not stock:
                raise OptimizationError(f"Placed shape references unknown stock: {placed_shape.stock_id}")
            
            # Check shape fits in stock (basic check)
            shape = placed_shape.shape
            if (shape.x < 0 or shape.y < 0 or 
                shape.x + getattr(shape, 'width', 0) > stock.width or
                shape.y + getattr(shape, 'height', 0) > stock.height):
                raise OptimizationError(f"Placed shape exceeds stock bounds: {placed_shape}")
    
    def get_optimization_history(self) -> List[CuttingResult]:
        """Get history of all optimizations performed"""
        return self.optimization_history.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of all optimizations"""
        if not self.optimization_history:
            return {"message": "No optimizations performed yet"}
        
        results = self.optimization_history
        
        return {
            "total_optimizations": len(results),
            "average_efficiency": sum(r.efficiency_percentage for r in results) / len(results),
            "average_computation_time": sum(r.computation_time for r in results) / len(results),
            "total_stocks_used": sum(r.total_stock_used for r in results),
            "total_orders_fulfilled": sum(r.total_orders_fulfilled for r in results),
            "total_cost": sum(r.total_cost for r in results),
            "best_efficiency": max(r.efficiency_percentage for r in results),
            "worst_efficiency": min(r.efficiency_percentage for r in results),
        }
    
    def export_logs(self, filepath: str):
        """Export optimization logs to file"""
        self.logger.export_logs(filepath)
    
    def clear_history(self):
        """Clear optimization history"""
        self.optimization_history.clear()
        self.logger.log_info("Optimization history cleared")
    
    def __str__(self):
        algorithm_name = self.algorithm.name if self.algorithm else "None"
        history_count = len(self.optimization_history)
        return f"Optimizer(algorithm={algorithm_name}, optimizations={history_count})" 