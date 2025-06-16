#!/usr/bin/env python3
"""
Quick Demo - Surface Cutting Optimizer
Fast demonstration for simple use cases
"""

import sys
import os
import logging
from datetime import datetime, timedelta
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
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm

from surface_optimizer.utils.logging import setup_logging, get_logger
from surface_optimizer.utils.visualization import visualize_cutting_plan


def create_simple_dataset():
    """Create a simple dataset for quick testing"""
    
    # Simple stock inventory
    stocks = [
        Stock(
            id="S001", width=2000, height=1000, thickness=5.0,
            material_type=MaterialType.METAL,
            location="Warehouse A",
            supplier="Metal Co",
            cost_per_unit=150.00
        ),
        Stock(
            id="S002", width=1500, height=800, thickness=3.0,
            material_type=MaterialType.GLASS,
            location="Warehouse B", 
            supplier="Glass Co",
            cost_per_unit=80.00
        ),
        Stock(
            id="S003", width=1200, height=600, thickness=10.0,
            material_type=MaterialType.WOOD,
            location="Warehouse C",
            supplier="Wood Co",
            cost_per_unit=60.00
        )
    ]
    
    # Simple orders
    orders = [
        Order(
            id="O001",
            shape=Rectangle(800, 400, 0, 0),
            quantity=2,
            priority=Priority.HIGH,
            material_type=MaterialType.METAL,
            thickness=5.0,
            customer_id="CUST001",
            unit_price=75.00,
            notes="Metal panels"
        ),
        Order(
            id="O002",
            shape=Circle(200, 0, 0),
            quantity=3,
            priority=Priority.MEDIUM,
            material_type=MaterialType.GLASS,
            thickness=3.0,
            customer_id="CUST002",
            unit_price=45.00,
            notes="Glass circles"
        ),
        Order(
            id="O003",
            shape=Rectangle(500, 300, 0, 0),
            quantity=1,
            priority=Priority.LOW,
            material_type=MaterialType.WOOD,
            thickness=10.0,
            customer_id="CUST003",
            unit_price=35.00,
            notes="Wood panel"
        )
    ]
    
    return stocks, orders


def run_quick_test():
    """Run quick algorithm test"""
    print("🚀 QUICK CUTTING OPTIMIZER TEST")
    print("="*50)
    
    # Setup simple logging
    logger = setup_logging(level=logging.INFO)
    logger.start_operation("quick_demo")
    
    # Create simple dataset
    stocks, orders = create_simple_dataset()
    
    print(f"📊 Dataset: {len(stocks)} stocks, {len(orders)} orders")
    
    # Test different algorithms
    algorithms = [
        ("Bottom-Left Fill", BottomLeftAlgorithm()),
        ("First Fit", FirstFitAlgorithm()),
        ("Genetic Algorithm (Fast)", GeneticAlgorithm(
            population_size=10, generations=20, auto_scale=False))
    ]
    
    config = OptimizationConfig(
        allow_rotation=True,
        prioritize_orders=True,
        group_by_material=True
    )
    
    best_result = None
    best_algorithm = None
    best_efficiency = 0
    
    for algo_name, algorithm in algorithms:
        print(f"\n⚡ Testing {algo_name}...")
        
        try:
            optimizer = Optimizer(config=config, logger=logger)
            optimizer.set_algorithm(algorithm)
            
            result = optimizer.optimize(stocks, orders)
            
            print(f"  ✅ Efficiency: {result.efficiency_percentage:.1f}%")
            print(f"  ✅ Orders fulfilled: {result.total_orders_fulfilled}/{len(orders)}")
            print(f"  ✅ Cost: ${result.total_cost:.2f}")
            print(f"  ✅ Time: {result.computation_time:.3f}s")
            
            if result.efficiency_percentage > best_efficiency:
                best_result = result
                best_algorithm = algo_name
                best_efficiency = result.efficiency_percentage
                
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    # Show best result
    if best_result:
        print(f"\n🏆 BEST RESULT: {best_algorithm}")
        print(f"   Efficiency: {best_result.efficiency_percentage:.1f}%")
        print(f"   Fulfillment: {best_result.total_orders_fulfilled}/{len(orders)} orders")
        print(f"   Cost: ${best_result.total_cost:.2f}")
        print(f"   Waste: {best_result.waste_percentage:.1f}%")
        
        # Generate visualization
        try:
            print(f"\n📸 Generating visualization...")
            visualize_cutting_plan(
                best_result, stocks, 
                save_path=f"quick_demo_{best_algorithm.lower().replace(' ', '_')}.png",
                output_dir="quick_results"
            )
            print("   ✅ Visualization saved to quick_results/")
        except Exception as e:
            print(f"   ⚠️ Visualization failed: {e}")
        
        # Simple report
        print(f"\n📄 SIMPLE REPORT:")
        print(f"   Algorithm: {best_algorithm}")
        print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Stocks used: {best_result.total_stock_used}")
        print(f"   Shapes placed: {len(best_result.placed_shapes)}")
        
        if best_result.unfulfilled_orders:
            print(f"   Unfulfilled orders: {len(best_result.unfulfilled_orders)}")
            for order in best_result.unfulfilled_orders:
                print(f"     - {order.id}: {order.shape}")
    
    logger.end_operation("quick_demo", success=True)
    print(f"\n✨ Quick demo completed!")


def run_scalability_test():
    """Test scalability with different problem sizes"""
    print("\n🔬 SCALABILITY TEST")
    print("="*50)
    
    logger = setup_logging(level=logging.INFO)
    
    # Test different problem sizes
    test_cases = [
        ("Tiny (2 stocks, 3 orders)", 2, 3),
        ("Small (5 stocks, 8 orders)", 5, 8),
        ("Medium (10 stocks, 15 orders)", 10, 15),
        ("Large (20 stocks, 30 orders)", 20, 30)
    ]
    
    algorithm = GeneticAlgorithm(auto_scale=True)
    config = OptimizationConfig(allow_rotation=True, prioritize_orders=True)
    
    for test_name, num_stocks, num_orders in test_cases:
        print(f"\n📏 {test_name}")
        
        # Generate test data
        stocks = []
        for i in range(num_stocks):
            stocks.append(Stock(
                id=f"S{i:03d}",
                width=1000 + (i % 3) * 500,
                height=800 + (i % 2) * 400,
                thickness=5.0,
                material_type=MaterialType.METAL,
                cost_per_unit=100.0
            ))
        
        orders = []
        for i in range(num_orders):
            shape = Rectangle(200 + (i % 5) * 100, 150 + (i % 3) * 75, 0, 0)
            orders.append(Order(
                id=f"O{i:03d}",
                shape=shape,
                quantity=1,
                priority=Priority.MEDIUM,
                material_type=MaterialType.METAL,
                thickness=5.0
            ))
        
        try:
            optimizer = Optimizer(config=config, logger=logger)
            optimizer.set_algorithm(algorithm)
            
            result = optimizer.optimize(stocks, orders)
            
            problem_size = num_stocks * num_orders
            
            print(f"   📊 Problem size: {problem_size}")
            print(f"   ⚡ Time: {result.computation_time:.3f}s")
            print(f"   📈 Efficiency: {result.efficiency_percentage:.1f}%")
            print(f"   ✅ Fulfilled: {result.total_orders_fulfilled}/{num_orders}")
            
            # Performance rating
            if result.computation_time < 1.0:
                rating = "⚡ Excellent"
            elif result.computation_time < 5.0:
                rating = "✅ Good"
            elif result.computation_time < 10.0:
                rating = "⚠️ Acceptable"
            else:
                rating = "🐌 Slow"
            
            print(f"   🏃 Performance: {rating}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")


def main():
    """Main function"""
    print("🎯 SURFACE CUTTING OPTIMIZER - QUICK DEMO")
    print("="*60)
    print("Fast testing for development and validation")
    print("="*60)
    
    try:
        # Run quick test
        run_quick_test()
        
        # Run scalability test
        run_scalability_test()
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"📁 Check 'quick_results/' for visualizations")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 