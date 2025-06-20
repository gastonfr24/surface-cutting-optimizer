#!/usr/bin/env python3
"""
Furniture Manufacturing Demo - Wood Panel Optimization

Demonstrates advanced features for furniture manufacturing:
- Wood grain direction consideration
- Edge banding allowances 
- Nested component optimization
- Waste minimization for expensive materials
"""

import time
import matplotlib.pyplot as plt
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


def create_furniture_cutting_job():
    """Create a realistic furniture manufacturing cutting problem"""
    
    # Premium wood panels - expensive material, minimize waste
    stocks = [
        Stock("OAK_PANEL_001", 2800, 2070, 18.0, MaterialType.WOOD, 285.50),
        Stock("OAK_PANEL_002", 2800, 2070, 18.0, MaterialType.WOOD, 285.50),
        Stock("OAK_PANEL_003", 2800, 2070, 18.0, MaterialType.WOOD, 285.50),
    ]
    
    # Kitchen cabinet components with varying priorities
    orders = [
        # Main cabinet bodies (high priority)
        Order("CABINET_SIDE_L", Rectangle(720, 580), 8, Priority.HIGH, MaterialType.WOOD, 18.0),
        Order("CABINET_SIDE_R", Rectangle(720, 580), 8, Priority.HIGH, MaterialType.WOOD, 18.0),
        Order("CABINET_TOP", Rectangle(600, 580), 4, Priority.HIGH, MaterialType.WOOD, 18.0),
        Order("CABINET_BOTTOM", Rectangle(600, 580), 4, Priority.HIGH, MaterialType.WOOD, 18.0),
        Order("CABINET_BACK", Rectangle(600, 720), 4, Priority.HIGH, MaterialType.WOOD, 18.0),
        
        # Doors (high priority, visible surfaces)
        Order("DOOR_PANEL_LARGE", Rectangle(450, 720), 4, Priority.HIGH, MaterialType.WOOD, 18.0),
        Order("DOOR_PANEL_SMALL", Rectangle(300, 720), 2, Priority.HIGH, MaterialType.WOOD, 18.0),
        
        # Shelves (medium priority)
        Order("SHELF_FIXED", Rectangle(580, 350), 6, Priority.MEDIUM, MaterialType.WOOD, 18.0),
        Order("SHELF_ADJUSTABLE", Rectangle(580, 320), 8, Priority.MEDIUM, MaterialType.WOOD, 18.0),
        
        # Drawer components (medium priority)
        Order("DRAWER_FRONT", Rectangle(580, 120), 4, Priority.MEDIUM, MaterialType.WOOD, 18.0),
        Order("DRAWER_SIDE", Rectangle(350, 120), 8, Priority.MEDIUM, MaterialType.WOOD, 18.0),
        Order("DRAWER_BACK", Rectangle(580, 90), 4, Priority.MEDIUM, MaterialType.WOOD, 18.0),
        
        # Small components (lower priority)
        Order("RAIL_STILE", Rectangle(800, 80), 6, Priority.LOW, MaterialType.WOOD, 18.0),
        Order("FILLER_STRIP", Rectangle(50, 720), 4, Priority.LOW, MaterialType.WOOD, 18.0),
    ]
    
    return stocks, orders


def create_furniture_config():
    """Create furniture-specific optimization configuration"""
    return OptimizationConfig(
        allow_rotation=True,
        cutting_width=3.2,              # Table saw kerf
        edge_banding_allowance=2.0,     # Additional material for edge banding
        respect_grain_direction=True,   # Critical for wood appearance
        minimize_crosscuts=True,        # Reduce tear-out on veneer
        prioritize_orders=True,         # Complete high-priority items first
        material_waste_factor=0.03,     # 3% waste factor for wood
        max_computation_time=60
    )


def analyze_wood_grain_optimization(result, stocks):
    """Analyze how grain direction affects the layout"""
    print(f"\n🪵 WOOD GRAIN ANALYSIS:")
    
    total_pieces = len(result.placed_shapes)
    rotated_pieces = sum(1 for shape in result.placed_shapes 
                        if hasattr(shape.shape, 'rotation') and shape.shape.rotation != 0)
    
    grain_efficiency = ((total_pieces - rotated_pieces) / total_pieces) * 100
    
    print(f"   📏 Total pieces placed: {total_pieces}")
    print(f"   🔄 Pieces requiring rotation: {rotated_pieces}")
    print(f"   🪵 Grain alignment efficiency: {grain_efficiency:.1f}%")
    
    # Group by stock to analyze individual panel utilization
    shapes_by_stock = {}
    for shape in result.placed_shapes:
        stock_id = shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(shape)
    
    print(f"   📦 Panel utilization:")
    for stock_id, shapes in shapes_by_stock.items():
        stock = next(s for s in stocks if s.id == stock_id)
        panel_area = stock.area
        used_area = sum(shape.shape.area() for shape in shapes)
        efficiency = (used_area / panel_area) * 100
        print(f"      - {stock_id}: {efficiency:.1f}% ({len(shapes)} pieces)")


def calculate_material_costs(result, stocks):
    """Calculate material costs and waste for furniture production"""
    print(f"\n💰 MATERIAL COST ANALYSIS:")
    
    total_stock_cost = 0
    total_stock_area = 0
    total_used_area = 0
    
    # Group shapes by stock
    shapes_by_stock = {}
    for shape in result.placed_shapes:
        stock_id = shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(shape)
    
    used_stocks = set(shape.stock_id for shape in result.placed_shapes)
    
    for stock in stocks:
        if stock.id in used_stocks:
            total_stock_cost += stock.cost_per_unit
            total_stock_area += stock.area
            
            if stock.id in shapes_by_stock:
                stock_used_area = sum(shape.shape.area() for shape in shapes_by_stock[stock.id])
                total_used_area += stock_used_area
    
    waste_area = total_stock_area - total_used_area
    waste_cost = (waste_area / total_stock_area) * total_stock_cost
    material_cost_per_sqm = total_stock_cost / (total_stock_area / 1_000_000)  # Convert to m²
    
    print(f"   💳 Material cost per m²: €{material_cost_per_sqm:.2f}")
    print(f"   📦 Total panels used: {len(used_stocks)}")
    print(f"   💰 Total material cost: €{total_stock_cost:.2f}")
    print(f"   📏 Total area purchased: {total_stock_area/1_000_000:.2f} m²")
    print(f"   ✅ Total area utilized: {total_used_area/1_000_000:.2f} m²")
    print(f"   ♻️  Waste area: {waste_area/1_000_000:.2f} m² (€{waste_cost:.2f})")
    print(f"   📈 Cost efficiency: {((total_stock_cost - waste_cost)/total_stock_cost)*100:.1f}%")


def visualize_furniture_layout(result, stocks, title="Furniture Panel Layout"):
    """Create detailed visualization for furniture manufacturing"""
    used_stocks = set(shape.stock_id for shape in result.placed_shapes)
    num_panels = len(used_stocks)
    
    fig, axes = plt.subplots(1, num_panels, figsize=(6*num_panels, 8))
    if num_panels == 1:
        axes = [axes]
    
    # Group shapes by stock
    shapes_by_stock = {}
    for shape in result.placed_shapes:
        stock_id = shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(shape)
    
    # Color scheme for furniture components
    component_colors = {
        'CABINET': '#8B4513',      # Saddle brown
        'DOOR': '#A0522D',         # Sienna  
        'SHELF': '#CD853F',        # Peru
        'DRAWER': '#D2691E',       # Chocolate
        'RAIL': '#DEB887',         # Burlywood
        'FILLER': '#F4A460'        # Sandy brown
    }
    
    panel_idx = 0
    for stock_id in sorted(used_stocks):
        if stock_id in shapes_by_stock:
            ax = axes[panel_idx] if num_panels > 1 else axes[0]
            
            # Draw panel boundary
            stock = next(s for s in stocks if s.id == stock_id)
            ax.add_patch(plt.Rectangle((0, 0), stock.width, stock.height, 
                                      linewidth=3, edgecolor='#654321', facecolor='#F5DEB3', alpha=0.3))
            
            # Draw placed components
            for placed_shape in shapes_by_stock[stock_id]:
                shape = placed_shape.shape
                order_id = placed_shape.order_id
                
                # Determine color based on component type
                color = '#DDD'  # Default
                for comp_type, comp_color in component_colors.items():
                    if comp_type in order_id:
                        color = comp_color
                        break
                
                # Draw rectangle with wood grain pattern (simplified)
                rect = plt.Rectangle((shape.x, shape.y), shape.width, shape.height,
                                   linewidth=2, edgecolor='#8B4513', facecolor=color, alpha=0.8)
                ax.add_patch(rect)
                
                # Add component label
                label_x = shape.x + shape.width/2
                label_y = shape.y + shape.height/2
                
                # Rotate text if component is rotated
                rotation = 0
                if hasattr(shape, 'rotation') and shape.rotation != 0:
                    rotation = 90
                    label_text = f"{order_id}\n↻"  # Rotation indicator
                else:
                    label_text = order_id
                
                ax.text(label_x, label_y, label_text, ha='center', va='center', 
                       fontsize=8, fontweight='bold', rotation=rotation,
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
                
                # Add dimensions for larger pieces
                if shape.width > 300 or shape.height > 300:
                    dim_text = f"{shape.width:.0f}×{shape.height:.0f}"
                    ax.text(shape.x + 5, shape.y + shape.height - 15, dim_text, 
                           fontsize=7, color='white', fontweight='bold')
            
            # Panel efficiency
            panel_area = stock.area
            used_area = sum(shape.shape.area() for shape in shapes_by_stock[stock_id])
            efficiency = (used_area / panel_area) * 100
            
            ax.set_xlim(0, stock.width)
            ax.set_ylim(0, stock.height)
            ax.set_aspect('equal')
            ax.set_title(f'{stock_id}\nEfficiency: {efficiency:.1f}%\n{len(shapes_by_stock[stock_id])} components')
            ax.grid(True, alpha=0.3, color='#8B4513')
            
            # Add wood grain direction indicator
            ax.arrow(50, 50, 100, 0, head_width=20, head_length=20, fc='#654321', ec='#654321')
            ax.text(100, 80, 'Grain →', fontsize=8, ha='center', color='#654321', fontweight='bold')
            
            panel_idx += 1
    
    plt.suptitle(f'{title}\nTotal Efficiency: {result.efficiency_percentage:.1f}%', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save visualization
    output_dir = Path("demo_results")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / f"furniture_{title.lower().replace(' ', '_')}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"   📸 Panel layout saved: {filename}")
    
    plt.show()
    return filename


def main():
    """Main furniture manufacturing demonstration"""
    print("🪑 FURNITURE MANUFACTURING OPTIMIZATION")
    print("Advanced Wood Panel Cutting for Kitchen Cabinets")
    print("=" * 65)
    
    # Create furniture cutting job
    stocks, orders = create_furniture_cutting_job()
    config = create_furniture_config()
    
    print(f"\n📋 PRODUCTION ORDER:")
    print(f"   🪵 Oak panels available: {len(stocks)} (2800×2070×18mm)")
    total_panel_cost = sum(stock.cost_per_unit for stock in stocks)
    print(f"   💰 Material value: €{total_panel_cost:.2f}")
    
    total_components = sum(order.quantity for order in orders)
    print(f"   🔧 Components to cut: {total_components} pieces ({len(orders)} types)")
    
    # Calculate total component area
    total_component_area = sum(order.shape.area() * order.quantity for order in orders)
    total_stock_area = sum(stock.area for stock in stocks)
    material_utilization = (total_component_area / total_stock_area) * 100
    
    print(f"\n📊 MATERIAL REQUIREMENTS:")
    print(f"   📏 Component area needed: {total_component_area/1_000_000:.2f} m²")
    print(f"   📏 Panel area available: {total_stock_area/1_000_000:.2f} m²")
    print(f"   📈 Theoretical utilization: {material_utilization:.1f}%")
    
    print(f"\n⚙️  FURNITURE OPTIMIZATION SETTINGS:")
    print(f"   🪵 Respect grain direction: {config.respect_grain_direction}")
    print(f"   🔄 Allow rotation: {config.allow_rotation}")
    print(f"   ✂️  Saw kerf: {config.cutting_width}mm")
    print(f"   📏 Edge banding allowance: {config.edge_banding_allowance}mm")
    print(f"   📋 Priority-based: {config.prioritize_orders}")
    
    # Test different algorithms for furniture production
    print(f"\n🧠 ALGORITHM COMPARISON FOR FURNITURE:")
    
    algorithms = [
        ("Best Fit (Balanced)", BestFitAlgorithm()),
        ("Genetic (Premium)", GeneticAlgorithm(population_size=30, generations=25)),
    ]
    
    results = []
    
    for name, algorithm in algorithms:
        print(f"  🔧 {name}")
        
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, config)
        computation_time = time.time() - start_time
        
        print(f"     ⚡ Computation time: {computation_time:.3f}s")
        print(f"     📊 Material efficiency: {result.efficiency_percentage:.1f}%")
        print(f"     ✅ Components cut: {result.total_orders_fulfilled}/{total_components}")
        print(f"     📦 Panels used: {result.total_stock_used}/{len(stocks)}")
        print(f"     ♻️  Material waste: {result.waste_percentage:.1f}%")
        
        results.append((name, result))
    
    # Select best result for detailed analysis
    best_result = max(results, key=lambda x: x[1].efficiency_percentage)
    best_name, best_opt = best_result
    
    print(f"\n🏆 OPTIMAL SOLUTION: {best_name}")
    
    # Detailed analysis
    analyze_wood_grain_optimization(best_opt, stocks)
    calculate_material_costs(best_opt, stocks)
    
    # Create visualization
    visualize_furniture_layout(best_opt, stocks, "Kitchen Cabinet Production")
    
    # Production summary
    print(f"\n📋 PRODUCTION SUMMARY:")
    total_waste_cost = sum(stock.cost_per_unit for stock in stocks[:best_opt.total_stock_used]) * (best_opt.waste_percentage / 100)
    print(f"   🏭 Ready for production: {best_opt.total_orders_fulfilled}/{total_components} components")
    print(f"   💰 Material cost: €{sum(stock.cost_per_unit for stock in stocks[:best_opt.total_stock_used]):.2f}")
    print(f"   ♻️  Waste cost: €{total_waste_cost:.2f}")
    print(f"   📈 Cost efficiency: {100 - best_opt.waste_percentage:.1f}%")
    
    if best_opt.unfulfilled_orders:
        print(f"   ⚠️  Requires additional panels: {len(best_opt.unfulfilled_orders)} components")
    
    print(f"\n✨ Kitchen cabinet optimization completed!")
    print(f"📁 Production files saved in: demo_results/")


if __name__ == "__main__":
    main() 