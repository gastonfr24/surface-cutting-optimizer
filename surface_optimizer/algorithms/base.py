"""
Base algorithm class for Surface Cutting Optimizer
"""

from abc import ABC, abstractmethod
from typing import List
from ..core.models import Stock, Order, CuttingResult, OptimizationConfig


class BaseAlgorithm(ABC):
    """Abstract base class for all optimization algorithms"""
    
    def __init__(self):
        self.name = "Base Algorithm"
    
    @abstractmethod
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """
        Optimize cutting plan for given stocks and orders
        
        Args:
            stocks: Available stock materials
            orders: Orders to fulfill
            config: Optimization configuration
            
        Returns:
            CuttingResult with optimization results
        """
        pass
    
    def preprocess_orders(self, orders: List[Order], config: OptimizationConfig) -> List[Order]:
        """Preprocess orders (e.g., sort by priority)"""
        if config.prioritize_orders:
            return sorted(orders, key=lambda o: o.priority.value, reverse=True)
        return orders.copy()
    
    def preprocess_stocks(self, stocks: List[Stock], config: OptimizationConfig) -> List[Stock]:
        """Preprocess stocks (e.g., sort by size)"""
        return sorted(stocks, key=lambda s: s.area, reverse=True)
    
    def __str__(self):
        return f"{self.name}" 