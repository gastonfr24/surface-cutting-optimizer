#!/usr/bin/env python3
"""
Minimal Example - Essential code to use the Surface Cutting Optimizer
====================================================================

This is the shortest possible example to get started.
"""

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm

def main():
    # 1. Create stock panels (only required: id, width, height)
    stocks = [
        Stock("PANEL_001", 1200, 800)  # Defaults: Glass material, 6mm thickness
    ]
    
    # 2. Create orders (only required: id, shape)
    orders = [
        Order("ORDER_A", Rectangle(300, 200)),           # Defaults: qty=1, medium priority, glass
        Order("ORDER_B", Rectangle(400, 300), 1, Priority.HIGH),  # Custom priority
        Order("ORDER_C", Rectangle(150, 100), 2)         # Custom quantity
    ]
    
    # 3. Configure and run optimization (defaults work fine)
    config = OptimizationConfig()  # All defaults: rotation=True, prioritize=True, etc.
    optimizer = Optimizer(config)
    optimizer.set_algorithm(FirstFitAlgorithm())
    
    result = optimizer.optimize(stocks, orders)
    
    # 4. Show results
    print(f"Efficiency: {result.efficiency_percentage:.1f}%")
    print(f"Pieces placed: {len(result.placed_shapes)}")
    print(f"Stocks used: {result.total_stock_used}")

if __name__ == "__main__":
    main() 