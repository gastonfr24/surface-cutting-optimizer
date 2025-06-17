#!/usr/bin/env python3
"""
🏢 Professional Surface Cutting Optimizer Demo

This demo showcases the full capabilities of the Surface Cutting Optimizer
in a professional/enterprise context with:

- Realistic industrial datasets
- Multiple algorithm comparison
- Comprehensive performance metrics
- Professional reporting
- Detailed visualizations
- Cost analysis

Ideal for evaluating the library's effectiveness for production use.
"""

import time
import os
import sys
from typing import Dict, List, Any

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from surface_optimizer import SurfaceOptimizer
from surface_optimizer.core.models import OptimizationConfig
from surface_optimizer.utils.visualization import CuttingVisualizer
from surface_optimizer.reporting.report_generator import ReportGenerator
from surface_optimizer.reporting.table_generator import (
    CuttingPlanTable, StockUtilizationTable, 
    OrderFulfillmentTable, CostAnalysisTable
)

class ProfessionalDemo:
    """
    Professional demonstration of the Surface Cutting Optimizer
    
    Features:
    - Enterprise-grade datasets
    - Multi-algorithm benchmarking
    - Professional reporting
    - Cost-benefit analysis
    """
    
    def __init__(self):
        self.optimizer = SurfaceOptimizer()
        self.visualizer = CuttingVisualizer()
        self.report_generator = ReportGenerator()
        self.results_dir = "results"
        
        # Create results directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories for results"""
        directories = [
            self.results_dir,
            f"{self.results_dir}/images",
            f"{self.results_dir}/reports",
            f"{self.results_dir}/tables"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def run_complete_demo(self):
        """Execute complete professional demonstration"""
        print("🏢 Professional Surface Cutting Optimizer Demo")
        print("=" * 60)
        
        # Load realistic datasets
        print("\n📊 Loading enterprise datasets...")
        furniture_case = self._create_furniture_manufacturing_case()
        glass_case = self._create_glass_cutting_case()
        metal_case = self._create_metal_fabrication_case()
        
        test_cases = [
            ("Furniture Manufacturing", furniture_case),
            ("Glass Cutting", glass_case),
            ("Metal Fabrication", metal_case)
        ]
        
        # Run comprehensive analysis for each case
        all_results = {}
        
        for case_name, case_data in test_cases:
            print(f"\n🔬 Analyzing: {case_name}")
            print("-" * 40)
            
            results = self._analyze_case(case_name, case_data)
            all_results[case_name] = results
            
            # Generate individual case report
            self._generate_case_report(case_name, case_data, results)
        
        # Generate comprehensive comparison report
        print("\n📋 Generating comprehensive analysis report...")
        self._generate_comparison_report(all_results)
        
        print("\n✅ Professional demo completed successfully!")
        print(f"📁 Results saved in: {self.results_dir}/")
        
        return all_results
    
    def _create_furniture_manufacturing_case(self) -> Dict:
        """Create realistic furniture manufacturing cutting scenario"""
        
        # Cabinet doors, drawers, shelves, and panels
        orders = [
            # Cabinet doors (high priority)
            {"id": "DOOR_001", "width": 120, "height": 80, "quantity": 15, 
             "material": "MDF_18mm", "priority": 1, "cost_per_unit": 25.0},
            
            # Drawer fronts
            {"id": "DRAWER_001", "width": 60, "height": 40, "quantity": 30, 
             "material": "MDF_18mm", "priority": 2, "cost_per_unit": 12.0},
            
            # Shelves
            {"id": "SHELF_001", "width": 200, "height": 30, "quantity": 8, 
             "material": "MDF_18mm", "priority": 2, "cost_per_unit": 18.0},
            
            # Side panels
            {"id": "PANEL_001", "width": 45, "height": 80, "quantity": 20, 
             "material": "MDF_18mm", "priority": 3, "cost_per_unit": 15.0},
            
            # Backs
            {"id": "BACK_001", "width": 120, "height": 100, "quantity": 10, 
             "material": "MDF_18mm", "priority": 3, "cost_per_unit": 20.0}
        ]
        
        # Standard furniture board sizes
        stock = [
            {"id": "MDF_250x120_18", "width": 250, "height": 120, 
             "material": "MDF_18mm", "cost": 35.0, "quantity": 8},
            
            {"id": "MDF_180x90_18", "width": 180, "height": 90, 
             "material": "MDF_18mm", "cost": 22.0, "quantity": 12},
            
            {"id": "MDF_300x150_18", "width": 300, "height": 150, 
             "material": "MDF_18mm", "cost": 45.0, "quantity": 6}
        ]
        
        return {
            "orders": orders,
            "stock": stock,
            "industry": "Furniture Manufacturing",
            "optimization_config": OptimizationConfig(
                allow_rotation=True,
                max_computation_time=30,
                precision_tolerance=0.5
            )
        }
    
    def _create_glass_cutting_case(self) -> Dict:
        """Create realistic glass cutting scenario"""
        
        # Windows, doors, and decorative panels
        orders = [
            # Standard windows
            {"id": "WIN_001", "width": 150, "height": 100, "quantity": 12,
             "material": "GLASS_4mm", "priority": 1, "cost_per_unit": 45.0},
            
            # Small windows
            {"id": "WIN_002", "width": 80, "height": 60, "quantity": 18,
             "material": "GLASS_4mm", "priority": 2, "cost_per_unit": 25.0},
            
            # Door panels
            {"id": "DOOR_001", "width": 60, "height": 180, "quantity": 6,
             "material": "GLASS_6mm", "priority": 1, "cost_per_unit": 65.0},
            
            # Decorative panels
            {"id": "DECO_001", "width": 40, "height": 40, "quantity": 25,
             "material": "GLASS_4mm", "priority": 3, "cost_per_unit": 15.0}
        ]
        
        # Standard glass sheets
        stock = [
            {"id": "GLASS_300x200_4", "width": 300, "height": 200,
             "material": "GLASS_4mm", "cost": 85.0, "quantity": 8},
            
            {"id": "GLASS_250x180_6", "width": 250, "height": 180,
             "material": "GLASS_6mm", "cost": 120.0, "quantity": 4},
            
            {"id": "GLASS_200x150_4", "width": 200, "height": 150,
             "material": "GLASS_4mm", "cost": 55.0, "quantity": 10}
        ]
        
        return {
            "orders": orders,
            "stock": stock,
            "industry": "Glass Cutting",
            "optimization_config": OptimizationConfig(
                allow_rotation=False,  # Glass typically cannot be rotated
                max_computation_time=45,
                precision_tolerance=0.1
            )
        }
    
    def _create_metal_fabrication_case(self) -> Dict:
        """Create realistic metal fabrication scenario"""
        
        # Brackets, plates, and structural components
        orders = [
            # Structural brackets
            {"id": "BRACKET_001", "width": 100, "height": 150, "quantity": 20,
             "material": "STEEL_3mm", "priority": 1, "cost_per_unit": 35.0},
            
            # Mounting plates
            {"id": "PLATE_001", "width": 80, "height": 80, "quantity": 35,
             "material": "STEEL_3mm", "priority": 2, "cost_per_unit": 18.0},
            
            # Reinforcement strips
            {"id": "STRIP_001", "width": 200, "height": 25, "quantity": 15,
             "material": "STEEL_3mm", "priority": 2, "cost_per_unit": 22.0},
            
            # Small connectors
            {"id": "CONN_001", "width": 30, "height": 50, "quantity": 50,
             "material": "STEEL_3mm", "priority": 3, "cost_per_unit": 8.0}
        ]
        
        # Standard steel sheets
        stock = [
            {"id": "STEEL_300x150_3", "width": 300, "height": 150,
             "material": "STEEL_3mm", "cost": 75.0, "quantity": 10},
            
            {"id": "STEEL_250x200_3", "width": 250, "height": 200,
             "material": "STEEL_3mm", "cost": 85.0, "quantity": 8},
            
            {"id": "STEEL_200x100_3", "width": 200, "height": 100,
             "material": "STEEL_3mm", "cost": 45.0, "quantity": 15}
        ]
        
        return {
            "orders": orders,
            "stock": stock,
            "industry": "Metal Fabrication",
            "optimization_config": OptimizationConfig(
                allow_rotation=True,
                max_computation_time=60,
                precision_tolerance=0.2
            )
        }
    
    def _analyze_case(self, case_name: str, case_data: Dict) -> Dict:
        """Perform comprehensive analysis on a test case"""
        
        orders = case_data["orders"]
        stock = case_data["stock"]
        config = case_data["optimization_config"]
        
        # Test multiple algorithms
        algorithms = ["first_fit", "best_fit", "genetic"]
        if len(orders) <= 50:  # Only test simulated annealing on smaller problems
            algorithms.append("simulated_annealing")
        
        results = {}
        
        for algorithm in algorithms:
            print(f"  🔄 Testing {algorithm}...")
            
            start_time = time.time()
            
            try:
                result = self.optimizer.optimize(
                    orders=orders,
                    stock=stock,
                    algorithm=algorithm,
                    config=config
                )
                
                execution_time = time.time() - start_time
                
                # Calculate additional metrics
                total_pieces = sum(order['quantity'] for order in orders)
                placed_pieces = len(result.placed_shapes)
                fulfillment_rate = (placed_pieces / total_pieces) * 100
                
                # Calculate costs
                cost_analysis = self._calculate_cost_analysis(result, orders, stock)
                
                results[algorithm] = {
                    "result": result,
                    "execution_time": execution_time,
                    "total_pieces": total_pieces,
                    "placed_pieces": placed_pieces,
                    "fulfillment_rate": fulfillment_rate,
                    "cost_analysis": cost_analysis,
                    "performance_rating": self._rate_performance(execution_time, result.efficiency_percentage)
                }
                
                print(f"    ✅ {algorithm}: {result.efficiency_percentage:.1f}% efficiency, "
                      f"{execution_time:.3f}s, {fulfillment_rate:.1f}% fulfillment")
                
            except Exception as e:
                print(f"    ❌ {algorithm}: Error - {str(e)}")
                results[algorithm] = {
                    "error": str(e),
                    "execution_time": time.time() - start_time
                }
        
        return results
    
    def _calculate_cost_analysis(self, result, orders: List[Dict], stock: List[Dict]) -> Dict:
        """Calculate detailed cost analysis"""
        
        # Material costs
        used_stocks = {}
        for shape in result.placed_shapes:
            stock_idx = shape['stock_index']
            if stock_idx not in used_stocks:
                used_stocks[stock_idx] = 0
            used_stocks[stock_idx] += 1
        
        material_cost = sum(stock[idx]['cost'] for idx in used_stocks.keys())
        
        # Production value (theoretical revenue from pieces)
        production_value = 0
        piece_counts = {}
        
        for shape in result.placed_shapes:
            piece_id = shape.get('piece_id', 'unknown')
            base_id = piece_id.split('_')[0] if '_' in piece_id else piece_id
            
            if base_id not in piece_counts:
                piece_counts[base_id] = 0
            piece_counts[base_id] += 1
        
        for order in orders:
            order_id = order['id']
            produced = piece_counts.get(order_id, 0)
            production_value += produced * order.get('cost_per_unit', 0)
        
        # Waste cost
        total_stock_area = sum(
            stock[idx]['width'] * stock[idx]['height'] 
            for idx in used_stocks.keys()
        )
        used_area = sum(
            shape['width'] * shape['height'] 
            for shape in result.placed_shapes
        )
        waste_area = total_stock_area - used_area
        waste_cost = (waste_area / total_stock_area) * material_cost if total_stock_area > 0 else 0
        
        return {
            "material_cost": material_cost,
            "production_value": production_value,
            "waste_cost": waste_cost,
            "net_value": production_value - material_cost,
            "roi_percentage": ((production_value - material_cost) / material_cost * 100) if material_cost > 0 else 0,
            "cost_per_efficiency": material_cost / result.efficiency_percentage if result.efficiency_percentage > 0 else 0
        }
    
    def _rate_performance(self, execution_time: float, efficiency: float) -> str:
        """Rate algorithm performance"""
        
        # Combined performance score
        time_score = 1.0 if execution_time < 1 else (5.0 / execution_time) if execution_time < 5 else 0.2
        efficiency_score = efficiency / 100.0
        
        combined_score = (time_score * 0.3 + efficiency_score * 0.7)
        
        if combined_score >= 0.8:
            return "Excellent"
        elif combined_score >= 0.6:
            return "Good"
        elif combined_score >= 0.4:
            return "Acceptable"
        else:
            return "Slow"
    
    def _generate_case_report(self, case_name: str, case_data: Dict, results: Dict):
        """Generate detailed report for individual case"""
        
        print(f"  📋 Generating report for {case_name}...")
        
        # Generate visualizations for best result
        best_algorithm = max(
            [alg for alg in results.keys() if 'result' in results[alg]],
            key=lambda alg: results[alg]['result'].efficiency_percentage,
            default=None
        )
        
        if best_algorithm and 'result' in results[best_algorithm]:
            best_result = results[best_algorithm]['result']
            
            # Create visualization
            image_path = f"{self.results_dir}/images/{case_name.lower().replace(' ', '_')}_best.png"
            self.visualizer.create_cutting_layout_visualization(
                best_result, case_data['stock'], 
                title=f"{case_name} - {best_algorithm.title()} Algorithm",
                save_path=image_path
            )
        
        # Generate detailed tables
        self._generate_case_tables(case_name, case_data, results)
    
    def _generate_case_tables(self, case_name: str, case_data: Dict, results: Dict):
        """Generate detailed tables for case analysis"""
        
        # Algorithm comparison table
        table_data = []
        for algorithm, result_data in results.items():
            if 'result' in result_data:
                result = result_data['result']
                cost = result_data['cost_analysis']
                
                table_data.append({
                    'Algorithm': algorithm.title(),
                    'Efficiency (%)': f"{result.efficiency_percentage:.1f}",
                    'Time (s)': f"{result_data['execution_time']:.3f}",
                    'Fulfillment (%)': f"{result_data['fulfillment_rate']:.1f}",
                    'Material Cost': f"${cost['material_cost']:.2f}",
                    'Net Value': f"${cost['net_value']:.2f}",
                    'ROI (%)': f"{cost['roi_percentage']:.1f}",
                    'Rating': result_data['performance_rating']
                })
        
        # Save comparison table
        comparison_table = CuttingPlanTable()
        comparison_html = comparison_table.create_algorithm_comparison_table(table_data)
        
        table_path = f"{self.results_dir}/tables/{case_name.lower().replace(' ', '_')}_comparison.html"
        with open(table_path, 'w', encoding='utf-8') as f:
            f.write(comparison_html)
    
    def _generate_comparison_report(self, all_results: Dict):
        """Generate comprehensive comparison report across all cases"""
        
        # Create summary comparison
        summary_data = []
        
        for case_name, case_results in all_results.items():
            for algorithm, result_data in case_results.items():
                if 'result' in result_data:
                    result = result_data['result']
                    cost = result_data['cost_analysis']
                    
                    summary_data.append({
                        'Case': case_name,
                        'Algorithm': algorithm.title(),
                        'Efficiency (%)': result.efficiency_percentage,
                        'Time (s)': result_data['execution_time'],
                        'Fulfillment (%)': result_data['fulfillment_rate'],
                        'Material Cost': cost['material_cost'],
                        'Net Value': cost['net_value'],
                        'ROI (%)': cost['roi_percentage'],
                        'Rating': result_data['performance_rating']
                    })
        
        # Generate comprehensive report
        report_content = self._create_executive_summary(summary_data, all_results)
        
        report_path = f"{self.results_dir}/reports/executive_summary.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"  📊 Executive summary saved: {report_path}")
    
    def _create_executive_summary(self, summary_data: List[Dict], all_results: Dict) -> str:
        """Create executive summary HTML report"""
        
        # Calculate aggregate statistics
        best_efficiency_by_case = {}
        best_algorithm_by_case = {}
        
        for case_name, case_results in all_results.items():
            best_eff = 0
            best_alg = None
            
            for algorithm, result_data in case_results.items():
                if 'result' in result_data:
                    eff = result_data['result'].efficiency_percentage
                    if eff > best_eff:
                        best_eff = eff
                        best_alg = algorithm
            
            best_efficiency_by_case[case_name] = best_eff
            best_algorithm_by_case[case_name] = best_alg
        
        # Calculate overall statistics
        total_cases = len(all_results)
        avg_efficiency = sum(best_efficiency_by_case.values()) / total_cases if total_cases > 0 else 0
        
        algorithm_performance = {}
        for data in summary_data:
            alg = data['Algorithm']
            if alg not in algorithm_performance:
                algorithm_performance[alg] = []
            algorithm_performance[alg].append(data['Efficiency (%)'])
        
        avg_by_algorithm = {
            alg: sum(efficiencies) / len(efficiencies)
            for alg, efficiencies in algorithm_performance.items()
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Surface Cutting Optimizer - Executive Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ text-align: center; padding: 20px; background: #ecf0f1; border-radius: 5px; }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #27ae60; }}
                .metric-label {{ color: #7f8c8d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #34495e; color: white; }}
                .excellent {{ color: #27ae60; font-weight: bold; }}
                .good {{ color: #f39c12; font-weight: bold; }}
                .acceptable {{ color: #e67e22; font-weight: bold; }}
                .slow {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏢 Surface Cutting Optimizer</h1>
                <h2>Executive Summary Report</h2>
                <p>Professional Performance Analysis</p>
            </div>
            
            <div class="section">
                <h2>📊 Key Performance Indicators</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{avg_efficiency:.1f}%</div>
                        <div class="metric-label">Average Efficiency</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{total_cases}</div>
                        <div class="metric-label">Test Cases</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{len(avg_by_algorithm)}</div>
                        <div class="metric-label">Algorithms Tested</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Best Results by Industry</h2>
                <table>
                    <tr>
                        <th>Industry</th>
                        <th>Best Algorithm</th>
                        <th>Efficiency</th>
                        <th>Status</th>
                    </tr>
        """
        
        for case_name in best_efficiency_by_case:
            efficiency = best_efficiency_by_case[case_name]
            algorithm = best_algorithm_by_case[case_name]
            status = "Excellent" if efficiency >= 80 else "Good" if efficiency >= 65 else "Acceptable"
            status_class = status.lower()
            
            html_content += f"""
                    <tr>
                        <td>{case_name}</td>
                        <td>{algorithm.title() if algorithm else 'N/A'}</td>
                        <td>{efficiency:.1f}%</td>
                        <td class="{status_class}">{status}</td>
                    </tr>
            """
        
        html_content += f"""
                </table>
            </div>
            
            <div class="section">
                <h2>⚙️ Algorithm Performance Summary</h2>
                <table>
                    <tr>
                        <th>Algorithm</th>
                        <th>Average Efficiency</th>
                        <th>Recommendation</th>
                    </tr>
        """
        
        for algorithm, avg_eff in sorted(avg_by_algorithm.items(), key=lambda x: x[1], reverse=True):
            if avg_eff >= 80:
                recommendation = "Excellent for production use"
                rec_class = "excellent"
            elif avg_eff >= 65:
                recommendation = "Good for most applications"
                rec_class = "good"
            elif avg_eff >= 50:
                recommendation = "Suitable for development/testing"
                rec_class = "acceptable"
            else:
                recommendation = "Not recommended for production"
                rec_class = "slow"
            
            html_content += f"""
                    <tr>
                        <td>{algorithm}</td>
                        <td>{avg_eff:.1f}%</td>
                        <td class="{rec_class}">{recommendation}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>💡 Key Recommendations</h2>
                <ul>
                    <li><strong>For Production:</strong> Use Genetic Algorithm for maximum efficiency</li>
                    <li><strong>For Development:</strong> Use First Fit for rapid prototyping</li>
                    <li><strong>For Balance:</strong> Use Best Fit for good speed/quality ratio</li>
                    <li><strong>For Complex Problems:</strong> Allow more computation time for better results</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>📈 Performance Notes</h2>
                <p><strong>Excellent:</strong> High efficiency, suitable for production use</p>
                <p><strong>Good:</strong> Acceptable efficiency for most applications</p>
                <p><strong>Acceptable:</strong> Basic efficiency, suitable for non-critical use</p>
                <p><strong>Slow:</strong> Low efficiency, optimization needed</p>
            </div>
        </body>
        </html>
        """
        
        return html_content


def main():
    """Run professional demonstration"""
    
    print("🚀 Starting Professional Surface Cutting Optimizer Demo")
    
    try:
        demo = ProfessionalDemo()
        results = demo.run_complete_demo()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📁 Generated files:")
        print("   - Executive summary: results/reports/executive_summary.html")
        print("   - Individual case visualizations: results/images/")
        print("   - Detailed comparison tables: results/tables/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)