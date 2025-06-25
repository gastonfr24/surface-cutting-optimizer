#!/usr/bin/env python3
"""
Demo 4: Smart Priority Sorting - Order prioritization with limited stock
========================================================================

🎯 Shows how priority system handles demand overflow scenarios

Key concepts:
• Priority-based order processing (HIGH > MEDIUM > LOW)
• Stock capacity vs demand analysis
• Intelligent order discarding when stock is insufficient
• Visual reports showing which orders were fulfilled/discarded
• SIMPLIFIED API - No complex imports! (NEW!)

Best for: Understanding priority handling and capacity management
"""

import pandas as pd
from pathlib import Path

# NEW SIMPLIFIED IMPORTS - Only one line needed! 🎉
from surface_optimizer import Stock, Order, MaterialType, Priority, Rectangle, optimize


def load_data_from_csv():
    """Load limited stock and high-demand orders from CSV"""
    
    print("📂 Loading Priority Test Data")
    print("-" * 30)
    
    # 1. Load limited stock (designed for overflow scenario)
    data_path = Path(__file__).parent / "data" / "04_priority"
    
    stock_df = pd.read_csv(data_path / "priority_stock.csv")
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
    
    # 2. Load orders with different priorities (designed to exceed capacity)
    orders_df = pd.read_csv(data_path / "priority_orders.csv")
    orders = [
        Order(
            id=row['order_id'],
            shape=Rectangle(row['width'], row['height']),
            quantity=row['quantity'],
            priority=Priority.HIGH if row['priority'] == 'HIGH' 
                    else Priority.MEDIUM if row['priority'] == 'MEDIUM'
                    else Priority.LOW,
            material_type=MaterialType.METAL
        )
        for _, row in orders_df.iterrows()
    ]
    
    print(f"✅ Loaded {len(stocks)} stock panels, {len(orders)} orders")
    
    # 3. Show capacity analysis
    total_stock_area = sum(s.width * s.height for s in stocks)
    total_demand_area = sum(o.shape.width * o.shape.height * o.quantity for o in orders)
    
    print(f"\n💡 Capacity Analysis:")
    print(f"   📦 Total stock: {total_stock_area:,} mm²")
    print(f"   📋 Total demand: {total_demand_area:,} mm²")
    print(f"   ⚠️  Overflow: {(total_demand_area/total_stock_area):.1f}x demand vs capacity")
    
    # 4. Show orders by priority
    print(f"\n📋 Orders by priority:")
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        priority_orders = [o for o in orders if o.priority.name == priority]
        if priority_orders:
            total_pieces = sum(o.quantity for o in priority_orders)
            print(f"   🔥 {priority}: {len(priority_orders)} orders, {total_pieces} pieces")
    
    return stocks, orders


def analyze_demand_vs_stock(stocks, orders):
    """Analyze capacity and predict overflow scenario"""
    
    print("\n📊 Detailed Capacity Analysis")
    print("-" * 32)
    
    # 1. Calculate areas
    stock_area = sum(s.width * s.height for s in stocks)
    demand_area = sum(o.shape.width * o.shape.height * o.quantity for o in orders)
    
    # 2. Show overflow prediction
    if demand_area > stock_area:
        overflow_ratio = demand_area / stock_area
        excess_area = demand_area - stock_area
        print(f"🚨 OVERFLOW SCENARIO:")
        print(f"   • Demand exceeds capacity by {overflow_ratio:.1f}x")
        print(f"   • {excess_area:,} mm² of orders will be discarded")
        print(f"   • Priority system will determine which orders survive")
    else:
        utilization = (demand_area / stock_area) * 100
        print(f"✅ SUFFICIENT CAPACITY:")
        print(f"   • Expected utilization: {utilization:.1f}%")
        print(f"   • All orders should fit")
    
    return stock_area, demand_area


def run_optimization(stocks, orders):
    """Run priority-based optimization (NEW SIMPLIFIED API)"""
    
    print("\n🚀 Priority-Based Optimization")
    print("-" * 32)
    
    # 1. Use smart optimization with priority processing
    print("🤖 Using intelligent algorithm selection")
    print("📊 Priority: 'speed' (best for priority scenarios)")
    print("🎯 Processing orders by priority: HIGH → MEDIUM → LOW")
    print("=" * 45)
    
    # 2. NEW SIMPLIFIED API - Auto-save files! 🎉
    result = optimize(
        stocks, orders,
        priority='speed',                             # Fast algorithms for priority demo
        allow_rotation=True,                          # Allow 90° rotation
        prioritize_orders=True,                       # Key: Process by priority first
        cutting_width=3.0,                            # 3mm blade kerf
        max_computation_time=15,                      # Quick processing
        save_visualization="priority_layout.png",    # NEW: Auto-save visualization
        save_report="priority_report.json",          # NEW: Auto-save report
        output_dir="demo/outputs/04_priority/results"  # Correct path pattern
    )
    
    print("=" * 45)
    result.show()  # NEW: Easy result display
    
    return result


def analyze_priority_results(result, orders):
    """Analyze which orders were placed vs discarded by priority"""
    
    print("\n📊 Priority Fulfillment Analysis")
    print("-" * 33)
    
    # 1. Group orders by priority and status
    placed_order_ids = set()
    for placed in result.placed_shapes:
        # Extract base order ID (remove piece suffix)
        base_id = placed.order_id.split('_piece_')[0] if '_piece_' in placed.order_id else placed.order_id
        placed_order_ids.add(base_id)
    
    priority_stats = {}
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        priority_orders = [o for o in orders if o.priority.name == priority]
        fulfilled = [o for o in priority_orders if o.id in placed_order_ids]
        discarded = [o for o in priority_orders if o.id not in placed_order_ids]
        
        priority_stats[priority] = {
            'fulfilled': fulfilled,
            'discarded': discarded,
            'total': priority_orders
        }
    
    # 2. Display results by priority
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        stats = priority_stats[priority]
        if not stats['total']:
            continue
            
        fulfilled_pieces = sum(o.quantity for o in stats['fulfilled'])
        discarded_pieces = sum(o.quantity for o in stats['discarded'])
        total_pieces = fulfilled_pieces + discarded_pieces
        
        print(f"\n🔥 {priority} PRIORITY:")
        print(f"   ✅ Fulfilled: {len(stats['fulfilled'])}/{len(stats['total'])} orders, {fulfilled_pieces} pieces")
        print(f"   ❌ Discarded: {len(stats['discarded'])} orders, {discarded_pieces} pieces")
        
        if total_pieces > 0:
            survival_rate = (fulfilled_pieces / total_pieces) * 100
            print(f"   📈 Survival rate: {survival_rate:.1f}%")
    
    return priority_stats


def generate_priority_management_report(result, stocks, orders):
    """Generate management report with priority analysis and visual summary"""
    
    print("\n📊 Generating Priority Management Report")
    print("-" * 42)
    
    # Create output directory
    output_dir = "demo/outputs/04_priority/management"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Generate PNG report with visual summary (simple way)
    print("🖼️  Creating visual summary image...")
    
    try:
        result.management_report("priority_visual_summary.png", output_dir,
                                figsize=(16, 12),
                                dpi=200,
                                format='png',
                                theme='professional',
                                show_detailed_info=True)
        print("   ✅ PNG Summary: Visual layout + priority analysis")
    
    except Exception as e:
        print(f"   ⚠️  PNG issue: {e}")
    
    # 2. Generate PDF version for professional use
    print("📄 Creating PDF executive summary...")
    
    try:
        result.management_report("priority_executive_summary.pdf", output_dir,
                                figsize=(14, 10),
                                dpi=300,
                                format='pdf',
                                theme='professional',
                                show_detailed_info=True)
        print("   ✅ Executive PDF: Professional priority report")
    
    except Exception as e:
        print(f"   ⚠️  PDF issue: {e}")
    
    print(f"\n📁 Management reports saved to: {output_dir}")
    
    return output_dir


def show_advanced_features(result, stocks, orders):
    """Show the new advanced convenience features (NEW)"""
    
    print("\n🎨 Advanced Features Demo")
    print("-" * 26)
    
    # Create results directory
    results_dir = Path("demo/outputs/04_priority/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Save layout visualization only
    print("💾 Saving layout visualization...")
    result.save_results(str(results_dir), "priority_analysis")
    
    print(f"✅ Files saved to: {results_dir}")
    
    # 2. Display key insights
    print(f"\n📊 Key Priority Insights:")
    print(f"   • Efficiency: {result.efficiency_percentage:.1f}%")
    print(f"   • Panels used: {result.total_stock_used}/{len(stocks)}")
    print(f"   • Total cost: ${result.total_cost:.2f}")
    print(f"   • Orders fulfilled: {result.total_orders_fulfilled}")
    print(f"   • Algorithm: {result.algorithm_used}")
    
    return results_dir


def main():
    """Demo 4: Priority-based optimization with stock limitations"""
    
    print("🎯 Demo 4: Smart Priority Sorting")
    print("=" * 34)
    print("📋 Workflow: Limited stock → Priority processing → Smart discarding")
    print("🆕 NEW: Simplified API - no complex imports!")
    
    # Step 1: Load data designed for overflow scenario
    stocks, orders = load_data_from_csv()
    if not stocks or not orders:
        return
    
    # Step 2: Analyze capacity vs demand
    stock_area, demand_area = analyze_demand_vs_stock(stocks, orders)
    
    # Step 3: Run priority-based optimization (NEW SIMPLIFIED WAY)
    result = run_optimization(stocks, orders)
    if not result:
        return
    
    # Step 4: Analyze priority fulfillment
    priority_stats = analyze_priority_results(result, orders)
    
    # Step 5: Generate management report with visual summary
    mgmt_dir = generate_priority_management_report(result, stocks, orders)
    
    # Step 6: Show advanced features (NEW)
    results_dir = show_advanced_features(result, stocks, orders)
    
    print("\n✅ Priority sorting demo completed!")
    print("\n🎉 NEW FEATURES USED:")
    print("   • ✅ Single import line (surface_optimizer)")
    print("   • ✅ Priority-based order processing")
    print("   • ✅ Auto-save visualization and reports")
    print("   • ✅ Built-in result.show() method")
    print("   • ✅ Management report with priority analysis")
    print("   • ✅ Visual summary PNG with stock usage")
    print("   • ✅ Complete result.save_results() package")
    
    print(f"\n💡 Key Learnings:")
    print(f"   • Priority system protects critical orders")
    print(f"   • Higher priority orders processed first")
    print(f"   • Smart discarding when capacity is exceeded")
    print(f"   • Visual reports show fulfillment by priority")
    print(f"   • Management reports include stock utilization")
    
    print(f"\n📁 Generated Files:")
    print(f"   • Executive PDF: {mgmt_dir}/priority_executive_summary.pdf")
    print(f"   • Visual Summary: {mgmt_dir}/priority_visual_summary.png")
    print(f"   • Layout Image: demo/outputs/04_priority/results/priority_layout.png")
    
    print("\n🚀 Next demos:")
    print("   • 05_reports_demo.py - Advanced reporting")
    print("   • 06_visualization_demo.py - Custom visualizations")


if __name__ == "__main__":
    main()
