# 🧠 Optimization Algorithms

Surface Cutting Optimizer includes **5 specialized algorithms** to solve the 2D cutting stock problem, each with unique characteristics adapted to different use scenarios.

## 📋 **Algorithm Summary**

| Algorithm | Type | Speed | Efficiency | Complexity | Use Case |
|-----------|------|-------|------------|------------|----------|
| [First Fit](basic/first_fit.md) | Basic | ⚡⚡⚡⚡⚡ | ⭐⭐ | O(n×m) | Rapid prototyping |
| [Best Fit](basic/best_fit.md) | Basic | ⚡⚡⚡⚡ | ⭐⭐⭐ | O(n×m log m) | Speed/quality balance |
| [Bottom Left](basic/bottom_left.md) | Basic | ⚡⚡⚡ | ⭐⭐⭐⭐ | O(n²) | Minimize waste |
| [Genetic Algorithm](advanced/genetic.md) | Advanced | ⚡⚡ | ⭐⭐⭐⭐⭐ | O(g×p×n) | Maximum efficiency |
| [Simulated Annealing](advanced/simulated_annealing.md) | Advanced | ⚡ | ⭐⭐⭐⭐⭐ | O(i×n) | Complex problems |

**Legend**: ⚡ = Speed, ⭐ = Efficiency

## 🎯 **Algorithm Selection Guide**

### For Development and Prototyping
```python
# Ultra-fast for testing
algorithm = "first_fit"
```

### For Production with Balance
```python
# Good speed/efficiency ratio
algorithm = "best_fit"
```

### For Maximum Efficiency
```python
# Best result, more computation time
algorithm = "genetic"
```

### For Specific Problems
```python
# Minimize corner waste
algorithm = "bottom_left"

# Very complex or irregular problems
algorithm = "simulated_annealing"
```

## 📊 **Performance Comparison**

### Typical Benchmarks (1000 pieces, 50 stocks)

| Algorithm | Time | Efficiency | Stocks Used | Waste |
|-----------|------|------------|-------------|-------|
| First Fit | 0.01s | 45-60% | High | 40-55% |
| Best Fit | 0.05s | 55-70% | Medium | 30-45% |
| Bottom Left | 0.2s | 65-75% | Medium-Low | 25-35% |
| Genetic | 2-10s | 75-90% | Low | 10-25% |
| Simulated Annealing | 5-30s | 80-95% | Very Low | 5-20% |

*Results vary depending on problem type and configuration*

## 🔧 **Advanced Configuration**

### Intelligent Auto-Scaling
Advanced algorithms include **automatic auto-scaling** based on problem complexity:

```python
# System automatically detects:
# - Problem size (small/medium/large)
# - Adjusts parameters in real time
# - Optimizes speed vs quality

config = OptimizationConfig(
    auto_scaling=True,  # Enabled by default
    max_computation_time=60,  # Time limit
    target_efficiency=0.8  # Desired efficiency
)
```

### Manual Parameter Configuration
```python
# For total control over behavior
config = OptimizationConfig(
    # Genetic algorithms
    population_size=50,
    generations=100,
    mutation_rate=0.1,
    
    # Simulated annealing
    initial_temperature=1000,
    cooling_rate=0.95,
    min_temperature=0.1,
    
    # General
    allow_rotation=True,
    precision_tolerance=0.001,
    parallel_processing=True
)
```

## 📖 **Detailed Documentation**

### Basic Algorithms
- **[First Fit](basic/first_fit.md)** - Ultra-fast greedy algorithm
- **[Best Fit](basic/best_fit.md)** - Optimal fit optimization
- **[Bottom Left](basic/bottom_left.md)** - Bottom-left-fill strategy

### Advanced Algorithms
- **[Genetic Algorithm](advanced/genetic.md)** - Evolutionary algorithm with auto-scaling
- **[Simulated Annealing](advanced/simulated_annealing.md)** - Adaptive simulated annealing

### Complementary Guides
- **[Configuration](configuration.md)** - Parameters and advanced options
- **[Benchmarks](benchmarks.md)** - Comparisons and test cases
- **[Troubleshooting](troubleshooting.md)** - Common problem solutions

## 🚀 **Quick Start**

```python
from surface_optimizer import SurfaceOptimizer

# Create optimizer
optimizer = SurfaceOptimizer()

# Sample data
orders = [
    {"width": 100, "height": 50, "quantity": 10},
    {"width": 80, "height": 60, "quantity": 5}
]
stock = [
    {"width": 300, "height": 200, "cost": 25.0}
]

# Optimize with automatic algorithm
result = optimizer.optimize(orders, stock)

# Optimize with specific algorithm
result = optimizer.optimize(orders, stock, algorithm='genetic')

# View results
print(f"Efficiency: {result.efficiency_percentage:.1f}%")
print(f"Stocks used: {result.total_stock_used}")
```

## 🔗 **References**

- [Installation and Configuration](../user/quick_start.md)
- [API Reference](../api/README.md)
- [Advanced Examples](../examples/README.md)
- [Contributing Guidelines](../CONTRIBUTING.md) 