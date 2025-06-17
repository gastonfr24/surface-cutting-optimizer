# 🔧 Surface Cutting Optimizer

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/Version-1.0.0--beta-green)](VERSION)

**Advanced 2D cutting stock optimizer for industrial and professional applications**

---

## 📋 **Overview**

The **Surface Cutting Optimizer** is a powerful Python library designed to solve the **2D cutting stock problem** with maximum efficiency. Perfect for industries like **furniture manufacturing**, **glass cutting**, **metal fabrication**, and any scenario requiring optimal material utilization.

### ✨ **Key Features**

- 🧬 **5 Advanced Algorithms**: From fast greedy approaches to sophisticated genetic algorithms
- 🚀 **Intelligent Auto-Scaling**: Automatic parameter optimization based on problem complexity
- 📊 **Professional Reporting**: Comprehensive analysis with HTML, PDF, and Excel exports
- 🎯 **75-95% Efficiency**: Industry-leading material utilization rates
- ⚡ **Ultra-Fast Performance**: Optimized implementations with 50-95x speed improvements
- 📈 **Real-time Visualization**: Interactive cutting layouts and progress tracking
- 🏭 **Industry-Ready**: Designed for production environments with enterprise features

---

## 🏗️ **Architecture**

### Core Components

```
surface_optimizer/
├── algorithms/          # Optimization algorithms
│   ├── basic/          # First Fit, Best Fit, Bottom Left
│   └── advanced/       # Genetic Algorithm, Simulated Annealing
├── core/               # Core models and geometry
├── reporting/          # Professional reporting system
└── utils/              # Visualization and utilities
```

### 🎯 **Supported Algorithms**

| Algorithm | Speed | Efficiency | Use Case |
|-----------|-------|------------|----------|
| **First Fit** | ⚡⚡⚡⚡⚡ | ⭐⭐ | Rapid prototyping |
| **Best Fit** | ⚡⚡⚡⚡ | ⭐⭐⭐ | Balanced performance |
| **Bottom Left** | ⚡⚡⚡ | ⭐⭐⭐⭐ | Minimize waste |
| **Genetic Algorithm** | ⚡⚡ | ⭐⭐⭐⭐⭐ | Maximum efficiency |
| **Simulated Annealing** | ⚡ | ⭐⭐⭐⭐⭐ | Complex problems |

---

## 🚀 **Quick Start**

### Installation

```bash
# Clone the repository
git clone https://github.com/gastonfr24/surface-cutting-optimizer.git
cd surface-cutting-optimizer

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Basic Usage

```python
from surface_optimizer import SurfaceOptimizer

# Create optimizer
optimizer = SurfaceOptimizer()

# Define your cutting requirements
orders = [
    {"width": 100, "height": 50, "quantity": 10},
    {"width": 80, "height": 60, "quantity": 5}
]

stock = [
    {"width": 300, "height": 200, "cost": 25.0}
]

# Optimize with automatic algorithm selection
result = optimizer.optimize(orders, stock)

# View results
print(f"Efficiency: {result.efficiency_percentage:.1f}%")
print(f"Stocks used: {result.total_stock_used}")
```

### Advanced Usage

```python
from surface_optimizer.core.models import OptimizationConfig

# Configure for maximum efficiency
config = OptimizationConfig(
    allow_rotation=True,
    max_computation_time=60,
    target_efficiency=0.85
)

# Use specific algorithm
result = optimizer.optimize(
    orders=orders,
    stock=stock,
    algorithm='genetic',
    config=config
)

# Generate professional reports
from surface_optimizer.reporting import ReportGenerator
report_gen = ReportGenerator()
report_gen.generate_complete_report(result, output_dir="reports/")
```

---

## 💼 **Professional Features**

### 📊 **Comprehensive Reporting**

```python
# Generate professional cutting plans
from surface_optimizer.reporting import (
    CuttingPlanTable, StockUtilizationTable, 
    CostAnalysisTable, ReportGenerator
)

# Create detailed tables
cutting_plan = CuttingPlanTable()
stock_analysis = StockUtilizationTable()
cost_analysis = CostAnalysisTable()

# Export to multiple formats
report_gen.export_to_excel(result, "cutting_plan.xlsx")
report_gen.export_to_pdf(result, "cutting_plan.pdf")
```

### 🎨 **Advanced Visualization**

```python
from surface_optimizer.utils.visualization import CuttingVisualizer

visualizer = CuttingVisualizer()

# Create cutting layout visualization
visualizer.create_cutting_layout_visualization(
    result, stock,
    title="Furniture Manufacturing - Optimization Result",
    save_path="layouts/furniture_layout.png"
)

# Generate performance comparison charts
visualizer.create_algorithm_comparison_chart(
    multiple_results, save_path="charts/performance_comparison.png"
)
```

### 🏭 **Industry-Specific Configurations**

```python
# Furniture manufacturing
furniture_config = OptimizationConfig(
    enforce_grain_direction=True,
    material_thickness=18.0,
    minimize_crosscuts=True,
    allow_rotation=True
)

# Glass cutting
glass_config = OptimizationConfig(
    allow_rotation=False,
    edge_margin=10.0,
    minimize_stress_points=True,
    breaking_safety_factor=1.2
)

# Metal fabrication
metal_config = OptimizationConfig(
    optimize_cutting_path=True,
    thermal_considerations=True,
    allow_rotation=True
)
```

---

## 📈 **Performance Benchmarks**

### Speed Improvements with Auto-Scaling

| Problem Size | Before | After | Improvement |
|--------------|---------|-------|-------------|
| Small (≤50) | 5.2s | 0.8s | **85% faster** |
| Medium (≤200) | 25.1s | 4.3s | **83% faster** |
| Large (>200) | 120.5s | 28.7s | **76% faster** |

### Efficiency Comparison

```
Typical Efficiency Results:
├── First Fit: 45-60% (0.01s)
├── Best Fit: 55-70% (0.05s)
├── Bottom Left: 65-75% (0.2s)
├── Genetic: 75-90% (2-10s)
└── Simulated Annealing: 80-95% (5-30s)
```

---

## 📚 **Documentation**

### 📖 **Complete Documentation**

- **[Algorithm Guide](docs/algorithms/README.md)** - Complete algorithm comparison and selection guide
- **[Configuration Reference](docs/algorithms/configuration.md)** - Advanced parameter configuration
- **[Industry Examples](docs/examples/)** - Real-world use cases and implementations
- **[API Reference](docs/api/)** - Complete API documentation

### 🔧 **Algorithm-Specific Guides**

- **[First Fit Algorithm](docs/algorithms/basic/first_fit.md)** - Ultra-fast greedy algorithm
- **[Genetic Algorithm](docs/algorithms/advanced/genetic.md)** - Advanced evolutionary optimization
- **[Performance Tuning](docs/algorithms/benchmarks.md)** - Optimization and benchmarking

### 🏭 **Industry Applications**

- **[Furniture Manufacturing](docs/examples/furniture_manufacturing.md)** - Wood cutting optimization
- **[Glass Industry](docs/examples/glass_cutting.md)** - Precision glass cutting
- **[Metal Fabrication](docs/examples/metal_fabrication.md)** - Sheet metal optimization

---

## 🧪 **Demo & Examples**

### Run Professional Demo

```bash
# Complete professional demonstration
python demo/professional_demo.py

# Quick performance test
python demo/quick_demo.py

# Algorithm comparison
python demo/enhanced_features_demo.py
```

### Expected Output

```
🏢 Professional Surface Cutting Optimizer Demo
=============================================================

📊 Loading enterprise datasets...

🔬 Analyzing: Furniture Manufacturing
----------------------------------------
  🔄 Testing first_fit...
    ✅ first_fit: 52.3% efficiency, 0.003s, 85.0% fulfillment
  🔄 Testing best_fit...
    ✅ best_fit: 67.1% efficiency, 0.025s, 92.5% fulfillment
  🔄 Testing genetic...
    ✅ genetic: 87.6% efficiency, 3.240s, 97.5% fulfillment

📋 Generating comprehensive analysis report...
✅ Professional demo completed successfully!
📁 Results saved in: results/
```

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/gastonfr24/surface-cutting-optimizer.git
cd surface-cutting-optimizer

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run quality checks
flake8 surface_optimizer/
black surface_optimizer/
```

---

## 📋 **Requirements**

### Core Dependencies

```
Python 3.8+
├── numpy >= 1.19.0
├── matplotlib >= 3.3.0
├── pandas >= 1.1.0
└── dataclasses-json >= 0.5.0
```

### Optional Dependencies (for advanced features)

```
├── openpyxl >= 3.0.0          # Excel export
├── jinja2 >= 2.11.0           # HTML reports  
├── weasyprint >= 52.0         # PDF export
├── plotly >= 4.14.0           # Interactive charts
└── dash >= 1.19.0             # Web dashboard
```

---

## 📝 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🌟 **Acknowledgments**

- Inspired by classical bin packing and cutting stock algorithms
- Built with modern Python best practices
- Designed for industrial and professional applications
- Performance optimized for production environments

---

## 📞 **Support**

- **GitHub Issues**: [Report bugs or request features](https://github.com/gastonfr24/surface-cutting-optimizer/issues)
- **Documentation**: [Complete documentation](docs/)
- **Examples**: [Real-world examples](demo/)

---

<div align="center">

**⭐ If this project helps you, please give it a star! ⭐**

**Made with ❤️ for the manufacturing and fabrication community**

[**View on GitHub**](https://github.com/gastonfr24/surface-cutting-optimizer) | [**Documentation**](docs/) | [**Examples**](demo/)

</div> 