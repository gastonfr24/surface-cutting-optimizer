#!/usr/bin/env python3
"""
Metal Fabrication Demo - Industrial Cutting Optimization

Demonstrates advanced features for metal fabrication:
- Different cutting methods (plasma, laser, waterjet)
- Thermal expansion considerations
- Cutting path optimization
- Material-specific constraints
"""

import time
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


def create_metal_fabrication_job():
    """Create a realistic metal fabrication cutting problem"""
    
    # Different metal sheets with varying properties
    stocks = [
        # Mild steel sheets
        Stock("STEEL_MS_001", 3000, 1500, 5.0, MaterialType.METAL, 145.80),
        Stock("STEEL_MS_002", 3000, 1500, 5.0, MaterialType.METAL, 145.80),
        
        # Stainless steel sheet (more expensive)
        Stock("STEEL_SS_001", 3000, 1500, 3.0, MaterialType.METAL, 285.40),
        
        # Aluminum sheet (different cutting requirements)
        Stock("ALUM_001", 3000, 1500, 4.0, MaterialType.METAL, 195.20),
    ]
    
    # HVAC ductwork and fabrication components
    orders = [
        # Main ductwork sections (rectangular)
        Order("DUCT_MAIN_A", Rectangle(800, 600), 4, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("DUCT_MAIN_B", Rectangle(600, 400), 6, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("DUCT_BRANCH", Rectangle(400, 300), 8, Priority.HIGH, MaterialType.METAL, 5.0),
        
        # Transition pieces
        Order("TRANSITION_LG", Rectangle(800, 500), 3, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("TRANSITION_SM", Rectangle(500, 300), 4, Priority.MEDIUM, MaterialType.METAL, 5.0),
        
        # Circular ductwork (requires different cutting)
        Order("ROUND_DUCT_16", Circle(200), 6, Priority.HIGH, MaterialType.METAL, 5.0),  # 16" diameter
        Order("ROUND_DUCT_12", Circle(150), 8, Priority.HIGH, MaterialType.METAL, 5.0),  # 12" diameter
        Order("ROUND_DUCT_8", Circle(100), 12, Priority.MEDIUM, MaterialType.METAL, 5.0), # 8" diameter
        
        # Support brackets and fittings
        Order("BRACKET_L", Rectangle(300, 200), 12, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("BRACKET_T", Rectangle(250, 150), 8, Priority.MEDIUM, MaterialType.METAL, 5.0),
        Order("FLANGE_LG", Rectangle(220, 220), 6, Priority.HIGH, MaterialType.METAL, 5.0),
        Order("FLANGE_SM", Rectangle(160, 160), 10, Priority.MEDIUM, MaterialType.METAL, 5.0),
        
        # Small components
        Order("STIFFENER", Rectangle(500, 50), 16, Priority.LOW, MaterialType.METAL, 5.0),
        Order("CLIP", Rectangle(80, 60), 24, Priority.LOW, MaterialType.METAL, 5.0),
    ]
    
    return stocks, orders


def create_cutting_method_configs():
    """Create different configurations for various cutting methods"""
    
    # Plasma cutting configuration
    plasma_config = OptimizationConfig(
        allow_rotation=True,
        cutting_width=4.5,                    # Plasma kerf width
        thermal_expansion_factor=0.0012,      # Steel thermal expansion
        optimize_cutting_path=True,           # Minimize torch travel
        material_waste_factor=0.04,           # 4% waste for thermal effects
        max_computation_time=90,
        prioritize_orders=True
    )
    
    # Laser cutting configuration  
    laser_config = OptimizationConfig(
        allow_rotation=True,
        cutting_width=0.3,                    # Precise laser kerf
        thermal_expansion_factor=0.0005,      # Minimal thermal effects
        optimize_cutting_path=True,           # Precise path optimization
        material_waste_factor=0.02,           # Minimal waste
        max_computation_time=120,
        prioritize_orders=True
    )
    
    # Waterjet cutting configuration
    waterjet_config = OptimizationConfig(
        allow_rotation=True,
        cutting_width=1.2,                    # Waterjet kerf
        thermal_expansion_factor=0.0,         # No thermal effects
        optimize_cutting_path=True,           # Minimize cutting time
        material_waste_factor=0.015,          # Very low waste
        max_computation_time=150,
        prioritize_orders=True
    )
    
    return {
        'Plasma': plasma_config,
        'Laser': laser_config, 
        'Waterjet': waterjet_config
    }


def analyze_cutting_efficiency(result, stocks, cutting_method):
    """Analyze cutting efficiency specific to metal fabrication"""
    
    print(f"\n🔥 {cutting_method.upper()} CUTTING ANALYSIS:")
    
    # Group shapes by type
    rectangular_pieces = []
    circular_pieces = []
    
    for shape in result.placed_shapes:
        if hasattr(shape.shape, 'width'):
            rectangular_pieces.append(shape)
        else:
            circular_pieces.append(shape)
    
    print(f"   📐 Rectangular pieces: {len(rectangular_pieces)}")
    print(f"   ⭕ Circular pieces: {len(circular_pieces)}")
    
    # Calculate cutting path estimate
    total_cutting_length = 0
    for shape in result.placed_shapes:
        if hasattr(shape.shape, 'width'):  # Rectangle
            perimeter = 2 * (shape.shape.width + shape.shape.height)
        else:  # Circle
            perimeter = 2 * np.pi * shape.shape.radius
        total_cutting_length += perimeter
    
    print(f"   ✂️  Total cutting length: {total_cutting_length/1000:.1f} meters")
    
    # Estimate cutting time based on method
    cutting_speeds = {
        'Plasma': 2000,      # mm/min for 5mm steel
        'Laser': 800,        # mm/min for 5mm steel
        'Waterjet': 300      # mm/min for 5mm steel
    }
    
    if cutting_method in cutting_speeds:
        cutting_time = total_cutting_length / cutting_speeds[cutting_method]
        print(f"   ⏱️  Estimated cutting time: {cutting_time:.1f} minutes")
    
    # Material utilization by sheet
    shapes_by_stock = {}
    for shape in result.placed_shapes:
        stock_id = shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(shape)
    
    print(f"   📊 Sheet utilization:")
    for stock_id, shapes in shapes_by_stock.items():
        stock = next(s for s in stocks if s.id == stock_id)
        sheet_area = stock.area
        used_area = sum(shape.shape.area() for shape in shapes)
        efficiency = (used_area / sheet_area) * 100
        material_type = "MS" if "MS" in stock_id else "SS" if "SS" in stock_id else "AL"
        print(f"      - {material_type} {stock_id}: {efficiency:.1f}% ({len(shapes)} pieces)")


def calculate_fabrication_costs(result, stocks, cutting_method):
    """Calculate complete fabrication costs including material and processing"""
    
    print(f"\n💰 FABRICATION COST ANALYSIS ({cutting_method}):")
    
    # Material costs
    used_stocks = set(shape.stock_id for shape in result.placed_shapes)
    total_material_cost = sum(stock.cost_per_unit for stock in stocks if stock.id in used_stocks)
    
    # Cutting costs per method (cost per minute)
    cutting_costs_per_min = {
        'Plasma': 3.50,      # €/min
        'Laser': 8.20,       # €/min  
        'Waterjet': 12.80    # €/min
    }
    
    # Calculate cutting time
    total_cutting_length = 0
    for shape in result.placed_shapes:
        if hasattr(shape.shape, 'width'):
            perimeter = 2 * (shape.shape.width + shape.shape.height)
        else:
            perimeter = 2 * np.pi * shape.shape.radius
        total_cutting_length += perimeter
    
    cutting_speeds = {'Plasma': 2000, 'Laser': 800, 'Waterjet': 300}
    cutting_time = total_cutting_length / cutting_speeds.get(cutting_method, 1000)
    cutting_cost = cutting_time * cutting_costs_per_min.get(cutting_method, 5.0)
    
    # Setup and programming costs
    setup_cost = 45.0  # Fixed setup cost
    
    total_cost = total_material_cost + cutting_cost + setup_cost
    
    print(f"   🏭 Material cost: €{total_material_cost:.2f}")
    print(f"   ✂️  Cutting cost: €{cutting_cost:.2f} ({cutting_time:.1f} min)")
    print(f"   ⚙️  Setup cost: €{setup_cost:.2f}")
    print(f"   💳 Total cost: €{total_cost:.2f}")
    
    # Cost per piece
    total_pieces = len(result.placed_shapes)
    cost_per_piece = total_cost / total_pieces if total_pieces > 0 else 0
    print(f"   📊 Cost per piece: €{cost_per_piece:.2f}")
    
    # Waste cost
    waste_cost = total_material_cost * (result.waste_percentage / 100)
    print(f"   ♻️  Material waste cost: €{waste_cost:.2f}")


def visualize_metal_cutting_layout(result, stocks, cutting_method, title="Metal Cutting Layout"):
    """Create detailed visualization for metal fabrication"""
    
    used_stocks = set(shape.stock_id for shape in result.placed_shapes)
    num_sheets = len(used_stocks)
    
    fig, axes = plt.subplots(1, num_sheets, figsize=(6*num_sheets, 8))
    if num_sheets == 1:
        axes = [axes]
    
    # Group shapes by stock
    shapes_by_stock = {}
    for shape in result.placed_shapes:
        stock_id = shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(shape)
    
    # Color scheme for metal components
    component_colors = {
        'DUCT': '#4682B4',         # Steel blue
        'TRANSITION': '#5F9EA0',   # Cadet blue
        'ROUND': '#87CEEB',        # Sky blue
        'BRACKET': '#708090',      # Slate gray
        'FLANGE': '#2F4F4F',       # Dark slate gray
        'STIFFENER': '#B0C4DE',    # Light steel blue
        'CLIP': '#D3D3D3'          # Light gray
    }
    
    # Cutting method colors
    kerf_colors = {
        'Plasma': '#FF6347',       # Tomato (hot)
        'Laser': '#00FF00',        # Lime (precise)
        'Waterjet': '#00BFFF'      # Deep sky blue (cold)
    }
    
    sheet_idx = 0
    for stock_id in sorted(used_stocks):
        if stock_id in shapes_by_stock:
            ax = axes[sheet_idx] if num_sheets > 1 else axes[0]
            
            # Draw sheet boundary with material indication
            stock = next(s for s in stocks if s.id == stock_id)
            
            # Material-specific background colors
            if 'MS' in stock_id:
                bg_color = '#F5F5DC'  # Beige for mild steel
            elif 'SS' in stock_id:
                bg_color = '#F8F8FF'  # Ghost white for stainless
            else:
                bg_color = '#F0F8FF'  # Alice blue for aluminum
            
            ax.add_patch(plt.Rectangle((0, 0), stock.width, stock.height, 
                                      linewidth=3, edgecolor='#2F4F4F', facecolor=bg_color, alpha=0.3))
            
            # Draw placed shapes with cutting indicators
            for placed_shape in shapes_by_stock[stock_id]:
                shape = placed_shape.shape
                order_id = placed_shape.order_id
                
                # Determine color based on component type
                color = '#DDD'  # Default
                for comp_type, comp_color in component_colors.items():
                    if comp_type in order_id:
                        color = comp_color
                        break
                
                if hasattr(shape, 'width'):  # Rectangle
                    # Draw main shape
                    rect = plt.Rectangle((shape.x, shape.y), shape.width, shape.height,
                                       linewidth=2, edgecolor=kerf_colors.get(cutting_method, '#000'), 
                                       facecolor=color, alpha=0.7)
                    ax.add_patch(rect)
                    
                    # Add cutting path indicators (simplified)
                    if cutting_method == 'Plasma':
                        # Show pierce points
                        ax.plot(shape.x + 10, shape.y + 10, 'ro', markersize=4)
                    
                    # Add component label
                    ax.text(shape.x + shape.width/2, shape.y + shape.height/2, 
                           order_id.replace('_', '\n'), ha='center', va='center', 
                           fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
                    
                else:  # Circle
                    # Draw main shape
                    circle = plt.Circle((shape.x, shape.y), shape.radius,
                                      linewidth=2, edgecolor=kerf_colors.get(cutting_method, '#000'),
                                      facecolor=color, alpha=0.7)
                    ax.add_patch(circle)
                    
                    # Add cutting start point
                    if cutting_method in ['Plasma', 'Laser']:
                        start_x = shape.x + shape.radius
                        start_y = shape.y
                        ax.plot(start_x, start_y, 'go', markersize=4)
                    
                    # Add label
                    ax.text(shape.x, shape.y, order_id.replace('_', '\n'), 
                           ha='center', va='center', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
                
                # Add dimensions for larger pieces
                if hasattr(shape, 'width') and (shape.width > 300 or shape.height > 300):
                    dim_text = f"{shape.width:.0f}×{shape.height:.0f}"
                    ax.text(shape.x + 5, shape.y + shape.height - 15, dim_text, 
                           fontsize=7, color='white', fontweight='bold')
                elif hasattr(shape, 'radius') and shape.radius > 100:
                    dim_text = f"⌀{shape.radius*2:.0f}"
                    ax.text(shape.x, shape.y - shape.radius - 20, dim_text, 
                           fontsize=7, ha='center', fontweight='bold')
            
            # Sheet info
            sheet_area = stock.area
            used_area = sum(shape.shape.area() for shape in shapes_by_stock[stock_id])
            efficiency = (used_area / sheet_area) * 100
            
            # Material type indicator
            material_type = "Mild Steel" if "MS" in stock_id else "Stainless Steel" if "SS" in stock_id else "Aluminum"
            
            ax.set_xlim(0, stock.width)
            ax.set_ylim(0, stock.height)
            ax.set_aspect('equal')
            ax.set_title(f'{material_type}\n{stock_id}\nEfficiency: {efficiency:.1f}%\n{len(shapes_by_stock[stock_id])} pieces')
            ax.grid(True, alpha=0.3, color='gray')
            
            # Add cutting method indicator
            method_color = kerf_colors.get(cutting_method, '#000')
            ax.text(stock.width - 100, 50, f'{cutting_method}\nCutting', 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=method_color, alpha=0.7, edgecolor='black'))
            
            sheet_idx += 1
    
    plt.suptitle(f'{title} - {cutting_method} Cutting\nTotal Efficiency: {result.efficiency_percentage:.1f}%', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save visualization
    output_dir = Path("demo_results")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / f"metal_{cutting_method.lower()}_{title.lower().replace(' ', '_')}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"   📸 Cutting plan saved: {filename}")
    
    plt.show()
    return filename


def main():
    """Main metal fabrication demonstration"""
    print("🔥 METAL FABRICATION OPTIMIZATION")
    print("Advanced Sheet Metal Cutting for HVAC Systems")
    print("=" * 65)
    
    # Create metal fabrication job
    stocks, orders = create_metal_fabrication_job()
    cutting_configs = create_cutting_method_configs()
    
    print(f"\n📋 FABRICATION ORDER:")
    print(f"   🛠️  Metal sheets available: {len(stocks)}")
    for stock in stocks:
        material_type = "Mild Steel" if "MS" in stock.id else "Stainless Steel" if "SS" in stock.id else "Aluminum"
        print(f"      - {material_type}: {stock.width}×{stock.height}×{stock.thickness}mm (€{stock.cost_per_unit:.2f})")
    
    total_components = sum(order.quantity for order in orders)
    print(f"   🔧 Components to cut: {total_components} pieces ({len(orders)} types)")
    
    # Calculate material requirements
    total_component_area = sum(order.shape.area() * order.quantity for order in orders)
    total_stock_area = sum(stock.area for stock in stocks)
    
    print(f"\n📊 MATERIAL ANALYSIS:")
    print(f"   📏 Component area needed: {total_component_area/1_000_000:.2f} m²")
    print(f"   📏 Sheet area available: {total_stock_area/1_000_000:.2f} m²")
    print(f"   📈 Theoretical utilization: {(total_component_area/total_stock_area)*100:.1f}%")
    
    # Test different cutting methods
    print(f"\n🔥 CUTTING METHOD COMPARISON:")
    
    results = []
    
    for method_name, config in cutting_configs.items():
        print(f"\n  🔧 {method_name} Cutting:")
        print(f"     ✂️  Kerf width: {config.cutting_width}mm")
        print(f"     🌡️  Thermal factor: {config.thermal_expansion_factor}")
        print(f"     ♻️  Waste factor: {config.material_waste_factor*100:.1f}%")
        
        # Use appropriate algorithm for cutting method
        if method_name == 'Plasma':
            algorithm = BottomLeftAlgorithm()  # Good for path optimization
        else:
            algorithm = GeneticAlgorithm(population_size=25, generations=20)  # Precision methods
        
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, config)
        computation_time = time.time() - start_time
        
        print(f"     ⚡ Computation time: {computation_time:.3f}s")
        print(f"     📊 Material efficiency: {result.efficiency_percentage:.1f}%")
        print(f"     ✅ Components cut: {result.total_orders_fulfilled}/{total_components}")
        print(f"     📦 Sheets used: {result.total_stock_used}/{len(stocks)}")
        
        results.append((method_name, result, config))
    
    # Select best result for detailed analysis
    best_result = max(results, key=lambda x: x[1].efficiency_percentage)
    best_method, best_opt, best_config = best_result
    
    print(f"\n🏆 OPTIMAL CUTTING METHOD: {best_method}")
    
    # Detailed analysis
    analyze_cutting_efficiency(best_opt, stocks, best_method)
    calculate_fabrication_costs(best_opt, stocks, best_method)
    
    # Create visualization
    visualize_metal_cutting_layout(best_opt, stocks, best_method, "HVAC Fabrication")
    
    # Method comparison summary
    print(f"\n📈 CUTTING METHOD COMPARISON SUMMARY:")
    print("   Method      Efficiency   Sheets   Cost/Min   Best For")
    print("   " + "-" * 60)
    
    for method_name, result, config in results:
        cutting_costs = {'Plasma': 3.50, 'Laser': 8.20, 'Waterjet': 12.80}
        cost_rate = cutting_costs.get(method_name, 5.0)
        best_use = {
            'Plasma': 'Thick steel, fast cuts',
            'Laser': 'Precision, thin materials', 
            'Waterjet': 'No heat affected zone'
        }
        print(f"   {method_name:<10} {result.efficiency_percentage:>8.1f}%   {result.total_stock_used:>5d}    €{cost_rate:>5.2f}    {best_use.get(method_name, 'General')}")
    
    # Production summary
    print(f"\n📋 PRODUCTION SUMMARY:")
    print(f"   🏭 Ready for cutting: {best_opt.total_orders_fulfilled}/{total_components} components")
    print(f"   🔥 Recommended method: {best_method}")
    print(f"   📊 Material efficiency: {best_opt.efficiency_percentage:.1f}%")
    print(f"   📦 Sheets required: {best_opt.total_stock_used}/{len(stocks)}")
    
    if best_opt.unfulfilled_orders:
        print(f"   ⚠️  Additional material needed: {len(best_opt.unfulfilled_orders)} components")
    
    print(f"\n✨ Metal fabrication optimization completed!")
    print(f"📁 Cutting plans saved in: demo_results/")


if __name__ == "__main__":
    main() 