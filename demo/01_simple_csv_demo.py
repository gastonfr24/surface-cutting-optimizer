#!/usr/bin/env python3
"""
Demo 1: Smart CSV Integration - Essential workflow for new users
==============================================================

🎯 Shows the fundamental workflow: CSV → Smart Optimization → Results

Key concepts:
• Loading stock and orders from CSV files
• Automatic algorithm selection (NEW!)
• Professional efficiency results (60-70%+)
• Saving visual and numerical outputs
• SIMPLIFIED API - No complex imports! (NEW!)

Quick start for: First-time users, CSV data integration, smart optimization
"""

import pandas as pd
from pathlib import Path

# NEW SIMPLIFIED IMPORTS - Only one line needed! 🎉
from surface_optimizer import Stock, Order, MaterialType, Priority, Rectangle, optimize


def load_data_from_csv():
    """Load stock and orders from CSV files - core workflow step 1"""
    
    print("📂 Loading CSV Data")
    print("-" * 20)
    
    try:
        # 1. Define data path
        data_path = Path(__file__).parent.parent / "demo" / "data" / "01_simple"
        
        # 2. Load stock panels from CSV
        stock_df = pd.read_csv(data_path / "simple_stock.csv")
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
        
        # 3. Load orders from CSV
        orders_df = pd.read_csv(data_path / "simple_orders.csv")
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
        
        print(f"✅ Loaded {len(stocks)} stock panels, {len(orders)} orders")
        return stocks, orders
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check CSV files exist in demo/data/01_simple/")
        return None, None


def run_optimization(stocks, orders):
    """Run optimization - core workflow step 2 (NEW SIMPLIFIED API)"""
    
    print("\n🚀 Running Smart Optimization")
    print("-" * 30)
    
    # 1. Use new smart optimization (automatic algorithm selection)
    print("🤖 Using intelligent algorithm selection")
    print("📊 Priority: 'balanced' (good efficiency + speed)")
    print("🔄 Optimizing... (see library logs below)")
    print("=" * 40)
    
    # 2. NEW SIMPLIFIED API - Auto-save files! 🎉
    result = optimize(
        stocks, orders,
        priority='balanced',                       # Automatic algorithm selection
        allow_rotation=True,                       # Allow 90° rotation
        prioritize_orders=True,                    # Process by priority
        cutting_width=3.0,                         # 3mm blade kerf
        save_visualization="layout.png",          # NEW: Auto-save visualization
        save_report="report.json",                # NEW: Auto-save report
        output_dir="demo/outputs/01_simple/results"  # NEW: Specify output directory
    )
    
    print("=" * 40)
    result.show()  # NEW: Easy result display
    
    return result


def show_advanced_features(result, stocks, orders):
    """Show the new advanced convenience features (NEW)"""
    
    print("\n🎨 NEW Advanced Features Demo")
    print("-" * 31)
    
    # Create results directory
    results_dir = Path(__file__).parent.parent / "demo" / "data" / "01_simple" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate different types of reports (NEW)
    print("📊 Generating cutting coordinates...")
    coord_data = result.generate_report("coordinates", "cutting_coordinates.json", str(results_dir))
    
    print("📈 Generating performance analysis...")
    perf_data = result.generate_report("performance", "performance_analysis.json", str(results_dir))
    
    print("🔍 Generating material breakdown...")
    material_data = result.generate_report("material", "material_breakdown.json", str(results_dir))
    
    # 2. Save everything at once (NEW convenience method)
    print("💾 Saving complete results package...")
    result.save_results(str(results_dir), "complete_analysis")
    
    print(f"✅ All files saved to: {results_dir}")
    
    # 3. Display key metrics
    print(f"\n📊 Key Performance Metrics:")
    print(f"   • Efficiency: {result.efficiency_percentage:.1f}%")
    print(f"   • Panels used: {result.total_stock_used}/{len(stocks)}")
    print(f"   • Total cost: ${result.total_cost:.2f}")
    print(f"   • Computation: {result.computation_time:.3f}s")
    print(f"   • Algorithm: {result.algorithm_used}")
    
    return coord_data, perf_data, material_data


def main():
    """Demo 1: Essential CSV workflow with NEW simplified API"""
    
    print("🎯 Demo 1: Smart CSV Integration")
    print("=" * 35)
    print("📋 Core workflow: CSV files → Smart Optimization → Results")
    print("🆕 NEW: Simplified API - no complex imports!")
    
    # Step 1: Load data from CSV files
    stocks, orders = load_data_from_csv()
    if not stocks or not orders:
        return
    
    # Step 2: Run optimization (NEW SIMPLIFIED WAY)
    result = run_optimization(stocks, orders)
    if not result:
        return
    
    # Step 3: Show advanced features (NEW)
    coord_data, perf_data, material_data = show_advanced_features(result, stocks, orders)
    
    print("\n✅ Demo completed! Check the generated files.")
    print("\n🎉 NEW FEATURES USED:")
    print("   • ✅ Single import line (surface_optimizer)")
    print("   • ✅ Auto-save visualization and reports") 
    print("   • ✅ Built-in result.show() method")
    print("   • ✅ Multiple report formats")
    print("   • ✅ Complete result.save_results() package")
    
    print("\n🚀 Next demos:")
    print("   • 02_multi_stock_demo.py - Multiple panels")
    print("   • 03_overflow_demo.py - Order discarding")
    print("   • 04_priority_sorting_demo.py - Priority handling")
    print("   • 05_reports_and_charts_demo.py - Advanced reporting (NEW!)")


if __name__ == "__main__":
    main()