#!/usr/bin/env python3
"""
Advanced Demo: Library Improvement Impact Analysis
==================================================

🎯 Shows the dramatic improvements achieved through smart algorithm selection

Key concepts:
• Comparing old vs new approaches
• Performance improvement metrics
• Algorithm selection strategies
• Efficiency optimization results

Quick start for: Performance analysis, algorithm comparison, optimization verification
"""

import pandas as pd
import time
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer import optimize


def load_test_data():
    """Load test data from existing simple demo - workflow step 1"""
    
    print("📂 Loading Test Data")
    print("-" * 20)
    
    try:
        # Load from existing simple demo data
        data_path = Path(__file__).parent.parent / "data" / "01_simple"
        
        # Load stocks
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
        
        # Load orders
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
        print(f"❌ Error loading data: {e}")
        return [], []


def analyze_old_approach(stocks, orders):
    """Analyze original approach using FirstFit - workflow step 2a"""
    
    print("\n🔴 ORIGINAL APPROACH ANALYSIS")
    print("=" * 40)
    print("📋 Method: FirstFit algorithm (hardcoded)")
    print("⚙️  Selection: Manual algorithm choice")
    print("🎯 Target: Basic functionality")
    
    # Configure old approach (manual FirstFit)
    config = OptimizationConfig(
        allow_rotation=True,
        prioritize_orders=True,
        cutting_width=3.0
    )
    
    optimizer = Optimizer(config)
    optimizer.set_algorithm(FirstFitAlgorithm())
    
    # Run and time the optimization
    start_time = time.time()
    result = optimizer.optimize(stocks, orders)
    elapsed = time.time() - start_time
    
    print(f"\n📊 OLD APPROACH RESULTS:")
    print(f"   • Efficiency: {result.efficiency_percentage:.1f}%")
    print(f"   • Time: {elapsed:.3f}s")
    print(f"   • Stocks used: {result.total_stock_used}")
    print(f"   • Orders fulfilled: {result.total_orders_fulfilled}")
    print(f"   • Algorithm: FirstFit (hardcoded)")
    
    return result, elapsed


def analyze_new_approach(stocks, orders):
    """Analyze new smart selection approach - workflow step 2b"""
    
    print("\n🟢 NEW APPROACH ANALYSIS")
    print("=" * 30)
    print("📋 Method: Smart algorithm selection")
    print("⚙️  Selection: Automatic based on problem complexity")
    print("🎯 Target: Professional efficiency")
    
    # Use new smart optimization
    start_time = time.time()
    result = optimize(
        stocks, orders, 
        priority='balanced',
        allow_rotation=True,
        prioritize_orders=True,
        cutting_width=3.0
    )
    elapsed = time.time() - start_time
    
    print(f"\n📊 NEW APPROACH RESULTS:")
    print(f"   • Efficiency: {result.efficiency_percentage:.1f}%")
    print(f"   • Time: {elapsed:.3f}s")
    print(f"   • Stocks used: {result.total_stock_used}")
    print(f"   • Orders fulfilled: {result.total_orders_fulfilled}")
    print(f"   • Algorithm: {result.metadata['algorithm_selection']['selected_algorithm']}")
    
    return result, elapsed


def test_priority_modes(stocks, orders):
    """Test all priority modes for comprehensive analysis - workflow step 2c"""
    
    print("\n🎯 PRIORITY MODES ANALYSIS")
    print("=" * 35)
    print("📋 Testing all automatic selection modes")
    
    priorities = ['speed', 'balanced', 'quality', 'maximum']
    results = {}
    
    for priority in priorities:
        print(f"\n🔧 Testing priority: {priority}")
        
        start_time = time.time()
        result = optimize(stocks, orders, priority=priority)
        elapsed = time.time() - start_time
        
        results[priority] = {
            'efficiency': result.efficiency_percentage,
            'time': elapsed,
            'algorithm': result.metadata['algorithm_selection']['selected_algorithm'],
            'stocks_used': result.total_stock_used,
            'orders_fulfilled': result.total_orders_fulfilled
        }
        
        print(f"   ✅ {result.efficiency_percentage:.1f}% in {elapsed:.3f}s ({result.metadata['algorithm_selection']['selected_algorithm']})")
    
    return results


def calculate_theoretical_limits(stocks, orders):
    """Calculate theoretical efficiency limits - workflow step 3"""
    
    print(f"\n🎯 THEORETICAL ANALYSIS")
    print("=" * 30)
    
    total_piece_area = sum(order.total_area for order in orders)
    total_stock_area = sum(stock.area for stock in stocks)
    theoretical_max = (total_piece_area / total_stock_area) * 100
    
    print(f"📏 Total piece area: {total_piece_area:,.0f} mm²")
    print(f"📦 Total stock area: {total_stock_area:,.0f} mm²")
    print(f"🎯 Theoretical maximum: {theoretical_max:.1f}%")
    print(f"💡 Perfect packing (impossible in practice)")
    
    return theoretical_max


def generate_comparison_report(old_result, old_time, new_result, new_time, priority_results, theoretical_max):
    """Generate comprehensive comparison report - workflow step 4"""
    
    print("\n\n📋 COMPREHENSIVE COMPARISON TABLE")
    print("=" * 60)
    
    # Main comparison
    improvement = new_result.efficiency_percentage - old_result.efficiency_percentage
    speed_improvement = old_time / new_time if new_time > 0 else float('inf')
    
    print(f"{'Metric':<25} {'Old Method':<15} {'New Method':<15} {'Improvement':<15}")
    print("-" * 70)
    print(f"{'Efficiency':<25} {old_result.efficiency_percentage:<15.1f}% {new_result.efficiency_percentage:<15.1f}% {improvement:+.1f}%")
    print(f"{'Execution Time':<25} {old_time:<15.3f}s {new_time:<15.3f}s {speed_improvement:.1f}x faster")
    print(f"{'Stocks Used':<25} {old_result.total_stock_used:<15} {new_result.total_stock_used:<15} {new_result.total_stock_used - old_result.total_stock_used:+}")
    print(f"{'Orders Fulfilled':<25} {old_result.total_orders_fulfilled:<15} {new_result.total_orders_fulfilled:<15} {new_result.total_orders_fulfilled - old_result.total_orders_fulfilled:+}")
    
    # Priority modes analysis
    print(f"\n🎯 PRIORITY MODES COMPARISON:")
    print(f"{'Priority':<12} {'Efficiency':<12} {'Time':<10} {'Algorithm':<20}")
    print("-" * 60)
    
    for priority, data in priority_results.items():
        print(f"{priority:<12} {data['efficiency']:<12.1f}% {data['time']:<10.3f}s {data['algorithm'][:18]:<20}")
    
    return improvement, speed_improvement


def save_impact_summary(improvement, speed_improvement, priority_results, theoretical_max):
    """Save impact analysis summary - workflow step 5"""
    
    print(f"\n💾 Saving Impact Analysis")
    print("=" * 25)
    
    # Create results directory
    results_dir = Path(__file__).parent / "data" / "impact_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Find best result
    best_priority = max(priority_results.items(), key=lambda x: x[1]['efficiency'])
    best_efficiency = best_priority[1]['efficiency']
    
    # Create summary
    summary = {
        "impact_analysis": {
            "absolute_improvement": f"{improvement:+.1f}%",
            "relative_improvement": f"{(improvement / 34.2) * 100:+.1f}%",
            "speed_improvement": f"{speed_improvement:.1f}x faster",
            "best_achievable": f"{best_efficiency:.1f}% ('{best_priority[0]}' mode)",
            "theoretical_ceiling": f"{theoretical_max:.1f}%",
            "efficiency_ratio": f"{(best_efficiency/theoretical_max)*100:.1f}% of theoretical maximum"
        },
        "priority_comparison": priority_results
    }
    
    # Save to JSON
    import json
    summary_path = results_dir / "impact_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ impact_summary.json - Complete analysis results")
    print(f"📁 Files saved to: {results_dir}")


def display_final_summary(improvement, speed_improvement, priority_results, theoretical_max):
    """Display final impact summary - workflow step 6"""
    
    print(f"\n\n🎉 IMPACT SUMMARY")
    print("=" * 20)
    
    best_priority = max(priority_results.items(), key=lambda x: x[1]['efficiency'])
    best_efficiency = best_priority[1]['efficiency']
    relative_improvement = (improvement / 34.2) * 100
    
    print(f"✅ Absolute improvement: {improvement:+.1f}%")
    print(f"✅ Relative improvement: {relative_improvement:+.1f}%")
    print(f"✅ Speed improvement: {speed_improvement:.1f}x faster")
    print(f"✅ Best achievable: {best_efficiency:.1f}% ('{best_priority[0]}' mode)")
    print(f"✅ Theoretical ceiling: {theoretical_max:.1f}%")
    print(f"✅ Current efficiency ratio: {(best_efficiency/theoretical_max)*100:.1f}% of theoretical maximum")
    
    # Recommendations
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
    if best_efficiency < theoretical_max * 0.7:
        print("   🔧 Further algorithm improvements recommended")
        print("   🧬 Consider implementing advanced algorithms")
    elif best_efficiency < theoretical_max * 0.85:
        print("   👍 Good efficiency achieved")
        print("   ⚡ Consider parallelization for speed improvements")
    else:
        print("   🌟 Excellent efficiency - near optimal!")
        print("   🚀 Focus on speed optimizations and user experience")


def main():
    """Advanced Demo: Library improvement impact analysis"""
    
    print("🔍 Advanced Demo: Library Improvement Impact Analysis")
    print("=" * 60)
    print("📊 Comprehensive analysis of optimization improvements")
    
    # Step 1: Load test data
    stocks, orders = load_test_data()
    if not stocks or not orders:
        return
    
    # Step 2: Analyze approaches
    old_result, old_time = analyze_old_approach(stocks, orders)
    new_result, new_time = analyze_new_approach(stocks, orders)
    
    # Step 3: Test all priority modes
    priority_results = test_priority_modes(stocks, orders)
    
    # Step 4: Calculate theoretical limits
    theoretical_max = calculate_theoretical_limits(stocks, orders)
    
    # Step 5: Generate comparison report
    improvement, speed_improvement = generate_comparison_report(
        old_result, old_time, new_result, new_time, priority_results, theoretical_max
    )
    
    # Step 6: Save results
    save_impact_summary(improvement, speed_improvement, priority_results, theoretical_max)
    
    # Step 7: Display final summary
    display_final_summary(improvement, speed_improvement, priority_results, theoretical_max)
    
    print("\n✅ Impact analysis completed! Check the generated files.")
    print("\n🚀 Next advanced demos:")
    print("   • hybrid_optimization_demo.py - Multi-algorithm approach")
    print("   • algorithm_comparison_demo.py - Performance benchmarking")


if __name__ == "__main__":
    main() 