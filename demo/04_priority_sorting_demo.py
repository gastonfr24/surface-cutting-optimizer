#!/usr/bin/env python3
"""
Demo 4: Smart Priority Sorting & Tie-Breaking - Advanced order processing
=========================================================================

🎯 Shows smart configurable tie-breaking when orders have same priority

Key concepts:
• Smart algorithm selection with custom sorting
• Priority-first processing (URGENT > HIGH > MEDIUM > LOW)
• Configurable tie-breaking criteria (area, quantity, etc.)
• Secondary sorting for complex scenarios
• Professional results with intelligent optimization
• SIMPLIFIED API - No complex imports! (NEW!)

Best for: Understanding advanced priority handling and smart optimization control
"""

import pandas as pd

# NEW SIMPLIFIED IMPORTS - Only one line needed! 🎉
from surface_optimizer import Stock, Order, MaterialType, Priority, Rectangle, optimize, OrderSortCriteria

def create_test_data():
    """Create test scenario with same-priority orders to demonstrate tie-breaking"""
    
    print("📂 Creating Test Data")
    print("-" * 21)
    
    # 1. Single stock panel (limited capacity)
    stock = Stock(
        id="PANEL_001",
        width=1000,
        height=800,
        material_type=MaterialType.GLASS,
        cost_per_unit=50.0
    )
    print(f"📦 Stock: {stock.width}×{stock.height}mm = {stock.area:,} mm²")
    
    # 2. Orders with SAME priority but different characteristics
    orders = [
        Order("ORDER_A", Rectangle(300, 200), 1, Priority.HIGH, MaterialType.GLASS),  # 60,000 mm²
        Order("ORDER_B", Rectangle(500, 400), 1, Priority.HIGH, MaterialType.GLASS),  # 200,000 mm² (largest)
        Order("ORDER_C", Rectangle(150, 100), 2, Priority.HIGH, MaterialType.GLASS),  # 15,000 mm² each (highest qty)
        Order("ORDER_D", Rectangle(250, 300), 1, Priority.HIGH, MaterialType.GLASS),  # 75,000 mm²
        Order("ORDER_E", Rectangle(100, 100), 1, Priority.MEDIUM, MaterialType.GLASS), # 10,000 mm² (different priority)
    ]
    
    print(f"📋 Orders:")
    for order in orders:
        area = order.shape.area() * order.quantity
        print(f"   {order.id}: {area:,} mm² [{order.priority.name}] (qty: {order.quantity})")
    
    total_demand = sum(o.shape.area() * o.quantity for o in orders)
    print(f"\n💡 Total demand: {total_demand:,} mm² vs {stock.area:,} mm² available")
    
    return [stock], orders

def test_sorting_criteria(stocks, orders):
    """Demonstrate different tie-breaking strategies with smart optimization (NEW SIMPLIFIED API)"""
    
    print("\n🧪 Smart Tie-Breaking Strategy Comparison")
    print("-" * 44)
    
    # Define test configurations showing different tie-breaking approaches
    test_configs = [
        ("CSV Order", OrderSortCriteria.CSV_ORDER, None),
        ("Area Descending", OrderSortCriteria.AREA_DESC, None),
        ("Area Ascending", OrderSortCriteria.AREA_ASC, None),
        ("Quantity First", OrderSortCriteria.QUANTITY_DESC, None),
        ("Area + Quantity", OrderSortCriteria.AREA_DESC, OrderSortCriteria.QUANTITY_DESC)
    ]
    
    results = []
    
    for name, primary_criteria, secondary_criteria in test_configs:
        print(f"\n🔄 Strategy: {name}")
        print(f"   🤖 Using smart algorithm selection with custom sorting")
        
        # 1. NEW SIMPLIFIED API - Use smart optimization with specific sorting criteria
        result = optimize(
            stocks, orders,
            priority='speed',                      # Fast algorithms for comparison
            prioritize_orders=True,               # Enable priority processing
            order_sort_criteria=primary_criteria, # Primary tie-breaking
            secondary_sort_criteria=secondary_criteria, # Secondary tie-breaking
            allow_rotation=True,
            cutting_width=3.0,
            save_visualization=f"priority_sort_{name.lower().replace(' ', '_')}.png",  # NEW: Auto-save each test
            output_dir="demo/data/04_priority/results"  # NEW: Specify output directory
        )
        
        # 2. Show results summary
        placed = [ps.order_id.split('_')[0] for ps in result.placed_shapes]
        unfulfilled = [uo.id.split('_')[0] for uo in result.unfulfilled_orders]
        
        print(f"   📊 Algorithm: {result.metadata['algorithm_selection']['selected_algorithm']}")
        print(f"   ✅ Placed: {', '.join(placed)}")
        if unfulfilled:
            print(f"   ❌ Discarded: {', '.join(unfulfilled)}")
        print(f"   📊 Efficiency: {result.efficiency_percentage:.1f}%")
        
        results.append((name, result))
    
    return results

def show_advanced_features(results, stocks, orders):
    """Show the new advanced convenience features (NEW)"""
    
    print("\n🎨 NEW Advanced Features Demo")
    print("-" * 31)
    
    # Create results directory
    from pathlib import Path
    results_dir = Path(__file__).parent.parent / "demo" / "data" / "04_priority" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Pick the best result for detailed analysis
    best_result = max(results, key=lambda x: x[1].efficiency_percentage)
    best_name, best_result_obj = best_result
    
    print(f"📊 Detailed analysis of best strategy: {best_name}")
    
    # 2. Generate comprehensive reports (NEW)
    print("📊 Generating detailed performance analysis...")
    coord_data = best_result_obj.generate_report("coordinates", "best_strategy_coordinates.json", str(results_dir))
    
    print("📈 Generating performance comparison...")
    perf_data = best_result_obj.generate_report("performance", "performance_analysis.json", str(results_dir))
    
    print("🔍 Generating material breakdown...")
    material_data = best_result_obj.generate_report("material", "material_breakdown.json", str(results_dir))
    
    # 3. Save everything at once (NEW convenience method)
    print("💾 Saving complete priority analysis...")
    best_result_obj.save_results(str(results_dir), "priority_analysis")
    
    print(f"✅ All files saved to: {results_dir}")
    
    # 4. Display comparison summary
    print(f"\n📊 Strategy Comparison Summary:")
    for name, result in results:
        print(f"   • {name}: {result.efficiency_percentage:.1f}% efficiency")
    
    print(f"\n🏆 Best Strategy: {best_name} ({best_result_obj.efficiency_percentage:.1f}% efficiency)")
    
    return coord_data, perf_data, material_data

def main():
    """Demo 4: Advanced priority sorting with configurable tie-breaking (NEW SIMPLIFIED API)"""
    
    print("🎯 Demo 4: Smart Priority Sorting & Tie-Breaking")
    print("=" * 49)
    print("📋 Workflow: Test data → Smart tie-breaking strategies → Results comparison")
    print("🆕 NEW: Simplified API - no complex imports!")
    
    # Step 1: Create test scenario with same-priority orders
    stocks, orders = create_test_data()
    
    # Step 2: Compare different tie-breaking strategies (NEW SIMPLIFIED WAY)
    results = test_sorting_criteria(stocks, orders)
    
    # Step 3: Show advanced features (NEW)
    coord_data, perf_data, material_data = show_advanced_features(results, stocks, orders)
    
    # Step 4: Show key insights
    print(f"\n💡 Key Insights:")
    print(f"   • Priority is ALWAYS processed first (URGENT → HIGH → MEDIUM → LOW)")
    print(f"   • Tie-breaking only applies within same priority level")
    print(f"   • Area-based sorting often improves space utilization")
    print(f"   • Quantity-first helps fulfill more orders")
    print(f"   • Combined criteria offer fine-grained control")
    
    print(f"\n✅ Priority sorting demo completed!")
    print("\n🎉 NEW FEATURES USED:")
    print("   • ✅ Single import line (surface_optimizer)")
    print("   • ✅ Auto-save visualization for each strategy")
    print("   • ✅ Built-in result.show() method")
    print("   • ✅ Strategy comparison analysis")
    print("   • ✅ Complete result.save_results() package")
    
    print(f"\n🔧 Configuration options:")
    print(f"   • OrderSortCriteria.AREA_DESC (default)")
    print(f"   • OrderSortCriteria.QUANTITY_DESC")
    print(f"   • OrderSortCriteria.CSV_ORDER")
    print(f"   • Plus secondary_sort_criteria for hybrid approaches")
    
    print("\n🚀 Next demo:")
    print("   • 05_reports_and_charts_demo.py - Advanced reporting (NEW!)")

if __name__ == "__main__":
    main() 