"""
Visualization utilities for Surface Cutting Optimizer
"""

from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ..core.models import Stock, CuttingResult
from ..core.geometry import Rectangle, Circle


def visualize_cutting_plan(result: CuttingResult, stocks: List[Stock], 
                          save_path: Optional[str] = None,
                          output_dir: str = "visualizations"):
    """Visualize the cutting plan with placed shapes"""
    
    if not result.placed_shapes:
        print("No shapes to visualize")
        return
    
    try:
        # Group shapes by stock
        shapes_by_stock = {}
        for placed_shape in result.placed_shapes:
            stock_id = placed_shape.stock_id
            if stock_id not in shapes_by_stock:
                shapes_by_stock[stock_id] = []
            shapes_by_stock[stock_id].append(placed_shape)
        
        # Create subplots
        num_stocks = len(shapes_by_stock)
        if num_stocks == 0:
            return
        
        cols = min(3, num_stocks)
        rows = (num_stocks + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows), 
                                squeeze=False)  # squeeze=False ensures consistent format
        
        # Flatten axes for easier indexing
        axes = axes.flatten()
        
        # Plot each stock
        stock_dict = {stock.id: stock for stock in stocks}
        
        for i, (stock_id, shapes) in enumerate(shapes_by_stock.items()):
            if i >= len(axes):
                break
                
            ax = axes[i]
            stock = stock_dict.get(stock_id)
            
            if not stock:
                continue
            
            # Draw stock outline
            stock_rect = patches.Rectangle(
                (0, 0), stock.width, stock.height,
                linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3
            )
            ax.add_patch(stock_rect)
            
            # Draw placed shapes with error handling
            try:
                colors = plt.cm.Set3(np.linspace(0, 1, len(shapes)))
            except:
                colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum'] * (len(shapes) // 5 + 1)
            
            for j, placed_shape in enumerate(shapes):
                shape = placed_shape.shape
                color = colors[j % len(colors)]
                
                try:
                    if isinstance(shape, Rectangle):
                        rect = patches.Rectangle(
                            (shape.x, shape.y), shape.width, shape.height,
                            linewidth=1, edgecolor='darkblue', facecolor=color, alpha=0.7
                        )
                        ax.add_patch(rect)
                        
                        # Add label
                        ax.text(shape.x + shape.width/2, shape.y + shape.height/2,
                               placed_shape.order_id.split('_')[0], 
                               ha='center', va='center', fontsize=8, weight='bold')
                        
                    elif isinstance(shape, Circle):
                        circle = patches.Circle(
                            (shape.x + shape.radius, shape.y + shape.radius), shape.radius,
                            linewidth=1, edgecolor='darkblue', facecolor=color, alpha=0.7
                        )
                        ax.add_patch(circle)
                        
                        # Add label
                        ax.text(shape.x + shape.radius, shape.y + shape.radius,
                               placed_shape.order_id.split('_')[0],
                               ha='center', va='center', fontsize=8, weight='bold')
                except Exception as e:
                    print(f"Warning: Could not draw shape {placed_shape.order_id}: {e}")
            
            # Set axis properties
            ax.set_xlim(0, stock.width)
            ax.set_ylim(0, stock.height)
            ax.set_aspect('equal')
            ax.set_title(f'Stock {stock_id}\n{stock.width}x{stock.height}mm', 
                        fontsize=10, weight='bold')
            ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for i in range(num_stocks, len(axes)):
            axes[i].set_visible(False)
        
        # Overall title
        efficiency = result.efficiency_percentage
        fig.suptitle(f'Cutting Plan - {result.algorithm_used}\n'
                    f'Efficiency: {efficiency:.1f}% | Stocks Used: {result.total_stock_used} | '
                    f'Orders Fulfilled: {result.total_orders_fulfilled}', 
                    fontsize=14, weight='bold')
        
        plt.tight_layout()
        
        if save_path:
            # Create output directory if it doesn't exist
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Construct full path
            full_path = output_path / save_path
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Cutting plan saved to {full_path}")
            plt.close()  # Close to free memory
        else:
            plt.show()
            
    except Exception as e:
        print(f"Visualization error: {e}")
        plt.close()  # Ensure cleanup even on error


def plot_algorithm_comparison(results: List[CuttingResult], algorithm_names: List[str],
                            save_path: Optional[str] = None,
                            output_dir: str = "visualizations"):
    """Plot comparison between different algorithms"""
    
    if not results or len(results) != len(algorithm_names):
        print("Invalid input for algorithm comparison")
        return
    
    try:
        # Extract metrics
        efficiencies = [r.efficiency_percentage for r in results]
        stocks_used = [r.total_stock_used for r in results]
        orders_fulfilled = [r.total_orders_fulfilled for r in results]
        computation_times = [r.computation_time for r in results]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Efficiency comparison
        bars1 = ax1.bar(algorithm_names, efficiencies, color='skyblue', alpha=0.7)
        ax1.set_title('Material Efficiency', fontsize=12, weight='bold')
        ax1.set_ylabel('Efficiency (%)')
        ax1.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, eff in zip(bars1, efficiencies):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{eff:.1f}%', ha='center', va='bottom', fontsize=10)
        
        # Stocks used comparison
        bars2 = ax2.bar(algorithm_names, stocks_used, color='lightcoral', alpha=0.7)
        ax2.set_title('Stocks Used', fontsize=12, weight='bold')
        ax2.set_ylabel('Number of Stocks')
        
        for bar, stock in zip(bars2, stocks_used):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{stock}', ha='center', va='bottom', fontsize=10)
        
        # Orders fulfilled comparison
        bars3 = ax3.bar(algorithm_names, orders_fulfilled, color='lightgreen', alpha=0.7)
        ax3.set_title('Orders Fulfilled', fontsize=12, weight='bold')
        ax3.set_ylabel('Number of Orders')
        
        for bar, orders in zip(bars3, orders_fulfilled):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{orders}', ha='center', va='bottom', fontsize=10)
        
        # Computation time comparison
        bars4 = ax4.bar(algorithm_names, computation_times, color='gold', alpha=0.7)
        ax4.set_title('Computation Time', fontsize=12, weight='bold')
        ax4.set_ylabel('Time (seconds)')
        
        for bar, time in zip(bars4, computation_times):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{time:.3f}s', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            full_path = output_path / save_path
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Algorithm comparison saved to {full_path}")
            plt.close()
        else:
            plt.show()
            
    except Exception as e:
        print(f"Comparison plot error: {e}")
        plt.close()


def plot_waste_analysis(result: CuttingResult, stocks: List[Stock],
                       save_path: Optional[str] = None,
                       output_dir: str = "visualizations"):
    """Plot waste analysis for optimization result"""
    
    used_stock_ids = set(ps.stock_id for ps in result.placed_shapes)
    used_stocks = [s for s in stocks if s.id in used_stock_ids]
    
    if not used_stocks:
        print("No stocks used to analyze")
        return
    
    try:
        # Calculate waste for each stock
        stock_data = []
        for stock in used_stocks:
            stock_shapes = [ps for ps in result.placed_shapes if ps.stock_id == stock.id]
            used_area = sum(ps.shape.area() for ps in stock_shapes)
            waste_area = stock.area - used_area
            waste_percentage = (waste_area / stock.area) * 100
            
            stock_data.append({
                'id': stock.id,
                'used_area': used_area,
                'waste_area': waste_area,
                'waste_percentage': waste_percentage,
                'total_area': stock.area
            })
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Waste percentage by stock
        stock_ids = [s['id'] for s in stock_data]
        waste_percentages = [s['waste_percentage'] for s in stock_data]
        
        bars1 = ax1.bar(stock_ids, waste_percentages, color='lightcoral', alpha=0.7)
        ax1.set_title('Waste Percentage by Stock', fontsize=12, weight='bold')
        ax1.set_ylabel('Waste (%)')
        ax1.set_xlabel('Stock ID')
        
        for bar, waste in zip(bars1, waste_percentages):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{waste:.1f}%', ha='center', va='bottom', fontsize=10)
        
        # Pie chart of total area usage
        total_used = sum(s['used_area'] for s in stock_data)
        total_waste = sum(s['waste_area'] for s in stock_data)
        
        ax2.pie([total_used, total_waste], 
               labels=['Used Area', 'Waste Area'],
               colors=['lightgreen', 'lightcoral'],
               autopct='%1.1f%%',
               startangle=90)
        ax2.set_title('Overall Area Utilization', fontsize=12, weight='bold')
        
        plt.tight_layout()
        
        if save_path:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            full_path = output_path / save_path
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Waste analysis saved to {full_path}")
            plt.close()
        else:
            plt.show()
            
    except Exception as e:
        print(f"Waste analysis error: {e}")
        plt.close()


def plot_efficiency_trends(results_history: List[CuttingResult],
                          save_path: Optional[str] = None,
                          output_dir: str = "visualizations"):
    """Plot efficiency trends over multiple optimizations"""
    
    if not results_history:
        print("No results history to plot")
        return
    
    try:
        efficiencies = [r.efficiency_percentage for r in results_history]
        timestamps = list(range(1, len(results_history) + 1))
        
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, efficiencies, marker='o', linestyle='-', 
                linewidth=2, markersize=8, color='blue', alpha=0.7)
        
        plt.title('Efficiency Trends Over Time', fontsize=14, weight='bold')
        plt.xlabel('Optimization Run')
        plt.ylabel('Efficiency (%)')
        plt.grid(True, alpha=0.3)
        
        # Add value labels
        for i, eff in enumerate(efficiencies):
            plt.annotate(f'{eff:.1f}%', (timestamps[i], eff), 
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        plt.tight_layout()
        
        if save_path:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            full_path = output_path / save_path
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Efficiency trends saved to {full_path}")
            plt.close()
        else:
            plt.show()
            
    except Exception as e:
        print(f"Efficiency trends error: {e}")
        plt.close() 