#!/usr/bin/env python3
"""
Demo 2: Smart Multi-Stock Optimization - Using multiple panels efficiently
=========================================================================

🎯 Shows intelligent optimization across multiple stock panels

Key concepts:
• Multiple panel sizes and costs
• Smart algorithm selection for complex cases
• Advanced cross-panel optimization strategy
• Professional-grade efficiency results (70%+)
• Simplified API - no multiple imports needed!

Best for: Real production scenarios with varied stock inventory
"""

import pandas as pd
from pathlib import Path

# NEW SIMPLIFIED IMPORTS - Only one line needed! 🎉
from surface_optimizer import Stock, Order, MaterialType, Priority, Rectangle, optimize


def load_data_from_csv():
    """Load multiple stock panels and orders from CSV"""
    
    print("📂 Loading Multi-Stock Data")
    print("-" * 28)
    
    # 1. Load multiple stock panels with different sizes/costs
    data_path = Path(__file__).parent.parent / "demo" / "data" / "02_multi"
    
    stock_df = pd.read_csv(data_path / "multi_stock.csv")
    stocks = [
        Stock(
            id=row['stock_id'],
            width=row['width'],
            height=row['height'],
            material_type=MaterialType.METAL,
            cost_per_unit=row['cost']
        )
        for _, row in stock_df.iterrows()
    ]
    
    # 2. Load orders (more than single panel can handle)
    orders_df = pd.read_csv(data_path / "multi_orders.csv")
    orders = [
        Order(
            id=row['order_id'],
            shape=Rectangle(row['width'], row['height']),
            quantity=row['quantity'],
            priority=Priority.HIGH if row['priority'] == 'HIGH' else Priority.MEDIUM,
            material_type=MaterialType.METAL
        )
        for _, row in orders_df.iterrows()
    ]
    
    print(f"✅ Loaded {len(stocks)} panels, {len(orders)} orders")
    
    # 3. Show panel inventory
    print("\n📦 Stock inventory:")
    for stock in stocks:
        print(f"   {stock.id}: {stock.width}×{stock.height}mm (${stock.cost_per_unit:.2f})")
    
    return stocks, orders


def run_optimization(stocks, orders):
    """Run intelligent multi-panel optimization"""
    
    print("\n🚀 Smart Multi-Panel Optimization")
    print("-" * 35)
    
    # 1. Use balanced optimization for reliable multi-panel scenarios
    print("🤖 Using intelligent algorithm selection")
    print("📊 Priority: 'speed' (using BestFit - no overlap issues)")
    print("🔄 Optimizing across multiple panels...")
    print("=" * 40)
    
    # 2. NEW SIMPLIFIED API - Auto-save files! 🎉
    result = optimize(
        stocks, orders,
        priority='speed',                           # Use BestFit which has no overlap issues
        allow_rotation=True,                        # Allow 90° rotation
        prioritize_orders=True,                     # Process by priority
        cutting_width=3.0,                          # 3mm blade kerf
        max_computation_time=30,                    # Sufficient time for optimization
        save_visualization="multi_layout.png",     # NEW: Auto-save visualization
        save_report="multi_report.json",           # NEW: Auto-save report
        output_dir="demo/outputs/02_multi"         # NEW: Specify output directory
    )
    
    print("=" * 40)
    result.show()  # NEW: Easy result display
    
    return result


def show_advanced_features(result, stocks, orders):
    """Show the new advanced convenience features"""
    
    print("\n🎨 Advanced Features Demo")
    print("-" * 26)
    
    # Create results directory
    results_dir = Path(__file__).parent.parent / "demo" / "data" / "02_multi"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Show cutting plan interactively (if running in Jupyter/interactive)
    print("🖼️  Showing cutting plan...")
    result.visualize()  # Shows in window if possible
    
    # 2. Generate different types of reports
    print("📊 Generating cutting coordinates...")
    coord_data = result.generate_report("coordinates", "cutting_coordinates.json", str(results_dir))
    
    print("📈 Generating performance analysis...")
    perf_data = result.generate_report("performance", "performance_analysis.json", str(results_dir))
    
    print("🔍 Generating material breakdown...")
    material_data = result.generate_report("material", "material_breakdown.json", str(results_dir))
    
    # 3. Save everything at once (convenience method)
    print("💾 Saving complete results package...")
    result.save_results(str(results_dir), "complete_analysis")
    
    print(f"✅ All files saved to: {results_dir}")
    
    # 4. Display key metrics
    print(f"\n📊 Key Metrics:")
    print(f"   • Efficiency: {result.efficiency_percentage:.1f}%")
    print(f"   • Panels used: {result.total_stock_used}/{len(stocks)}")
    print(f"   • Total cost: ${result.total_cost:.2f}")
    print(f"   • Computation: {result.computation_time:.3f}s")
    
    return coord_data, perf_data, material_data


def main():
    """Demo 2: Multi-panel optimization workflow with NEW simplified API"""
    
    print("🎯 Demo 2: Smart Multi-Panel Optimization")
    print("=" * 42)
    print("📋 Workflow: Multiple panels → Smart selection → Optimal usage")
    print("🆕 NEW: Simplified API - no complex imports!")
    
    # Step 1: Load multiple stock panels
    stocks, orders = load_data_from_csv()
    if not stocks or not orders:
        return
    
    # Step 2: Run cross-panel optimization (NEW SIMPLIFIED WAY)
    result = run_optimization(stocks, orders)
    if not result:
        return
    
    # Step 3: Show advanced features (NEW)
    coord_data, perf_data, material_data = show_advanced_features(result, stocks, orders)
    
    print("\n✅ Multi-panel demo completed!")
    print("\n🎉 NEW FEATURES USED:")
    print("   • ✅ Single import line (surface_optimizer)")
    print("   • ✅ Auto-save visualization and reports")
    print("   • ✅ Built-in result.show() method")
    print("   • ✅ Convenient result.visualize() method")
    print("   • ✅ Multiple report formats")
    print("   • ✅ Complete result.save_results() package")
    
    print("\n🚀 Next demos:")
    print("   • 03_overflow_demo.py - Order discarding")
    print("   • 04_priority_sorting_demo.py - Priority handling")


if __name__ == "__main__":
    main() 