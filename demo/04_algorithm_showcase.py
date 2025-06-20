#!/usr/bin/env python3
"""
Algorithm Showcase Demo - Technical Performance Comparison

Demonstrates the technical capabilities and characteristics of each optimization algorithm:
- Performance analysis across different problem complexities
- Algorithm-specific strengths and use cases
- Computational complexity comparison
- Solution quality metrics
"""

import time
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm
from surface_optimizer.algorithms.advanced.hybrid_genetic import HybridGeneticAlgorithm


def create_test_problems():
    """Create different complexity test problems for algorithm evaluation"""
    
    # Standard stock for all tests
    standard_stocks = [
        Stock("SHEET_001", 3000, 1500, 5.0, MaterialType.METAL, 150.0),
        Stock("SHEET_002", 3000, 1500, 5.0, MaterialType.METAL, 150.0),
        Stock("SHEET_003", 3000, 1500, 5.0, MaterialType.METAL, 150.0),
    ]
    
    # Simple problem - few large pieces
    simple_orders = [
        Order("LARGE_A", Rectangle(800, 600), 3, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("LARGE_B", Rectangle(700, 500), 2, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("MEDIUM_A", Rectangle(500, 400), 4, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("MEDIUM_B", Rectangle(400, 300), 3, Priority.MEDIUM, MaterialType.METAL, 5.0),
    ]
    
    # Medium complexity - mixed sizes
    medium_orders = [
        Order("LARGE_RECT", Rectangle(1000, 600), 2, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("MED_RECT_A", Rectangle(600, 400), 4, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("MED_RECT_B", Rectangle(500, 350), 3, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("SMALL_RECT", Rectangle(300, 200), 8, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("CIRCLE_LG", Circle(200), 3, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("CIRCLE_MD", Circle(150), 5, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("CIRCLE_SM", Circle(100), 6, Priority.LOW, MaterialType.METAL, 5.0),
        Order("STRIPS", Rectangle(1200, 80), 4, Priority.LOW, MaterialType.METAL, 5.0),
    ]
    
    # Complex problem - many small pieces with constraints
    complex_orders = [
        Order("MAIN_PANEL", Rectangle(1200, 800), 2, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("SUB_PANEL_A", Rectangle(600, 450), 4, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("SUB_PANEL_B", Rectangle(500, 400), 3, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("BRACKET_L", Rectangle(350, 250), 8, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("BRACKET_M", Rectangle(280, 200), 6, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("BRACKET_S", Rectangle(200, 150), 10, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("CIRCLE_A", Circle(180), 4, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("CIRCLE_B", Circle(120), 6, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("CIRCLE_C", Circle(80), 8, Priority.LOW, MaterialType.METAL, 5.0),
        Order("STRIP_LONG", Rectangle(1500, 60), 3, Priority.LOW, MaterialType.METAL, 5.0),
        Order("STRIP_MED", Rectangle(800, 40), 6, Priority.LOW, MaterialType.METAL, 5.0),
        Order("STRIP_SHORT", Rectangle(400, 30), 10, Priority.LOW, MaterialType.METAL, 5.0),
        Order("SMALL_PARTS", Rectangle(150, 100), 15, Priority.LOW, MaterialType.METAL, 5.0),
        Order("TINY_PARTS", Rectangle(80, 60), 20, Priority.LOW, MaterialType.METAL, 5.0),
    ]
    
    return {
        'Simple': (standard_stocks, simple_orders),
        'Medium': (standard_stocks, medium_orders),
        'Complex': (standard_stocks, complex_orders)
    }


def get_algorithm_configurations():
    """Get all available algorithms with their configurations"""
    
    algorithms = {
        'First Fit': {
            'algorithm': FirstFitAlgorithm(),
            'description': 'Fast greedy placement - first available position',
            'complexity': 'O(n log n)',
            'strengths': ['Very fast execution', 'Low memory usage', 'Predictable results'],
            'best_for': 'Rapid prototyping, real-time applications',
            'color': '#FF6B6B'
        },
        'Best Fit': {
            'algorithm': BestFitAlgorithm(),
            'description': 'Improved placement - best fitting position',
            'complexity': 'O(n²)',
            'strengths': ['Better space utilization', 'Moderate speed', 'Good balance'],
            'best_for': 'General purpose optimization',
            'color': '#4ECDC4'
        },
        'Bottom Left': {
            'algorithm': BottomLeftAlgorithm(),
            'description': 'Compact layout - minimize vertical waste',
            'complexity': 'O(n²)',
            'strengths': ['Compact layouts', 'Reduced vertical waste', 'Good for strips'],
            'best_for': 'Long strips, minimizing height',
            'color': '#45B7D1'
        },
        'Genetic': {
            'algorithm': GeneticAlgorithm(population_size=30, generations=25, mutation_rate=0.1),
            'description': 'Evolutionary optimization - global search',
            'complexity': 'O(generations × population × n²)',
            'strengths': ['High efficiency', 'Global optimization', 'Handles constraints'],
            'best_for': 'Maximum efficiency requirements',
            'color': '#96CEB4'
        },
        'Hybrid Genetic': {
            'algorithm': HybridGeneticAlgorithm(population_size=25, generations=20),
            'description': 'Adaptive evolution - combines multiple strategies',
            'complexity': 'O(adaptive)',
            'strengths': ['Adaptive approach', 'Self-optimizing', 'Robust results'],
            'best_for': 'Complex problems, unknown patterns',
            'color': '#FFEAA7'
        }
    }
    
    return algorithms


def benchmark_algorithm(name, algorithm, stocks, orders, config):
    """Benchmark a single algorithm with detailed metrics"""
    
    optimizer = Optimizer()
    optimizer.set_algorithm(algorithm)
    
    # Measure execution time
    start_time = time.time()
    result = optimizer.optimize(stocks, orders, config)
    execution_time = time.time() - start_time
    
    # Calculate additional metrics
    total_orders = sum(order.quantity for order in orders)
    total_order_area = sum(order.shape.area() * order.quantity for order in orders)
    total_stock_area = sum(stock.area for stock in stocks)
    
    # Performance metrics
    fulfillment_rate = (result.total_orders_fulfilled / total_orders) * 100
    theoretical_max = (total_order_area / total_stock_area) * 100
    efficiency_ratio = result.efficiency_percentage / theoretical_max if theoretical_max > 0 else 0
    
    # Memory and complexity indicators (simplified)
    pieces_per_second = total_orders / execution_time if execution_time > 0 else 0
    
    metrics = {
        'execution_time': execution_time,
        'efficiency_percentage': result.efficiency_percentage,
        'fulfillment_rate': fulfillment_rate,
        'stocks_used': result.total_stock_used,
        'waste_percentage': result.waste_percentage,
        'pieces_fulfilled': result.total_orders_fulfilled,
        'total_pieces': total_orders,
        'efficiency_ratio': efficiency_ratio,
        'pieces_per_second': pieces_per_second,
        'result': result
    }
    
    return metrics


def create_performance_comparison_chart(all_results, algorithms):
    """Create comprehensive performance comparison visualization"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    problems = ['Simple', 'Medium', 'Complex']
    algorithm_names = list(algorithms.keys())
    colors = [algorithms[name]['color'] for name in algorithm_names]
    
    # 1. Execution Time Comparison
    ax = axes[0]
    problem_times = {prob: [] for prob in problems}
    for prob in problems:
        for algo_name in algorithm_names:
            problem_times[prob].append(all_results[prob][algo_name]['execution_time'])
    
    x = np.arange(len(problems))
    width = 0.15
    for i, algo_name in enumerate(algorithm_names):
        times = [problem_times[prob][i] for prob in problems]
        ax.bar(x + i*width, times, width, label=algo_name, color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Problem Complexity')
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title('Algorithm Execution Time Comparison')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(problems)
    ax.legend()
    ax.set_yscale('log')
    
    # 2. Efficiency Comparison
    ax = axes[1]
    problem_efficiencies = {prob: [] for prob in problems}
    for prob in problems:
        for algo_name in algorithm_names:
            problem_efficiencies[prob].append(all_results[prob][algo_name]['efficiency_percentage'])
    
    for i, algo_name in enumerate(algorithm_names):
        efficiencies = [problem_efficiencies[prob][i] for prob in problems]
        ax.bar(x + i*width, efficiencies, width, label=algo_name, color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Problem Complexity')
    ax.set_ylabel('Material Efficiency (%)')
    ax.set_title('Algorithm Efficiency Comparison')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(problems)
    ax.legend()
    
    # 3. Fulfillment Rate
    ax = axes[2]
    problem_fulfillment = {prob: [] for prob in problems}
    for prob in problems:
        for algo_name in algorithm_names:
            problem_fulfillment[prob].append(all_results[prob][algo_name]['fulfillment_rate'])
    
    for i, algo_name in enumerate(algorithm_names):
        fulfillments = [problem_fulfillment[prob][i] for prob in problems]
        ax.bar(x + i*width, fulfillments, width, label=algo_name, color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Problem Complexity')
    ax.set_ylabel('Order Fulfillment (%)')
    ax.set_title('Algorithm Fulfillment Rate')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(problems)
    ax.legend()
    
    # 4. Processing Speed (pieces per second)
    ax = axes[3]
    problem_speed = {prob: [] for prob in problems}
    for prob in problems:
        for algo_name in algorithm_names:
            problem_speed[prob].append(all_results[prob][algo_name]['pieces_per_second'])
    
    for i, algo_name in enumerate(algorithm_names):
        speeds = [problem_speed[prob][i] for prob in problems]
        ax.bar(x + i*width, speeds, width, label=algo_name, color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Problem Complexity')
    ax.set_ylabel('Processing Speed (pieces/second)')
    ax.set_title('Algorithm Processing Speed')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(problems)
    ax.legend()
    ax.set_yscale('log')
    
    # 5. Efficiency vs Speed Trade-off
    ax = axes[4]
    for prob in problems:
        speeds = [all_results[prob][algo_name]['pieces_per_second'] for algo_name in algorithm_names]
        efficiencies = [all_results[prob][algo_name]['efficiency_percentage'] for algo_name in algorithm_names]
        
        scatter = ax.scatter(speeds, efficiencies, s=100, alpha=0.7, label=f'{prob} Problem')
        
        # Add algorithm labels
        for i, algo_name in enumerate(algorithm_names):
            ax.annotate(algo_name[:3], (speeds[i], efficiencies[i]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax.set_xlabel('Processing Speed (pieces/second)')
    ax.set_ylabel('Material Efficiency (%)')
    ax.set_title('Efficiency vs Speed Trade-off')
    ax.legend()
    ax.set_xscale('log')
    
    # 6. Stocks Utilization
    ax = axes[5]
    problem_stocks = {prob: [] for prob in problems}
    for prob in problems:
        for algo_name in algorithm_names:
            problem_stocks[prob].append(all_results[prob][algo_name]['stocks_used'])
    
    for i, algo_name in enumerate(algorithm_names):
        stocks_used = [problem_stocks[prob][i] for prob in problems]
        ax.bar(x + i*width, stocks_used, width, label=algo_name, color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Problem Complexity')
    ax.set_ylabel('Number of Stocks Used')
    ax.set_title('Stock Material Utilization')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(problems)
    ax.legend()
    
    plt.tight_layout()
    
    # Save chart
    output_dir = Path("demo_results")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / "algorithm_performance_comparison.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"📊 Performance comparison chart saved: {filename}")
    
    plt.show()
    return filename


def create_algorithm_summary_table(all_results, algorithms):
    """Create a comprehensive summary table of algorithm performance"""
    
    print(f"\n📊 COMPREHENSIVE ALGORITHM ANALYSIS")
    print("=" * 120)
    
    # Header
    print(f"{'Algorithm':<15} {'Complexity':<25} {'Best Use Case':<35} {'Avg Efficiency':<12} {'Avg Speed':<10}")
    print("-" * 120)
    
    # Calculate averages across all problems
    for algo_name, algo_info in algorithms.items():
        avg_efficiency = np.mean([all_results[prob][algo_name]['efficiency_percentage'] 
                                 for prob in all_results.keys()])
        avg_speed = np.mean([all_results[prob][algo_name]['pieces_per_second'] 
                           for prob in all_results.keys()])
        
        print(f"{algo_name:<15} {algo_info['complexity']:<25} {algo_info['best_for']:<35} "
              f"{avg_efficiency:<11.1f}% {avg_speed:<9.1f}")
    
    print("\n📈 DETAILED PERFORMANCE BY PROBLEM COMPLEXITY")
    print("-" * 120)
    
    for problem_name in ['Simple', 'Medium', 'Complex']:
        print(f"\n🔍 {problem_name.upper()} PROBLEM:")
        print(f"{'Algorithm':<15} {'Time(s)':<8} {'Efficiency':<11} {'Fulfillment':<12} {'Stocks':<7} {'Waste':<7}")
        print("-" * 70)
        
        # Sort by efficiency for this problem
        problem_results = sorted(all_results[problem_name].items(), 
                               key=lambda x: x[1]['efficiency_percentage'], reverse=True)
        
        for algo_name, metrics in problem_results:
            print(f"{algo_name:<15} {metrics['execution_time']:<7.3f} "
                  f"{metrics['efficiency_percentage']:<10.1f}% "
                  f"{metrics['fulfillment_rate']:<11.1f}% "
                  f"{metrics['stocks_used']:<6d} "
                  f"{metrics['waste_percentage']:<6.1f}%")
    
    # Algorithm strengths and recommendations
    print(f"\n🎯 ALGORITHM RECOMMENDATIONS BY SCENARIO")
    print("-" * 120)
    
    scenarios = {
        '⚡ Speed Critical': 'First Fit - Fastest execution for real-time applications',
        '📊 Balanced Performance': 'Best Fit - Good balance of speed and efficiency',
        '🏗️ Compact Layouts': 'Bottom Left - Minimizes vertical waste, good for strips',
        '🎯 Maximum Efficiency': 'Genetic - Highest material utilization, worth the wait',
        '🧠 Complex Problems': 'Hybrid Genetic - Adaptive approach for unknown patterns',
        '💰 Cost Sensitive': 'Genetic/Hybrid - Higher efficiency = lower material costs',
        '🏭 Production Lines': 'Best Fit/Bottom Left - Reliable, moderate computation',
        '🔬 Research/Analysis': 'Genetic/Hybrid - Optimal solutions for comparison'
    }
    
    for scenario, recommendation in scenarios.items():
        print(f"   {scenario:<20}: {recommendation}")


def main():
    """Main algorithm showcase demonstration"""
    print("🧠 ALGORITHM SHOWCASE - TECHNICAL PERFORMANCE ANALYSIS")
    print("Advanced Optimization Algorithms for 2D Cutting Problems")
    print("=" * 80)
    
    # Create test problems
    test_problems = create_test_problems()
    algorithms = get_algorithm_configurations()
    
    print(f"\n🔬 TEST PROBLEMS OVERVIEW:")
    for problem_name, (stocks, orders) in test_problems.items():
        total_orders = sum(order.quantity for order in orders)
        total_area = sum(order.shape.area() * order.quantity for order in orders)
        print(f"   {problem_name:<8}: {total_orders:>3d} pieces, {len(orders):>2d} types, "
              f"{total_area/1_000_000:>5.2f} m² area")
    
    print(f"\n🧬 ALGORITHMS TO EVALUATE:")
    for algo_name, algo_info in algorithms.items():
        print(f"   {algo_name:<15}: {algo_info['description']}")
        print(f"   {' '*15}  Complexity: {algo_info['complexity']}")
        print(f"   {' '*15}  Best for: {algo_info['best_for']}")
    
    # Standard configuration for fair comparison
    standard_config = OptimizationConfig(
        allow_rotation=True,
        cutting_width=3.0,
        prioritize_orders=True,
        max_computation_time=120
    )
    
    print(f"\n⚙️  BENCHMARK CONFIGURATION:")
    print(f"   🔄 Rotation: {standard_config.allow_rotation}")
    print(f"   ✂️  Cutting width: {standard_config.cutting_width}mm")
    print(f"   📋 Prioritization: {standard_config.prioritize_orders}")
    print(f"   ⏱️  Max time: {standard_config.max_computation_time}s")
    
    # Run comprehensive benchmarks
    print(f"\n🚀 RUNNING COMPREHENSIVE BENCHMARKS...")
    print("=" * 80)
    
    all_results = {}
    
    for problem_name, (stocks, orders) in test_problems.items():
        print(f"\n📋 {problem_name.upper()} PROBLEM BENCHMARK:")
        all_results[problem_name] = {}
        
        for algo_name, algo_info in algorithms.items():
            print(f"   🔧 Testing {algo_name}...", end=' ')
            
            try:
                metrics = benchmark_algorithm(
                    algo_name, algo_info['algorithm'], stocks, orders, standard_config
                )
                all_results[problem_name][algo_name] = metrics
                
                print(f"✅ {metrics['efficiency_percentage']:.1f}% efficiency, "
                      f"{metrics['execution_time']:.3f}s")
                
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
                # Use default metrics for failed tests
                all_results[problem_name][algo_name] = {
                    'execution_time': float('inf'),
                    'efficiency_percentage': 0.0,
                    'fulfillment_rate': 0.0,
                    'stocks_used': 0,
                    'waste_percentage': 100.0,
                    'pieces_fulfilled': 0,
                    'total_pieces': sum(order.quantity for order in orders),
                    'efficiency_ratio': 0.0,
                    'pieces_per_second': 0.0
                }
    
    # Create comprehensive analysis
    create_algorithm_summary_table(all_results, algorithms)
    create_performance_comparison_chart(all_results, algorithms)
    
    # Find best algorithm for each metric
    print(f"\n🏆 BEST PERFORMERS BY METRIC:")
    print("-" * 50)
    
    metrics_to_analyze = [
        ('efficiency_percentage', 'Material Efficiency', 'max', '%'),
        ('execution_time', 'Speed (lowest time)', 'min', 's'),
        ('fulfillment_rate', 'Order Fulfillment', 'max', '%'),
        ('pieces_per_second', 'Processing Speed', 'max', '/s')
    ]
    
    for metric, description, direction, unit in metrics_to_analyze:
        best_algos = []
        for problem_name in test_problems.keys():
            if direction == 'max':
                best_algo = max(all_results[problem_name].items(), 
                              key=lambda x: x[1][metric])
            else:
                best_algo = min(all_results[problem_name].items(), 
                              key=lambda x: x[1][metric])
            best_algos.append((problem_name, best_algo[0], best_algo[1][metric]))
        
        print(f"\n   🎯 {description}:")
        for problem, algo, value in best_algos:
            print(f"      {problem:<8}: {algo:<15} ({value:.3f}{unit})")
    
    print(f"\n✨ Algorithm showcase completed!")
    print(f"📁 Analysis results saved in: demo_results/")
    print(f"\n💡 KEY INSIGHTS:")
    print(f"   • First Fit: Best for speed-critical applications")
    print(f"   • Best Fit: Excellent balance for general use")
    print(f"   • Bottom Left: Superior for compact layouts")
    print(f"   • Genetic: Maximum efficiency for material optimization")
    print(f"   • Hybrid Genetic: Best adaptability for complex problems")


if __name__ == "__main__":
    main() 