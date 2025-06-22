#!/usr/bin/env python3
"""
Advanced Demo: Hybrid Multi-Algorithm Optimization
==================================================

🎯 Shows the hybrid optimizer that runs multiple algorithms concurrently

Key concepts:
• Multi-algorithm concurrent execution
• Intelligent result selection
• Performance score calculation
• Best-of-breed optimization

Quick start for: Maximum efficiency optimization, complex problems, professional results
"""

import pandas as pd
import time
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer import optimize


def load_complex_test_data():
    """Load more complex test data to showcase hybrid benefits - workflow step 1"""
    
    print("📂 Loading Complex Test Data")
    print("-" * 30)
    
    try:
        # Load from multi-stock demo data (more complex)
        data_path = Path(__file__).parent.parent / "data" / "02_multi"
        
        # Load stocks
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
        
        # Load orders
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
        
        print(f"✅ Loaded {len(stocks)} stock panels, {len(orders)} orders")
        print(f"📊 Problem complexity: {sum(order.quantity for order in orders)} total pieces")
        return stocks, orders
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("💡 Falling back to simple data...")
        
        # Fallback to simple data
        data_path = Path(__file__).parent.parent / "data" / "01_simple"
        
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
        
        print(f"✅ Loaded {len(stocks)} stock panels, {len(orders)} orders (fallback)")
        return stocks, orders


def run_single_algorithm_test(stocks, orders, algorithm_name):
    """Run a single algorithm for comparison - workflow step 2a"""
    
    print(f"\n🔧 Testing: {algorithm_name}")
    print("-" * 25)
    
    start_time = time.time()
    
    try:
        result = optimize(
            stocks, orders,
            algorithm=algorithm_name,
            allow_rotation=True,
            prioritize_orders=True,
            cutting_width=3.0,
            max_computation_time=30.0  # 30 second limit
        )
        elapsed = time.time() - start_time
        
        print(f"✅ {algorithm_name}: {result.efficiency_percentage:.1f}% in {elapsed:.3f}s")
        
        return {
            'algorithm': algorithm_name,
            'efficiency': result.efficiency_percentage,
            'time': elapsed,
            'stocks_used': result.total_stock_used,
            'orders_fulfilled': result.total_orders_fulfilled,
            'pieces_placed': len(result.placed_shapes),
            'success': True
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {algorithm_name}: Failed in {elapsed:.3f}s - {e}")
        
        return {
            'algorithm': algorithm_name,
            'efficiency': 0.0,
            'time': elapsed,
            'error': str(e),
            'success': False
        }


def run_individual_algorithms(stocks, orders):
    """Run individual algorithms for comparison - workflow step 2b"""
    
    print("\n⚖️ INDIVIDUAL ALGORITHM TESTING")
    print("=" * 40)
    print("📋 Testing each algorithm individually for comparison")
    
    algorithms = ['best_fit', 'first_fit', 'bottom_left', 'genetic']
    results = {}
    
    for algorithm in algorithms:
        result = run_single_algorithm_test(stocks, orders, algorithm)
        results[algorithm] = result
    
    return results


def run_hybrid_optimization(stocks, orders):
    """Run hybrid optimizer - workflow step 3"""
    
    print("\n🚀 HYBRID MULTI-ALGORITHM OPTIMIZATION")
    print("=" * 45)
    print("📋 Running multiple algorithms concurrently and selecting best result")
    
    start_time = time.time()
    
    try:
        # Use hybrid optimizer through manual selection
        result = optimize(
            stocks, orders,
            algorithm='hybrid',
            allow_rotation=True,
            prioritize_orders=True,
            cutting_width=3.0,
            max_computation_time=60.0  # More time for hybrid approach
        )
        elapsed = time.time() - start_time
        
        print(f"✅ Hybrid optimization completed in {elapsed:.3f}s")
        
        # Extract hybrid metadata
        hybrid_meta = result.metadata.get('hybrid_analysis', {})
        
        print(f"\n📊 HYBRID OPTIMIZER RESULTS:")
        print(f"   • Final efficiency: {result.efficiency_percentage:.1f}%")
        print(f"   • Total time: {elapsed:.3f}s")
        print(f"   • Algorithms tested: {hybrid_meta.get('algorithms_tested', 'unknown')}")
        print(f"   • Best algorithm: {hybrid_meta.get('best_algorithm', 'unknown')}")
        print(f"   • Stocks used: {result.total_stock_used}")
        print(f"   • Orders fulfilled: {result.total_orders_fulfilled}")
        
        return {
            'efficiency': result.efficiency_percentage,
            'time': elapsed,
            'stocks_used': result.total_stock_used,
            'orders_fulfilled': result.total_orders_fulfilled,
            'pieces_placed': len(result.placed_shapes),
            'best_algorithm': hybrid_meta.get('best_algorithm', 'unknown'),
            'algorithms_tested': hybrid_meta.get('algorithms_tested', 0),
            'metadata': hybrid_meta,
            'success': True
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Hybrid optimization failed in {elapsed:.3f}s - {e}")
        
        return {
            'efficiency': 0.0,
            'time': elapsed,
            'error': str(e),
            'success': False
        }


def analyze_hybrid_performance(individual_results, hybrid_result):
    """Analyze hybrid vs individual performance - workflow step 4"""
    
    print("\n📊 PERFORMANCE ANALYSIS")
    print("=" * 30)
    
    if not hybrid_result['success']:
        print("❌ Hybrid optimization failed - cannot perform analysis")
        return
    
    # Find best individual algorithm
    successful_individual = {k: v for k, v in individual_results.items() if v['success']}
    
    if not successful_individual:
        print("❌ No individual algorithms succeeded - cannot compare")
        return
    
    best_individual = max(successful_individual.values(), key=lambda x: x['efficiency'])
    
    print(f"🏆 Best individual algorithm: {best_individual['algorithm']}")
    print(f"   • Efficiency: {best_individual['efficiency']:.1f}%")
    print(f"   • Time: {best_individual['time']:.3f}s")
    
    print(f"\n🚀 Hybrid optimizer:")
    print(f"   • Efficiency: {hybrid_result['efficiency']:.1f}%")
    print(f"   • Time: {hybrid_result['time']:.3f}s")
    print(f"   • Best algorithm selected: {hybrid_result['best_algorithm']}")
    
    # Calculate improvements
    efficiency_improvement = hybrid_result['efficiency'] - best_individual['efficiency']
    time_ratio = hybrid_result['time'] / best_individual['time'] if best_individual['time'] > 0 else float('inf')
    
    print(f"\n📈 HYBRID ADVANTAGE:")
    print(f"   • Efficiency improvement: {efficiency_improvement:+.1f}%")
    if efficiency_improvement > 0:
        print(f"   • Relative improvement: {(efficiency_improvement/best_individual['efficiency'])*100:+.1f}%")
    print(f"   • Time multiplier: {time_ratio:.1f}x")
    
    return efficiency_improvement, time_ratio


def generate_detailed_comparison(individual_results, hybrid_result):
    """Generate detailed comparison table - workflow step 5"""
    
    print("\n\n📋 DETAILED ALGORITHM COMPARISON")
    print("=" * 50)
    
    print(f"{'Algorithm':<15} {'Efficiency':<12} {'Time':<8} {'Success':<8} {'Note':<20}")
    print("-" * 70)
    
    # Individual algorithms
    for alg_name, result in individual_results.items():
        if result['success']:
            note = "✅ Success"
            print(f"{alg_name:<15} {result['efficiency']:<12.1f}% {result['time']:<8.3f}s {result['success']:<8} {note:<20}")
        else:
            note = "❌ Failed"
            print(f"{alg_name:<15} {'N/A':<12} {result['time']:<8.3f}s {result['success']:<8} {note:<20}")
    
    # Hybrid optimizer
    if hybrid_result['success']:
        note = f"Best: {hybrid_result['best_algorithm']}"
        print(f"{'hybrid':<15} {hybrid_result['efficiency']:<12.1f}% {hybrid_result['time']:<8.3f}s {hybrid_result['success']:<8} {note:<20}")
    else:
        note = "❌ Failed"
        print(f"{'hybrid':<15} {'N/A':<12} {hybrid_result['time']:<8.3f}s {hybrid_result['success']:<8} {note:<20}")


def save_hybrid_analysis(individual_results, hybrid_result, efficiency_improvement, time_ratio):
    """Save hybrid analysis results - workflow step 6"""
    
    print(f"\n💾 Saving Hybrid Analysis")
    print("=" * 25)
    
    # Create results directory
    results_dir = Path(__file__).parent / "data" / "hybrid_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Create comprehensive analysis
    analysis = {
        "hybrid_optimization_analysis": {
            "hybrid_result": hybrid_result,
            "individual_results": individual_results,
            "performance_comparison": {
                "efficiency_improvement": f"{efficiency_improvement:+.1f}%" if efficiency_improvement else "N/A",
                "time_multiplier": f"{time_ratio:.1f}x" if time_ratio else "N/A",
                "best_individual": max([r for r in individual_results.values() if r['success']], 
                                     key=lambda x: x['efficiency'], default={'algorithm': 'none'})['algorithm']
            }
        }
    }
    
    # Save to JSON
    import json
    analysis_path = results_dir / "hybrid_analysis.json"
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ hybrid_analysis.json - Complete hybrid analysis")
    print(f"📁 Files saved to: {results_dir}")


def display_hybrid_summary(individual_results, hybrid_result):
    """Display final hybrid optimization summary - workflow step 7"""
    
    print(f"\n\n🎉 HYBRID OPTIMIZATION SUMMARY")
    print("=" * 35)
    
    if not hybrid_result['success']:
        print("❌ Hybrid optimization was not successful")
        print("💡 Try with simpler problems or check algorithm implementations")
        return
    
    successful_count = sum(1 for r in individual_results.values() if r['success'])
    total_algorithms = len(individual_results)
    
    print(f"✅ Hybrid optimization successful!")
    print(f"✅ Tested {total_algorithms} algorithms ({successful_count} successful)")
    print(f"✅ Selected best algorithm: {hybrid_result['best_algorithm']}")
    print(f"✅ Final efficiency: {hybrid_result['efficiency']:.1f}%")
    print(f"✅ Total execution time: {hybrid_result['time']:.3f}s")
    
    # Get hybrid metadata if available
    if 'metadata' in hybrid_result and hybrid_result['metadata']:
        meta = hybrid_result['metadata']
        if 'results_summary' in meta:
            print(f"\n🏆 Top performing algorithms:")
            for i, summary in enumerate(meta['results_summary'][:3], 1):
                print(f"   {i}. {summary['algorithm']}: {summary['efficiency']:.1f}% in {summary['time']:.3f}s")
    
    print(f"\n💡 HYBRID OPTIMIZER BENEFITS:")
    print("   🚀 Automatic best-algorithm selection")
    print("   ⚡ Parallel execution for speed")
    print("   🎯 Consistent high-quality results")
    print("   🔧 No manual algorithm tuning required")


def main():
    """Advanced Demo: Hybrid multi-algorithm optimization"""
    
    print("🚀 Advanced Demo: Hybrid Multi-Algorithm Optimization")
    print("=" * 60)
    print("📊 Demonstrating concurrent multi-algorithm optimization")
    
    # Step 1: Load complex test data
    stocks, orders = load_complex_test_data()
    if not stocks or not orders:
        return
    
    # Step 2: Run individual algorithms for comparison
    individual_results = run_individual_algorithms(stocks, orders)
    
    # Step 3: Run hybrid optimization
    hybrid_result = run_hybrid_optimization(stocks, orders)
    
    # Step 4: Analyze performance
    efficiency_improvement, time_ratio = analyze_hybrid_performance(individual_results, hybrid_result) or (None, None)
    
    # Step 5: Generate detailed comparison
    generate_detailed_comparison(individual_results, hybrid_result)
    
    # Step 6: Save analysis
    save_hybrid_analysis(individual_results, hybrid_result, efficiency_improvement, time_ratio)
    
    # Step 7: Display summary
    display_hybrid_summary(individual_results, hybrid_result)
    
    print("\n✅ Hybrid optimization demo completed! Check the generated files.")
    print("\n🚀 Next advanced demos:")
    print("   • algorithm_comparison_demo.py - Performance benchmarking")
    print("   • scalability_analysis_demo.py - Large-scale optimization")


if __name__ == "__main__":
    main() 