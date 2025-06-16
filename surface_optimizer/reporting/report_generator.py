"""
Report Generator for Surface Cutting Optimizer
Main report generation and analysis
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..core.models import Stock, Order, CuttingResult
from ..utils.logging import get_logger


@dataclass
class CuttingReport:
    """Main cutting report structure"""
    title: str
    generation_date: datetime
    optimization_result: CuttingResult
    stocks: List[Stock]
    orders: List[Order]
    metadata: Dict[str, Any]


@dataclass  
class PerformanceReport:
    """Performance analysis report"""
    efficiency_metrics: Dict[str, float]
    cost_analysis: Dict[str, float]
    fulfillment_analysis: Dict[str, Any]
    waste_analysis: Dict[str, float]
    optimization_time: float
    
    
@dataclass
class MaterialReport:
    """Material utilization report"""
    material_breakdown: Dict[str, Dict[str, Any]]
    waste_by_material: Dict[str, float]
    cost_by_material: Dict[str, float]
    efficiency_by_material: Dict[str, float]


class ReportGenerator:
    """Main report generator"""
    
    def __init__(self):
        self.logger = get_logger()
        
    def generate_cutting_report(self, result: CuttingResult, stocks: List[Stock], 
                               orders: List[Order], title: str = "Cutting Report") -> CuttingReport:
        """Generate main cutting report"""
        
        return CuttingReport(
            title=title,
            generation_date=datetime.now(),
            optimization_result=result,
            stocks=stocks,
            orders=orders,
            metadata={
                "total_stocks": len(stocks),
                "total_orders": len(orders),
                "efficiency": result.efficiency_percentage,
                "fulfillment_rate": result.fulfillment_rate
            }
        )
    
    def generate_performance_report(self, result: CuttingResult) -> PerformanceReport:
        """Generate performance analysis report"""
        
        return PerformanceReport(
            efficiency_metrics={
                "overall_efficiency": result.efficiency_percentage,
                "waste_percentage": result.waste_percentage,
                "material_utilization": result.efficiency_percentage
            },
            cost_analysis={
                "total_cost": result.total_cost,
                "cost_per_area": result.cost_per_area,
                "cost_efficiency": result.efficiency_percentage / 100.0
            },
            fulfillment_analysis={
                "fulfillment_rate": result.fulfillment_rate,
                "orders_fulfilled": result.total_orders_fulfilled,
                "orders_pending": len(result.unfulfilled_orders)
            },
            waste_analysis={
                "waste_percentage": result.waste_percentage,
                "total_waste_cost": result.total_cost * result.waste_percentage / 100.0
            },
            optimization_time=result.computation_time
        )
    
    def generate_material_report(self, result: CuttingResult, stocks: List[Stock]) -> MaterialReport:
        """Generate material utilization report"""
        
        stock_dict = {stock.id: stock for stock in stocks}
        material_data = {}
        
        # Analyze by material
        for placed_shape in result.placed_shapes:
            stock = stock_dict.get(placed_shape.stock_id)
            if not stock:
                continue
                
            material = stock.material_type.value
            if material not in material_data:
                material_data[material] = {
                    'used_area': 0,
                    'total_area': 0,
                    'cost': 0,
                    'pieces': 0
                }
            
            material_data[material]['used_area'] += placed_shape.shape.area()
            material_data[material]['pieces'] += 1
        
        # Add stock data
        for stock in stocks:
            if any(ps.stock_id == stock.id for ps in result.placed_shapes):
                material = stock.material_type.value
                if material in material_data:
                    material_data[material]['total_area'] += stock.area
                    material_data[material]['cost'] += stock.total_cost
        
        # Calculate metrics
        waste_by_material = {}
        cost_by_material = {}
        efficiency_by_material = {}
        
        for material, data in material_data.items():
            efficiency = (data['used_area'] / data['total_area'] * 100) if data['total_area'] > 0 else 0
            waste = 100 - efficiency
            
            efficiency_by_material[material] = efficiency
            waste_by_material[material] = waste
            cost_by_material[material] = data['cost']
        
        return MaterialReport(
            material_breakdown=material_data,
            waste_by_material=waste_by_material,
            cost_by_material=cost_by_material,
            efficiency_by_material=efficiency_by_material
        )