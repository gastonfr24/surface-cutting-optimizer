#!/usr/bin/env python3
"""
Enhanced Features Demo - Surface Cutting Optimizer
Demonstrates logging, improved models, and advanced features
"""

import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import surface_optimizer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from surface_optimizer.core.models import (
    Stock, Order, OptimizationConfig, 
    MaterialType, Priority, StockStatus, OrderStatus,
    MaterialProperties
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.utils.logging import setup_logging, get_logger
from surface_optimizer.utils.metrics import generate_metrics_report


def create_enhanced_demo_data():
    """Create enhanced demo data with new features"""
    print("🔧 Creating enhanced demo data...")
    
    # Create stocks with enhanced features
    stocks = [
        Stock(
            id="S1_GLASS", width=2000, height=1000, thickness=6.0,
            material_type=MaterialType.GLASS,
            location="Warehouse A-1",
            supplier="Glass Corp",
            batch_number="GC2024-001",
            quality_grade="A+",
            purchase_date=datetime.now() - timedelta(days=30),
            tags=["premium", "clear"],
            notes="High-quality clear glass"
        ),
        Stock(
            id="S2_METAL", width=1500, height=1200, thickness=3.0,
            material_type=MaterialType.METAL,
            location="Warehouse B-2",
            supplier="Metal Works Inc",
            batch_number="MW2024-042",
            quality_grade="A",
            purchase_date=datetime.now() - timedelta(days=15),
            tags=["aluminum", "anodized"],
            notes="Anodized aluminum sheet"
        ),
        Stock(
            id="S3_WOOD", width=2440, height=1220, thickness=18.0,
            material_type=MaterialType.WOOD,
            location="Warehouse C-3",
            supplier="Forest Products Ltd",
            batch_number="FP2024-189",
            quality_grade="B+",
            purchase_date=datetime.now() - timedelta(days=7),
            tags=["plywood", "marine_grade"],
            notes="Marine grade plywood"
        )
    ]
    
    # Create orders with enhanced features
    orders = [
        Order(
            id="ORD_001", 
            shape=Rectangle(800, 600, 0, 0),
            quantity=2,
            priority=Priority.HIGH,
            material_type=MaterialType.GLASS,
            thickness=6.0,
            customer_id="CUST_A123",
            order_date=datetime.now() - timedelta(days=5),
            due_date=datetime.now() + timedelta(days=2),
            unit_price=45.50,
            tags=["architectural", "safety"],
            notes="Safety glass for building entrance"
        ),
        Order(
            id="ORD_002",
            shape=Circle(200, 0, 0),
            quantity=1,
            priority=Priority.URGENT,
            material_type=MaterialType.METAL,
            thickness=3.0,
            customer_id="CUST_B456",
            order_date=datetime.now() - timedelta(days=2),
            due_date=datetime.now() + timedelta(hours=8),
            unit_price=125.00,
            tags=["aerospace", "precision"],
            special_requirements={"tolerance": 0.1, "surface_finish": "mirror"},
            notes="Precision aerospace component"
        ),
        Order(
            id="ORD_003",
            shape=Rectangle(1200, 800, 0, 0),
            quantity=1,
            priority=Priority.MEDIUM,
            material_type=MaterialType.WOOD,
            thickness=18.0,
            customer_id="CUST_C789",
            order_date=datetime.now() - timedelta(days=1),
            due_date=datetime.now() + timedelta(days=7),
            unit_price=89.99,
            tags=["furniture", "custom"],
            notes="Custom furniture panel"
        ),
        Order(
            id="ORD_004",
            shape=Rectangle(400, 300, 0, 0),
            quantity=3,
            priority=Priority.LOW,
            material_type=MaterialType.GLASS,
            thickness=6.0,
            customer_id="CUST_A123",
            order_date=datetime.now() - timedelta(days=3),
            due_date=datetime.now() + timedelta(days=10),
            unit_price=22.75,
            tags=["standard", "bulk"],
            notes="Standard window panels"
        )
    ]
    
    return stocks, orders


def demonstrate_enhanced_models():
    """Demonstrate enhanced model features"""
    print("\n📊 Demonstrating Enhanced Models")
    print("=" * 50)
    
    stocks, orders = create_enhanced_demo_data()
    
    # Show stock information
    print("\n📦 Enhanced Stock Information:")
    for stock in stocks:
        print(f"  • {stock}")
        print(f"    Area: {stock.area_m2:.2f} m² | Weight: {stock.weight_kg:.1f} kg")
        print(f"    Cost: ${stock.total_cost:.2f} | Status: {stock.status.value}")
        print(f"    Location: {stock.location} | Supplier: {stock.supplier}")
        
        # Validate stock
        issues = stock.validate()
        if issues:
            print(f"    ⚠️ Issues: {', '.join(issues)}")
        else:
            print(f"    ✅ No issues found")
        print()
    
    # Show order information
    print("\n📋 Enhanced Order Information:")
    for order in orders:
        print(f"  • {order}")
        print(f"    Total Value: ${order.total_value:.2f} | Area: {order.total_area/1000:.1f} dm²")
        print(f"    Customer: {order.customer_id} | Due in: {order.days_until_due} days")
        print(f"    Tags: {', '.join(order.tags)}")
        
        # Validate order
        issues = order.validate()
        if issues:
            print(f"    ⚠️ Issues: {', '.join(issues)}")
        else:
            print(f"    ✅ No issues found")
        print()
    
    return stocks, orders


def demonstrate_logging():
    """Demonstrate logging capabilities"""
    print("\n📝 Demonstrating Logging System")
    print("=" * 50)
    
    # Setup custom logger
    logger = setup_logging(log_dir="demo_logs")
    
    # Log some operations
    logger.start_operation("demo_preparation", {"items": 5, "type": "enhanced_demo"})
    
    logger.logger.info("Initializing enhanced features demo")
    logger.logger.debug("Debug message: System ready")
    logger.logger.warning("Warning: This is a demo environment")
    
    logger.end_operation("demo_preparation", success=True, 
                        result={"status": "ready", "components": "loaded"})
    
    return logger


def demonstrate_optimization_with_logging():
    """Demonstrate optimization with enhanced logging"""
    print("\n🚀 Demonstrating Enhanced Optimization")
    print("=" * 50)
    
    # Get demo data
    stocks, orders = create_enhanced_demo_data()
    
    # Setup logger
    logger = get_logger()
    
    # Create enhanced configuration
    config = OptimizationConfig(
        allow_rotation=True,
        cutting_width=2.5,
        prioritize_orders=True,
        group_by_material=True,
        group_by_thickness=True,
        optimize_for_cost=True,
        placement_precision=0.5,
        max_computation_time=30.0
    )
    
    # Validate configuration
    config_issues = config.validate()
    if config_issues:
        print(f"⚠️ Configuration issues: {config_issues}")
    else:
        print("✅ Configuration validated successfully")
    
    # Create optimizer with logging
    optimizer = Optimizer(config=config, logger=logger)
    optimizer.set_algorithm(BottomLeftAlgorithm())
    
    print(f"\n🔧 {optimizer}")
    
    # Run optimization
    try:
        result = optimizer.optimize(stocks, orders)
        
        print(f"\n📊 Optimization Results:")
        print(f"  • Algorithm: {result.algorithm_used}")
        print(f"  • Stocks used: {result.total_stock_used}")
        print(f"  • Orders fulfilled: {result.total_orders_fulfilled}/{len(orders)}")
        print(f"  • Efficiency: {result.efficiency_percentage:.1f}%")
        print(f"  • Waste: {result.waste_percentage:.1f}%")
        print(f"  • Total cost: ${result.total_cost:.2f}")
        print(f"  • Cost per m²: ${result.cost_per_area:.2f}")
        print(f"  • Fulfillment rate: {result.fulfillment_rate:.1f}%")
        print(f"  • Computation time: {result.computation_time:.3f}s")
        
        # Show placed shapes
        if result.placed_shapes:
            print(f"\n🎯 Placed Shapes ({len(result.placed_shapes)}):")
            for ps in result.placed_shapes:
                print(f"  • {ps}")
                print(f"    Area: {ps.shape.area()/1000:.1f} dm² | Position: {ps.position}")
        
        # Show unfulfilled orders
        if result.unfulfilled_orders:
            print(f"\n❌ Unfulfilled Orders ({len(result.unfulfilled_orders)}):")
            for order in result.unfulfilled_orders:
                print(f"  • {order.id}: {order.shape} (Priority: {order.priority.name})")
        
        # Export detailed results
        result.export_summary("demo_logs/optimization_result.json")
        print(f"\n📄 Detailed results exported to: demo_logs/optimization_result.json")
        
        return result
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        return None


def demonstrate_performance_tracking():
    """Demonstrate performance tracking features"""
    print("\n📈 Demonstrating Performance Tracking")
    print("=" * 50)
    
    stocks, orders = create_enhanced_demo_data()
    logger = get_logger()
    
    # Create optimizer
    optimizer = Optimizer(logger=logger)
    optimizer.set_algorithm(BottomLeftAlgorithm())
    
    # Run multiple optimizations with different configs
    configs = [
        OptimizationConfig(allow_rotation=False, prioritize_orders=False),
        OptimizationConfig(allow_rotation=True, prioritize_orders=False),
        OptimizationConfig(allow_rotation=True, prioritize_orders=True),
    ]
    
    print("Running multiple optimizations...")
    
    for i, config in enumerate(configs, 1):
        print(f"\n🔄 Optimization {i}/3 (Rotation: {config.allow_rotation}, Priority: {config.prioritize_orders})")
        
        optimizer.config = config
        try:
            result = optimizer.optimize(stocks, orders)
            print(f"  ✅ Efficiency: {result.efficiency_percentage:.1f}% | Time: {result.computation_time:.3f}s")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    # Show performance summary
    print(f"\n📊 Performance Summary:")
    summary = optimizer.get_performance_summary()
    
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  • {key.replace('_', ' ').title()}: {value:.2f}")
        else:
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Export logs
    optimizer.export_logs("demo_logs/performance_logs.json")
    print(f"\n📄 Performance logs exported to: demo_logs/performance_logs.json")
    
    return optimizer


def main():
    """Main demo function"""
    print("🎨 Surface Cutting Optimizer - Enhanced Features Demo")
    print("=" * 60)
    
    try:
        # Demonstrate enhanced models
        stocks, orders = demonstrate_enhanced_models()
        
        # Demonstrate logging
        logger = demonstrate_logging()
        
        # Demonstrate optimization with logging
        result = demonstrate_optimization_with_logging()
        
        # Demonstrate performance tracking
        optimizer = demonstrate_performance_tracking()
        
        # Show logger summary
        print(f"\n📝 Logger Summary:")
        log_summary = logger.get_summary()
        for key, value in log_summary.items():
            if isinstance(value, float):
                print(f"  • {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n🎉 Enhanced Features Demo Completed!")
        print(f"Check the demo_logs/ directory for exported files.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 