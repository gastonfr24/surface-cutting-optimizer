#!/usr/bin/env python3
"""
Professional Demo - Surface Cutting Optimizer
Complete demonstration of professional-grade features:
- Multiple advanced algorithms
- Comprehensive reporting system
- Professional table generation
- Cost analysis and optimization
- Performance comparison
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to sys.path to import surface_optimizer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from surface_optimizer.core.models import (
    Stock, Order, OptimizationConfig, 
    MaterialType, Priority, StockStatus, OrderStatus,
    MaterialProperties
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer

# Import all algorithms
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm
from surface_optimizer.algorithms.advanced.simulated_annealing import SimulatedAnnealingAlgorithm

# Import reporting system
from surface_optimizer.reporting.table_generator import TableGenerator, TableConfig

from surface_optimizer.utils.logging import setup_logging, get_logger
from surface_optimizer.utils.metrics import generate_metrics_report


def create_professional_dataset():
    """Create a professional dataset simulating real-world scenarios"""
    print("Creating professional dataset...")
    
    # Create diverse stock inventory
    stocks = [
        # Glass inventory
        Stock(
            id="GLS_001", width=3000, height=2000, thickness=6.0,
            material_type=MaterialType.GLASS,
            location="Warehouse A-1-01",
            supplier="Premium Glass Ltd",
            batch_number="PGL2024-Q1-045",
            quality_grade="A+",
            purchase_date=datetime.now() - timedelta(days=45),
            cost_per_unit=180.00,
            tags=["architectural", "tempered", "premium"]
        ),
        Stock(
            id="GLS_002", width=2500, height=1800, thickness=8.0,
            material_type=MaterialType.GLASS,
            location="Warehouse A-1-02",
            supplier="Premium Glass Ltd", 
            batch_number="PGL2024-Q1-046",
            quality_grade="A",
            purchase_date=datetime.now() - timedelta(days=40),
            cost_per_unit=195.00,
            tags=["architectural", "extra_thick"]
        ),
        Stock(
            id="GLS_003", width=2000, height=1000, thickness=4.0,
            material_type=MaterialType.GLASS,
            location="Warehouse A-2-01",
            supplier="Standard Glass Co",
            batch_number="SGC2024-B12",
            quality_grade="B+",
            purchase_date=datetime.now() - timedelta(days=20),
            cost_per_unit=95.00,
            tags=["standard", "thin"]
        ),
        
        # Metal inventory  
        Stock(
            id="MTL_001", width=2440, height=1220, thickness=3.0,
            material_type=MaterialType.METAL,
            location="Warehouse B-1-01",
            supplier="Steel Solutions Inc",
            batch_number="SSI2024-ALU-089",
            quality_grade="A+",
            purchase_date=datetime.now() - timedelta(days=15),
            cost_per_unit=285.00,
            tags=["aluminum", "aerospace_grade", "anodized"]
        ),
        Stock(
            id="MTL_002", width=2000, height=1500, thickness=5.0,
            material_type=MaterialType.METAL,
            location="Warehouse B-1-02", 
            supplier="Steel Solutions Inc",
            batch_number="SSI2024-ALU-090",
            quality_grade="A",
            purchase_date=datetime.now() - timedelta(days=12),
            cost_per_unit=425.00,
            tags=["aluminum", "thick", "marine_grade"]
        ),
        
        # Wood inventory
        Stock(
            id="WOD_001", width=2440, height=1220, thickness=18.0,
            material_type=MaterialType.WOOD,
            location="Warehouse C-1-01",
            supplier="Forest Products Ltd",
            batch_number="FPL2024-PLY-156",
            quality_grade="A",
            purchase_date=datetime.now() - timedelta(days=8),
            cost_per_unit=145.00,
            tags=["plywood", "marine_grade", "birch"]
        ),
        Stock(
            id="WOD_002", width=3050, height=1525, thickness=12.0,
            material_type=MaterialType.WOOD,
            location="Warehouse C-1-02",
            supplier="Forest Products Ltd",
            batch_number="FPL2024-MDF-089",
            quality_grade="B+",
            purchase_date=datetime.now() - timedelta(days=5),
            cost_per_unit=125.00,
            tags=["mdf", "furniture_grade"]
        ),
        
        # Additional wood stock
        Stock(
            id="WOD_003", width=2440, height=1220, thickness=12.0,
            material_type=MaterialType.WOOD,
            location="Warehouse C-2-01",
            supplier="Forest Products Ltd",
            batch_number="FPL2024-MDF-090",
            quality_grade="B+",
            purchase_date=datetime.now() - timedelta(days=3),
            cost_per_unit=135.00,
            tags=["mdf", "extra_stock"]
        )
    ]
    
    # Create diverse order portfolio
    orders = [
        # High-priority architectural project
        Order(
            id="ARCH_001",
            shape=Rectangle(1800, 1200, 0, 0),
            quantity=4,
            priority=Priority.URGENT,
            material_type=MaterialType.GLASS,
            thickness=6.0,
            customer_id="CUST_ARCH_DESIGN",
            order_date=datetime.now() - timedelta(days=7),
            due_date=datetime.now() + timedelta(days=3),
            unit_price=245.00,
            tags=["architectural", "building_facade", "urgent"],
            notes="Critical path item for building facade installation"
        ),
        
        # Aerospace precision components
        Order(
            id="AERO_001",
            shape=Circle(350, 0, 0),
            quantity=6,
            priority=Priority.HIGH,
            material_type=MaterialType.METAL,
            thickness=3.0,
            customer_id="CUST_AEROSPACE_TECH",
            order_date=datetime.now() - timedelta(days=5),
            due_date=datetime.now() + timedelta(days=10),
            unit_price=189.50,
            tags=["aerospace", "precision", "circular"],
            special_requirements={"tolerance": 0.05, "surface_finish": "mirror"},
            notes="Precision aerospace components with tight tolerances"
        ),
        
        # Custom furniture panels (reduced quantity)
        Order(
            id="FURN_001", 
            shape=Rectangle(1200, 800, 0, 0),
            quantity=3,
            priority=Priority.MEDIUM,
            material_type=MaterialType.WOOD,
            thickness=18.0,
            customer_id="CUST_LUXURY_FURNITURE",
            order_date=datetime.now() - timedelta(days=3),
            due_date=datetime.now() + timedelta(days=14),
            unit_price=125.00,
            tags=["furniture", "luxury", "custom"],
            notes="High-end furniture panels for luxury kitchen project"
        ),
        
        # Standard glass panels (bulk order)
        Order(
            id="STD_001",
            shape=Rectangle(600, 400, 0, 0),
            quantity=12,
            priority=Priority.MEDIUM,
            material_type=MaterialType.GLASS,
            thickness=4.0,
            customer_id="CUST_CONSTRUCTION_CO",
            order_date=datetime.now() - timedelta(days=2),
            due_date=datetime.now() + timedelta(days=21),
            unit_price=45.00,
            tags=["standard", "construction", "bulk"],
            notes="Standard window panels for residential construction"
        ),
        
        # Metal fabrication rectangles
        Order(
            id="FAB_001",
            shape=Rectangle(800, 600, 0, 0),
            quantity=5,
            priority=Priority.HIGH,
            material_type=MaterialType.METAL,
            thickness=5.0,
            customer_id="CUST_MARINE_WORKS",
            order_date=datetime.now() - timedelta(days=4),
            due_date=datetime.now() + timedelta(days=7),
            unit_price=167.50,
            tags=["marine", "fabrication", "thick"],
            notes="Marine grade aluminum panels for boat construction"
        ),
        
        # Small precision circles
        Order(
            id="PREC_001",
            shape=Circle(125, 0, 0),
            quantity=15,
            priority=Priority.LOW,
            material_type=MaterialType.METAL,
            thickness=3.0,
            customer_id="CUST_PRECISION_PARTS",
            order_date=datetime.now() - timedelta(days=1),
            due_date=datetime.now() + timedelta(days=30),
            unit_price=28.75,
            tags=["precision", "small_batch", "circles"],
            notes="Small precision discs for mechanical assemblies"
        ),
        
        # Large wood panel (reduced size)
        Order(
            id="WOOD_001",
            shape=Rectangle(1500, 700, 0, 0),
            quantity=1,
            priority=Priority.MEDIUM,
            material_type=MaterialType.WOOD,
            thickness=12.0,
            customer_id="CUST_CABINET_MAKER",
            order_date=datetime.now() - timedelta(days=6),
            due_date=datetime.now() + timedelta(days=12),
            unit_price=275.00,
            tags=["large_panel", "cabinet", "custom"],
            notes="Large cabinet doors for commercial kitchen project"
        )
    ]
    
    return stocks, orders


def run_algorithm_comparison(stocks, orders):
    """Run comprehensive algorithm comparison"""
    print("\n" + "="*80)
    print("PROFESSIONAL ALGORITHM COMPARISON")
    print("="*80)
    
    # Define algorithms to test (optimized for performance)
    algorithms = [
        ("Bottom-Left Fill", BottomLeftAlgorithm()),
        ("First Fit", FirstFitAlgorithm()),  
        ("Genetic Algorithm (Auto)", GeneticAlgorithm(auto_scale=True)),
        ("Simulated Annealing (Auto)", SimulatedAnnealingAlgorithm(auto_scale=True)),
        ("Genetic Algorithm (Fast)", GeneticAlgorithm(
            population_size=15, generations=25, auto_scale=False)),
        ("Simulated Annealing (Fast)", SimulatedAnnealingAlgorithm(
            initial_temperature=200.0, 
            cooling_rate=0.9,
            max_iterations=200,
            iterations_per_temp=15,
            auto_scale=False
        ))
    ]
    
    # Different configurations to test
    configs = [
        ("Standard", OptimizationConfig(
            allow_rotation=True,
            prioritize_orders=True,
            group_by_material=True
        )),
        ("Cost Optimized", OptimizationConfig(
            allow_rotation=True,
            prioritize_orders=True,
            group_by_material=True,
            optimize_for_cost=True
        )),
        ("High Precision", OptimizationConfig(
            allow_rotation=True,
            prioritize_orders=True,
            group_by_material=True,
            placement_precision=0.1,
            angle_precision=0.5
        ))
    ]
    
    results = {}
    logger = get_logger()
    
    for config_name, config in configs:
        print(f"\n--- Configuration: {config_name} ---")
        results[config_name] = {}
        
        for algo_name, algorithm in algorithms:
            print(f"Running {algo_name}...")
            
            try:
                optimizer = Optimizer(config=config, logger=logger)
                optimizer.set_algorithm(algorithm)
                
                result = optimizer.optimize(stocks, orders)
                results[config_name][algo_name] = result
                
                print(f"  ✓ Efficiency: {result.efficiency_percentage:.1f}%")
                print(f"  ✓ Orders fulfilled: {result.total_orders_fulfilled}/{len(orders)}")
                print(f"  ✓ Cost: ${result.total_cost:.2f}")
                print(f"  ✓ Time: {result.computation_time:.3f}s")
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                results[config_name][algo_name] = None
    
    return results


def generate_professional_reports(results, stocks, orders):
    """Generate comprehensive professional reports"""
    print("\n" + "="*80)
    print("GENERATING PROFESSIONAL REPORTS")
    print("="*80)
    
    # Create reports directory
    reports_dir = Path("professional_reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Configure table generation
    table_config = TableConfig(
        show_material_details=True,
        show_cost_breakdown=True,
        show_waste_analysis=True,
        show_timestamps=True,
        currency_symbol="$",
        area_unit="m²",
        precision=2
    )
    
    table_generator = TableGenerator(table_config)
    
    # Generate reports for each configuration's best result
    for config_name, config_results in results.items():
        if not config_results:
            continue
        
        print(f"\nGenerating reports for {config_name} configuration...")
        
        # Find best result (highest efficiency)
        best_result = None
        best_algorithm = None
        best_efficiency = 0
        
        for algo_name, result in config_results.items():
            if result and result.efficiency_percentage > best_efficiency:
                best_result = result
                best_algorithm = algo_name
                best_efficiency = result.efficiency_percentage
        
        if not best_result:
            print(f"  No valid results for {config_name}")
            continue
        
        print(f"  Best algorithm: {best_algorithm} ({best_efficiency:.1f}% efficiency)")
        
        # Generate all tables
        try:
            tables = table_generator.generate_all_tables(best_result, stocks, orders)
            
            # Save each table to CSV
            config_dir = reports_dir / config_name.lower().replace(' ', '_')
            config_dir.mkdir(exist_ok=True)
            
            for table_name, df in tables.items():
                if df is not None and not df.empty:
                    csv_file = config_dir / f"{table_name}.csv"
                    df.to_csv(csv_file, index=False)
                    print(f"  ✓ Saved {table_name}.csv ({len(df)} rows)")
                    
                    # Print sample of key tables
                    if table_name in ['cutting_plan', 'stock_utilization', 'order_fulfillment']:
                        print(f"\n  📊 {table_name.replace('_', ' ').title()} Sample:")
                        print(df.head(3).to_string(index=False, max_cols=8))
            
            # Generate summary report
            summary_file = config_dir / "optimization_summary.txt"
            with open(summary_file, 'w') as f:
                f.write(f"OPTIMIZATION SUMMARY - {config_name}\n")
                f.write("="*50 + "\n\n")
                f.write(f"Algorithm Used: {best_algorithm}\n")
                f.write(f"Optimization Date: {best_result.optimization_date}\n")
                f.write(f"Computation Time: {best_result.computation_time:.3f} seconds\n\n")
                
                f.write("PERFORMANCE METRICS:\n")
                f.write(f"- Efficiency: {best_result.efficiency_percentage:.2f}%\n")
                f.write(f"- Waste: {best_result.waste_percentage:.2f}%\n")
                f.write(f"- Stocks Used: {best_result.total_stock_used}\n")
                f.write(f"- Orders Fulfilled: {best_result.total_orders_fulfilled}/{len(orders)}\n")
                f.write(f"- Fulfillment Rate: {best_result.fulfillment_rate:.2f}%\n")
                f.write(f"- Total Cost: ${best_result.total_cost:.2f}\n")
                f.write(f"- Cost per m²: ${best_result.cost_per_area:.2f}\n\n")
                
                if best_result.metadata:
                    f.write("ALGORITHM DETAILS:\n")
                    for key, value in best_result.metadata.items():
                        if not isinstance(value, dict):
                            f.write(f"- {key}: {value}\n")
                
                f.write(f"\nUNFULFILLED ORDERS ({len(best_result.unfulfilled_orders)}):\n")
                for order in best_result.unfulfilled_orders:
                    f.write(f"- {order.id}: {order.shape} (Priority: {order.priority.name})\n")
            
            print(f"  ✓ Saved optimization_summary.txt")
            
        except Exception as e:
            print(f"  ✗ Report generation failed: {e}")
    
    print(f"\n📁 All reports saved to: {reports_dir.absolute()}")


def display_performance_comparison(results):
    """Display performance comparison table"""
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON MATRIX")
    print("="*80)
    
    # Create comparison table
    import pandas as pd
    
    comparison_data = []
    
    for config_name, config_results in results.items():
        for algo_name, result in config_results.items():
            if result:
                comparison_data.append({
                    'Configuration': config_name,
                    'Algorithm': algo_name,
                    'Efficiency_%': round(result.efficiency_percentage, 2),
                    'Orders_Fulfilled': f"{result.total_orders_fulfilled}/{len(orders)}",
                    'Fulfillment_%': round(result.fulfillment_rate, 2),
                    'Stocks_Used': result.total_stock_used,
                    'Total_Cost_$': round(result.total_cost, 2),
                    'Cost_per_m2_$': round(result.cost_per_area, 2),
                    'Computation_Time_s': round(result.computation_time, 3),
                    'Waste_%': round(result.waste_percentage, 2)
                })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        
        # Sort by efficiency (descending)
        df = df.sort_values('Efficiency_%', ascending=False)
        
        print(df.to_string(index=False))
        
        # Save comparison
        comparison_file = Path("professional_reports/performance_comparison.csv")
        df.to_csv(comparison_file, index=False)
        print(f"\n📊 Performance comparison saved to: {comparison_file}")
        
        # Highlight best performers
        best_efficiency = df.iloc[0]
        best_cost = df.loc[df['Cost_per_m2_$'].idxmin()]
        best_fulfillment = df.loc[df['Fulfillment_%'].idxmax()]
        
        print(f"\n🏆 BEST PERFORMERS:")
        print(f"  Highest Efficiency: {best_efficiency['Algorithm']} ({best_efficiency['Configuration']}) - {best_efficiency['Efficiency_%']}%")
        print(f"  Lowest Cost/m²: {best_cost['Algorithm']} ({best_cost['Configuration']}) - ${best_cost['Cost_per_m2_$']}/m²")
        print(f"  Best Fulfillment: {best_fulfillment['Algorithm']} ({best_fulfillment['Configuration']}) - {best_fulfillment['Fulfillment_%']}%")


def main():
    """Main professional demo function"""
    print("🏭 SURFACE CUTTING OPTIMIZER - PROFESSIONAL DEMONSTRATION")
    print("="*80)
    print("This demo showcases enterprise-grade features:")
    print("• Advanced optimization algorithms (Genetic, Simulated Annealing)")
    print("• Comprehensive reporting system")
    print("• Professional table generation")
    print("• Cost analysis and optimization")
    print("• Performance comparison across algorithms")
    print("• Export capabilities for enterprise integration")
    print("="*80)
    
    try:
        # Setup professional logging
        logger = setup_logging(log_dir="professional_logs")
        logger.start_operation("professional_demonstration")
        
        # Create professional dataset
        stocks, orders = create_professional_dataset()
        
        print(f"\n📊 DATASET OVERVIEW:")
        print(f"  • Stocks: {len(stocks)} (Total value: ${sum(s.total_cost for s in stocks):.2f})")
        print(f"  • Orders: {len(orders)} (Total value: ${sum(getattr(o, 'total_value', 0) for o in orders):.2f})")
        print(f"  • Materials: {len(set(s.material_type for s in stocks))}")
        print(f"  • Customers: {len(set(getattr(o, 'customer_id', '') for o in orders))}")
        
        # Run algorithm comparison
        results = run_algorithm_comparison(stocks, orders)
        
        # Display performance comparison
        display_performance_comparison(results)
        
        # Generate professional reports
        generate_professional_reports(results, stocks, orders)
        
        # Show optimization history and summary
        print(f"\n📈 OPTIMIZATION SUMMARY:")
        summary = logger.get_summary()
        print(f"  • Total Operations: {summary['total_operations']}")
        print(f"  • Success Rate: {summary['success_rate']:.1f}%")
        print(f"  • Total Time: {summary['total_time_seconds']:.3f}s")
        
        # Export logs
        logger.export_logs("professional_logs/demonstration_logs.json")
        
        logger.end_operation("professional_demonstration", success=True)
        
        print(f"\n🎉 PROFESSIONAL DEMONSTRATION COMPLETED!")
        print(f"📁 Check these directories for outputs:")
        print(f"  • professional_reports/ - Comprehensive cutting reports")
        print(f"  • professional_logs/ - Detailed operation logs")
        print(f"\n💼 Ready for enterprise integration!")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()