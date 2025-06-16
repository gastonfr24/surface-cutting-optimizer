"""
First Fit Algorithm - Placeholder implementation  
"""

from typing import List
from ...core.models import Stock, Order, CuttingResult, OptimizationConfig
from ..base import BaseAlgorithm


class FirstFitAlgorithm(BaseAlgorithm):
    """First Fit algorithm - placeholder implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "First Fit"
    
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """First Fit optimization - currently returns empty result"""
        
        result = CuttingResult()
        result.algorithm_used = self.name
        result.unfulfilled_orders = orders.copy()
        result.total_stock_used = 0
        result.total_orders_fulfilled = 0
        result.efficiency_percentage = 0.0
        
        # TODO: Implement First Fit algorithm
        # Should place shapes in the first stock that has space
        
        return result 