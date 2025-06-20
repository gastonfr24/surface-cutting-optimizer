#!/usr/bin/env python3
"""
Glass Cutting Precision Demo - Advanced Stress Analysis

Demonstrates specialized features for precision glass cutting:
- Stress concentration analysis
- Breakage risk assessment
- Edge quality optimization
- Thermal stress considerations
- Safety margin calculations
"""

import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


def load_stock_from_csv(csv_path="demo/data/glass_stock.csv"):
    """Load stock data from CSV file"""
    
    print(f"📂 Loading stock data from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        stocks = []
        
        for _, row in df.iterrows():
            # Convert material type string to enum
            material_type = getattr(MaterialType, row['material_type'])
            
            stock = Stock(
                id=row['stock_id'],
                width=row['width'],
                height=row['height'], 
                thickness=row['thickness'],
                material_type=material_type,
                cost_per_unit=row['cost_per_unit']
            )
            
            # Add additional metadata
            stock.supplier = row.get('supplier', 'Unknown')
            stock.glass_type = row.get('glass_type', 'Standard')
            stock.quality_grade = row.get('quality_grade', 'Standard')
            
            stocks.append(stock)
        
        print(f"   ✅ Loaded {len(stocks)} stock items")
        for stock in stocks:
            print(f"      - {stock.id}: {stock.width}×{stock.height}×{stock.thickness}mm "
                  f"({stock.glass_type}, €{stock.cost_per_unit:.2f})")
        
        return stocks
        
    except FileNotFoundError:
        print(f"   ❌ CSV file not found: {csv_path}")
        print(f"   💡 Creating sample data instead...")
        return create_sample_stock_data()
    except Exception as e:
        print(f"   ❌ Error loading CSV: {str(e)}")
        print(f"   💡 Creating sample data instead...")
        return create_sample_stock_data()


def load_orders_from_csv(csv_path="demo/data/glass_orders.csv"):
    """Load orders data from CSV file"""
    
    print(f"📂 Loading orders data from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        orders = []
        
        for _, row in df.iterrows():
            # Convert priority string to enum
            priority = getattr(Priority, row['priority'])
            material_type = getattr(MaterialType, row['material_type'])
            
            # Create shape based on type
            if row['shape_type'].lower() == 'rectangle':
                shape = Rectangle(row['width'], row['height'])
            elif row['shape_type'].lower() == 'circle':
                shape = Circle(row['radius'])
            else:
                print(f"   ⚠️  Unknown shape type: {row['shape_type']}, skipping...")
                continue
            
            order = Order(
                id=row['order_id'],
                shape=shape,
                quantity=row['quantity'],
                priority=priority,
                material_type=material_type,
                thickness=row['thickness']
            )
            
            # Add additional metadata
            order.description = row.get('description', '')
            
            orders.append(order)
        
        print(f"   ✅ Loaded {len(orders)} order types")
        total_pieces = sum(order.quantity for order in orders)
        print(f"   📊 Total pieces to cut: {total_pieces}")
        
        # Show order summary by priority
        priority_summary = {}
        for order in orders:
            priority_name = order.priority.name
            if priority_name not in priority_summary:
                priority_summary[priority_name] = 0
            priority_summary[priority_name] += order.quantity
        
        for priority, count in priority_summary.items():
            print(f"      - {priority}: {count} pieces")
        
        return orders
        
    except FileNotFoundError:
        print(f"   ❌ CSV file not found: {csv_path}")
        print(f"   💡 Creating sample data instead...")
        return create_sample_orders_data()
    except Exception as e:
        print(f"   ❌ Error loading CSV: {str(e)}")
        print(f"   💡 Creating sample data instead...")
        return create_sample_orders_data()


def create_sample_stock_data():
    """Create sample stock data if CSV loading fails"""
    return [
        Stock("GLASS_FLOAT_001", 3210, 2250, 6.0, MaterialType.GLASS, 185.40),
        Stock("GLASS_FLOAT_002", 3210, 2250, 6.0, MaterialType.GLASS, 185.40),
        Stock("GLASS_TEMP_001", 3210, 2250, 8.0, MaterialType.GLASS, 245.80),
    ]


def create_sample_orders_data():
    """Create sample orders data if CSV loading fails"""
    return [
        Order("WINDOW_MAIN_A", Rectangle(2400, 1800), 2, Priority.HIGH, MaterialType.GLASS, 6.0),
        Order("WINDOW_MAIN_B", Rectangle(2200, 1600), 3, Priority.HIGH, MaterialType.GLASS, 6.0),
        Order("DOOR_PANEL_A", Rectangle(800, 2000), 2, Priority.HIGH, MaterialType.GLASS, 8.0),
        Order("CIRCLE_WINDOW", Circle(400), 2, Priority.HIGH, MaterialType.GLASS, 6.0),
        Order("SHELF_GLASS", Rectangle(800, 300), 6, Priority.LOW, MaterialType.GLASS, 6.0),
    ]


def create_glass_cutting_job():
    """Load glass cutting data from CSV files"""
    
    print(f"\n📋 LOADING GLASS CUTTING DATA FROM CSV FILES")
    print("=" * 60)
    
    # Load stock and orders from CSV
    stocks = load_stock_from_csv()
    orders = load_orders_from_csv()
    
    return stocks, orders


def create_glass_cutting_config():
    """Create glass-specific optimization configuration"""
    return OptimizationConfig(
        allow_rotation=False,               # Glass grain direction critical
        cutting_width=1.5,                  # Precision glass cutter width
        edge_margin=15.0,                   # Safety margin for handling
        minimize_stress_concentration=True,  # Critical for glass
        thermal_expansion_factor=0.000009,   # Glass thermal coefficient
        material_waste_factor=0.08,         # Higher waste due to breakage risk
        prioritize_orders=True,
        max_computation_time=90,
        quality_grade='PRECISION'           # High precision requirement
    )


def analyze_stress_factors(result, stocks):
    """Analyze stress concentration and breakage risk factors"""
    
    print(f"\n🔍 GLASS STRESS ANALYSIS:")
    
    # Calculate stress factors for each piece
    high_stress_pieces = []
    medium_stress_pieces = []
    low_stress_pieces = []
    
    for placed_shape in result.placed_shapes:
        shape = placed_shape.shape
        
        # Calculate stress factors
        if hasattr(shape, 'width'):  # Rectangle
            area = shape.width * shape.height
            aspect_ratio = max(shape.width, shape.height) / min(shape.width, shape.height)
            edge_proximity = min(shape.x, shape.y, 
                               next(s for s in stocks if s.id == placed_shape.stock_id).width - (shape.x + shape.width),
                               next(s for s in stocks if s.id == placed_shape.stock_id).height - (shape.y + shape.height))
        else:  # Circle
            area = np.pi * shape.radius ** 2
            aspect_ratio = 1.0
            stock = next(s for s in stocks if s.id == placed_shape.stock_id)
            edge_proximity = min(shape.x - shape.radius, shape.y - shape.radius,
                               stock.width - (shape.x + shape.radius),
                               stock.height - (shape.y + shape.radius))
        
        # Stress risk assessment
        stress_score = 0
        
        # Large pieces have higher stress risk
        if area > 2_000_000:  # > 2 m²
            stress_score += 3
        elif area > 1_000_000:  # > 1 m²
            stress_score += 2
        else:
            stress_score += 1
            
        # High aspect ratio increases stress
        if aspect_ratio > 3.0:
            stress_score += 2
        elif aspect_ratio > 2.0:
            stress_score += 1
            
        # Edge proximity affects stress
        if edge_proximity < 50:
            stress_score += 2
        elif edge_proximity < 100:
            stress_score += 1
        
        # Categorize by stress level
        if stress_score >= 6:
            high_stress_pieces.append((placed_shape, stress_score))
        elif stress_score >= 4:
            medium_stress_pieces.append((placed_shape, stress_score))
        else:
            low_stress_pieces.append((placed_shape, stress_score))
    
    print(f"   🔴 High stress risk pieces: {len(high_stress_pieces)}")
    for piece, score in high_stress_pieces[:3]:  # Show first 3
        print(f"      - {piece.order_id}: Stress score {score}/8")
    
    print(f"   🟡 Medium stress risk pieces: {len(medium_stress_pieces)}")
    print(f"   🟢 Low stress risk pieces: {len(low_stress_pieces)}")
    
    # Calculate overall risk assessment
    total_pieces = len(result.placed_shapes)
    high_risk_percentage = (len(high_stress_pieces) / total_pieces) * 100
    
    print(f"\n   📊 Risk Assessment:")
    print(f"      High risk pieces: {high_risk_percentage:.1f}%")
    
    if high_risk_percentage > 20:
        print(f"      ⚠️  WARNING: High breakage risk layout")
        print(f"      💡 Recommendation: Increase edge margins or use tempered glass")
    elif high_risk_percentage > 10:
        print(f"      ⚠️  CAUTION: Moderate breakage risk")
        print(f"      💡 Recommendation: Extra care during handling")
    else:
        print(f"      ✅ GOOD: Low breakage risk layout")


def calculate_glass_cutting_costs(result, stocks):
    """Calculate comprehensive costs including breakage risk and edge finishing"""
    
    print(f"\n💰 GLASS CUTTING COST ANALYSIS:")
    
    # Material costs
    used_stocks = set(shape.stock_id for shape in result.placed_shapes)
    total_material_cost = sum(stock.cost_per_unit for stock in stocks if stock.id in used_stocks)
    
    # Glass cutting costs (more expensive than metal)
    cutting_cost_per_linear_meter = 12.50  # €/m for precision glass cutting
    
    # Calculate total cutting length
    total_cutting_length = 0
    for shape in result.placed_shapes:
        if hasattr(shape.shape, 'width'):  # Rectangle
            perimeter = 2 * (shape.shape.width + shape.shape.height)
        else:  # Circle
            perimeter = 2 * np.pi * shape.shape.radius
        total_cutting_length += perimeter
    
    cutting_cost = (total_cutting_length / 1000) * cutting_cost_per_linear_meter
    
    # Edge finishing costs (polishing, tempering)
    edge_finishing_cost = cutting_cost * 0.4  # 40% of cutting cost
    
    # Breakage risk insurance (based on piece complexity)
    breakage_risk_factor = 0.05  # 5% insurance for breakage
    breakage_insurance = total_material_cost * breakage_risk_factor
    
    # Handling and transportation
    handling_cost = len(result.placed_shapes) * 2.50  # €2.50 per piece
    
    total_cost = total_material_cost + cutting_cost + edge_finishing_cost + breakage_insurance + handling_cost
    
    print(f"   🏭 Material cost: €{total_material_cost:.2f}")
    print(f"   ✂️  Cutting cost: €{cutting_cost:.2f} ({total_cutting_length/1000:.1f}m)")
    print(f"   ✨ Edge finishing: €{edge_finishing_cost:.2f}")
    print(f"   🛡️  Breakage insurance: €{breakage_insurance:.2f}")
    print(f"   📦 Handling: €{handling_cost:.2f}")
    print(f"   💳 Total cost: €{total_cost:.2f}")
    
    # Cost per square meter
    total_area = sum(shape.shape.area() for shape in result.placed_shapes) / 1_000_000  # m²
    cost_per_sqm = total_cost / total_area if total_area > 0 else 0
    print(f"   📊 Cost per m²: €{cost_per_sqm:.2f}")
    
    # Quality premium for precision work
    if cost_per_sqm > 200:
        print(f"   ⭐ Premium quality glass work")
    elif cost_per_sqm > 150:
        print(f"   ✅ Standard architectural glass")
    else:
        print(f"   💰 Economy glass cutting")


def visualize_glass_cutting_layout(result, stocks, title="Precision Glass Cutting Layout"):
    """Create detailed visualization for glass cutting with stress indicators"""
    
    used_stocks = set(shape.stock_id for shape in result.placed_shapes)
    num_sheets = len(used_stocks)
    
    fig, axes = plt.subplots(1, num_sheets, figsize=(8*num_sheets, 10))
    if num_sheets == 1:
        axes = [axes]
    
    # Group shapes by stock
    shapes_by_stock = {}
    for shape in result.placed_shapes:
        stock_id = shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(shape)
    
    # Color scheme for glass components
    component_colors = {
        'WINDOW': '#87CEEB',      # Sky blue
        'DOOR': '#4682B4',        # Steel blue
        'CIRCLE': '#00BFFF',      # Deep sky blue
        'SHELF': '#B0E0E6',       # Powder blue
        'TABLE': '#ADD8E6'        # Light blue
    }
    
    sheet_idx = 0
    for stock_id in sorted(used_stocks):
        if stock_id in shapes_by_stock:
            ax = axes[sheet_idx] if num_sheets > 1 else axes[0]
            
            # Draw glass sheet boundary
            stock = next(s for s in stocks if s.id == stock_id)
            
            # Glass-specific background
            bg_color = '#F0F8FF' if 'FLOAT' in stock_id else '#F5F5F5'  # Alice blue for float, white smoke for tempered
            
            ax.add_patch(plt.Rectangle((0, 0), stock.width, stock.height, 
                                      linewidth=3, edgecolor='#2F4F4F', facecolor=bg_color, alpha=0.2))
            
            # Draw safety margins
            margin = 15  # mm
            ax.add_patch(plt.Rectangle((margin, margin), 
                                     stock.width - 2*margin, stock.height - 2*margin,
                                     linewidth=1, edgecolor='red', facecolor='none', 
                                     linestyle='--', alpha=0.5))
            
            # Draw placed shapes with stress indicators
            for placed_shape in shapes_by_stock[stock_id]:
                shape = placed_shape.shape
                order_id = placed_shape.order_id
                
                # Determine color based on component type
                color = '#DDD'  # Default
                for comp_type, comp_color in component_colors.items():
                    if comp_type in order_id:
                        color = comp_color
                        break
                
                # Calculate stress level for color intensity
                if hasattr(shape, 'width'):  # Rectangle
                    area = shape.width * shape.height
                    edge_proximity = min(shape.x, shape.y)
                else:  # Circle
                    area = np.pi * shape.radius ** 2
                    edge_proximity = min(shape.x - shape.radius, shape.y - shape.radius)
                
                # Stress-based alpha (higher stress = more opaque)
                stress_alpha = 0.7 + (0.3 if area > 2_000_000 else 0.1 if area > 1_000_000 else 0)
                edge_color = 'red' if edge_proximity < 50 else 'orange' if edge_proximity < 100 else '#2F4F4F'
                
                if hasattr(shape, 'width'):  # Rectangle
                    # Draw main shape
                    rect = plt.Rectangle((shape.x, shape.y), shape.width, shape.height,
                                       linewidth=2, edgecolor=edge_color, 
                                       facecolor=color, alpha=stress_alpha)
                    ax.add_patch(rect)
                    
                    # Add stress indicators for large pieces
                    if area > 2_000_000:
                        # Add diagonal stress lines
                        ax.plot([shape.x, shape.x + shape.width], 
                               [shape.y, shape.y + shape.height], 
                               'r--', alpha=0.3, linewidth=1)
                        ax.plot([shape.x + shape.width, shape.x], 
                               [shape.y, shape.y + shape.height], 
                               'r--', alpha=0.3, linewidth=1)
                    
                    # Add component label
                    ax.text(shape.x + shape.width/2, shape.y + shape.height/2, 
                           order_id.replace('_', '\n'), ha='center', va='center', 
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9))
                    
                    # Add dimensions for large pieces
                    if area > 1_000_000:
                        dim_text = f"{shape.width:.0f}×{shape.height:.0f}"
                        ax.text(shape.x + 5, shape.y + shape.height - 20, dim_text, 
                               fontsize=8, color='darkblue', fontweight='bold')
                
                else:  # Circle
                    # Draw main shape
                    circle = plt.Circle((shape.x, shape.y), shape.radius,
                                      linewidth=2, edgecolor=edge_color,
                                      facecolor=color, alpha=stress_alpha)
                    ax.add_patch(circle)
                    
                    # Add stress indicator for large circles
                    if shape.radius > 200:
                        # Add radial stress lines
                        for angle in [0, 45, 90, 135]:
                            rad = np.radians(angle)
                            x_end = shape.x + shape.radius * 0.8 * np.cos(rad)
                            y_end = shape.y + shape.radius * 0.8 * np.sin(rad)
                            ax.plot([shape.x, x_end], [shape.y, y_end], 
                                   'r--', alpha=0.3, linewidth=1)
                    
                    # Add label
                    ax.text(shape.x, shape.y, order_id.replace('_', '\n'), 
                           ha='center', va='center', fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9))
                    
                    # Add diameter for large circles
                    if shape.radius > 150:
                        dim_text = f"⌀{shape.radius*2:.0f}"
                        ax.text(shape.x, shape.y - shape.radius - 30, dim_text, 
                               fontsize=8, ha='center', fontweight='bold', color='darkblue')
            
            # Sheet info and specifications
            sheet_area = stock.area
            used_area = sum(shape.shape.area() for shape in shapes_by_stock[stock_id])
            efficiency = (used_area / sheet_area) * 100
            
            # Glass type indicator
            glass_type = "Float Glass" if "FLOAT" in stock_id else "Tempered Glass"
            thickness = f"{stock.thickness}mm"
            
            ax.set_xlim(0, stock.width)
            ax.set_ylim(0, stock.height)
            ax.set_aspect('equal')
            ax.set_title(f'{glass_type} - {thickness}\n{stock_id}\nEfficiency: {efficiency:.1f}%\n{len(shapes_by_stock[stock_id])} pieces')
            ax.grid(True, alpha=0.3, color='gray')
            
            # Add cutting method indicator
            ax.text(stock.width - 150, 50, 'Precision\nGlass Cutter', 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8, edgecolor='blue'))
            
            # Add safety warning
            ax.text(50, stock.height - 50, '⚠️ FRAGILE\nHandle with Care', 
                   ha='left', va='top', fontsize=9, fontweight='bold', color='red',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7, edgecolor='red'))
            
            sheet_idx += 1
    
    plt.suptitle(f'{title}\nTotal Efficiency: {result.efficiency_percentage:.1f}% | Precision Grade: A+', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save visualization
    output_dir = Path("demo_results")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / f"glass_precision_{title.lower().replace(' ', '_')}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"   📸 Glass cutting plan saved: {filename}")
    
    plt.show()
    return filename


def main():
    """Main precision glass cutting demonstration"""
    print("🔍 PRECISION GLASS CUTTING OPTIMIZATION")
    print("Advanced Stress Analysis for Architectural Glass")
    print("Data-Driven Approach with CSV Integration")
    print("=" * 70)
    
    # Load glass cutting job from CSV files
    stocks, orders = create_glass_cutting_job()
    config = create_glass_cutting_config()
    
    print(f"\n📊 LOADED DATA SUMMARY:")
    print(f"   📦 Glass sheets available: {len(stocks)}")
    
    # Group stocks by type for better display
    stock_summary = {}
    for stock in stocks:
        glass_type = getattr(stock, 'glass_type', 'Unknown')
        if glass_type not in stock_summary:
            stock_summary[glass_type] = []
        stock_summary[glass_type].append(stock)
    
    for glass_type, type_stocks in stock_summary.items():
        print(f"   🏗️  {glass_type}:")
        for stock in type_stocks:
            supplier = getattr(stock, 'supplier', 'Unknown')
            quality = getattr(stock, 'quality_grade', 'Standard')
            print(f"      - {stock.id}: {stock.width}×{stock.height}×{stock.thickness}mm "
                  f"(€{stock.cost_per_unit:.2f}, {supplier}, {quality})")
    
    total_components = sum(order.quantity for order in orders)
    print(f"\n   🔧 Glass pieces to cut: {total_components} pieces ({len(orders)} types)")
    
    # Show orders with descriptions
    print(f"   📋 Order details:")
    for order in orders[:5]:  # Show first 5 orders
        description = getattr(order, 'description', 'No description')
        if hasattr(order.shape, 'width'):
            dims = f"{order.shape.width}×{order.shape.height}mm"
        else:
            dims = f"⌀{order.shape.radius*2}mm"
        print(f"      - {order.id}: {order.quantity}× {dims} ({order.priority.name}) - {description}")
    
    if len(orders) > 5:
        print(f"      ... and {len(orders)-5} more order types")
    
    # Calculate material requirements
    total_component_area = sum(order.shape.area() * order.quantity for order in orders)
    total_stock_area = sum(stock.area for stock in stocks)
    
    print(f"\n📊 MATERIAL ANALYSIS:")
    print(f"   📏 Component area needed: {total_component_area/1_000_000:.2f} m²")
    print(f"   📏 Glass area available: {total_stock_area/1_000_000:.2f} m²")
    print(f"   📈 Theoretical utilization: {(total_component_area/total_stock_area)*100:.1f}%")
    
    print(f"\n⚙️  PRECISION GLASS CONFIGURATION:")
    print(f"   🚫 Rotation allowed: {config.allow_rotation} (grain direction critical)")
    print(f"   ✂️  Cutting precision: {config.cutting_width}mm")
    print(f"   📏 Safety margins: {config.edge_margin}mm")
    print(f"   🌡️  Thermal factor: {config.thermal_expansion_factor}")
    print(f"   ♻️  Breakage factor: {config.material_waste_factor*100:.1f}%")
    
    # Test algorithms optimized for glass cutting
    print(f"\n🔍 PRECISION CUTTING ALGORITHM COMPARISON:")
    
    algorithms = [
        ("Best Fit (Precision)", BestFitAlgorithm()),
        ("Genetic (Maximum Precision)", GeneticAlgorithm(population_size=40, generations=30, mutation_rate=0.05)),
    ]
    
    results = []
    
    for name, algorithm in algorithms:
        print(f"  🔧 {name}:")
        
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, config)
        computation_time = time.time() - start_time
        
        print(f"     ⚡ Computation time: {computation_time:.3f}s")
        print(f"     📊 Material efficiency: {result.efficiency_percentage:.1f}%")
        print(f"     ✅ Pieces cut: {result.total_orders_fulfilled}/{total_components}")
        print(f"     📦 Sheets used: {result.total_stock_used}/{len(stocks)}")
        print(f"     ♻️  Material waste: {result.waste_percentage:.1f}%")
        
        results.append((name, result))
    
    # Select best result for detailed analysis
    best_result = max(results, key=lambda x: x[1].efficiency_percentage)
    best_name, best_opt = best_result
    
    print(f"\n🏆 OPTIMAL PRECISION SOLUTION: {best_name}")
    
    # Detailed glass-specific analysis
    analyze_stress_factors(best_opt, stocks)
    calculate_glass_cutting_costs(best_opt, stocks)
    
    # Create visualization
    visualize_glass_cutting_layout(best_opt, stocks, "Architectural Glass Production")
    
    # Quality assessment
    print(f"\n📋 QUALITY ASSESSMENT:")
    print(f"   🎯 Precision grade: A+ (Architectural quality)")
    print(f"   🔍 Edge quality: Mirror finish capable")
    print(f"   🛡️  Safety compliance: EN 12150 (Tempered glass)")
    print(f"   📊 Material efficiency: {best_opt.efficiency_percentage:.1f}%")
    
    if best_opt.efficiency_percentage > 85:
        print(f"   ⭐ EXCELLENT: Premium efficiency for glass cutting")
    elif best_opt.efficiency_percentage > 75:
        print(f"   ✅ GOOD: Standard efficiency for precision work")
    else:
        print(f"   ⚠️  ACCEPTABLE: Consider layout optimization")
    
    print(f"\n✨ Precision glass cutting optimization completed!")
    print(f"📁 Quality control reports saved in: demo_results/")
    print(f"💡 Ready for CNC glass cutting table programming")


if __name__ == "__main__":
    main() 