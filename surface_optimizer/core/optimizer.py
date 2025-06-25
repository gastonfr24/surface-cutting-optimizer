"""
Main optimizer class for Surface Cutting Optimizer
Enhanced with logging and advanced features
"""

import time
from typing import List, Optional, Dict, Any
from pathlib import Path
from .models import Stock, Order, CuttingResult, OptimizationConfig
from .validators import validate_stocks, validate_orders, validate_stock_order_compatibility
from .exceptions import OptimizationError, ValidationError
from ..algorithms.base import BaseAlgorithm
from ..utils.logging import get_logger, OptimizationLogger


class Optimizer:
    """Main optimizer class that coordinates algorithms and validation"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None, logger: Optional[OptimizationLogger] = None):
        self.config = config or OptimizationConfig()
        self.algorithm: Optional[BaseAlgorithm] = None
        self.logger = logger or get_logger()
        self.optimization_history: List[CuttingResult] = []
        self._last_result: Optional[CuttingResult] = None
        self._last_stocks: Optional[List[Stock]] = None
        self._last_orders: Optional[List[Order]] = None
    
    def set_algorithm(self, algorithm: BaseAlgorithm):
        """Set the optimization algorithm to use"""
        self.algorithm = algorithm
    
    def optimize(self, stocks: List[Stock], orders: List[Order]) -> CuttingResult:
        """
        Optimize cutting plan for given stocks and orders
        
        Args:
            stocks: List of available stock materials
            orders: List of cutting orders to fulfill
            
        Returns:
            CuttingResult with optimization results
            
        Raises:
            OptimizationError: If optimization fails
            ValidationError: If inputs are invalid
        """
        self.logger.start_operation("optimize", {
            "stocks_count": len(stocks),
            "orders_count": len(orders),
            "algorithm": self.algorithm.name if self.algorithm else "None"
        })
        
        try:
            # Log initialization
            self.logger.info("📊 OPTIMIZATION ANALYSIS:")
            
            # Calculate areas
            total_stock_area = sum(stock.area for stock in stocks)
            total_demand_area = sum(order.total_area for order in orders)
            utilization = (total_demand_area / total_stock_area * 100) if total_stock_area > 0 else 0
            
            self.logger.info(f"   • Stock panels: {len(stocks)} ({total_stock_area:,.0f} mm²)")
            self.logger.info(f"   • Orders: {len(orders)} ({total_demand_area:,.0f} mm²)")
            self.logger.info(f"   • Theoretical utilization: {utilization:.1f}%")
            
            if utilization > 100:
                self.logger.warning(f"   ⚠️  Demand exceeds available stock by {utilization - 100:.1f}%")
            elif utilization > 85:
                self.logger.info(f"   ⚡ High utilization - optimization will be challenging")
            else:
                self.logger.info(f"   ✅ Sufficient stock available")
            
            # Validate configuration
            config_issues = self.config.validate()
            if config_issues:
                self.logger.log_validation("configuration", 1, config_issues)
                raise OptimizationError(f"Invalid configuration: {'; '.join(config_issues)}")
            
            # Handle empty orders case early
            if not orders:
                self.logger.info("   ℹ️  No orders to process - returning empty result")
                empty_result = CuttingResult()
                empty_result.computation_time = time.time() - time.time()
                empty_result.efficiency_percentage = 0.0
                empty_result.total_stock_used = 0
                empty_result.total_orders_fulfilled = 0
                empty_result.total_cost = 0.0
                empty_result.placed_shapes = []
                empty_result.unfulfilled_orders = []
                
                # Store empty result for reporting
                self._last_result = empty_result
                self._last_stocks = stocks
                self._last_orders = orders
                self.optimization_history.append(empty_result)
                
                self.logger.end_operation("optimize", success=True, 
                                        result={"message": "No orders to process"})
                return empty_result
            
            # Validate inputs
            try:
                stock_issues = []
                order_issues = []
                
                for stock in stocks:
                    stock_issues.extend(stock.validate())
                
                for order in orders:
                    order_issues.extend(order.validate())
                
                self.logger.log_validation("stocks", len(stocks), stock_issues)
                self.logger.log_validation("orders", len(orders), order_issues)
                
                validate_stocks(stocks)
                validate_orders(orders)
                if orders:  # Only validate compatibility if there are orders
                    validate_stock_order_compatibility(stocks, orders)
                
            except ValidationError as e:
                self.logger.end_operation("optimize", success=False, 
                                        result={"error": f"Validation failed: {e}"})
                raise OptimizationError(f"Validation failed: {e}")
            
            # Check algorithm is set
            if self.algorithm is None:
                self.logger.end_operation("optimize", success=False, 
                                        result={"error": "No algorithm set"})
                raise OptimizationError("No algorithm set. Use set_algorithm() first.")
            
            # Log algorithm start
            self.logger.log_algorithm_start(self.algorithm.name, len(stocks), len(orders))
            
            # Track computation time
            start_time = time.time()
            
            # Run optimization
            result = self.algorithm.optimize(stocks, orders, self.config)
            
            # Set computation time
            result.computation_time = time.time() - start_time
            
            # Calculate costs
            result.total_cost = sum(stock.total_cost for stock in stocks 
                                  if any(ps.stock_id == stock.id for ps in result.placed_shapes))
            
            # Validate result
            self._validate_result(result, stocks, orders)
            
            # Log results
            result_summary = {
                "stocks_used": result.total_stock_used,
                "orders_fulfilled": result.total_orders_fulfilled,
                "efficiency": result.efficiency_percentage,
                "computation_time": result.computation_time,
                "total_cost": result.total_cost
            }
            
            self.logger.log_algorithm_result(result_summary)
            self.logger.end_operation("optimize", success=True, result=result_summary)
            
            # Store in history and cache for convenience methods
            self.optimization_history.append(result)
            self._last_result = result
            self._last_stocks = stocks
            self._last_orders = orders
            
            return result
            
        except Exception as e:
            self.logger.end_operation("optimize", success=False, 
                                    result={"error": str(e)})
            raise OptimizationError(f"Optimization failed: {e}")
    
    def visualize(self, save_path: Optional[str] = None, output_dir: str = "visualizations") -> bool:
        """
        Visualize the last optimization result
        
        Args:
            save_path: Filename to save (None to show interactively)
            output_dir: Directory to save visualization
            
        Returns:
            True if successful, False otherwise
        """
        if not self._last_result or not self._last_stocks:
            print("❌ No optimization result to visualize. Run optimize() first.")
            return False
        
        try:
            from ..utils.visualization import visualize_cutting_plan
            visualize_cutting_plan(self._last_result, self._last_stocks, save_path, output_dir)
            if save_path:
                print(f"✅ Visualization saved: {output_dir}/{save_path}")
            return True
        except Exception as e:
            print(f"❌ Visualization failed: {e}")
            return False
    
    def generate_report(self, format: str = "json", save_path: Optional[str] = None, 
                       output_dir: str = "reports", config: Optional[Any] = None) -> Dict[str, Any]:
        """
        🚀 ADVANCED REPORT GENERATOR with full customization support
        
        ✅ Multiple formats: JSON, HTML, PDF, Excel, CSV, XML, Markdown, TXT
        ✅ Full customization: language, company info, project details
        ✅ Advanced filters: material, priority, size, efficiency ranges
        ✅ Usage-specific configs: CNC, accounting, presentation, audit
        ✅ Industrial standards: metric/imperial units, precision control
        ✅ Compliance: ISO standards, traceability, digital signatures
        
        Args:
            format: Basic format ('json', 'coordinates', 'performance', 'material') or 
                   Advanced format via config.format (HTML, PDF, Excel, etc.)
            save_path: Filename to save (None for no file output)
            output_dir: Directory to save report
            config: Advanced ReportConfig for full customization. Examples:
            
                # Professional presentation report in Spanish
                config = ReportConfig(
                    format=ReportFormat.HTML,
                    language=ReportLanguage.SPANISH,
                    usage=ReportUsage.PRESENTATION,
                    company_info=CompanyInfo(name="Mi Empresa", address="Madrid"),
                    project_info=ProjectInfo(name="Proyecto 2024", client="Cliente VIP"),
                    filters=FilterCriteria(materials=[MaterialType.WOOD], min_efficiency=60.0),
                    unit_system=UnitSystem.METRIC,
                    compliance_standards=[ComplianceStandard.ISO_9001],
                    include_recommendations=True,
                    confidentiality_level="confidential"
                )
                
                # CNC machine instructions in English
                config = ReportConfig(
                    format=ReportFormat.XML,
                    language=ReportLanguage.ENGLISH,
                    usage=ReportUsage.CNC_MACHINE,
                    unit_system=UnitSystem.IMPERIAL,
                    include_cutting_instructions=True,
                    decimal_precision=3
                )
                
                # Compliance audit report
                config = ReportConfig(
                    format=ReportFormat.PDF,
                    usage=ReportUsage.AUDIT,
                    compliance_standards=[ComplianceStandard.ISO_9001, ComplianceStandard.ISO_14001],
                    include_signatures=True,
                    digital_signature=True,
                    confidentiality_level="restricted"
                )
            
        Returns:
            Report data as dictionary or file path for advanced reports
        """
        if not self._last_result:
            print("❌ No optimization result to report. Run optimize() first.")
            return {}
        
        try:
            from ..reporting.report_generator import ReportGenerator, ReportConfig, ReportFormat
            report_gen = ReportGenerator()
            
            # 🚀 ADVANCED REPORT HANDLING
            if config is not None and not isinstance(config, dict):
                # Advanced ReportConfig object - use new system
                from ..reporting.report_generator import ReportFormat
                
                if not save_path:
                    print("⚠️ Advanced reports require save_path. Defaulting to 'advanced_report'")
                    save_path = "advanced_report"
                
                format_extensions = {
                    ReportFormat.JSON: ".json",
                    ReportFormat.HTML: ".html",
                    ReportFormat.PDF: ".pdf",
                    ReportFormat.EXCEL: ".xlsx",
                    ReportFormat.CSV: ".csv",
                    ReportFormat.XML: ".xml",
                    ReportFormat.MARKDOWN: ".md",
                    ReportFormat.TXT: ".txt"
                }
                
                ext = format_extensions.get(config.format, ".json")
                if not save_path.endswith(ext):
                    save_path = save_path + ext
                
                output_path = Path(output_dir) / save_path
                output_path.parent.mkdir(exist_ok=True, parents=True)
                
                generated_path = report_gen.generate_advanced_report(
                    self._last_result, self._last_stocks, self._last_orders, config, str(output_path)
                )
                
                print(f"✅ Advanced {config.format.value.upper()} report saved: {generated_path}")
                print(f"   📋 Language: {config.language.value}")
                print(f"   🎯 Usage: {config.usage.value}")
                print(f"   📏 Units: {config.unit_system.value}")
                if config.filters:
                    print(f"   🔍 Filters applied: Yes")
                if config.compliance_standards:
                    print(f"   ✅ Compliance: {', '.join(std.value for std in config.compliance_standards)}")
                
                return {"generated_file": generated_path, "format": config.format.value}
            
            # 📊 LEGACY REPORT HANDLING (for backward compatibility)
            else:
                if format == "coordinates":
                    report = report_gen.generate_cutting_coordinates_report(self._last_result, self._last_stocks)
                    data = {
                        "summary": report.summary,
                        "cutting_plan": report.cutting_plan,
                        "generated_date": report.generation_date.isoformat()
                    }
                elif format == "performance":
                    report = report_gen.generate_performance_report(self._last_result)
                    data = {
                        "efficiency_metrics": report.efficiency_metrics,
                        "cost_analysis": report.cost_analysis,
                        "fulfillment_analysis": report.fulfillment_analysis,
                        "waste_analysis": report.waste_analysis,
                        "optimization_time": report.optimization_time
                    }
                elif format == "material":
                    report = report_gen.generate_material_report(self._last_result, self._last_stocks)
                    data = {
                        "material_breakdown": report.material_breakdown,
                        "waste_by_material": report.waste_by_material,
                        "cost_by_material": report.cost_by_material,
                        "efficiency_by_material": report.efficiency_by_material
                    }
                elif format == "html":
                    # Generate HTML report
                    cutting_report = report_gen.generate_cutting_report(
                        self._last_result, self._last_stocks, self._last_orders, "Optimization Report"
                    )
                    performance_report = report_gen.generate_performance_report(self._last_result)
                    
                    # Create HTML content
                    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cutting_report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metric {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .metric strong {{ color: #2980b9; }}
        .efficiency {{ font-size: 1.2em; color: #27ae60; font-weight: bold; }}
        .cost {{ color: #e74c3c; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        .footer {{ margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{cutting_report.title}</h1>
        <p><strong>Generated:</strong> {cutting_report.generation_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📊 Performance Summary</h2>
        <div class="metric">
            <strong>Overall Efficiency:</strong> 
            <span class="efficiency">{performance_report.efficiency_metrics['overall_efficiency']:.1f}%</span>
        </div>
        <div class="metric">
            <strong>Material Utilization:</strong> {performance_report.efficiency_metrics['material_utilization']:.1f}%
        </div>
        <div class="metric">
            <strong>Fulfillment Rate:</strong> {performance_report.fulfillment_analysis['fulfillment_rate']:.1f}%
        </div>
        
        <h2>💰 Cost Analysis</h2>
        <div class="metric">
            <strong>Total Cost:</strong> 
            <span class="cost">${performance_report.cost_analysis['total_cost']:.2f}</span>
        </div>
        <div class="metric">
            <strong>Cost per Area:</strong> ${performance_report.cost_analysis['cost_per_area']:.2f}/m²
        </div>
        <div class="metric">
            <strong>Waste Cost:</strong> 
            <span class="cost">${performance_report.waste_analysis['total_waste_cost']:.2f}</span>
        </div>
        
        <h2>📋 Summary Statistics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Stocks</td><td>{cutting_report.metadata.get('total_stocks', 0)}</td></tr>
            <tr><td>Total Orders</td><td>{cutting_report.metadata.get('total_orders', 0)}</td></tr>
            <tr><td>Orders Fulfilled</td><td>{performance_report.fulfillment_analysis['orders_fulfilled']}</td></tr>
            <tr><td>Computation Time</td><td>{performance_report.optimization_time:.3f}s</td></tr>
            <tr><td>Algorithm Used</td><td>{self._last_result.algorithm_used}</td></tr>
        </table>
        
        <div class="footer">
            <p>Report generated by Surface Cutting Optimizer</p>
        </div>
    </div>
</body>
</html>"""
                    data = html_content
                else:  # json (full report)
                    cutting_report = report_gen.generate_cutting_report(
                        self._last_result, self._last_stocks, self._last_orders, "Optimization Report"
                    )
                    performance_report = report_gen.generate_performance_report(self._last_result)
                    
                    data = {
                        "title": cutting_report.title,
                        "generation_date": cutting_report.generation_date.isoformat(),
                        "summary": cutting_report.metadata,
                        "performance": {
                            "efficiency_metrics": performance_report.efficiency_metrics,
                            "cost_analysis": performance_report.cost_analysis,
                            "fulfillment_analysis": performance_report.fulfillment_analysis,
                            "waste_analysis": performance_report.waste_analysis,
                            "optimization_time": performance_report.optimization_time
                        },
                        "algorithm": self._last_result.algorithm_used,
                        "metadata": self._last_result.metadata
                    }
                
                # Save if requested
                if save_path:
                    output_path = Path(output_dir)
                    output_path.mkdir(exist_ok=True, parents=True)  # Create parent directories
                    
                    full_path = output_path / save_path
                    
                    if format == "html":
                        # Save as HTML text file
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(data)
                    else:
                        # Save as JSON
                        import json
                        with open(full_path, 'w') as f:
                            json.dump(data, f, indent=2)
                    
                    print(f"✅ Report saved: {full_path}")
                
                return data
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def save_results(self, output_dir: str = "results", prefix: str = "optimization") -> bool:
        """
        Save both visualization and report (convenience method)
        
        Args:
            output_dir: Directory to save files
            prefix: Filename prefix
            
        Returns:
            True if successful, False otherwise
        """
        if not self._last_result:
            print("❌ No optimization result to save. Run optimize() first.")
            return False
        
        try:
            # Save visualization
            viz_success = self.visualize(f"{prefix}_layout.png", output_dir)
            
            # Save full report
            report_success = self.generate_report("json", f"{prefix}_report.json", output_dir) != {}
            
            # Save cutting coordinates
            coord_success = self.generate_report("coordinates", f"{prefix}_coordinates.json", output_dir) != {}
            
            if viz_success and report_success and coord_success:
                print(f"✅ All files saved to: {output_dir}/")
                return True
            else:
                print("⚠️ Some files failed to save")
                return False
                
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def compare_algorithms(self, algorithms: List[BaseAlgorithm], 
                          stocks: List[Stock], orders: List[Order]) -> List[CuttingResult]:
        """
        Compare multiple algorithms on the same problem
        
        Args:
            algorithms: List of algorithms to compare
            stocks: Stock materials
            orders: Orders to fulfill
            
        Returns:
            List of CuttingResult, one per algorithm
        """
        results = []
        
        for algorithm in algorithms:
            original_algorithm = self.algorithm
            self.set_algorithm(algorithm)
            
            try:
                result = self.optimize(stocks, orders)
                results.append(result)
            except Exception as e:
                # Create failed result
                failed_result = CuttingResult()
                failed_result.algorithm_used = algorithm.name
                failed_result.metadata = {"error": str(e)}
                results.append(failed_result)
            
            # Restore original algorithm
            self.algorithm = original_algorithm
        
        return results
    
    def plot_comparison(self, results: List[CuttingResult], algorithm_names: List[str], 
                       save_path: Optional[str] = None, output_dir: str = "visualizations") -> bool:
        """
        Plot algorithm comparison results
        
        Args:
            results: List of CuttingResult from compare_algorithms
            algorithm_names: Names of algorithms
            save_path: Filename to save (None to show)
            output_dir: Directory to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from ..utils.visualization import plot_algorithm_comparison
            plot_algorithm_comparison(results, algorithm_names, save_path, output_dir)
            if save_path:
                print(f"✅ Comparison chart saved: {output_dir}/{save_path}")
            return True
        except Exception as e:
            print(f"❌ Comparison plot failed: {e}")
            return False
    
    def _validate_result(self, result: CuttingResult, 
                        stocks: List[Stock], orders: List[Order]):
        """Validate optimization result"""
        # Basic sanity checks
        if result.total_stock_used < 0:
            raise OptimizationError("Invalid result: negative stock usage")
        
        if result.total_orders_fulfilled < 0:
            raise OptimizationError("Invalid result: negative orders fulfilled")
        
        if result.efficiency_percentage < 0 or result.efficiency_percentage > 100:
            raise OptimizationError(f"Invalid efficiency: {result.efficiency_percentage}%")
        
        # Check placed shapes don't exceed stock bounds
        stock_dict = {stock.id: stock for stock in stocks}
        
        for placed_shape in result.placed_shapes:
            stock = stock_dict.get(placed_shape.stock_id)
            if not stock:
                raise OptimizationError(f"Placed shape references unknown stock: {placed_shape.stock_id}")
            
            # Check shape fits in stock (basic check)
            shape = placed_shape.shape
            if (shape.x < 0 or shape.y < 0 or 
                shape.x + getattr(shape, 'width', 0) > stock.width or
                shape.y + getattr(shape, 'height', 0) > stock.height):
                raise OptimizationError(f"Placed shape exceeds stock bounds: {placed_shape}")
    
    def get_optimization_history(self) -> List[CuttingResult]:
        """Get history of all optimizations performed"""
        return self.optimization_history.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of all optimizations"""
        if not self.optimization_history:
            return {"message": "No optimizations performed yet"}
        
        results = self.optimization_history
        
        return {
            "total_optimizations": len(results),
            "average_efficiency": sum(r.efficiency_percentage for r in results) / len(results),
            "average_computation_time": sum(r.computation_time for r in results) / len(results),
            "total_time": sum(r.computation_time for r in results),
            "total_stocks_used": sum(r.total_stock_used for r in results),
            "total_orders_fulfilled": sum(r.total_orders_fulfilled for r in results),
            "total_cost": sum(r.total_cost for r in results),
            "best_efficiency": max(r.efficiency_percentage for r in results),
            "worst_efficiency": min(r.efficiency_percentage for r in results),
        }
    
    def export_logs(self, filepath: str):
        """Export optimization logs to file"""
        self.logger.export_logs(filepath)
    
    def clear_history(self):
        """Clear optimization history"""
        self.optimization_history.clear()
        self.logger.info("Optimization history cleared")
    
    def __str__(self):
        algorithm_name = self.algorithm.name if self.algorithm else "None"
        history_count = len(self.optimization_history)
        return f"Optimizer(algorithm={algorithm_name}, optimizations={history_count})" 