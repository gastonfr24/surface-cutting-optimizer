#!/usr/bin/env python3
"""
CSV Data Integration Demo - Universal Data-Driven Optimization

Demonstrates how to integrate real-world data from CSV files:
- Load stock and orders from CSV files
- Support multiple material types (glass, wood, metal, etc.)
- Handle different shape types (rectangles, circles, polygons)
- Flexible data validation and error handling
- Professional data processing workflow
"""

import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


class CSVDataLoader:
    """Professional CSV data loader with validation and error handling"""
    
    def __init__(self, data_directory: str = "demo/data"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
    
    def load_stock_data(self, csv_filename: str) -> List[Stock]:
        """Load stock data from CSV with comprehensive validation"""
        
        csv_path = self.data_directory / csv_filename
        print(f"📂 Loading stock data from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Validate required columns
            required_columns = ['stock_id', 'width', 'height', 'thickness', 'material_type', 'cost_per_unit']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            stocks = []
            
            for idx, row in df.iterrows():
                try:
                    # Convert material type string to enum
                    material_type = getattr(MaterialType, row['material_type'].upper())
                    
                    # Validate numeric fields
                    width = float(row['width'])
                    height = float(row['height'])
                    thickness = float(row['thickness'])
                    cost = float(row['cost_per_unit'])
                    
                    if width <= 0 or height <= 0 or thickness <= 0 or cost < 0:
                        print(f"   ⚠️  Row {idx+2}: Invalid dimensions or cost, skipping...")
                        continue
                    
                    stock = Stock(
                        id=str(row['stock_id']),
                        width=width,
                        height=height,
                        thickness=thickness,
                        material_type=material_type,
                        cost_per_unit=cost
                    )
                    
                    # Add optional metadata
                    for optional_field in ['supplier', 'grade', 'wood_type', 'glass_type', 'metal_type']:
                        if optional_field in row and pd.notna(row[optional_field]):
                            setattr(stock, optional_field, str(row[optional_field]))
                    
                    stocks.append(stock)
                    
                except (ValueError, AttributeError) as e:
                    print(f"   ⚠️  Row {idx+2}: Error processing data - {str(e)}, skipping...")
                    continue
            
            print(f"   ✅ Successfully loaded {len(stocks)} stock items")
            
            # Display summary by material type
            material_summary = {}
            for stock in stocks:
                mat_type = stock.material_type.name
                if mat_type not in material_summary:
                    material_summary[mat_type] = {'count': 0, 'total_area': 0, 'total_cost': 0}
                
                area = stock.width * stock.height / 1_000_000  # m²
                material_summary[mat_type]['count'] += 1
                material_summary[mat_type]['total_area'] += area
                material_summary[mat_type]['total_cost'] += stock.cost_per_unit
            
            for mat_type, summary in material_summary.items():
                avg_cost_per_sqm = summary['total_cost'] / summary['total_area'] if summary['total_area'] > 0 else 0
                print(f"      - {mat_type}: {summary['count']} sheets, "
                      f"{summary['total_area']:.1f} m², €{avg_cost_per_sqm:.2f}/m²")
            
            return stocks
            
        except FileNotFoundError:
            print(f"   ❌ CSV file not found: {csv_path}")
            print(f"   💡 Available files in {self.data_directory}:")
            for file in self.data_directory.glob("*.csv"):
                print(f"      - {file.name}")
            return []
            
        except Exception as e:
            print(f"   ❌ Error loading stock CSV: {str(e)}")
            return []
    
    def load_orders_data(self, csv_filename: str) -> List[Order]:
        """Load orders data from CSV with comprehensive validation"""
        
        csv_path = self.data_directory / csv_filename
        print(f"📂 Loading orders data from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Validate required columns
            required_columns = ['order_id', 'shape_type', 'quantity', 'priority', 'material_type', 'thickness']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            orders = []
            
            for idx, row in df.iterrows():
                try:
                    # Convert enums
                    priority = getattr(Priority, row['priority'].upper())
                    material_type = getattr(MaterialType, row['material_type'].upper())
                    
                    # Create shape based on type
                    shape_type = str(row['shape_type']).lower()
                    
                    if shape_type == 'rectangle':
                        if 'width' not in row or 'height' not in row:
                            print(f"   ⚠️  Row {idx+2}: Rectangle missing width/height, skipping...")
                            continue
                        
                        width = float(row['width'])
                        height = float(row['height'])
                        
                        if width <= 0 or height <= 0:
                            print(f"   ⚠️  Row {idx+2}: Invalid rectangle dimensions, skipping...")
                            continue
                        
                        shape = Rectangle(width, height)
                        
                    elif shape_type == 'circle':
                        if 'radius' not in row:
                            print(f"   ⚠️  Row {idx+2}: Circle missing radius, skipping...")
                            continue
                        
                        radius = float(row['radius'])
                        
                        if radius <= 0:
                            print(f"   ⚠️  Row {idx+2}: Invalid circle radius, skipping...")
                            continue
                        
                        shape = Circle(radius)
                        
                    else:
                        print(f"   ⚠️  Row {idx+2}: Unsupported shape type '{shape_type}', skipping...")
                        continue
                    
                    # Validate other fields
                    quantity = int(row['quantity'])
                    thickness = float(row['thickness'])
                    
                    if quantity <= 0 or thickness <= 0:
                        print(f"   ⚠️  Row {idx+2}: Invalid quantity or thickness, skipping...")
                        continue
                    
                    order = Order(
                        id=str(row['order_id']),
                        shape=shape,
                        quantity=quantity,
                        priority=priority,
                        material_type=material_type,
                        thickness=thickness
                    )
                    
                    # Add optional metadata
                    for optional_field in ['description', 'grain_direction', 'finish_type', 'edge_treatment']:
                        if optional_field in row and pd.notna(row[optional_field]):
                            setattr(order, optional_field, str(row[optional_field]))
                    
                    orders.append(order)
                    
                except (ValueError, AttributeError) as e:
                    print(f"   ⚠️  Row {idx+2}: Error processing data - {str(e)}, skipping...")
                    continue
            
            print(f"   ✅ Successfully loaded {len(orders)} order types")
            
            # Display summary
            total_pieces = sum(order.quantity for order in orders)
            total_area = sum(order.shape.area() * order.quantity for order in orders) / 1_000_000  # m²
            
            print(f"   📊 Total pieces: {total_pieces}")
            print(f"   📏 Total area: {total_area:.2f} m²")
            
            # Priority breakdown
            priority_summary = {}
            for order in orders:
                priority_name = order.priority.name
                if priority_name not in priority_summary:
                    priority_summary[priority_name] = 0
                priority_summary[priority_name] += order.quantity
            
            for priority, count in priority_summary.items():
                print(f"      - {priority} priority: {count} pieces")
            
            return orders
            
        except FileNotFoundError:
            print(f"   ❌ CSV file not found: {csv_path}")
            print(f"   💡 Available files in {self.data_directory}:")
            for file in self.data_directory.glob("*.csv"):
                print(f"      - {file.name}")
            return []
            
        except Exception as e:
            print(f"   ❌ Error loading orders CSV: {str(e)}")
            return []
    
    def create_sample_csv_files(self):
        """Create sample CSV files for demonstration"""
        
        print(f"📝 Creating sample CSV files in {self.data_directory}...")
        
        # Sample stock data
        sample_stock = pd.DataFrame([
            {
                'stock_id': 'SAMPLE_001',
                'width': 3000,
                'height': 1500,
                'thickness': 5.0,
                'material_type': 'METAL',
                'cost_per_unit': 150.00,
                'supplier': 'Sample Supplier',
                'grade': 'Standard'
            },
            {
                'stock_id': 'SAMPLE_002',
                'width': 2800,
                'height': 2070,
                'thickness': 18.0,
                'material_type': 'WOOD',
                'cost_per_unit': 285.50,
                'supplier': 'Wood Supplier',
                'wood_type': 'Oak'
            }
        ])
        
        sample_stock.to_csv(self.data_directory / 'sample_stock.csv', index=False)
        
        # Sample orders data
        sample_orders = pd.DataFrame([
            {
                'order_id': 'PART_001',
                'shape_type': 'rectangle',
                'width': 400,
                'height': 300,
                'radius': '',
                'quantity': 5,
                'priority': 'HIGH',
                'material_type': 'METAL',
                'thickness': 5.0,
                'description': 'Sample metal part'
            },
            {
                'order_id': 'CIRCLE_001',
                'shape_type': 'circle',
                'width': '',
                'height': '',
                'radius': 150,
                'quantity': 3,
                'priority': 'MEDIUM',
                'material_type': 'METAL',
                'thickness': 5.0,
                'description': 'Sample circular part'
            }
        ])
        
        sample_orders.to_csv(self.data_directory / 'sample_orders.csv', index=False)
        
        print(f"   ✅ Created sample_stock.csv and sample_orders.csv")


def create_material_specific_config(material_type: MaterialType) -> OptimizationConfig:
    """Create optimized configuration based on material type"""
    
    if material_type == MaterialType.GLASS:
        return OptimizationConfig(
            allow_rotation=False,
            cutting_width=1.5,
            edge_margin=15.0,
            material_waste_factor=0.08,
            prioritize_orders=True,
            max_computation_time=90
        )
    elif material_type == MaterialType.WOOD:
        return OptimizationConfig(
            allow_rotation=True,
            cutting_width=3.2,
            edge_margin=5.0,
            material_waste_factor=0.05,
            prioritize_orders=True,
            max_computation_time=60
        )
    elif material_type == MaterialType.METAL:
        return OptimizationConfig(
            allow_rotation=True,
            cutting_width=4.5,
            edge_margin=10.0,
            material_waste_factor=0.04,
            prioritize_orders=True,
            max_computation_time=75
        )
    else:
        # Default configuration
        return OptimizationConfig(
            allow_rotation=True,
            cutting_width=3.0,
            edge_margin=5.0,
            material_waste_factor=0.05,
            prioritize_orders=True,
            max_computation_time=60
        )


def analyze_csv_data_quality(stocks: List[Stock], orders: List[Order]) -> dict:
    """Analyze the quality and completeness of loaded data"""
    
    analysis = {
        'stock_analysis': {},
        'order_analysis': {},
        'compatibility': {},
        'recommendations': []
    }
    
    # Stock analysis
    if stocks:
        stock_materials = set(stock.material_type for stock in stocks)
        total_stock_area = sum(stock.area for stock in stocks) / 1_000_000  # m²
        total_stock_cost = sum(stock.cost_per_unit for stock in stocks)
        
        analysis['stock_analysis'] = {
            'count': len(stocks),
            'material_types': [mat.name for mat in stock_materials],
            'total_area_m2': round(total_stock_area, 2),
            'total_cost': round(total_stock_cost, 2),
            'avg_cost_per_m2': round(total_stock_cost / total_stock_area, 2) if total_stock_area > 0 else 0
        }
    
    # Order analysis
    if orders:
        order_materials = set(order.material_type for order in orders)
        total_order_pieces = sum(order.quantity for order in orders)
        total_order_area = sum(order.shape.area() * order.quantity for order in orders) / 1_000_000  # m²
        
        analysis['order_analysis'] = {
            'order_types': len(orders),
            'total_pieces': total_order_pieces,
            'material_types': [mat.name for mat in order_materials],
            'total_area_m2': round(total_order_area, 2)
        }
    
    # Compatibility analysis
    if stocks and orders:
        stock_materials = set(stock.material_type for stock in stocks)
        order_materials = set(order.material_type for order in orders)
        
        compatible_materials = stock_materials.intersection(order_materials)
        incompatible_orders = order_materials - stock_materials
        excess_stock = stock_materials - order_materials
        
        analysis['compatibility'] = {
            'compatible_materials': [mat.name for mat in compatible_materials],
            'missing_stock_for': [mat.name for mat in incompatible_orders],
            'excess_stock_types': [mat.name for mat in excess_stock]
        }
        
        # Generate recommendations
        if incompatible_orders:
            analysis['recommendations'].append(
                f"⚠️  Missing stock for materials: {', '.join(mat.name for mat in incompatible_orders)}"
            )
        
        if excess_stock:
            analysis['recommendations'].append(
                f"💡 Excess stock available for: {', '.join(mat.name for mat in excess_stock)}"
            )
        
        # Utilization estimate
        if total_stock_area > 0 and total_order_area > 0:
            theoretical_utilization = (total_order_area / total_stock_area) * 100
            analysis['compatibility']['theoretical_utilization'] = round(theoretical_utilization, 1)
            
            if theoretical_utilization > 95:
                analysis['recommendations'].append("⚠️  Very high material utilization - consider additional stock")
            elif theoretical_utilization < 50:
                analysis['recommendations'].append("💡 Low material utilization - optimize stock selection")
    
    return analysis


def run_optimization_comparison(stocks: List[Stock], orders: List[Order]) -> List[Tuple[str, any]]:
    """Run optimization with multiple algorithms and compare results"""
    
    if not stocks or not orders:
        print("   ❌ Cannot run optimization - missing stock or orders data")
        return []
    
    # Determine primary material type for configuration
    order_materials = [order.material_type for order in orders]
    primary_material = max(set(order_materials), key=order_materials.count)
    
    config = create_material_specific_config(primary_material)
    
    print(f"   ⚙️  Using {primary_material.name} optimized configuration:")
    print(f"      - Rotation allowed: {config.allow_rotation}")
    print(f"      - Cutting width: {config.cutting_width}mm")
    print(f"      - Edge margin: {config.edge_margin}mm")
    print(f"      - Waste factor: {config.material_waste_factor*100:.1f}%")
    
    algorithms = [
        ("Best Fit", BestFitAlgorithm()),
        ("Genetic Algorithm", GeneticAlgorithm(population_size=30, generations=20))
    ]
    
    results = []
    
    for name, algorithm in algorithms:
        print(f"   🔧 Running {name}...")
        
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, config)
        computation_time = time.time() - start_time
        
        print(f"      ⚡ Time: {computation_time:.3f}s")
        print(f"      📊 Efficiency: {result.efficiency_percentage:.1f}%")
        print(f"      ✅ Fulfilled: {result.total_orders_fulfilled}/{sum(o.quantity for o in orders)}")
        
        results.append((name, result))
    
    return results


def main():
    """Main CSV data integration demonstration"""
    print("📊 CSV DATA INTEGRATION DEMO")
    print("Universal Data-Driven Cutting Optimization")
    print("=" * 60)
    
    # Initialize data loader
    loader = CSVDataLoader()
    
    # Check for available CSV files
    available_files = list(loader.data_directory.glob("*.csv"))
    
    print(f"\n📁 Available CSV files in {loader.data_directory}:")
    if available_files:
        for file in available_files:
            print(f"   - {file.name}")
    else:
        print("   No CSV files found - creating samples...")
        loader.create_sample_csv_files()
        available_files = list(loader.data_directory.glob("*.csv"))
    
    # Demo with different material types
    demo_scenarios = [
        ("Glass Cutting", "glass_stock.csv", "glass_orders.csv"),
        ("Furniture Manufacturing", "furniture_stock.csv", "furniture_orders.csv"),
        ("Sample Data", "sample_stock.csv", "sample_orders.csv")
    ]
    
    for scenario_name, stock_file, orders_file in demo_scenarios:
        print(f"\n🎯 {scenario_name.upper()} SCENARIO")
        print("-" * 50)
        
        # Load data
        stocks = loader.load_stock_data(stock_file)
        orders = loader.load_orders_data(orders_file)
        
        if not stocks and not orders:
            print(f"   ⏭️  Skipping {scenario_name} - no data files found")
            continue
        
        # Analyze data quality
        print(f"\n📊 Data Quality Analysis:")
        analysis = analyze_csv_data_quality(stocks, orders)
        
        if analysis['stock_analysis']:
            stock_info = analysis['stock_analysis']
            print(f"   📦 Stock: {stock_info['count']} items, {stock_info['total_area_m2']} m², "
                  f"€{stock_info['avg_cost_per_m2']:.2f}/m²")
        
        if analysis['order_analysis']:
            order_info = analysis['order_analysis']
            print(f"   📋 Orders: {order_info['order_types']} types, {order_info['total_pieces']} pieces, "
                  f"{order_info['total_area_m2']} m²")
        
        if analysis['compatibility']:
            comp_info = analysis['compatibility']
            if 'theoretical_utilization' in comp_info:
                print(f"   📈 Theoretical utilization: {comp_info['theoretical_utilization']}%")
        
        for recommendation in analysis['recommendations']:
            print(f"   {recommendation}")
        
        # Run optimization if data is compatible
        if stocks and orders and analysis['compatibility']['compatible_materials']:
            print(f"\n🚀 Running Optimization:")
            results = run_optimization_comparison(stocks, orders)
            
            if results:
                best_result = max(results, key=lambda x: x[1].efficiency_percentage)
                best_name, best_opt = best_result
                
                print(f"\n   🏆 Best Result: {best_name}")
                print(f"      📊 Efficiency: {best_opt.efficiency_percentage:.1f}%")
                print(f"      📦 Stocks used: {best_opt.total_stock_used}")
                print(f"      ♻️  Waste: {best_opt.waste_percentage:.1f}%")
        
        print()  # Add spacing between scenarios
    
    print("✨ CSV Data Integration Demo Completed!")
    print("\n💡 Key Benefits of CSV Integration:")
    print("   • Real-world data compatibility")
    print("   • Flexible material type support")
    print("   • Professional data validation")
    print("   • Easy integration with ERP systems")
    print("   • Automated error handling and reporting")


if __name__ == "__main__":
    main() 