#!/usr/bin/env python3
"""
Demo 3: Smart Overflow Handling - Order discarding when demand exceeds stock
===========================================================================

🎯 Shows how smart optimization handles insufficient stock capacity

Key concepts:
• Demand vs stock area analysis
• Intelligent algorithm selection for priority handling
• Smart priority-based processing
• Unfulfilled order reporting
• SIMPLIFIED API - No complex imports! (NEW!)

Best for: Understanding capacity limits and smart order prioritization
"""

import pandas as pd
from pathlib import Path

# NEW SIMPLIFIED IMPORTS - Only one line needed! 🎉
from surface_optimizer import Stock, Order, MaterialType, Priority, Rectangle, optimize


def load_data_from_csv():
    """Load data designed to demonstrate overflow scenarios"""
    
    print("📂 Loading Overflow Test Data")
    print("-" * 30)
    
    # 1. Load limited stock (small panel)
    data_path = Path(__file__).parent.parent / "demo" / "data" / "03_overflow"
    
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
    
    # 2. Load orders (designed to exceed stock capacity)
    orders_df = pd.read_csv(data_path / "simple_orders.csv")
    orders = [
        Order(
            id=row['order_id'],
            shape=Rectangle(row['width'], row['height']),
            quantity=row['quantity'],
            priority=Priority.URGENT if row['priority'] == 'URGENT' 
                    else Priority.HIGH if row['priority'] == 'HIGH'
                    else Priority.MEDIUM if row['priority'] == 'MEDIUM'
                    else Priority.LOW,
            material_type=MaterialType.METAL
        )
        for _, row in orders_df.iterrows()
    ]
    
    print(f"✅ Loaded {len(stocks)} stock panel, {len(orders)} orders")
    return stocks, orders


def analyze_demand_vs_stock(stocks, orders):
    """Analyze capacity and predict overflow scenario"""
    
    print("\n📊 Capacity Analysis")
    print("-" * 20)
    
    # 1. Calculate total areas
    panel_area = stocks[0].width * stocks[0].height
    total_requested = sum(order.shape.width * order.shape.height * order.quantity for order in orders)
    
    print(f"📦 Available: {panel_area:,} mm² ({stocks[0].width}×{stocks[0].height})")
    print(f"📋 Requested: {total_requested:,} mm² (all orders)")
    
    # 2. Overflow calculation and prediction
    if total_requested > panel_area:
        overflow_ratio = total_requested / panel_area
        print(f"🔥 Overflow: {overflow_ratio:.1f}x demand exceeds capacity")
        print("⚠️  Some orders will be discarded")
    else:
        utilization = (total_requested / panel_area) * 100
        print(f"✅ Utilization: {utilization:.1f}% - all orders should fit")
    
    # 3. Show order priorities (processing order matters)
    print(f"\n📋 Orders by priority:")
    for order in orders:
        area = order.shape.width * order.shape.height * order.quantity
        print(f"   {order.id}: {area:,} mm² [{order.priority.name}]")


def run_optimization(stocks, orders):
    """Run smart optimization with priority-based processing (NEW SIMPLIFIED API)"""
    
    print("\n🚀 Smart Priority-Based Optimization")
    print("-" * 38)
    
    # 1. Use smart optimization with priority processing
    print("🤖 Using intelligent algorithm selection")
    print("📊 Priority: 'speed' (focused on priority handling)")
    print("🔄 Processing orders by priority...")
    print("=" * 35)
    
    # 2. NEW SIMPLIFIED API - Auto-save files! 🎉
    result = optimize(
        stocks, orders,
        priority='speed',                             # Fast algorithms for priority demo
        allow_rotation=True,                          # Allow 90° rotation
        prioritize_orders=True,                       # Key: Process by priority first
        cutting_width=3.0,                            # 3mm blade kerf
        max_computation_time=10,                      # Fast processing for overflow demo
        save_visualization="overflow_layout.png",    # NEW: Auto-save visualization
        save_report="overflow_report.json",          # NEW: Auto-save report
        output_dir="demo/data/03_overflow/results"   # NEW: Specify output directory
    )
    
    print("=" * 35)
    result.show()  # NEW: Easy result display
    
    # 3. Show overflow analysis
    total_pieces = sum(order.quantity for order in orders)
    placed_pieces = len(result.placed_shapes)
    discarded_pieces = len(result.unfulfilled_orders)
    
    print(f"📦 Placed: {placed_pieces}/{total_pieces} pieces")
    print(f"❌ Discarded: {discarded_pieces} pieces")
    
    return result


def analyze_results(result, orders):
    """Analyze which orders were placed vs discarded and why"""
    
    print("\n📊 Detailed Results Analysis")
    print("-" * 30)
    
    # 1. Show placed pieces with their priorities
    if result.placed_shapes:
        print("✅ Successfully placed pieces:")
        placed_by_priority = {}
        for placed in result.placed_shapes:
            # Find original order to get priority
            original_order = next((o for o in orders if o.id in placed.order_id), None)
            if original_order:
                priority = original_order.priority.name
                if priority not in placed_by_priority:
                    placed_by_priority[priority] = []
                placed_by_priority[priority].append(placed.order_id)
        
        for priority in ['URGENT', 'HIGH', 'MEDIUM', 'LOW']:
            if priority in placed_by_priority:
                pieces = placed_by_priority[priority]
                print(f"   {priority}: {', '.join(pieces)}")
    
    # 2. Show discarded pieces with their priorities  
    if result.unfulfilled_orders:
        print("\n❌ Discarded pieces (no space):")
        discarded_by_priority = {}
        for unfulfilled in result.unfulfilled_orders:
            # Find original order
            order_id_base = unfulfilled.id.split('_')[0]
            original_order = next((o for o in orders if o.id == order_id_base), None)
            
            if original_order:
                priority = original_order.priority.name
                if priority not in discarded_by_priority:
                    discarded_by_priority[priority] = []
                discarded_by_priority[priority].append(unfulfilled.id)
        
        for priority in ['URGENT', 'HIGH', 'MEDIUM', 'LOW']:
            if priority in discarded_by_priority:
                pieces = discarded_by_priority[priority]
                print(f"   {priority}: {', '.join(pieces)}")
    
    # 3. Key insight about priority processing
    print(f"\n💡 Priority Impact:")
    print("   Higher priority orders processed first → better placement chance")
    print("   Lower priority orders more likely to be discarded")


def show_advanced_features(result, stocks, orders):
    """Show the new advanced convenience features (NEW)"""
    
    print("\n🎨 NEW Advanced Features Demo")
    print("-" * 31)
    
    # Create results directory
    results_dir = Path(__file__).parent.parent / "demo" / "data" / "03_overflow" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate overflow-specific reports (NEW)
    print("📊 Generating unfulfilled orders report...")
    coord_data = result.generate_report("coordinates", "cutting_coordinates.json", str(results_dir))
    
    print("📈 Generating performance analysis...")
    perf_data = result.generate_report("performance", "performance_analysis.json", str(results_dir))
    
    print("🔍 Generating material breakdown...")
    material_data = result.generate_report("material", "material_breakdown.json", str(results_dir))
    
    # 2. Save everything at once (NEW convenience method)
    print("💾 Saving complete overflow analysis...")
    result.save_results(str(results_dir), "overflow_analysis")
    
    print(f"✅ All files saved to: {results_dir}")
    
    # 3. Display overflow metrics
    total_orders = len([o for order in orders for _ in range(order.quantity)])
    fulfilled_orders = len(result.placed_shapes)
    unfulfilled_orders = len(result.unfulfilled_orders)
    
    print(f"\n📊 Overflow Impact Analysis:")
    print(f"   • Orders requested: {total_orders}")
    print(f"   • Orders fulfilled: {fulfilled_orders}")
    print(f"   • Orders discarded: {unfulfilled_orders}")
    print(f"   • Fulfillment rate: {(fulfilled_orders/total_orders*100):.1f}%")
    print(f"   • Algorithm efficiency: {result.efficiency_percentage:.1f}%")
    
    return coord_data, perf_data, material_data


def main():
    """Demo 3: Overflow handling workflow with NEW simplified API"""
    
    print("🎯 Demo 3: Smart Overflow Handling")
    print("=" * 35)
    print("📋 Workflow: Demand > Stock → Priority processing → Smart discarding")
    print("🆕 NEW: Simplified API - no complex imports!")
    
    # Step 1: Load overflow test data
    stocks, orders = load_data_from_csv()
    if not stocks or not orders:
        return
    
    # Step 2: Analyze capacity vs demand
    analyze_demand_vs_stock(stocks, orders)
    
    # Step 3: Run smart priority-based optimization (NEW SIMPLIFIED WAY)
    result = run_optimization(stocks, orders)
    if not result:
        return
    
    # Step 4: Analyze placement vs discarding results
    analyze_results(result, orders)
    
    # Step 5: Show advanced features (NEW)
    coord_data, perf_data, material_data = show_advanced_features(result, stocks, orders)
    
    print("\n✅ Overflow demo completed!")
    print("\n🎉 NEW FEATURES USED:")
    print("   • ✅ Single import line (surface_optimizer)")
    print("   • ✅ Auto-save visualization and reports")
    print("   • ✅ Built-in result.show() method")
    print("   • ✅ Overflow-specific analysis")
    print("   • ✅ Complete result.save_results() package")
    
    print("\n🚀 Next demos:")
    print("   • 04_priority_sorting_demo.py - Priority handling details")
    print("   • 05_reports_and_charts_demo.py - Advanced reporting (NEW!)")
    print("\n💡 Key learning: Smart algorithms respect priorities even under overflow!")


if __name__ == "__main__":
    main() 