"""
Dashboard for Surface Cutting Optimizer
Web-based dashboard for visualization and monitoring
"""

from typing import List, Dict, Any
from ..core.models import Stock, Order, CuttingResult


class Dashboard:
    """Web dashboard for optimization visualization"""
    
    def __init__(self):
        self.results_cache = {}
    
    def create_dashboard(self, result: CuttingResult, stocks: List[Stock], 
                        orders: List[Order]) -> Dict[str, Any]:
        """Create dashboard data structure"""
        
        return {
            "efficiency": result.efficiency_percentage,
            "cost": result.total_cost,
            "fulfillment": result.fulfillment_rate,
            "stocks_used": result.total_stock_used,
            "orders_fulfilled": result.total_orders_fulfilled
        }
    
    def generate_html(self, dashboard_data: Dict[str, Any]) -> str:
        """Generate HTML dashboard"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cutting Optimizer Dashboard</title>
        </head>
        <body>
            <h1>Optimization Results</h1>
            <div class="metrics">
                <div>Efficiency: {dashboard_data['efficiency']:.1f}%</div>
                <div>Cost: ${dashboard_data['cost']:.2f}</div>
                <div>Fulfillment: {dashboard_data['fulfillment']:.1f}%</div>
            </div>
        </body>
        </html>
        """
        
        return html 