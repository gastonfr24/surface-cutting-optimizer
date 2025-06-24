# Quick Start Guide - Simplified API 🚀

## Before vs After: API Simplification

### ❌ Old Way (Complex)
```python
# Multiple imports needed
from surface_optimizer.core.models import Stock, Order, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.utils.visualization import visualize_cutting_plan
from surface_optimizer.reporting.report_generator import ReportGenerator

# Manual setup required
optimizer = Optimizer()
algorithm = BestFitAlgorithm()
optimizer.set_algorithm(algorithm)

# Run optimization
result = optimizer.optimize(stocks, orders)

# Manual visualization and reporting
visualize_cutting_plan(result, stocks, save_path="plan.png")
report_gen = ReportGenerator()
report = report_gen.generate_cutting_coordinates_report(result, stocks)
```

### ✅ New Way (Simplified)
```python
# Single import line - everything you need!
from surface_optimizer import Stock, Order, MaterialType, Priority, Rectangle, optimize

# One-line optimization with auto-save
result = optimize(
    stocks, orders,
    priority='balanced',                      # Automatic algorithm selection
    save_visualization="plan.png",           # Auto-save visualization
    save_report="report.json"                # Auto-save report
)

# Easy result display and additional operations
result.show()                               # Quick summary
result.visualize()                          # Interactive display
result.generate_report("coordinates")       # Multiple report types
result.save_results()                       # Save everything at once
```

---

## 🚀 Ultra-Quick Start (30 seconds)

### 1. Create your data
```python
from surface_optimizer import Stock, Order, Rectangle, MaterialType, optimize

# Define available stock
stocks = [
    Stock(id="PANEL_1", width=1200, height=800, material_type=MaterialType.WOOD, cost_per_unit=25.0),
    Stock(id="PANEL_2", width=1000, height=600, material_type=MaterialType.WOOD, cost_per_unit=18.0)
]

# Define what to cut
orders = [
    Order(id="PIECE_1", shape=Rectangle(300, 200), quantity=2, material_type=MaterialType.WOOD),
    Order(id="PIECE_2", shape=Rectangle(150, 400), quantity=1, material_type=MaterialType.WOOD),
    Order(id="PIECE_3", shape=Rectangle(250, 250), quantity=3, material_type=MaterialType.WOOD)
]
```

### 2. Optimize and save everything
```python
# Single line optimization with auto-save
result = optimize(
    stocks, orders,
    save_visualization="cutting_plan.png",
    save_report="optimization_report.json"
)

# Display results
result.show()
```

### 3. That's it! 🎉
You now have:
- ✅ Optimized cutting plan
- ✅ Visualization saved as PNG
- ✅ Complete report saved as JSON
- ✅ Results displayed in console

---

## 📊 Advanced Features (Still Simple!)

### Different Algorithm Priorities
```python
# Speed (fastest)
result = optimize(stocks, orders, priority='speed')

# Quality (better efficiency)
result = optimize(stocks, orders, priority='quality')

# Maximum efficiency (best results)
result = optimize(stocks, orders, priority='maximum')
```

### Multiple Report Types
```python
result = optimize(stocks, orders)

# Different report formats
cutting_coords = result.generate_report("coordinates", "cuts.json")
performance = result.generate_report("performance", "metrics.json")
materials = result.generate_report("material", "materials.json")

# Save everything at once
result.save_results("my_project", "analysis_v1")
```

### Interactive Workflow
```python
result = optimize(stocks, orders)

# Quick summary
result.show()

# Show cutting plan (opens window if possible)
result.visualize()

# Show cutting plan and save
result.visualize("my_plan.png")

# Complete package
result.save_results()
```

### Comparison Mode
```python
from surface_optimizer import compare_algorithms

# Compare multiple algorithms easily
comparison = compare_algorithms(stocks, orders, ['best_fit', 'genetic', 'hybrid'])
print(comparison)
```

---

## 🔧 Configuration Options

### Basic Configuration
```python
result = optimize(
    stocks, orders,
    allow_rotation=True,           # Allow 90° rotation
    cutting_width=3.0,             # Blade kerf in mm
    max_computation_time=30,       # Time limit in seconds
    prioritize_orders=True         # Process by order priority
)
```

### Custom Output Directories
```python
result = optimize(
    stocks, orders,
    save_visualization="plan.png",
    save_report="report.json",
    output_dir="results/project_2023"    # Custom directory
)
```

### Advanced Configuration
```python
from surface_optimizer import OptimizationConfig

config = OptimizationConfig(
    allow_rotation=True,
    cutting_width=2.5,
    max_computation_time=60,
    prioritize_orders=True,
    gap_between_pieces=1.0
)

result = optimize(stocks, orders, config=config)
```

---

## 🎯 Real-World Example

```python
from surface_optimizer import Stock, Order, Rectangle, MaterialType, Priority, optimize
import pandas as pd

# Load from CSV (typical workflow)
stock_df = pd.read_csv("inventory.csv")
stocks = [
    Stock(
        id=row['id'],
        width=row['width'],
        height=row['height'],
        material_type=MaterialType.METAL,
        cost_per_unit=row['cost']
    )
    for _, row in stock_df.iterrows()
]

orders_df = pd.read_csv("cutting_orders.csv")
orders = [
    Order(
        id=row['id'],
        shape=Rectangle(row['width'], row['height']),
        quantity=row['qty'],
        priority=Priority.HIGH if row['urgent'] else Priority.MEDIUM,
        material_type=MaterialType.METAL
    )
    for _, row in orders_df.iterrows()
]

# Optimize with production settings
result = optimize(
    stocks, orders,
    priority='quality',                    # Focus on efficiency
    allow_rotation=True,                   # Standard practice
    cutting_width=3.0,                     # Plasma cutter kerf
    save_visualization="production_plan.png",
    save_report="production_report.json",
    output_dir="production/2023_12_15"
)

# Display for operator
result.show()
print(f"💰 Total cost: ${result.total_cost:.2f}")
print(f"♻️  Material efficiency: {result.efficiency_percentage:.1f}%")
print(f"📦 Panels needed: {result.total_stock_used}")

# Generate CNC coordinates
cnc_data = result.generate_report("coordinates", "cnc_program.json")
```

---

## 🆚 Migration Guide

### If you're using the old API:

**Replace this:**
```python
from surface_optimizer.core.models import Stock, Order
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.utils.visualization import visualize_cutting_plan
```

**With this:**
```python
from surface_optimizer import Stock, Order, optimize
```

**Replace this:**
```python
optimizer = Optimizer()
optimizer.set_algorithm(BestFitAlgorithm())
result = optimizer.optimize(stocks, orders)
visualize_cutting_plan(result, stocks, "plan.png")
```

**With this:**
```python
result = optimize(stocks, orders, save_visualization="plan.png")
result.show()
```

---

## ✨ Key Benefits

1. **🔥 90% fewer import lines** - Just import what you need
2. **⚡ One-line optimization** - No manual setup required
3. **💾 Auto-save everything** - Visualization + reports in one go
4. **🎨 Interactive results** - Built-in display and visualization methods
5. **📊 Multiple report formats** - Coordinates, performance, materials
6. **🤖 Smart defaults** - Automatic algorithm selection
7. **🔄 Backward compatible** - Old API still works

---

## 🚀 What's Next?

1. **Try the demos** - Run `python demo/02_multi_stock_demo.py`
2. **Check examples** - See `demo/` folder for more use cases
3. **Read the docs** - Full documentation available
4. **Join the community** - Report issues and suggestions

The Surface Cutting Optimizer just became **10x easier to use** while remaining just as powerful! 🎉

---

**💡 Tip**: Empieza con casos simples y ve aumentando la complejidad gradualmente. La librería incluye casos de test con soluciones óptimas conocidas para que puedas validar tus resultados. 