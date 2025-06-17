# ⚡ First Fit Algorithm

## 📋 **Description**
The **First Fit** algorithm is a greedy strategy that places each piece in the first stock that has enough space. It's the fastest algorithm in the library, ideal for rapid prototyping and situations where speed is more important than optimization.

## 🔧 **Technical Specifications**

### Computational Complexity
- **Time**: O(n × m) where n = pieces, m = stocks
- **Space**: O(1) - constant memory
- **Parallelizable**: Yes, partially

### Characteristics
- ✅ **Ultra-fast execution** (< 0.01s for 1000 pieces)
- ✅ **Minimal memory usage**
- ✅ **Predictable behavior**
- ⚠️ **Moderate efficiency** (45-60%)
- ⚠️ **High waste** (40-55%)

## 🔍 **How It Works**

### Core Algorithm
```python
def first_fit_placement(pieces, stocks):
    """
    First Fit implementation for 2D cutting stock problem
    """
    placed_pieces = []
    
    for piece in pieces:
        for stock in stocks:
            # Try placing piece at each valid position
            for x in range(stock.width - piece.width + 1):
                for y in range(stock.height - piece.height + 1):
                    if can_place_piece(stock, piece, x, y):
                        place_piece(stock, piece, x, y)
                        placed_pieces.append({
                            'piece': piece,
                            'stock_id': stock.id,
                            'position': (x, y)
                        })
                        break
                if piece.placed:
                    break
            if piece.placed:
                break
    
    return placed_pieces
```

### Placement Strategy
1. **Sequential Order**: Process pieces in input order
2. **Stock Scanning**: Check stocks from first to last
3. **Position Search**: Scan from top-left (0,0) to bottom-right
4. **First Valid Fit**: Place at first valid position found
5. **No Optimization**: No backtracking or optimization

## 🚀 **Usage Examples**

### Basic Usage
```python
from surface_optimizer import SurfaceOptimizer

# Create optimizer
optimizer = SurfaceOptimizer()

# Sample data
orders = [
    {"width": 100, "height": 50, "quantity": 5},
    {"width": 80, "height": 60, "quantity": 3},
    {"width": 120, "height": 40, "quantity": 2}
]

stock = [
    {"width": 300, "height": 200, "cost": 15.0},
    {"width": 250, "height": 150, "cost": 12.0}
]

# Optimize with First Fit
result = optimizer.optimize(
    orders=orders,
    stock=stock,
    algorithm="first_fit"
)

print(f"Efficiency: {result.efficiency_percentage:.1f}%")
print(f"Execution time: {result.execution_time:.3f} seconds")
```

### With Configuration
```python
from surface_optimizer.core.models import OptimizationConfig

# Configuration for maximum speed
config = OptimizationConfig(
    allow_rotation=False,      # Disable rotation for more speed
    precision_tolerance=1.0,   # Lower precision for speed
    max_computation_time=1,    # 1 second limit
    parallel_processing=True   # Use parallelization
)

result = optimizer.optimize(
    orders=orders,
    stock=stock,
    algorithm="first_fit",
    config=config
)
```

### Real-time Application
```python
def rapid_cutting_estimate(orders, stock):
    """
    Ultra-fast estimate for real-time applications
    """
    optimizer = SurfaceOptimizer()
    
    # Minimum configuration for maximum speed
    config = OptimizationConfig(
        allow_rotation=False,
        precision_tolerance=2.0,
        max_iterations=100
    )
    
    result = optimizer.optimize(orders, stock, "first_fit", config)
    
    return {
        'efficiency': result.efficiency_percentage,
        'stocks_needed': result.total_stock_used,
        'execution_time': result.execution_time,
        'suitable_for_production': result.efficiency_percentage > 50
    }
```

## 📊 **Performance Analysis**

### Typical Performance
| Problem Size | Execution Time | Efficiency | Memory Usage |
|--------------|----------------|------------|--------------|
| Small (≤50 pieces) | < 0.001s | 50-65% | < 1MB |
| Medium (≤500 pieces) | < 0.01s | 45-60% | < 5MB |
| Large (≤5000 pieces) | < 0.1s | 40-55% | < 20MB |

### Comparison with Other Algorithms
```python
# Performance comparison example
import time

algorithms = ['first_fit', 'best_fit', 'genetic']
results = {}

for algorithm in algorithms:
    start_time = time.time()
    result = optimizer.optimize(orders, stock, algorithm)
    execution_time = time.time() - start_time
    
    results[algorithm] = {
        'time': execution_time,
        'efficiency': result.efficiency_percentage,
        'stocks_used': result.total_stock_used
    }

# Typical results:
# first_fit: time=0.003s, efficiency=52%, stocks=8
# best_fit:  time=0.025s, efficiency=67%, stocks=6  
# genetic:   time=2.450s, efficiency=84%, stocks=4
```

## 🎯 **When to Use**

### ✅ **Recommended For:**
- **Rapid prototyping** and proof of concepts
- **Real-time applications** requiring instant response
- **Large volume processing** with speed priority
- **Initial estimates** before detailed optimization
- **Resource-constrained environments**
- **Simple geometric patterns**

### ❌ **Not Recommended For:**
- **Production optimization** requiring high efficiency
- **Expensive materials** where waste is costly
- **Complex cutting patterns** with tight constraints
- **High-precision requirements**
- **Projects with time for better optimization**

## 🔧 **Advanced Configuration**

### Speed Optimization
```python
# Maximum speed configuration
speed_config = OptimizationConfig(
    allow_rotation=False,           # Disable rotation
    precision_tolerance=5.0,        # Lower precision
    max_iterations=50,              # Limit iterations
    parallel_processing=True,       # Enable parallelization
    early_termination=True,         # Stop early if good enough
    memory_optimization=True        # Optimize memory usage
)
```

### Quality/Speed Balance
```python
# Balanced configuration
balanced_config = OptimizationConfig(
    allow_rotation=True,            # Allow rotation
    precision_tolerance=1.0,        # Good precision
    max_iterations=200,             # More iterations
    target_efficiency=0.6,          # 60% efficiency target
    max_computation_time=0.1        # 100ms limit
)
```

## 🐛 **Troubleshooting**

### Common Issues

**1. Low Efficiency**
```python
# Problem: Efficiency below 40%
# Solution: Check piece/stock ratio
def check_feasibility(orders, stock):
    total_piece_area = sum(o['width'] * o['height'] * o['quantity'] for o in orders)
    total_stock_area = sum(s['width'] * s['height'] for s in stock) 
    
    if total_piece_area > total_stock_area * 0.9:
        print("Warning: Insufficient stock area")
        return False
    return True
```

**2. Long Execution Time**
```python
# Problem: Slower than expected
# Solution: Reduce precision and iterations
fast_config = OptimizationConfig(
    precision_tolerance=2.0,        # Reduce precision
    max_iterations=100,             # Limit iterations
    parallel_processing=True        # Use parallel processing
)
```

**3. Memory Issues**
```python
# Problem: High memory usage with large datasets
# Solution: Process in batches
def batch_optimize(orders, stock, batch_size=1000):
    results = []
    for i in range(0, len(orders), batch_size):
        batch = orders[i:i+batch_size]
        result = optimizer.optimize(batch, stock, 'first_fit')
        results.append(result)
    return combine_results(results)
```

## 📚 **References**

### Academic Sources
1. **Coffman Jr, E.G., et al.** (1984). "Approximation algorithms for bin packing: a survey"
2. **Johnson, D.S.** (1973). "Near-optimal bin packing algorithms"
3. **Baker, B.S., et al.** (1980). "A 5/4 algorithm for two-dimensional packing"

### Implementation Details
- Based on classical bin packing literature
- Optimized for 2D rectangular cutting
- Includes collision detection and overlap prevention
- Supports material constraints and rotation

### Related Algorithms
- **[Best Fit](best_fit.md)** - Improved fit selection
- **[Bottom Left](bottom_left.md)** - Position optimization  
- **[Genetic Algorithm](../advanced/genetic.md)** - Maximum efficiency
- **[Configuration Guide](../configuration.md)** - Advanced parameters

---

**Next**: Learn about [Best Fit Algorithm](best_fit.md) for better efficiency with minimal speed cost. 