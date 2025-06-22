"""
Base algorithm class for Surface Cutting Optimizer
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from ..core.models import Stock, Order, CuttingResult, OptimizationConfig, OrderSortCriteria


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
        """Preprocess orders with configurable sorting criteria"""
        if not config.prioritize_orders:
            return orders.copy()
        
        def get_sort_key(order: Order, criteria: OrderSortCriteria):
            """Get sort key for given criteria"""
            if criteria == OrderSortCriteria.AREA_DESC:
                return -order.shape.area()  # Negative for descending
            elif criteria == OrderSortCriteria.AREA_ASC:
                return order.shape.area()
            elif criteria == OrderSortCriteria.DUE_DATE:
                return order.due_date or datetime.max
            elif criteria == OrderSortCriteria.QUANTITY_DESC:
                return -order.quantity
            elif criteria == OrderSortCriteria.QUANTITY_ASC:
                return order.quantity
            elif criteria == OrderSortCriteria.ORDER_DATE:
                return order.order_date or datetime.max
            elif criteria == OrderSortCriteria.CUSTOMER_ID:
                return order.customer_id
            elif criteria == OrderSortCriteria.CSV_ORDER:
                return 0  # Keep original order
            else:
                return 0
        
        def multi_criteria_key(order: Order):
            """Generate multi-criteria sort key"""
            keys = [
                order.priority.weight,  # Primary: priority (higher weight = higher priority)
                get_sort_key(order, config.order_sort_criteria)  # Secondary: configured criteria
            ]
            
            # Add tertiary sort if configured
            if config.secondary_sort_criteria and config.secondary_sort_criteria != config.order_sort_criteria:
                keys.append(get_sort_key(order, config.secondary_sort_criteria))
            
            return tuple(keys)
        
        # Sort by priority first, then by configured criteria
        if config.order_sort_criteria == OrderSortCriteria.CSV_ORDER:
            # Special case: only sort by priority, keep CSV order for same priority
            return sorted(orders, key=lambda o: o.priority.weight, reverse=True)
        else:
            # Multi-criteria sorting
            return sorted(orders, key=multi_criteria_key, reverse=True)
    
    def preprocess_stocks(self, stocks: List[Stock], config: OptimizationConfig) -> List[Stock]:
        """Preprocess stocks (e.g., sort by size)"""
        return sorted(stocks, key=lambda s: s.area, reverse=True)
    
    def __str__(self):
        return f"{self.name}" 