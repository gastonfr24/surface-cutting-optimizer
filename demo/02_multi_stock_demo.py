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

Best for: Real production scenarios with varied stock inventory
"""

import pandas as pd
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer import optimize
from surface_optimizer.utils.visualization import visualize_cutting_plan
from surface_optimizer.reporting.report_generator import ReportGenerator


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
    print("📊 Priority: 'balanced' (reliable efficiency for multi-panel)")
    print("🔄 Optimizing across multiple panels...")
    print("=" * 40)
    
    # 2. Smart optimization with balanced approach for multi-panel case
    result = optimize(
        stocks, orders,
        priority='balanced',          # Reliable algorithms for multi-panel
        allow_rotation=True,          # Allow 90° rotation
        prioritize_orders=True,       # Process by priority
        cutting_width=3.0,            # 3mm blade kerf
        max_computation_time=30       # Sufficient time for optimization
    )
    
    print("=" * 40)
    print(f"✅ Completed: {result.efficiency_percentage:.1f}% efficiency")
    print(f"🤖 Algorithm used: {result.metadata['algorithm_selection']['selected_algorithm']}")
    print(f"📦 Used {result.total_stock_used}/{len(stocks)} panels")
    
    return result


def save_results(result, stocks):
    """Save multi-panel results"""
    
    print("\n💾 Saving Multi-Panel Results")
    print("-" * 30)
    
    # 1. Create output directory
    results_dir = Path(__file__).parent.parent / "demo" / "data" / "02_multi" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Generate multi-panel layout visualization
    visualize_cutting_plan(result, stocks, save_path="multi_layout.png", output_dir=str(results_dir))
    print("✅ multi_layout.png - Multi-panel cutting plan")
    
    # 3. Generate comprehensive report
    report_gen = ReportGenerator()
    cutting_report = report_gen.generate_cutting_coordinates_report(result, stocks)
    
    import json
    report_path = results_dir / "multi_report.json"
    with open(report_path, 'w') as f:
        json.dump({
            "summary": cutting_report.summary,
            "cutting_plan": cutting_report.cutting_plan,
            "generated_date": cutting_report.generation_date.isoformat()
        }, f, indent=2)
    
    print("✅ multi_report.json - Panel-by-panel coordinates")
    print(f"📁 Files saved to: {results_dir}")


def main():
    """Demo 2: Multi-panel optimization workflow"""
    
    print("🎯 Demo 2: Smart Multi-Panel Optimization")
    print("=" * 42)
    print("📋 Workflow: Multiple panels → Smart selection → Optimal usage")
    
    # Step 1: Load multiple stock panels
    stocks, orders = load_data_from_csv()
    if not stocks or not orders:
        return
    
    # Step 2: Run cross-panel optimization
    result = run_optimization(stocks, orders)
    if not result:
        return
    
    # Step 3: Save multi-panel results
    save_results(result, stocks)
    
    print("\n✅ Multi-panel demo completed!")
    print("\n🚀 Next demos:")
    print("   • 03_overflow_demo.py - Order discarding")
    print("   • 04_priority_sorting_demo.py - Priority handling")


if __name__ == "__main__":
    main() 