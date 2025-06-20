#!/usr/bin/env python3
"""
Surface Cutting Optimizer - Quick Start Demo

Professional 2D cutting optimization library showcasing core functionality.
Demonstrates efficient material utilization across different algorithms.
"""

import time
import matplotlib.pyplot as plt
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


def create_demo_problem():
    """Create a realistic cutting optimization problem"""
    
    # Available stock materials
    stocks = [
        Stock("STEEL_001", 3000, 1500, 5.0, MaterialType.METAL, 245.80),
        Stock("STEEL_002", 3000, 1500, 5.0, MaterialType.METAL, 245.80),
    ]
    
    # Orders to fulfill - mix of rectangular and circular cuts
    orders = [
        Order("BRACKET_A", Rectangle(400, 300), 6, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("BRACKET_B", Rectangle(350, 250), 4, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("CIRCLE_A", Circle(150), 3, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("PANEL_A", Rectangle(800, 600), 2, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("PANEL_B", Rectangle(500, 400), 3, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("SMALL_PARTS", Rectangle(200, 150), 8, Priority.LOW, MaterialType.METAL, 5.0),
    ]
    
    return stocks, orders


def demonstrate_algorithm(name, algorithm, stocks, orders, config):
    """Demonstrate a single algorithm"""
    print(f"  🔧 {name}")
    
    optimizer = Optimizer()
    optimizer.set_algorithm(algorithm)
    
    start_time = time.time()
    result = optimizer.optimize(stocks, orders, config)
    computation_time = time.time() - start_time
    
    print(f"     ⚡ Computation time: {computation_time:.3f}s")
    print(f"     📊 Material efficiency: {result.efficiency_percentage:.1f}%")
    print(f"     ✅ Orders fulfilled: {result.total_orders_fulfilled}/{sum(o.quantity for o in orders)}")
    print(f"     📦 Stocks used: {result.total_stock_used}/{len(stocks)}")
    print(f"     ♻️  Material waste: {result.waste_percentage:.1f}%")
    
    return result


def visualize_results(result, stocks, title="Cutting Plan"):
    """Create visualization of cutting plan"""
    fig, axes = plt.subplots(1, result.total_stock_used, figsize=(5*result.total_stock_used, 4))
    if result.total_stock_used == 1:
        axes = [axes]
    
    # Group placed shapes by stock
    shapes_by_stock = {}
    for shape in result.placed_shapes:
        stock_id = shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(shape)
    
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray']
    
    for i, (stock_id, shapes) in enumerate(shapes_by_stock.items()):
        ax = axes[i] if len(axes) > 1 else axes[0]
        
        # Draw stock boundary
        stock = next(s for s in stocks if s.id == stock_id)
        ax.add_patch(plt.Rectangle((0, 0), stock.width, stock.height, 
                                  linewidth=2, edgecolor='black', facecolor='white'))
        
        # Draw placed shapes
        for j, placed_shape in enumerate(shapes):
            shape = placed_shape.shape
            color = colors[j % len(colors)]
            
            if hasattr(shape, 'width'):  # Rectangle
                rect = plt.Rectangle((shape.x, shape.y), shape.width, shape.height,
                                   linewidth=1, edgecolor='darkblue', facecolor=color, alpha=0.7)
                ax.add_patch(rect)
                # Add label
                ax.text(shape.x + shape.width/2, shape.y + shape.height/2, 
                       placed_shape.order_id, ha='center', va='center', fontsize=8)
            else:  # Circle
                circle = plt.Circle((shape.x, shape.y), shape.radius,
                                  linewidth=1, edgecolor='darkblue', facecolor=color, alpha=0.7)
                ax.add_patch(circle)
                ax.text(shape.x, shape.y, placed_shape.order_id, ha='center', va='center', fontsize=8)
        
        ax.set_xlim(0, stock.width)
        ax.set_ylim(0, stock.height)
        ax.set_aspect('equal')
        ax.set_title(f'Stock {stock_id}\nEfficiency: {result.efficiency_percentage:.1f}%')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save visualization
    output_dir = Path("demo_results")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / f"{title.lower().replace(' ', '_')}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"     📸 Visualization saved: {filename}")
    
    plt.show()
    return filename


def main():
    """Main demonstration function"""
    print("🏭 SURFACE CUTTING OPTIMIZER")
    print("Professional 2D Cutting Optimization Library")
    print("=" * 60)
    
    # Create demonstration problem
    stocks, orders = create_demo_problem()
    
    print(f"\n📋 CUTTING PROBLEM:")
    print(f"   📦 Available stocks: {len(stocks)}")
    for stock in stocks:
        print(f"      - {stock.id}: {stock.width}×{stock.height}mm ({stock.material_type.value})")
    
    total_orders = sum(order.quantity for order in orders)
    print(f"   📋 Total orders: {total_orders} pieces ({len(orders)} types)")
    for order in orders:
        if hasattr(order.shape, 'width'):
            dims = f"{order.shape.width}×{order.shape.height}mm"
        else:
            dims = f"⌀{order.shape.radius*2}mm"
        print(f"      - {order.id}: {order.quantity}× {dims} ({order.priority.name})")
    
    # Calculate total material requirements
    total_order_area = sum(order.shape.area() * order.quantity for order in orders)
    total_stock_area = sum(stock.area for stock in stocks)
    theoretical_efficiency = (total_order_area / total_stock_area) * 100
    
    print(f"\n📊 MATERIAL ANALYSIS:")
    print(f"   📏 Total order area: {total_order_area:,.0f} mm²")
    print(f"   📏 Total stock area: {total_stock_area:,.0f} mm²")
    print(f"   📈 Theoretical max efficiency: {theoretical_efficiency:.1f}%")
    
    # Optimization configuration
    config = OptimizationConfig(
        allow_rotation=True,
        cutting_width=3.0,
        prioritize_orders=True
    )
    
    print(f"\n⚙️  OPTIMIZATION SETTINGS:")
    print(f"   🔄 Rotation allowed: {config.allow_rotation}")
    print(f"   ✂️  Cutting width: {config.cutting_width}mm")
    print(f"   📋 Priority ordering: {config.prioritize_orders}")
    
    # Test different algorithms
    print(f"\n🧠 ALGORITHM COMPARISON:")
    algorithms = [
        ("First Fit (Greedy)", FirstFitAlgorithm()),
        ("Genetic Algorithm", GeneticAlgorithm(population_size=20, generations=15)),
    ]
    
    results = []
    
    for name, algorithm in algorithms:
        result = demonstrate_algorithm(name, algorithm, stocks, orders, config)
        results.append((name, result))
        
        # Visualize the best result
        if result.efficiency_percentage > 70:  # Good result worth visualizing
            visualize_results(result, stocks, f"{name} - Cutting Plan")
    
    # Summary comparison
    print(f"\n📈 ALGORITHM PERFORMANCE SUMMARY:")
    print("   Algorithm               Efficiency   Time      Fulfillment")
    print("   " + "-" * 55)
    
    for name, result in results:
        fulfillment_rate = (result.total_orders_fulfilled / total_orders) * 100
        print(f"   {name:<22} {result.efficiency_percentage:>7.1f}%   {result.computation_time:>6.3f}s   {fulfillment_rate:>8.1f}%")
    
    # Find best result
    best_result = max(results, key=lambda x: x[1].efficiency_percentage)
    best_name, best_opt = best_result
    
    print(f"\n🏆 BEST PERFORMANCE: {best_name}")
    print(f"   📊 Material efficiency: {best_opt.efficiency_percentage:.1f}%")
    print(f"   ♻️  Waste reduction: {100 - best_opt.waste_percentage:.1f}%")
    print(f"   ✅ Order fulfillment: {best_opt.total_orders_fulfilled}/{total_orders} pieces")
    
    if best_opt.unfulfilled_orders:
        print(f"   ⚠️  Unfulfilled orders: {len(best_opt.unfulfilled_orders)}")
        for order in best_opt.unfulfilled_orders[:3]:  # Show first 3
            print(f"      - {order.id} (insufficient material)")
    
    print(f"\n✨ Optimization completed!")
    print(f"📁 Results saved in: demo_results/")
    
    return best_opt


if __name__ == "__main__":
    main() 