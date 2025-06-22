# Demo Scripts - Essential Workflows
## Simplified examples for new users

The demo scripts showcase core workflows of the Surface Cutting Optimizer library in a concise, easy-to-follow format.

## Quick Start

1. **Activate virtual environment:**
   ```bash
   env/Scripts/activate  # Windows
   source env/bin/activate  # Linux/Mac
   ```

2. **Run demos in order:**
   ```bash
   python demo/01_simple_csv_demo.py     # Basic CSV workflow
   python demo/02_multi_stock_demo.py    # Multiple panels
   python demo/03_overflow_demo.py       # Order discarding
   python demo/04_priority_sorting_demo.py  # Priority handling
   ```

## Demo Overview

| Demo | Purpose | Key Concepts | Duration |
|------|---------|--------------|----------|
| **01_simple_csv_demo.py** | Basic CSV integration | CSV loading, optimization, results output | 2-3 min |
| **02_multi_stock_demo.py** | Multi-panel optimization | Panel selection, cross-panel efficiency | 3-4 min |
| **03_overflow_demo.py** | Capacity handling | Priority processing, order discarding | 2-3 min |
| **04_priority_sorting_demo.py** | Advanced sorting | Tie-breaking strategies, configurable criteria | 1-2 min |

## Essential Code Pattern

All demos follow this core pattern:
```python
from surface_optimizer.core.models import Stock, Order, OptimizationConfig
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm

# 1. Create data (minimal required parameters)
stocks = [Stock("PANEL_001", 1200, 800)]  # id, width, height
orders = [Order("ORDER_A", Rectangle(300, 200))]  # id, shape

# 2. Configure optimization (defaults work great)
config = OptimizationConfig()  # rotation=True, prioritize=True, etc.
optimizer = Optimizer(config)
optimizer.set_algorithm(FirstFitAlgorithm())

# 3. Run optimization (library handles logging)
result = optimizer.optimize(stocks, orders)

# 4. Use results
print(f"Efficiency: {result.efficiency_percentage:.1f}%")
```

## Parameter Reference

### Stock() - Only 3 required parameters
```python
Stock(id, width, height)  # Minimal
Stock(id, width, height, thickness=6.0, material_type=MaterialType.GLASS, cost_per_unit=0.0)  # Full
```

**Required:**
- `id` (str) - Unique identifier
- `width` (float) - Width in mm
- `height` (float) - Height in mm

**Optional with defaults:**
- `thickness=6.0` - Thickness in mm
- `material_type=MaterialType.GLASS` - Material type
- `cost_per_unit=0.0` - Cost per panel

### Order() - Only 2 required parameters  
```python
Order(id, shape)  # Minimal
Order(id, shape, quantity=1, priority=Priority.MEDIUM, material_type=MaterialType.GLASS)  # Full
```

**Required:**
- `id` (str) - Unique identifier
- `shape` (Shape) - Rectangle(width, height) or Circle(radius)

**Optional with defaults:**
- `quantity=1` - Number of pieces needed
- `priority=Priority.MEDIUM` - Order priority (LOW, MEDIUM, HIGH, URGENT)
- `material_type=MaterialType.GLASS` - Must match stock material

### OptimizationConfig() - All parameters optional
```python
OptimizationConfig()  # All defaults
OptimizationConfig(allow_rotation=True, prioritize_orders=True, cutting_width=3.0)  # Custom
```

**Common options:**
- `allow_rotation=True` - Allow 90° piece rotation
- `prioritize_orders=True` - Process by priority level
- `cutting_width=3.0` - Blade kerf width in mm
- `order_sort_criteria=OrderSortCriteria.AREA_DESC` - Tie-breaking strategy

## Demo Details

### Demo 1: Basic CSV Integration
**File:** `demo/01_simple_csv_demo.py`

Shows the fundamental workflow: CSV files → Optimization → Results

**What it demonstrates:**
- Loading stock and orders from CSV files
- Basic optimization configuration  
- Interpreting efficiency results
- Saving visual and numerical outputs

**CSV Format:**
```csv
# simple_stock.csv
stock_id,width,height,cost
PANEL_001,1200,800,25.50

# simple_orders.csv
order_id,width,height,quantity,priority
ORDER_A,300,200,1,HIGH
```

### Demo 2: Multi-Panel Optimization
**File:** `demo/02_multi_stock_demo.py`

Shows optimization across multiple stock panels with different sizes and costs.

**What it demonstrates:**
- Multiple panel sizes and costs
- Cross-panel optimization strategy
- Stock utilization comparison
- Panel selection efficiency

**Key insight:** The optimizer automatically selects the most efficient panels.

### Demo 3: Overflow Handling
**File:** `demo/03_overflow_demo.py`

Shows what happens when demand exceeds stock capacity.

**What it demonstrates:**
- Capacity analysis and overflow prediction
- Priority-based processing (URGENT orders first)
- Order discarding behavior
- Unfulfilled order reporting

**Key insight:** Higher priority orders get processed first and are less likely to be discarded.

### Demo 4: Priority Sorting & Tie-Breaking
**File:** `demo/04_priority_sorting_demo.py`

Shows advanced order processing with configurable tie-breaking.

**What it demonstrates:**
- Priority-first processing (URGENT > HIGH > MEDIUM > LOW)
- Configurable tie-breaking when orders have same priority
- Different sorting strategies (area, quantity, date)
- Processing order impact on results

**Tie-breaking options:**
- `OrderSortCriteria.AREA_DESC` - Largest pieces first
- `OrderSortCriteria.QUANTITY_DESC` - Highest quantity first
- `OrderSortCriteria.CSV_ORDER` - Original CSV sequence

## Output Files

Each demo generates:
- **layout.png** - Visual cutting plan for production
- **report.json** - CNC-ready coordinates and metadata

Files are saved to: `demo/data/{demo_name}/results/`

## Advanced Usage

### Custom Materials
```python
from surface_optimizer.core.models import MaterialType

# Different materials
steel_stock = Stock("STEEL_001", 1000, 600, material_type=MaterialType.METAL)
wood_stock = Stock("WOOD_001", 1200, 800, material_type=MaterialType.WOOD)

# Orders must match stock material
steel_order = Order("CUT_001", Rectangle(200, 150), material_type=MaterialType.METAL)
```

### Priority Levels
```python
from surface_optimizer.core.models import Priority

orders = [
    Order("URGENT_ORDER", Rectangle(300, 200), priority=Priority.URGENT),   # Processed first
    Order("HIGH_ORDER", Rectangle(250, 180), priority=Priority.HIGH),       # Processed second
    Order("NORMAL_ORDER", Rectangle(200, 150), priority=Priority.MEDIUM),   # Processed third
    Order("LOW_ORDER", Rectangle(150, 100), priority=Priority.LOW)          # Processed last
]
```

### Algorithm Selection
```python
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm

# Try different algorithms
optimizer.set_algorithm(FirstFitAlgorithm())  # Fastest
optimizer.set_algorithm(BestFitAlgorithm())   # Better efficiency
optimizer.set_algorithm(BottomLeftAlgorithm())  # Compact placement
```

## Troubleshooting

### Common Issues

**"No module named 'surface_optimizer'"**
```bash
# Activate virtual environment
env/Scripts/activate  # Windows
source env/bin/activate  # Linux/Mac
```

**"No stocks available for material type"**
- Check that stock and order materials match
- Default is `MaterialType.GLASS` for both

**"Optimization failed: No valid placements found"**
- Check that pieces can physically fit in stock
- Verify dimensions are positive
- Try enabling rotation: `allow_rotation=True`

**Low efficiency results**
- Try different algorithms
- Enable rotation
- Check if stock size is appropriate for pieces

### Performance Tips

1. **Use appropriate stock sizes** - Too large = low efficiency, too small = pieces won't fit
2. **Enable rotation** - `allow_rotation=True` often improves efficiency significantly
3. **Prioritize important orders** - Use `Priority.HIGH` or `Priority.URGENT`
4. **Try different algorithms** - `BestFit` often gives better efficiency than `FirstFit`

## Integration Examples

### Web Application
```python
def optimize_cutting_plan(stock_data, order_data):
    stocks = [Stock(s['id'], s['width'], s['height']) for s in stock_data]
    orders = [Order(o['id'], Rectangle(o['width'], o['height'])) for o in order_data]
    
    optimizer = Optimizer(OptimizationConfig())
    optimizer.set_algorithm(FirstFitAlgorithm())
    
    result = optimizer.optimize(stocks, orders)
    
    return {
        'efficiency': result.efficiency_percentage,
        'stocks_used': result.total_stock_used,
        'pieces_placed': len(result.placed_shapes),
        'coordinates': [{'id': p.order_id, 'x': p.position[0], 'y': p.position[1]} 
                       for p in result.placed_shapes]
    }
```

### Database Integration
```python
def load_from_database():
    # Load from your database
    stocks = []
    for row in db.execute("SELECT * FROM stock_panels WHERE available=1"):
        stocks.append(Stock(row.id, row.width, row.height, cost_per_unit=row.cost))
    
    orders = []
    for row in db.execute("SELECT * FROM orders WHERE status='pending'"):
        priority = Priority.HIGH if row.urgent else Priority.MEDIUM
        orders.append(Order(row.id, Rectangle(row.width, row.height), 
                          quantity=row.qty, priority=priority))
    
    return stocks, orders
```

## Next Steps

After running the demos:
1. **Try your own data** - Create CSV files with your dimensions
2. **Experiment with algorithms** - Compare FirstFit vs BestFit vs BottomLeft
3. **Custom configurations** - Adjust parameters for your specific needs
4. **Production integration** - Use the library in your applications

For advanced features, see:
- [Quick Start Guide](quick_start.md)
- [Algorithm Documentation](../algorithms/README.md)
- [API Reference](../README.md) 