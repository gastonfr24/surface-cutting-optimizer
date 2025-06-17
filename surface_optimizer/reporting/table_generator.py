"""
📊 Professional Table Generator for Cutting Optimization Reports

This module provides specialized table generators for creating professional
reports with cutting plans, stock utilization, order fulfillment, and cost analysis.

Features:
- HTML tables with professional styling
- Export to Excel, PDF, and CSV
- Customizable formatting and branding
- Interactive elements for web reports
- Performance metrics visualization
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..core.models import Stock, Order, CuttingResult, PlacedShape, MaterialType
from ..utils.logging import get_logger


@dataclass
class TableConfig:
    """Configuration for table generation"""
    show_material_details: bool = True
    show_cost_breakdown: bool = True
    show_waste_analysis: bool = True
    show_timestamps: bool = True
    currency_symbol: str = "$"
    area_unit: str = "m²"
    precision: int = 2


class CuttingPlanTable:
    """
    Professional table generator for cutting plans
    
    Creates detailed tables showing piece placements, stock usage,
    and optimization metrics with professional formatting.
    """
    
    def __init__(self, config: Optional[TableConfig] = None):
        self.config = config or TableConfig()
        self.logger = get_logger()
    
    def generate(self, result: CuttingResult, stocks: List[Stock], 
                orders: List[Order]) -> pd.DataFrame:
        """Generate cutting plan table"""
        
        self.logger.start_operation("generate_cutting_plan_table")
        
        try:
            # Create lookup dictionaries
            stock_dict = {stock.id: stock for stock in stocks}
            
            # Build order lookup (handle expanded orders)
            order_dict = {}
            for order in orders:
                order_dict[order.id] = order
                # Also add expanded versions
                for i in range(order.quantity):
                    order_dict[f"{order.id}_{i+1}"] = order
            
            data = []
            
            for i, placed_shape in enumerate(result.placed_shapes, 1):
                stock = stock_dict.get(placed_shape.stock_id)
                order = order_dict.get(placed_shape.order_id)
                
                if not stock or not order:
                    continue
                
                # Extract sequence number from expanded order ID
                if '_' in placed_shape.order_id:
                    base_order_id, sequence = placed_shape.order_id.rsplit('_', 1)
                else:
                    base_order_id = placed_shape.order_id
                    sequence = "1"
                
                row = {
                    'Cut_ID': f"CUT_{i:03d}",
                    'Order_ID': base_order_id,
                    'Sequence': sequence,
                    'Stock_ID': stock.id,
                    'Material': stock.material_type.value.title(),
                    'Thickness_mm': stock.thickness,
                    'Shape_Type': placed_shape.shape.__class__.__name__,
                    'Position_X_mm': round(placed_shape.shape.x, self.config.precision),
                    'Position_Y_mm': round(placed_shape.shape.y, self.config.precision),
                    'Rotation_deg': placed_shape.rotation_applied,
                    'Area_mm2': round(placed_shape.shape.area(), self.config.precision),
                    'Area_m2': round(placed_shape.shape.area() / 1_000_000, 4),
                    'Priority': order.priority.name,
                    'Customer_ID': getattr(order, 'customer_id', ''),
                }
                
                # Add shape-specific dimensions
                if hasattr(placed_shape.shape, 'width'):
                    row['Width_mm'] = placed_shape.shape.width
                    row['Height_mm'] = placed_shape.shape.height
                elif hasattr(placed_shape.shape, 'radius'):
                    row['Radius_mm'] = placed_shape.shape.radius
                    row['Diameter_mm'] = placed_shape.shape.radius * 2
                
                # Add cost information
                if self.config.show_cost_breakdown:
                    stock_area_used = placed_shape.shape.area() / stock.area
                    allocated_cost = stock.total_cost * stock_area_used
                    row['Allocated_Cost'] = round(allocated_cost, self.config.precision)
                    row['Cost_per_m2'] = round(allocated_cost / (placed_shape.shape.area() / 1_000_000), 
                                             self.config.precision)
                
                # Add timestamps
                if self.config.show_timestamps:
                    row['Placement_Time'] = getattr(placed_shape, 'placement_time', datetime.now())
                    row['Cutting_Sequence'] = getattr(placed_shape, 'cutting_sequence', i)
                    row['Est_Cutting_Time_min'] = getattr(placed_shape, 'estimated_cutting_time', 0)
                
                # Add material details
                if self.config.show_material_details:
                    row['Stock_Location'] = stock.location
                    row['Stock_Supplier'] = stock.supplier
                    row['Quality_Grade'] = stock.quality_grade
                    row['Due_Date'] = getattr(order, 'due_date', None)
                    row['Order_Notes'] = order.notes
                
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Sort by cutting sequence or stock ID
            if 'Cutting_Sequence' in df.columns:
                df = df.sort_values(['Stock_ID', 'Cutting_Sequence'])
            else:
                df = df.sort_values(['Stock_ID', 'Cut_ID'])
            
            self.logger.end_operation("generate_cutting_plan_table", success=True, 
                                    result={"rows": len(df)})
            
            return df
            
        except Exception as e:
            self.logger.end_operation("generate_cutting_plan_table", success=False, 
                                    result={"error": str(e)})
            raise


class StockUtilizationTable:
    """Stock utilization analysis table"""
    
    def __init__(self, config: Optional[TableConfig] = None):
        self.config = config or TableConfig()
        self.logger = get_logger()
    
    def generate(self, result: CuttingResult, stocks: List[Stock]) -> pd.DataFrame:
        """Generate stock utilization table"""
        
        self.logger.start_operation("generate_stock_utilization_table")
        
        try:
            stock_dict = {stock.id: stock for stock in stocks}
            data = []
            
            # Group placed shapes by stock
            stock_usage = {}
            for placed_shape in result.placed_shapes:
                stock_id = placed_shape.stock_id
                if stock_id not in stock_usage:
                    stock_usage[stock_id] = []
                stock_usage[stock_id].append(placed_shape)
            
            # Analyze each stock
            for stock in stocks:
                shapes_on_stock = stock_usage.get(stock.id, [])
                
                total_used_area = sum(ps.shape.area() for ps in shapes_on_stock)
                efficiency = (total_used_area / stock.area * 100) if stock.area > 0 else 0
                waste_area = stock.area - total_used_area
                waste_percentage = 100 - efficiency
                
                row = {
                    'Stock_ID': stock.id,
                    'Material': stock.material_type.value.title(),
                    'Dimensions_mm': f"{stock.width} x {stock.height}",
                    'Thickness_mm': stock.thickness,
                    'Total_Area_mm2': stock.area,
                    'Total_Area_m2': round(stock.area / 1_000_000, 4),
                    'Used_Area_mm2': round(total_used_area, self.config.precision),
                    'Used_Area_m2': round(total_used_area / 1_000_000, 4),
                    'Waste_Area_mm2': round(waste_area, self.config.precision),
                    'Waste_Area_m2': round(waste_area / 1_000_000, 4),
                    'Efficiency_pct': round(efficiency, self.config.precision),
                    'Waste_pct': round(waste_percentage, self.config.precision),
                    'Pieces_Cut': len(shapes_on_stock),
                    'Status': 'Used' if shapes_on_stock else 'Unused',
                    'Stock_Cost': round(stock.total_cost, self.config.precision),
                    'Cost_per_m2': round(stock.total_cost / (stock.area / 1_000_000), 
                                       self.config.precision),
                }
                
                # Add material properties
                if self.config.show_material_details:
                    row['Location'] = stock.location
                    row['Supplier'] = stock.supplier
                    row['Quality_Grade'] = stock.quality_grade
                    row['Purchase_Date'] = getattr(stock, 'purchase_date', None)
                    row['Batch_Number'] = stock.batch_number
                
                # Calculate cost efficiency
                if shapes_on_stock:
                    cost_per_used_area = stock.total_cost / (total_used_area / 1_000_000)
                    row['Cost_per_Used_m2'] = round(cost_per_used_area, self.config.precision)
                else:
                    row['Cost_per_Used_m2'] = 0
                
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Sort by efficiency (highest first)
            df = df.sort_values('Efficiency_pct', ascending=False)
            
            self.logger.end_operation("generate_stock_utilization_table", success=True, 
                                    result={"stocks_analyzed": len(df)})
            
            return df
            
        except Exception as e:
            self.logger.end_operation("generate_stock_utilization_table", success=False, 
                                    result={"error": str(e)})
            raise


class OrderFulfillmentTable:
    """Order fulfillment analysis table"""
    
    def __init__(self, config: Optional[TableConfig] = None):
        self.config = config or TableConfig()
        self.logger = get_logger()
    
    def generate(self, result: CuttingResult, orders: List[Order]) -> pd.DataFrame:
        """Generate order fulfillment table"""
        
        self.logger.start_operation("generate_order_fulfillment_table")
        
        try:
            data = []
            
            # Track fulfilled orders
            fulfilled_orders = {}
            for placed_shape in result.placed_shapes:
                order_id = placed_shape.order_id
                if '_' in order_id:
                    base_order_id = order_id.rsplit('_', 1)[0]
                else:
                    base_order_id = order_id
                
                if base_order_id not in fulfilled_orders:
                    fulfilled_orders[base_order_id] = []
                fulfilled_orders[base_order_id].append(placed_shape)
            
            # Analyze each order
            for order in orders:
                placed_shapes = fulfilled_orders.get(order.id, [])
                fulfilled_quantity = len(placed_shapes)
                fulfillment_rate = (fulfilled_quantity / order.quantity * 100) if order.quantity > 0 else 0
                
                status = "Fulfilled" if fulfilled_quantity == order.quantity else \
                        "Partially Fulfilled" if fulfilled_quantity > 0 else "Unfulfilled"
                
                row = {
                    'Order_ID': order.id,
                    'Customer_ID': getattr(order, 'customer_id', ''),
                    'Material': order.material_type.value.title(),
                    'Shape_Type': order.shape.__class__.__name__,
                    'Priority': order.priority.name,
                    'Priority_Weight': order.priority.weight,
                    'Quantity_Ordered': order.quantity,
                    'Quantity_Fulfilled': fulfilled_quantity,
                    'Quantity_Remaining': order.quantity - fulfilled_quantity,
                    'Fulfillment_Rate_pct': round(fulfillment_rate, self.config.precision),
                    'Status': status,
                    'Unit_Area_mm2': round(order.shape.area(), self.config.precision),
                    'Unit_Area_m2': round(order.shape.area() / 1_000_000, 4),
                    'Total_Area_mm2': round(order.total_area, self.config.precision),
                    'Total_Area_m2': round(order.total_area / 1_000_000, 4),
                    'Unit_Price': getattr(order, 'unit_price', 0),
                    'Total_Value': getattr(order, 'total_value', 0),
                }
                
                # Add shape-specific dimensions
                if hasattr(order.shape, 'width'):
                    row['Width_mm'] = order.shape.width
                    row['Height_mm'] = order.shape.height
                elif hasattr(order.shape, 'radius'):
                    row['Radius_mm'] = order.shape.radius
                    row['Diameter_mm'] = order.shape.radius * 2
                
                # Add timing information
                if self.config.show_timestamps:
                    row['Order_Date'] = getattr(order, 'order_date', None)
                    row['Due_Date'] = getattr(order, 'due_date', None)
                    row['Days_Until_Due'] = getattr(order, 'days_until_due', None)
                    row['Is_Overdue'] = getattr(order, 'is_overdue', False)
                
                # Add stock assignments for fulfilled pieces
                if placed_shapes:
                    stock_ids = list(set(ps.stock_id for ps in placed_shapes))
                    row['Assigned_Stocks'] = ', '.join(stock_ids)
                    
                    # Calculate value fulfilled
                    value_fulfilled = (fulfilled_quantity / order.quantity) * getattr(order, 'total_value', 0)
                    row['Value_Fulfilled'] = round(value_fulfilled, self.config.precision)
                    row['Value_Remaining'] = round(getattr(order, 'total_value', 0) - value_fulfilled, 
                                                 self.config.precision)
                else:
                    row['Assigned_Stocks'] = ''
                    row['Value_Fulfilled'] = 0
                    row['Value_Remaining'] = getattr(order, 'total_value', 0)
                
                row['Notes'] = order.notes
                
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Sort by priority (highest first), then by fulfillment rate (lowest first)
            df = df.sort_values(['Priority_Weight', 'Fulfillment_Rate_pct'], 
                              ascending=[False, True])
            
            self.logger.end_operation("generate_order_fulfillment_table", success=True, 
                                    result={"orders_analyzed": len(df)})
            
            return df
            
        except Exception as e:
            self.logger.end_operation("generate_order_fulfillment_table", success=False, 
                                    result={"error": str(e)})
            raise


class CostAnalysisTable:
    """Cost analysis table"""
    
    def __init__(self, config: Optional[TableConfig] = None):
        self.config = config or TableConfig()
        self.logger = get_logger()
    
    def generate(self, result: CuttingResult, stocks: List[Stock], 
                orders: List[Order]) -> Dict[str, pd.DataFrame]:
        """Generate comprehensive cost analysis tables"""
        
        self.logger.start_operation("generate_cost_analysis_table")
        
        try:
            tables = {}
            
            # Cost by material
            tables['cost_by_material'] = self._generate_cost_by_material(result, stocks, orders)
            
            # Cost by stock
            tables['cost_by_stock'] = self._generate_cost_by_stock(result, stocks)
            
            # Cost by customer
            tables['cost_by_customer'] = self._generate_cost_by_customer(result, stocks, orders)
            
            # Overall cost summary
            tables['cost_summary'] = self._generate_cost_summary(result, stocks, orders)
            
            self.logger.end_operation("generate_cost_analysis_table", success=True, 
                                    result={"tables_generated": len(tables)})
            
            return tables
            
        except Exception as e:
            self.logger.end_operation("generate_cost_analysis_table", success=False, 
                                    result={"error": str(e)})
            raise
    
    def _generate_cost_by_material(self, result: CuttingResult, stocks: List[Stock], 
                                  orders: List[Order]) -> pd.DataFrame:
        """Generate cost analysis by material type"""
        
        stock_dict = {stock.id: stock for stock in stocks}
        material_costs = {}
        
        for placed_shape in result.placed_shapes:
            stock = stock_dict.get(placed_shape.stock_id)
            if not stock:
                continue
            
            material = stock.material_type
            if material not in material_costs:
                material_costs[material] = {
                    'total_stock_cost': 0,
                    'total_stock_area': 0,
                    'total_used_area': 0,
                    'pieces_cut': 0,
                    'stocks_used': set()
                }
            
            material_costs[material]['total_used_area'] += placed_shape.shape.area()
            material_costs[material]['pieces_cut'] += 1
            material_costs[material]['stocks_used'].add(stock.id)
        
        # Add stock costs
        for stock in stocks:
            if any(ps.stock_id == stock.id for ps in result.placed_shapes):
                material = stock.material_type
                if material in material_costs:
                    material_costs[material]['total_stock_cost'] += stock.total_cost
                    material_costs[material]['total_stock_area'] += stock.area
        
        data = []
        for material, costs in material_costs.items():
            efficiency = (costs['total_used_area'] / costs['total_stock_area'] * 100) \
                        if costs['total_stock_area'] > 0 else 0
            
            cost_per_m2 = costs['total_stock_cost'] / (costs['total_stock_area'] / 1_000_000) \
                         if costs['total_stock_area'] > 0 else 0
            
            data.append({
                'Material': material.value.title(),
                'Stocks_Used': len(costs['stocks_used']),
                'Total_Stock_Cost': round(costs['total_stock_cost'], self.config.precision),
                'Total_Stock_Area_m2': round(costs['total_stock_area'] / 1_000_000, 4),
                'Total_Used_Area_m2': round(costs['total_used_area'] / 1_000_000, 4),
                'Efficiency_pct': round(efficiency, self.config.precision),
                'Cost_per_m2': round(cost_per_m2, self.config.precision),
                'Pieces_Cut': costs['pieces_cut'],
                'Avg_Cost_per_Piece': round(costs['total_stock_cost'] / costs['pieces_cut'], 
                                          self.config.precision) if costs['pieces_cut'] > 0 else 0
            })
        
        return pd.DataFrame(data).sort_values('Total_Stock_Cost', ascending=False)
    
    def _generate_cost_by_stock(self, result: CuttingResult, stocks: List[Stock]) -> pd.DataFrame:
        """Generate cost analysis by stock"""
        
        stock_dict = {stock.id: stock for stock in stocks}
        data = []
        
        # Group by stock
        stock_usage = {}
        for placed_shape in result.placed_shapes:
            stock_id = placed_shape.stock_id
            if stock_id not in stock_usage:
                stock_usage[stock_id] = []
            stock_usage[stock_id].append(placed_shape)
        
        for stock in stocks:
            shapes_on_stock = stock_usage.get(stock.id, [])
            used_area = sum(ps.shape.area() for ps in shapes_on_stock)
            efficiency = (used_area / stock.area * 100) if stock.area > 0 else 0
            
            cost_per_piece = stock.total_cost / len(shapes_on_stock) if shapes_on_stock else 0
            cost_per_used_m2 = stock.total_cost / (used_area / 1_000_000) if used_area > 0 else 0
            
            data.append({
                'Stock_ID': stock.id,
                'Material': stock.material_type.value.title(),
                'Stock_Cost': round(stock.total_cost, self.config.precision),
                'Stock_Area_m2': round(stock.area / 1_000_000, 4),
                'Used_Area_m2': round(used_area / 1_000_000, 4),
                'Efficiency_pct': round(efficiency, self.config.precision),
                'Pieces_Cut': len(shapes_on_stock),
                'Cost_per_Piece': round(cost_per_piece, self.config.precision),
                'Cost_per_Used_m2': round(cost_per_used_m2, self.config.precision),
                'Status': 'Used' if shapes_on_stock else 'Unused'
            })
        
        return pd.DataFrame(data).sort_values('Stock_Cost', ascending=False)
    
    def _generate_cost_by_customer(self, result: CuttingResult, stocks: List[Stock], 
                                  orders: List[Order]) -> pd.DataFrame:
        """Generate cost analysis by customer"""
        
        stock_dict = {stock.id: stock for stock in stocks}
        order_dict = {}
        for order in orders:
            order_dict[order.id] = order
            for i in range(order.quantity):
                order_dict[f"{order.id}_{i+1}"] = order
        
        customer_costs = {}
        
        for placed_shape in result.placed_shapes:
            stock = stock_dict.get(placed_shape.stock_id)
            order = order_dict.get(placed_shape.order_id)
            
            if not stock or not order:
                continue
            
            customer_id = getattr(order, 'customer_id', 'Unknown')
            
            if customer_id not in customer_costs:
                customer_costs[customer_id] = {
                    'total_cost': 0,
                    'total_area': 0,
                    'pieces': 0,
                    'orders': set(),
                    'materials': set()
                }
            
            # Allocate cost proportionally
            area_ratio = placed_shape.shape.area() / stock.area
            allocated_cost = stock.total_cost * area_ratio
            
            customer_costs[customer_id]['total_cost'] += allocated_cost
            customer_costs[customer_id]['total_area'] += placed_shape.shape.area()
            customer_costs[customer_id]['pieces'] += 1
            
            base_order_id = placed_shape.order_id.rsplit('_', 1)[0] if '_' in placed_shape.order_id else placed_shape.order_id
            customer_costs[customer_id]['orders'].add(base_order_id)
            customer_costs[customer_id]['materials'].add(stock.material_type.value)
        
        data = []
        for customer_id, costs in customer_costs.items():
            data.append({
                'Customer_ID': customer_id,
                'Total_Cost': round(costs['total_cost'], self.config.precision),
                'Total_Area_m2': round(costs['total_area'] / 1_000_000, 4),
                'Cost_per_m2': round(costs['total_cost'] / (costs['total_area'] / 1_000_000), 
                                   self.config.precision) if costs['total_area'] > 0 else 0,
                'Pieces_Cut': costs['pieces'],
                'Orders_Count': len(costs['orders']),
                'Materials_Used': ', '.join(costs['materials']),
                'Avg_Cost_per_Piece': round(costs['total_cost'] / costs['pieces'], 
                                          self.config.precision) if costs['pieces'] > 0 else 0
            })
        
        return pd.DataFrame(data).sort_values('Total_Cost', ascending=False)
    
    def _generate_cost_summary(self, result: CuttingResult, stocks: List[Stock], 
                              orders: List[Order]) -> pd.DataFrame:
        """Generate overall cost summary"""
        
        used_stocks = {ps.stock_id for ps in result.placed_shapes}
        total_stock_cost = sum(stock.total_cost for stock in stocks if stock.id in used_stocks)
        total_stock_area = sum(stock.area for stock in stocks if stock.id in used_stocks)
        total_used_area = sum(ps.shape.area() for ps in result.placed_shapes)
        
        data = [{
            'Metric': 'Total Stocks Used',
            'Value': len(used_stocks),
            'Unit': 'stocks'
        }, {
            'Metric': 'Total Stock Cost',
            'Value': round(total_stock_cost, self.config.precision),
            'Unit': self.config.currency_symbol
        }, {
            'Metric': 'Total Stock Area',
            'Value': round(total_stock_area / 1_000_000, 4),
            'Unit': self.config.area_unit
        }, {
            'Metric': 'Total Used Area',
            'Value': round(total_used_area / 1_000_000, 4),
            'Unit': self.config.area_unit
        }, {
            'Metric': 'Overall Efficiency',
            'Value': round(result.efficiency_percentage, self.config.precision),
            'Unit': '%'
        }, {
            'Metric': 'Cost per Used Area',
            'Value': round(total_stock_cost / (total_used_area / 1_000_000), self.config.precision) if total_used_area > 0 else 0,
            'Unit': f"{self.config.currency_symbol}/{self.config.area_unit}"
        }, {
            'Metric': 'Waste Cost',
            'Value': round(total_stock_cost * (100 - result.efficiency_percentage) / 100, self.config.precision),
            'Unit': self.config.currency_symbol
        }]
        
        return pd.DataFrame(data)


class TableGenerator:
    """Main table generator class"""
    
    def __init__(self, config: Optional[TableConfig] = None):
        self.config = config or TableConfig()
        self.cutting_plan = CuttingPlanTable(config)
        self.stock_utilization = StockUtilizationTable(config)
        self.order_fulfillment = OrderFulfillmentTable(config)
        self.cost_analysis = CostAnalysisTable(config)
        self.logger = get_logger()
    
    def generate_all_tables(self, result: CuttingResult, stocks: List[Stock], 
                           orders: List[Order]) -> Dict[str, pd.DataFrame]:
        """Generate all report tables"""
        
        self.logger.start_operation("generate_all_tables")
        
        try:
            tables = {}
            
            # Main tables
            tables['cutting_plan'] = self.cutting_plan.generate(result, stocks, orders)
            tables['stock_utilization'] = self.stock_utilization.generate(result, stocks)
            tables['order_fulfillment'] = self.order_fulfillment.generate(result, orders)
            
            # Cost analysis tables
            cost_tables = self.cost_analysis.generate(result, stocks, orders)
            tables.update(cost_tables)
            
            self.logger.end_operation("generate_all_tables", success=True, 
                                    result={"tables_generated": len(tables)})
            
            return tables
            
        except Exception as e:
            self.logger.end_operation("generate_all_tables", success=False, 
                                    result={"error": str(e)})
            raise 