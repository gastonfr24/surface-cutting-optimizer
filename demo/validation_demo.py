#!/usr/bin/env python3
"""
Validation Demo - Surface Cutting Optimizer
Comprehensive validation of results, coherence checking, and overlap detection
"""

import sys
import os
import logging
import math
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path to import surface_optimizer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from surface_optimizer.core.models import (
    Stock, Order, OptimizationConfig, 
    MaterialType, Priority
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer

# Import algorithms
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm

from surface_optimizer.utils.logging import setup_logging
from surface_optimizer.utils.visualization import visualize_cutting_plan


def check_shape_overlap(shape1, shape2):
    """Check if two shapes overlap"""
    
    if isinstance(shape1, Rectangle) and isinstance(shape2, Rectangle):
        # Rectangle overlap check
        r1_left = shape1.x
        r1_right = shape1.x + shape1.width
        r1_bottom = shape1.y
        r1_top = shape1.y + shape1.height
        
        r2_left = shape2.x
        r2_right = shape2.x + shape2.width
        r2_bottom = shape2.y
        r2_top = shape2.y + shape2.height
        
        # No overlap if one rectangle is to the left, right, above, or below the other
        if (r1_right <= r2_left or r2_right <= r1_left or 
            r1_top <= r2_bottom or r2_top <= r1_bottom):
            return False, 0.0
        
        # Calculate overlap area
        overlap_width = min(r1_right, r2_right) - max(r1_left, r2_left)
        overlap_height = min(r1_top, r2_top) - max(r1_bottom, r2_bottom)
        overlap_area = overlap_width * overlap_height
        
        return True, overlap_area
        
    elif isinstance(shape1, Circle) and isinstance(shape2, Circle):
        # Circle overlap check
        c1_x = shape1.x + shape1.radius
        c1_y = shape1.y + shape1.radius
        c2_x = shape2.x + shape2.radius
        c2_y = shape2.y + shape2.radius
        
        distance = math.sqrt((c1_x - c2_x)**2 + (c1_y - c2_y)**2)
        min_distance = shape1.radius + shape2.radius
        
        if distance >= min_distance:
            return False, 0.0
        
        # Approximate overlap area for circles
        overlap_area = min(shape1.area(), shape2.area()) * 0.5  # Rough approximation
        return True, overlap_area
        
    elif isinstance(shape1, Rectangle) and isinstance(shape2, Circle):
        # Rectangle-Circle overlap (simplified)
        circle_center_x = shape2.x + shape2.radius
        circle_center_y = shape2.y + shape2.radius
        
        # Check if circle center is within rectangle bounds expanded by radius
        rect_left = shape1.x - shape2.radius
        rect_right = shape1.x + shape1.width + shape2.radius
        rect_bottom = shape1.y - shape2.radius
        rect_top = shape1.y + shape1.height + shape2.radius
        
        if (circle_center_x >= rect_left and circle_center_x <= rect_right and
            circle_center_y >= rect_bottom and circle_center_y <= rect_top):
            overlap_area = min(shape1.area(), shape2.area()) * 0.3  # Conservative estimate
            return True, overlap_area
        
        return False, 0.0
        
    elif isinstance(shape1, Circle) and isinstance(shape2, Rectangle):
        return check_shape_overlap(shape2, shape1)
    
    return False, 0.0


def validate_cutting_result(result, stocks, orders):
    """Comprehensive validation of cutting result"""
    
    print("\n🔍 COMPREHENSIVE RESULT VALIDATION")
    print("="*60)
    
    validation_issues = []
    warnings = []
    
    # 1. Basic consistency checks
    print("📋 Basic Consistency Checks:")
    
    if not result.placed_shapes:
        validation_issues.append("No shapes were placed")
        print("  ❌ No shapes placed")
        return validation_issues, warnings
    
    print(f"  ✅ {len(result.placed_shapes)} shapes placed")
    
    # 2. Material consistency
    print("\n🧪 Material Consistency:")
    material_mismatches = 0
    
    for placed_shape in result.placed_shapes:
        # Find corresponding order
        order_id = placed_shape.order_id
        base_order_id = order_id.rsplit('_', 1)[0] if '_' in order_id else order_id
        
        order = None
        for o in orders:
            if o.id == base_order_id:
                order = o
                break
        
        if not order:
            validation_issues.append(f"Order {order_id} not found in original orders")
            continue
        
        # Find corresponding stock
        stock = None
        for s in stocks:
            if s.id == placed_shape.stock_id:
                stock = s
                break
        
        if not stock:
            validation_issues.append(f"Stock {placed_shape.stock_id} not found")
            continue
        
        # Check material consistency
        if stock.material_type != order.material_type:
            material_mismatches += 1
            validation_issues.append(
                f"Material mismatch: Order {order_id} ({order.material_type}) "
                f"placed on {stock.id} ({stock.material_type})"
            )
    
    if material_mismatches == 0:
        print("  ✅ All materials consistent")
    else:
        print(f"  ❌ {material_mismatches} material mismatches")
    
    # 3. Bounds checking
    print("\n📐 Bounds Checking:")
    bounds_violations = 0
    
    for placed_shape in result.placed_shapes:
        stock = None
        for s in stocks:
            if s.id == placed_shape.stock_id:
                stock = s
                break
        
        if not stock:
            continue
        
        shape = placed_shape.shape
        
        if isinstance(shape, Rectangle):
            if (shape.x < 0 or shape.y < 0 or 
                shape.x + shape.width > stock.width or 
                shape.y + shape.height > stock.height):
                bounds_violations += 1
                validation_issues.append(
                    f"Shape {placed_shape.order_id} exceeds stock bounds: "
                    f"pos=({shape.x}, {shape.y}), size=({shape.width}x{shape.height}), "
                    f"stock=({stock.width}x{stock.height})"
                )
        
        elif isinstance(shape, Circle):
            if (shape.x < 0 or shape.y < 0 or 
                shape.x + 2*shape.radius > stock.width or 
                shape.y + 2*shape.radius > stock.height):
                bounds_violations += 1
                validation_issues.append(
                    f"Circle {placed_shape.order_id} exceeds stock bounds: "
                    f"pos=({shape.x}, {shape.y}), radius={shape.radius}, "
                    f"stock=({stock.width}x{stock.height})"
                )
    
    if bounds_violations == 0:
        print("  ✅ All shapes within bounds")
    else:
        print(f"  ❌ {bounds_violations} bounds violations")
    
    # 4. Overlap detection
    print("\n🔄 Overlap Detection:")
    total_overlaps = 0
    total_overlap_area = 0.0
    
    # Group shapes by stock for efficient overlap checking
    shapes_by_stock = {}
    for placed_shape in result.placed_shapes:
        stock_id = placed_shape.stock_id
        if stock_id not in shapes_by_stock:
            shapes_by_stock[stock_id] = []
        shapes_by_stock[stock_id].append(placed_shape)
    
    for stock_id, shapes in shapes_by_stock.items():
        stock_overlaps = 0
        stock_overlap_area = 0.0
        
        for i in range(len(shapes)):
            for j in range(i + 1, len(shapes)):
                overlaps, overlap_area = check_shape_overlap(shapes[i].shape, shapes[j].shape)
                if overlaps:
                    stock_overlaps += 1
                    stock_overlap_area += overlap_area
                    validation_issues.append(
                        f"Overlap detected in stock {stock_id}: "
                        f"{shapes[i].order_id} overlaps with {shapes[j].order_id} "
                        f"(area: {overlap_area:.2f})"
                    )
        
        if stock_overlaps == 0:
            print(f"  ✅ Stock {stock_id}: No overlaps")
        else:
            print(f"  ❌ Stock {stock_id}: {stock_overlaps} overlaps (area: {stock_overlap_area:.2f})")
            total_overlaps += stock_overlaps
            total_overlap_area += stock_overlap_area
    
    # 5. Efficiency validation
    print("\n📊 Efficiency Validation:")
    
    # Calculate actual efficiency
    total_used_area = sum(ps.shape.area() for ps in result.placed_shapes)
    used_stock_ids = {ps.stock_id for ps in result.placed_shapes}
    total_stock_area = sum(s.area for s in stocks if s.id in used_stock_ids)
    
    if total_stock_area > 0:
        calculated_efficiency = (total_used_area / total_stock_area) * 100
        reported_efficiency = result.efficiency_percentage
        
        efficiency_diff = abs(calculated_efficiency - reported_efficiency)
        
        print(f"  📈 Calculated efficiency: {calculated_efficiency:.2f}%")
        print(f"  📈 Reported efficiency: {reported_efficiency:.2f}%")
        print(f"  📈 Difference: {efficiency_diff:.2f}%")
        
        if efficiency_diff > 1.0:  # Allow 1% tolerance
            validation_issues.append(
                f"Efficiency calculation mismatch: calculated={calculated_efficiency:.2f}%, "
                f"reported={reported_efficiency:.2f}%"
            )
        else:
            print("  ✅ Efficiency calculation consistent")
    else:
        print("  ⚠️ No stock area used - cannot validate efficiency")
    
    # 6. Order fulfillment validation
    print("\n📦 Order Fulfillment Validation:")
    
    placed_order_ids = set()
    for ps in result.placed_shapes:
        base_id = ps.order_id.rsplit('_', 1)[0] if '_' in ps.order_id else ps.order_id
        placed_order_ids.add(base_id)
    
    original_order_ids = {o.id for o in orders}
    
    print(f"  📋 Original orders: {len(original_order_ids)}")
    print(f"  📋 Fulfilled orders: {len(placed_order_ids)}")
    print(f"  📋 Reported fulfilled: {result.total_orders_fulfilled}")
    
    if len(placed_order_ids) != result.total_orders_fulfilled:
        validation_issues.append(
            f"Order fulfillment mismatch: calculated={len(placed_order_ids)}, "
            f"reported={result.total_orders_fulfilled}"
        )
    else:
        print("  ✅ Order fulfillment count consistent")
    
    # Summary
    print("\n📋 VALIDATION SUMMARY:")
    print("="*60)
    
    if not validation_issues:
        print("✅ ALL VALIDATIONS PASSED - Result is coherent and valid")
    else:
        print(f"❌ {len(validation_issues)} VALIDATION ISSUES FOUND:")
        for i, issue in enumerate(validation_issues, 1):
            print(f"  {i}. {issue}")
    
    if warnings:
        print(f"\n⚠️ {len(warnings)} WARNINGS:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    return validation_issues, warnings


def create_known_good_dataset():
    """Create a dataset with known optimal solution for testing"""
    
    # Simple case: 2 rectangles that should fit perfectly in 1 stock
    stocks = [
        Stock(
            id="STOCK_001", 
            width=2000, height=1000, thickness=5.0,
            material_type=MaterialType.METAL,
            cost_per_unit=100.00
        )
    ]
    
    orders = [
        Order(
            id="ORDER_001",
            shape=Rectangle(1000, 500, 0, 0),  # Half the stock
            quantity=1,
            priority=Priority.HIGH,
            material_type=MaterialType.METAL,
            thickness=5.0
        ),
        Order(
            id="ORDER_002", 
            shape=Rectangle(1000, 500, 0, 0),  # Other half
            quantity=1,
            priority=Priority.HIGH,
            material_type=MaterialType.METAL,
            thickness=5.0
        )
    ]
    
    expected_result = {
        "efficiency_min": 95.0,  # Should be very high
        "orders_fulfilled": 2,
        "stocks_used": 1,
        "overlaps_allowed": 0
    }
    
    return stocks, orders, expected_result


def run_coherence_test():
    """Run comprehensive coherence testing"""
    
    print("🎯 COHERENCE AND VALIDATION TESTING")
    print("="*80)
    
    logger = setup_logging(level=logging.INFO)
    
    # Test with known good dataset
    print("\n🧪 TESTING WITH KNOWN OPTIMAL CASE:")
    stocks, orders, expected = create_known_good_dataset()
    
    algorithms = [
        ("Bottom-Left", BottomLeftAlgorithm()),
        ("Genetic Algorithm", GeneticAlgorithm(auto_scale=True))
    ]
    
    config = OptimizationConfig(
        allow_rotation=True,
        prioritize_orders=True
    )
    
    all_results = []
    
    for algo_name, algorithm in algorithms:
        print(f"\n🔬 Testing {algo_name}:")
        print("-" * 40)
        
        try:
            optimizer = Optimizer(config=config, logger=logger)
            optimizer.set_algorithm(algorithm)
            
            result = optimizer.optimize(stocks, orders)
            all_results.append((algo_name, result))
            
            # Basic metrics
            print(f"  📊 Efficiency: {result.efficiency_percentage:.1f}%")
            print(f"  📦 Orders fulfilled: {result.total_orders_fulfilled}/{len(orders)}")
            print(f"  🏭 Stocks used: {result.total_stock_used}")
            print(f"  💰 Cost: ${result.total_cost:.2f}")
            print(f"  ⏱️ Time: {result.computation_time:.3f}s")
            
            # Validate against expectations
            print(f"\n  🎯 Expected vs Actual:")
            efficiency_ok = result.efficiency_percentage >= expected["efficiency_min"]
            orders_ok = result.total_orders_fulfilled >= expected["orders_fulfilled"]
            stocks_ok = result.total_stock_used <= expected["stocks_used"]
            
            print(f"    Efficiency: {result.efficiency_percentage:.1f}% >= {expected['efficiency_min']}% {'✅' if efficiency_ok else '❌'}")
            print(f"    Orders: {result.total_orders_fulfilled} >= {expected['orders_fulfilled']} {'✅' if orders_ok else '❌'}")
            print(f"    Stocks: {result.total_stock_used} <= {expected['stocks_used']} {'✅' if stocks_ok else '❌'}")
            
            # Comprehensive validation
            issues, warnings = validate_cutting_result(result, stocks, orders)
            
            # Generate visualization for inspection
            try:
                visualize_cutting_plan(
                    result, stocks,
                    save_path=f"validation_{algo_name.lower().replace(' ', '_')}.png",
                    output_dir="validation_results"
                )
                print(f"  📸 Visualization saved: validation_results/validation_{algo_name.lower().replace(' ', '_')}.png")
            except Exception as e:
                print(f"  ⚠️ Visualization failed: {e}")
            
        except Exception as e:
            print(f"  ❌ Algorithm failed: {e}")
    
    # Compare algorithms
    if len(all_results) > 1:
        print(f"\n🔄 ALGORITHM COMPARISON:")
        print("-" * 40)
        
        for i, (name1, result1) in enumerate(all_results):
            for j, (name2, result2) in enumerate(all_results[i+1:], i+1):
                print(f"\n  {name1} vs {name2}:")
                print(f"    Efficiency: {result1.efficiency_percentage:.1f}% vs {result2.efficiency_percentage:.1f}%")
                print(f"    Time: {result1.computation_time:.3f}s vs {result2.computation_time:.3f}s")
                
                # Check for consistency
                eff_diff = abs(result1.efficiency_percentage - result2.efficiency_percentage)
                if eff_diff > 10.0:
                    print(f"    ⚠️ Large efficiency difference: {eff_diff:.1f}%")
                else:
                    print(f"    ✅ Consistent efficiency (diff: {eff_diff:.1f}%)")


def main():
    """Main validation function"""
    
    print("🔍 SURFACE CUTTING OPTIMIZER - VALIDATION & COHERENCE TESTING")
    print("="*80)
    print("Comprehensive validation of optimization results")
    print("="*80)
    
    try:
        run_coherence_test()
        
        print(f"\n🎉 VALIDATION TESTING COMPLETED!")
        print(f"📁 Check 'validation_results/' for detailed visualizations")
        
    except Exception as e:
        print(f"❌ Validation testing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 