#!/usr/bin/env python3
"""
Demo 4: Priority Sorting & Tie-Breaking - Advanced order processing
===================================================================

🎯 Shows configurable tie-breaking when orders have same priority

Key concepts:
• Priority-first processing (URGENT > HIGH > MEDIUM > LOW)
• Configurable tie-breaking criteria (area, quantity, etc.)
• Secondary sorting for complex scenarios
• Processing order impact on results

Best for: Understanding advanced priority handling and optimization control
"""

import pandas as pd
from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority, OrderSortCriteria
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm

def create_test_data():
    """Create test scenario with same-priority orders to demonstrate tie-breaking"""
    
    print("📂 Creating Test Data")
    print("-" * 21)
    
    # 1. Single stock panel (limited capacity)
    stock = Stock(
        id="PANEL_001",
        width=1000,
        height=800,
        material_type=MaterialType.GLASS
    )
    print(f"📦 Stock: {stock.width}×{stock.height}mm = {stock.area:,} mm²")
    
    # 2. Orders with SAME priority but different characteristics
    orders = [
        Order("ORDER_A", Rectangle(300, 200), 1, Priority.HIGH),  # 60,000 mm²
        Order("ORDER_B", Rectangle(500, 400), 1, Priority.HIGH),  # 200,000 mm² (largest)
        Order("ORDER_C", Rectangle(150, 100), 2, Priority.HIGH),  # 15,000 mm² each (highest qty)
        Order("ORDER_D", Rectangle(250, 300), 1, Priority.HIGH),  # 75,000 mm²
        Order("ORDER_E", Rectangle(100, 100), 1, Priority.MEDIUM), # 10,000 mm² (different priority)
    ]
    
    print(f"📋 Orders:")
    for order in orders:
        area = order.shape.area() * order.quantity
        print(f"   {order.id}: {area:,} mm² [{order.priority.name}] (qty: {order.quantity})")
    
    total_demand = sum(o.shape.area() * o.quantity for o in orders)
    print(f"\n💡 Total demand: {total_demand:,} mm² vs {stock.area:,} mm² available")
    
    return [stock], orders

def test_sorting_criteria(stocks, orders):
    """Demonstrate different tie-breaking strategies"""
    
    print("\n🧪 Tie-Breaking Strategy Comparison")
    print("-" * 38)
    
    algorithm = FirstFitAlgorithm()
    
    # Define test configurations showing different tie-breaking approaches
    test_configs = [
        ("CSV Order", OrderSortCriteria.CSV_ORDER, None),
        ("Area Descending", OrderSortCriteria.AREA_DESC, None),
        ("Area Ascending", OrderSortCriteria.AREA_ASC, None),
        ("Quantity First", OrderSortCriteria.QUANTITY_DESC, None),
        ("Area + Quantity", OrderSortCriteria.AREA_DESC, OrderSortCriteria.QUANTITY_DESC)
    ]
    
    for name, primary_criteria, secondary_criteria in test_configs:
        print(f"\n🔄 Strategy: {name}")
        
        # 1. Configure optimization with specific sorting
        config = OptimizationConfig(
            prioritize_orders=True,
            order_sort_criteria=primary_criteria,
            secondary_sort_criteria=secondary_criteria
        )
        
        # 2. Show processing order (priority first, then tie-breaking)
        processed_orders = algorithm.preprocess_orders(orders, config)
        processing_order = []
        for order in processed_orders:
            processing_order.append(f"{order.id}[{order.priority.name}]")
        print(f"   Processing order: {' → '.join(processing_order)}")
        
        # 3. Run optimization and show results
        result = algorithm.optimize(stocks, orders, config)
        
        placed = [ps.order_id.split('_')[0] for ps in result.placed_shapes]
        unfulfilled = [uo.id.split('_')[0] for uo in result.unfulfilled_orders]
        
        print(f"   ✅ Placed: {', '.join(placed)}")
        if unfulfilled:
            print(f"   ❌ Discarded: {', '.join(unfulfilled)}")
        print(f"   📊 Efficiency: {result.efficiency_percentage:.1f}%")

def main():
    """Demo 4: Advanced priority sorting with configurable tie-breaking"""
    
    print("🎯 Demo 4: Priority Sorting & Tie-Breaking")
    print("=" * 43)
    print("📋 Workflow: Test data → Tie-breaking strategies → Results comparison")
    
    # Step 1: Create test scenario with same-priority orders
    stocks, orders = create_test_data()
    
    # Step 2: Compare different tie-breaking strategies
    test_sorting_criteria(stocks, orders)
    
    # Step 3: Show key insights
    print(f"\n💡 Key Insights:")
    print(f"   • Priority is ALWAYS processed first (URGENT → HIGH → MEDIUM → LOW)")
    print(f"   • Tie-breaking only applies within same priority level")
    print(f"   • Area-based sorting often improves space utilization")
    print(f"   • Quantity-first helps fulfill more orders")
    print(f"   • Combined criteria offer fine-grained control")
    
    print(f"\n✅ Priority sorting demo completed!")
    print(f"\n🔧 Configuration options:")
    print(f"   • OrderSortCriteria.AREA_DESC (default)")
    print(f"   • OrderSortCriteria.QUANTITY_DESC")
    print(f"   • OrderSortCriteria.CSV_ORDER")
    print(f"   • Plus secondary_sort_criteria for hybrid approaches")

if __name__ == "__main__":
    main() 