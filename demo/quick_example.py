#!/usr/bin/env python3
"""
Smart Minimal Example - Essential code to use the Surface Cutting Optimizer
==========================================================================

This is the shortest possible example to get professional results.
Now with intelligent algorithm selection for maximum efficiency!
"""

from surface_optimizer.core.models import Stock, Order, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer import optimize

def main():
    # 1. Create stock panels (only required: id, width, height)
    stocks = [
        Stock("PANEL_001", 1200, 800)  # Defaults: Glass material, 6mm thickness
    ]
    
    # 2. Create orders (only required: id, shape)
    orders = [
        Order("ORDER_A", Rectangle(300, 200)),                    # Defaults: qty=1, medium priority
        Order("ORDER_B", Rectangle(400, 300), 1, Priority.HIGH), # Custom priority
        Order("ORDER_C", Rectangle(150, 100), 2)                 # Custom quantity
    ]
    
    # 3. One-line smart optimization with automatic algorithm selection!
    result = optimize(stocks, orders, priority='balanced')
    
    # 4. Show professional results
    print(f"🎯 Efficiency: {result.efficiency_percentage:.1f}%")
    print(f"🤖 Algorithm: {result.metadata['algorithm_selection']['selected_algorithm']}")
    print(f"📦 Pieces placed: {len(result.placed_shapes)}")
    print(f"📋 Stocks used: {result.total_stock_used}")
    print("✅ Professional cutting optimization in 1 line of code!")

if __name__ == "__main__":
    main() 