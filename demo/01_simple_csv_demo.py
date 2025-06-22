#!/usr/bin/env python3
"""
Demo 1: Basic CSV Integration - Essential workflow for new users
===============================================================

🎯 Shows the fundamental workflow: CSV → Optimization → Results

Key concepts:
• Loading stock and orders from CSV files
• Basic optimization configuration  
• Interpreting efficiency results
• Saving visual and numerical outputs

Quick start for: First-time users, CSV data integration
"""

import pandas as pd
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.utils.visualization import visualize_cutting_plan
from surface_optimizer.reporting.report_generator import ReportGenerator


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
    """Run optimization - core workflow step 2"""
    
    print("\n🚀 Running Optimization")
    print("-" * 25)
    
    # 1. Configure optimization (basic settings)
    config = OptimizationConfig(
        allow_rotation=True,           # Allow 90° rotation
        prioritize_orders=True,        # Process by priority
        cutting_width=3.0             # 3mm blade kerf
    )
    
    # 2. Set up optimizer with FirstFit algorithm
    optimizer = Optimizer(config)
    optimizer.set_algorithm(FirstFitAlgorithm())
    
    # 3. Run optimization (library handles logging)
    print("🔄 Optimizing... (see library logs below)")
    print("=" * 40)
    
    result = optimizer.optimize(stocks, orders)
    
    print("=" * 40)
    print(f"✅ Completed: {result.efficiency_percentage:.1f}% efficiency")
    
    return result


def save_results(result, stocks):
    """Save optimization results - core workflow step 3"""
    
    print("\n💾 Saving Results")
    print("-" * 17)
    
    # 1. Create output directory
    results_dir = Path(__file__).parent.parent / "demo" / "data" / "01_simple" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Generate visual layout (PNG image)
    visualize_cutting_plan(result, stocks, save_path="layout.png", output_dir=str(results_dir))
    print("✅ layout.png - Visual cutting plan")
    
    # 3. Generate cutting report (JSON with coordinates)
    report_gen = ReportGenerator()
    cutting_report = report_gen.generate_cutting_coordinates_report(result, stocks)
    
    import json
    report_path = results_dir / "report.json"
    with open(report_path, 'w') as f:
        json.dump({
            "summary": cutting_report.summary,
            "cutting_plan": cutting_report.cutting_plan,
            "generated_date": cutting_report.generation_date.isoformat()
        }, f, indent=2)
    
    print("✅ report.json - CNC coordinates")
    print(f"📁 Files saved to: {results_dir}")


def main():
    """Demo 1: Essential CSV workflow - Load → Optimize → Save"""
    
    print("🎯 Demo 1: Basic CSV Integration")
    print("=" * 35)
    print("📋 Core workflow: CSV files → Optimization → Results")
    
    # Step 1: Load data from CSV files
    stocks, orders = load_data_from_csv()
    if not stocks or not orders:
        return
    
    # Step 2: Run optimization
    result = run_optimization(stocks, orders)
    if not result:
        return
    
    # Step 3: Save results
    save_results(result, stocks)
    
    print("\n✅ Demo completed! Check the generated files.")
    print("\n🚀 Next demos:")
    print("   • 02_multi_stock_demo.py - Multiple panels")
    print("   • 03_overflow_demo.py - Order discarding")
    print("   • 04_priority_sorting_demo.py - Priority handling")


if __name__ == "__main__":
    main()