"""
Visualization utilities for Surface Cutting Optimizer
"""

from typing import List, Optional, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle as MPLRectangle
import numpy as np
from ..core.models import Stock, CuttingResult, PlacedShape
from ..core.geometry import Rectangle, Circle


def visualize_cutting_plan(result: CuttingResult, stocks: List[Stock], 
                          save_path: Optional[str] = None,
                          output_dir: str = "visualizations",
                          # Image configuration
                          figsize: Optional[tuple] = None,
                          dpi: int = 300,
                          format: str = 'png',
                          # Visual styling
                          theme: str = 'default',
                          show_grid: bool = True,
                          grid_alpha: float = 0.3,
                          # Information display
                          show_efficiency: bool = True,
                          show_dimensions: bool = True,
                          show_labels: bool = True,
                          show_cost: bool = False,
                          # Layout options
                          layout_style: str = 'auto',
                          max_cols: int = 3):
    """
    Visualize the cutting plan with placed shapes
    
    Args:
        result: CuttingResult from optimization
        stocks: List of Stock objects used
        save_path: Filename to save (None to show interactively)
        output_dir: Directory to save visualization
        
        # Image configuration
        figsize: Figure size as (width, height) in inches, None for auto
        dpi: Image resolution (300 for high quality, 150 for web, 72 for draft)
        format: Image format ('png', 'jpg', 'pdf', 'svg')
        
        # Visual styling
        theme: Color theme ('default', 'professional', 'colorful', 'minimal')
        show_grid: Whether to show grid lines
        grid_alpha: Grid transparency (0.0 = invisible, 1.0 = opaque)
        
        # Information display
        show_efficiency: Include efficiency in title
        show_dimensions: Show stock dimensions
        show_labels: Show piece labels on shapes
        show_cost: Include cost information
        
        # Layout options
        layout_style: Layout arrangement ('auto', 'grid', 'single_row')
        max_cols: Maximum columns in grid layout
    """
    
    if not result.placed_shapes:
        print("No shapes to visualize")
        return
    
    try:
        # Define color themes
        themes = {
            'default': {
                'background': 'lightgray',
                'stock_edge': 'black',
                'shape_edge': 'darkblue',
                'colors': ['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum']
            },
            'professional': {
                'background': 'white',
                'stock_edge': '#2c3e50',
                'shape_edge': '#34495e',
                'colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
            },
            'colorful': {
                'background': '#f8f9fa',
                'stock_edge': '#343a40',
                'shape_edge': '#495057',
                'colors': ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3']
            },
            'minimal': {
                'background': '#fafafa',
                'stock_edge': '#666666',
                'shape_edge': '#333333',
                'colors': ['#e3e3e3', '#d1d1d1', '#c0c0c0', '#afafaf', '#9e9e9e']
            }
        }
        
        current_theme = themes.get(theme, themes['default'])
        
        # Group shapes by stock
        shapes_by_stock = {}
        for placed_shape in result.placed_shapes:
            stock_id = placed_shape.stock_id
            if stock_id not in shapes_by_stock:
                shapes_by_stock[stock_id] = []
            shapes_by_stock[stock_id].append(placed_shape)
        
        # Create subplots with dynamic layout
        num_stocks = len(shapes_by_stock)
        if num_stocks == 0:
            return
        
        # Calculate layout based on style
        if layout_style == 'single_row':
            cols = num_stocks
            rows = 1
        elif layout_style == 'grid':
            cols = min(max_cols, num_stocks)
            rows = (num_stocks + cols - 1) // cols
        else:  # auto
            if num_stocks <= 3:
                cols = num_stocks
                rows = 1
            else:
                cols = min(max_cols, num_stocks)
        rows = (num_stocks + cols - 1) // cols
        
        # Calculate figure size
        if figsize is None:
            base_width = 5
            base_height = 4
            auto_figsize = (base_width * cols, base_height * rows)
        else:
            auto_figsize = figsize
        
        fig, axes = plt.subplots(rows, cols, figsize=auto_figsize, 
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
            
            # Draw stock outline with theme colors
            stock_rect = patches.Rectangle(
                (0, 0), stock.width, stock.height,
                linewidth=2, edgecolor=current_theme['stock_edge'], 
                facecolor=current_theme['background'], alpha=0.3
            )
            ax.add_patch(stock_rect)
            
            # Draw placed shapes with error handling and theme colors
            try:
                if theme == 'default':
                    colors = plt.cm.Set3(np.linspace(0, 1, len(shapes)))
                else:
                    colors = current_theme['colors'] * (len(shapes) // len(current_theme['colors']) + 1)
            except:
                colors = current_theme['colors'] * (len(shapes) // len(current_theme['colors']) + 1)
            
            for j, placed_shape in enumerate(shapes):
                shape = placed_shape.shape
                color = colors[j % len(colors)]
                
                try:
                    if isinstance(shape, Rectangle):
                        rect = patches.Rectangle(
                            (shape.x, shape.y), shape.width, shape.height,
                            linewidth=1, edgecolor=current_theme['shape_edge'], 
                            facecolor=color, alpha=0.7
                        )
                        ax.add_patch(rect)
                        
                        # Add label with adaptive font size
                        # Calculate adaptive font size based on shape dimensions
                        min_dimension = min(shape.width, shape.height)
                        if min_dimension < 80:
                            font_size = max(4, min_dimension / 20)  # Very small text for small shapes
                        elif min_dimension < 150:
                            font_size = max(5, min_dimension / 25)  # Small text
                        else:
                            font_size = max(6, min(8, min_dimension / 30))  # Normal text
                        
                        if show_labels:
                            ax.text(shape.x + shape.width/2, shape.y + shape.height/2,
                                   placed_shape.order_id.split('_')[0], 
                                   ha='center', va='center', fontsize=font_size, weight='bold')
                        
                    elif isinstance(shape, Circle):
                        circle = patches.Circle(
                            (shape.x + shape.radius, shape.y + shape.radius), shape.radius,
                            linewidth=1, edgecolor=current_theme['shape_edge'], 
                            facecolor=color, alpha=0.7
                        )
                        ax.add_patch(circle)
                        
                        # Add label with adaptive font size
                        # Calculate adaptive font size based on circle diameter
                        diameter = shape.radius * 2
                        if diameter < 80:
                            font_size = max(4, diameter / 20)  # Very small text for small circles
                        elif diameter < 150:
                            font_size = max(5, diameter / 25)  # Small text
                        else:
                            font_size = max(6, min(8, diameter / 30))  # Normal text
                        
                        if show_labels:
                            ax.text(shape.x + shape.radius, shape.y + shape.radius,
                                   placed_shape.order_id.split('_')[0],
                                   ha='center', va='center', fontsize=font_size, weight='bold')
                except Exception as e:
                    print(f"Warning: Could not draw shape {placed_shape.order_id}: {e}")
            
            # Set axis properties
            ax.set_xlim(0, stock.width)
            ax.set_ylim(0, stock.height)
            ax.set_aspect('equal')
            
            # Build title with conditional information
            title_parts = [f'Stock {stock_id}']
            if show_dimensions:
                title_parts.append(f'{stock.width}x{stock.height}mm')
            if show_cost and hasattr(stock, 'cost_per_unit'):
                title_parts.append(f'${stock.cost_per_unit:.2f}')
            
            ax.set_title('\n'.join(title_parts), fontsize=10, weight='bold')
            
            # Configure grid
            if show_grid:
                ax.grid(True, alpha=grid_alpha)
            else:
                ax.grid(False)
        
        # Hide unused subplots
        for i in range(num_stocks, len(axes)):
            axes[i].set_visible(False)
        
        # Overall title with conditional information
        title_parts = [f'Cutting Plan - {result.algorithm_used}']
        
        info_line = []
        if show_efficiency:
            info_line.append(f'Efficiency: {result.efficiency_percentage:.1f}%')
        info_line.append(f'Stocks Used: {result.total_stock_used}')
        info_line.append(f'Orders Fulfilled: {result.total_orders_fulfilled}')
        if show_cost:
            info_line.append(f'Cost: ${result.total_cost:.2f}')
        
        if info_line:
            title_parts.append(' | '.join(info_line))
        
        fig.suptitle('\n'.join(title_parts), fontsize=14, weight='bold')
        
        # Use tight_layout with padding to prevent title overlap
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        if save_path:
            # Create output directory if it doesn't exist
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Construct full path with format
            file_name = save_path
            if not save_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.svg')):
                file_name = f"{save_path}.{format}"
            
            full_path = output_path / file_name
            plt.savefig(full_path, dpi=dpi, bbox_inches='tight', format=format)
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
            output_path.mkdir(parents=True, exist_ok=True)
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
            output_path.mkdir(parents=True, exist_ok=True)
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
            output_path.mkdir(parents=True, exist_ok=True)
            full_path = output_path / save_path
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Efficiency trends saved to {full_path}")
            plt.close()
        else:
            plt.show()
            
    except Exception as e:
        print(f"Efficiency trends error: {e}")
        plt.close() 


def visualize_management_report(result: CuttingResult, stocks: List[Stock], orders=None,
                              save_path: Optional[str] = None,
                              output_dir: str = "visualizations",
                              figsize: tuple = (16, 10),
                              dpi: int = 300,
                              format: str = 'pdf',
                              theme: str = 'professional',
                              show_detailed_info: bool = True):
    """
    📊 Enhanced visualization specifically for management reports
    
    Features:
    - Fixed title spacing to prevent overlap
    - Detailed stock and order information panel
    - Professional layout optimized for presentations
    - Summary statistics and efficiency metrics
    
    Args:
        result: CuttingResult from optimization
        stocks: List of Stock objects used
        orders: List of Order objects (optional, for detailed info)
        save_path: Filename to save
        output_dir: Directory to save visualization
        figsize: Figure size (width, height)
        dpi: Image resolution
        format: Output format
        theme: Color theme
        show_detailed_info: Include detailed info panel
    """
    try:
        # Set up themes
        themes = {
            'professional': {
                'bg_color': 'white',
                'stock_color': '#f8f9fa',
                'stock_edge': '#3498db',
                'shape_colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'],
                'shape_edge': '#2c3e50',
                'text_color': '#2c3e50',
                'grid_color': '#bdc3c7'
            }
        }
        
        current_theme = themes.get(theme, themes['professional'])
        
        # Create figure with custom layout for management report
        if show_detailed_info:
            fig = plt.figure(figsize=figsize)
            # Create custom layout: main plot + info panel with better spacing
            gs = fig.add_gridspec(3, 5, height_ratios=[0.8, 0.1, 4], width_ratios=[3, 3, 3, 0.1, 2.5], 
                                hspace=0.15, wspace=0.1)
            
            # Title area (spans top row)
            title_ax = fig.add_subplot(gs[0, :])
            title_ax.axis('off')
            
            # Main cutting plan area (with spacing)
            main_ax = fig.add_subplot(gs[2, :3])
            
            # Info panel (with better width)
            info_ax = fig.add_subplot(gs[2, 4])
            info_ax.axis('off')
        else:
            fig, main_ax = plt.subplots(figsize=figsize)
        
        # Get used stocks
        used_stock_ids = set(ps.stock_id for ps in result.placed_shapes)
        used_stocks = [s for s in stocks if s.id in used_stock_ids]
        
        if not used_stocks:
            print("No stocks to visualize")
            return
        
        # Plot cutting plans in main area
        num_stocks = len(used_stocks)
        if num_stocks == 1:
            # Single stock - use full main area
            ax = main_ax
            stock = used_stocks[0]
            plot_single_stock(ax, stock, result, current_theme, True, True)
        else:
            # Multiple stocks - create subplots within main area
            cols = min(3, num_stocks)
            rows = (num_stocks + cols - 1) // cols
            
            main_ax.axis('off')  # Hide main axis
            
            for i, stock in enumerate(used_stocks):
                row = i // cols
                col = i % cols
                # Create subplot within main area
                sub_ax = fig.add_subplot(rows, cols, i + 1)
                plot_single_stock(sub_ax, stock, result, current_theme, True, True)
        
        # Add management report title
        if show_detailed_info:
            title_text = f"EXECUTIVE CUTTING OPTIMIZATION REPORT"
            subtitle_text = f"Algorithm: {result.algorithm_used.upper()}"
            metrics_text = f"Efficiency: {result.efficiency_percentage:.1f}% | Total Cost: ${result.total_cost:.2f} | Processing Time: {result.computation_time:.3f}s"
            
            title_ax.text(0.5, 0.8, title_text, ha='center', va='center', 
                         fontsize=18, weight='bold', color=current_theme['text_color'])
            title_ax.text(0.5, 0.5, subtitle_text, ha='center', va='center', 
                         fontsize=14, weight='bold', color='#2c3e50')
            title_ax.text(0.5, 0.2, metrics_text, ha='center', va='center', 
                         fontsize=12, style='italic', color=current_theme['text_color'])
        
        # Add detailed information panel
        if show_detailed_info:
            add_info_panel(info_ax, result, used_stocks, orders, current_theme)
        
        # Save the report
        if save_path:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            file_name = save_path
            if not save_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.svg')):
                file_name = f"{save_path}.{format}"
            
            full_path = output_path / file_name
            plt.savefig(full_path, dpi=dpi, bbox_inches='tight', format=format, 
                       facecolor='white', edgecolor='none')
            print(f"Management report saved to {full_path}")
            plt.close()
        else:
            plt.show()
            
    except Exception as e:
        print(f"Management report error: {e}")
        plt.close()


def plot_single_stock(ax, stock: Stock, result: CuttingResult, theme: Dict, 
                     show_labels: bool = True, show_dimensions: bool = True):
    """Plot a single stock with its placed shapes"""
    
    # Set background
    ax.set_facecolor(theme['bg_color'])
    
    # Draw stock outline
    stock_rect = MPLRectangle((0, 0), stock.width, stock.height,
                             linewidth=2, edgecolor=theme['stock_edge'],
                             facecolor=theme['stock_color'], alpha=0.3)
    ax.add_patch(stock_rect)
    
    # Draw placed shapes
    stock_shapes = [ps for ps in result.placed_shapes if ps.stock_id == stock.id]
    color_cycle = theme['shape_colors']
    
    for i, placed_shape in enumerate(stock_shapes):
        color = color_cycle[i % len(color_cycle)]
        shape = placed_shape.shape
        
        if isinstance(shape, Rectangle):
            rect = patches.Rectangle(
                (shape.x, shape.y), shape.width, shape.height,
                linewidth=1, edgecolor=theme['shape_edge'], 
                facecolor=color, alpha=0.7
            )
            ax.add_patch(rect)
            
            # Add label with adaptive font size
            min_dimension = min(shape.width, shape.height)
            if min_dimension < 80:
                font_size = max(4, min_dimension / 20)
            elif min_dimension < 150:
                font_size = max(5, min_dimension / 25)
            else:
                font_size = max(6, min(8, min_dimension / 30))
            
            if show_labels:
                ax.text(shape.x + shape.width/2, shape.y + shape.height/2,
                       placed_shape.order_id.split('_')[0], 
                       ha='center', va='center', fontsize=font_size, weight='bold')
        
        elif isinstance(shape, Circle):
            circle = patches.Circle(
                (shape.x + shape.radius, shape.y + shape.radius), shape.radius,
                linewidth=1, edgecolor=theme['shape_edge'], 
                facecolor=color, alpha=0.7
            )
            ax.add_patch(circle)
            
            diameter = shape.radius * 2
            if diameter < 80:
                font_size = max(4, diameter / 20)
            elif diameter < 150:
                font_size = max(5, diameter / 25)
            else:
                font_size = max(6, min(8, diameter / 30))
            
            if show_labels:
                ax.text(shape.x + shape.radius, shape.y + shape.radius,
                       placed_shape.order_id.split('_')[0],
                       ha='center', va='center', fontsize=font_size, weight='bold')
    
    # Configure axes
    ax.set_xlim(0, stock.width)
    ax.set_ylim(0, stock.height)
    ax.set_aspect('equal')
    
    # Title with dimensions
    title_parts = [f'Stock {stock.id}']
    if show_dimensions:
        title_parts.append(f'{stock.width}×{stock.height}mm')
    
    ax.set_title(' - '.join(title_parts), fontsize=10, weight='bold', 
                color=theme['text_color'])
    
    # Grid
    ax.grid(True, alpha=0.2, color=theme['grid_color'])


def add_info_panel(ax, result: CuttingResult, used_stocks: List[Stock], 
                  orders=None, theme: Dict = None):
    """Add detailed information panel to the management report"""
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Add main panel border and background
    from matplotlib.patches import Rectangle as MPLRect
    panel_border = MPLRect((0.01, 0.01), 0.98, 0.98, 
                          linewidth=2, edgecolor='#2c3e50', 
                          facecolor='#fafbfc', alpha=0.9)
    ax.add_patch(panel_border)
    
    # Title with background
    title_bg = MPLRect((0.02, 0.9), 0.96, 0.08, 
                      facecolor='#2c3e50', alpha=0.1, linewidth=0)
    ax.add_patch(title_bg)
    
    ax.text(0.5, 0.94, 'DETAILED SUMMARY', ha='center', va='center', 
           fontsize=12, weight='bold', color='#2c3e50')
    
    y_pos = 0.88
    line_height = 0.04
    
    # Add background rectangles for better organization
    from matplotlib.patches import Rectangle as MPLRect
    
    # Efficiency metrics section
    section_height = 0.12
    ax.add_patch(MPLRect((0.02, y_pos - section_height), 0.96, section_height, 
                        facecolor='#f8f9fa', alpha=0.5, linewidth=0))
    
    ax.text(0.05, y_pos - 0.01, 'EFFICIENCY METRICS', ha='left', va='top', 
           fontsize=10, weight='bold', color=theme['text_color'])
    y_pos -= line_height * 1.2
    
    ax.text(0.1, y_pos, f'Overall: {result.efficiency_percentage:.1f}%', 
           ha='left', va='top', fontsize=9, color=theme['text_color'])
    y_pos -= line_height * 0.8
    
    ax.text(0.1, y_pos, f'Algorithm: {result.algorithm_used}', 
           ha='left', va='top', fontsize=9, color=theme['text_color'])
    y_pos -= line_height * 0.8
    
    ax.text(0.1, y_pos, f'Time: {result.computation_time:.3f}s', 
           ha='left', va='top', fontsize=9, color=theme['text_color'])
    y_pos -= line_height * 1.5
    
    # Stock information section
    section_height = 0.12
    ax.add_patch(MPLRect((0.02, y_pos - section_height), 0.96, section_height, 
                        facecolor='#e8f4fd', alpha=0.5, linewidth=0))
    
    ax.text(0.05, y_pos - 0.01, 'STOCK USAGE', ha='left', va='top', 
           fontsize=10, weight='bold', color=theme['text_color'])
    y_pos -= line_height * 1.2
    
    ax.text(0.1, y_pos, f'Total stocks: {len(used_stocks)}', 
           ha='left', va='top', fontsize=9, color=theme['text_color'])
    y_pos -= line_height * 0.8
    
    total_stock_area = sum(s.area for s in used_stocks)
    ax.text(0.1, y_pos, f'Total area: {total_stock_area:,.0f}mm²', 
           ha='left', va='top', fontsize=9, color=theme['text_color'])
    y_pos -= line_height * 0.8
    
    ax.text(0.1, y_pos, f'Total cost: ${result.total_cost:.2f}', 
           ha='left', va='top', fontsize=9, color=theme['text_color'])
    y_pos -= line_height * 1.5
    
    # Stock details section
    section_height = 0.15
    ax.add_patch(MPLRect((0.02, y_pos - section_height), 0.96, section_height, 
                        facecolor='#f0f8f0', alpha=0.5, linewidth=0))
    
    ax.text(0.05, y_pos - 0.01, 'STOCK DETAILS', ha='left', va='top', 
           fontsize=10, weight='bold', color=theme['text_color'])
    y_pos -= line_height * 1.2
    
    for stock in used_stocks[:3]:  # Show first 3 stocks
        stock_shapes = [ps for ps in result.placed_shapes if ps.stock_id == stock.id]
        used_area = sum(ps.shape.area() for ps in stock_shapes)
        efficiency = (used_area / stock.area) * 100
        
        ax.text(0.1, y_pos, f'{stock.id}: {efficiency:.1f}% used', 
               ha='left', va='top', fontsize=8, color=theme['text_color'])
        y_pos -= line_height * 0.7
    
    if len(used_stocks) > 3:
        ax.text(0.1, y_pos, f'... and {len(used_stocks) - 3} more stocks', 
               ha='left', va='top', fontsize=8, color=theme['text_color'])
        y_pos -= line_height * 0.7
    
    y_pos -= line_height * 0.8
    
    # Order information section
    if orders:
        section_height = 0.18
        ax.add_patch(MPLRect((0.02, y_pos - section_height), 0.96, section_height, 
                            facecolor='#fff8e1', alpha=0.5, linewidth=0))
        
        ax.text(0.05, y_pos - 0.01, 'ORDER FULFILLMENT', ha='left', va='top', 
               fontsize=10, weight='bold', color=theme['text_color'])
        y_pos -= line_height * 1.2
        
        total_orders = len(orders)
        total_pieces = sum(order.quantity for order in orders)
        fulfilled_orders = result.total_orders_fulfilled
        
        ax.text(0.1, y_pos, f'Orders: {fulfilled_orders}/{total_orders}', 
               ha='left', va='top', fontsize=9, color=theme['text_color'])
        y_pos -= line_height * 0.8
        
        ax.text(0.1, y_pos, f'Total pieces: {total_pieces}', 
               ha='left', va='top', fontsize=9, color=theme['text_color'])
        y_pos -= line_height * 0.8
        
        # Group orders by priority
        from surface_optimizer.core.models import Priority
        priority_counts = {}
        for order in orders:
            priority = order.priority.name if hasattr(order.priority, 'name') else str(order.priority)
            priority_counts[priority] = priority_counts.get(priority, 0) + order.quantity
        
        for priority, count in priority_counts.items():
            ax.text(0.1, y_pos, f'{priority}: {count} pieces', 
                   ha='left', va='top', fontsize=8, color=theme['text_color'])
            y_pos -= line_height * 0.7 