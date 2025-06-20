# 🔧 Surface Cutting Optimizer

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/Version-1.0.0--beta-green)](VERSION)

**Professional 2D cutting optimization library for industrial applications**

---

## 📋 **Overview**

The **Surface Cutting Optimizer** is a powerful Python library designed to solve complex **2D cutting stock problems** with advanced algorithms and professional-grade features. Engineered for industries requiring precision material utilization including **furniture manufacturing**, **glass cutting**, **metal fabrication**, **textile production**, and **packaging**.

### ✨ **Core Capabilities**

- 🧬 **Advanced Algorithms**: Multiple optimization approaches from fast heuristics to genetic algorithms
- 🎯 **High Efficiency**: Achieve 75-95% material utilization with intelligent placement strategies
- ⚡ **Performance Optimized**: Fast computation for both small batches and large-scale production
- 📊 **Professional Reporting**: Comprehensive analysis with visualization and export capabilities
- 🔧 **Industrial Features**: Rotation control, material constraints, priority handling, and custom configurations
- 📈 **Real-time Analytics**: Performance metrics, waste analysis, and optimization insights
- 🏭 **Production Ready**: Robust error handling and validation for manufacturing environments

### 🛠️ **Technical Specifications**

- **Geometry Support**: Rectangles, circles, polygons with complex constraints
- **Material Types**: Metal, wood, glass, fabric, plastic with specific properties
- **Cutting Precision**: Configurable cutting widths and material thickness handling
- **Rotation Logic**: Intelligent shape rotation with directional constraints
- **Priority Systems**: Order prioritization with custom urgency levels
- **Validation**: Comprehensive overlap detection and boundary checking

---

## 🏗️ **Architecture**

### Core Components

```
surface_optimizer/
├── algorithms/          # Optimization algorithms
│   ├── basic/          # First Fit, Best Fit, Bottom Left
│   └── advanced/       # Genetic Algorithm, Simulated Annealing, Hybrid
├── core/               # Core models and geometry engine
│   ├── models.py       # Stock, Order, Configuration models
│   ├── geometry.py     # Shape classes and calculations
│   └── optimizer.py    # Main optimization engine
├── reporting/          # Professional reporting system
└── utils/              # Visualization and utilities
```

### 🎯 **Algorithm Portfolio**

| Algorithm | Complexity | Best Use Case | Characteristics |
|-----------|------------|---------------|-----------------|
| **First Fit** | O(n log n) | Rapid processing | Fast, good for simple layouts |
| **Best Fit** | O(n²) | Balanced efficiency | Moderate speed, better placement |
| **Bottom Left** | O(n²) | Compact layouts | Minimizes vertical waste |
| **Genetic Algorithm** | Configurable | Maximum efficiency | Evolutionary approach, highly optimized |
| **Hybrid Genetic** | Adaptive | Complex problems | Combines multiple strategies |

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
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.core.models import Stock, Order, OptimizationConfig
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm

# Create optimizer with algorithm
optimizer = Optimizer()
optimizer.set_algorithm(FirstFitAlgorithm())

# Define materials and orders
stocks = [Stock("SHEET_001", 3000, 1500, thickness=5.0)]
orders = [
    Order("PART_A", Rectangle(400, 300), quantity=10),
    Order("PART_B", Rectangle(350, 250), quantity=6)
]

# Configure optimization parameters
config = OptimizationConfig(
    allow_rotation=True,
    cutting_width=3.0,
    prioritize_orders=True
)

# Execute optimization
result = optimizer.optimize(stocks, orders, config)

# Analyze results
print(f"Material efficiency: {result.efficiency_percentage:.1f}%")
print(f"Stocks utilized: {result.total_stock_used}")
print(f"Orders fulfilled: {result.total_orders_fulfilled}")
```

### Advanced Configuration

```python
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm

# Configure genetic algorithm for complex problems
genetic_algo = GeneticAlgorithm(
    population_size=50,
    generations=100,
    mutation_rate=0.1,
    crossover_rate=0.8
)

optimizer.set_algorithm(genetic_algo)

# Industrial configuration
industrial_config = OptimizationConfig(
    allow_rotation=True,
    cutting_width=3.2,          # Laser cutting kerf
    material_waste_factor=0.02,  # 2% material loss factor
    prioritize_orders=True,
    max_computation_time=120    # 2 minutes max
)

result = optimizer.optimize(stocks, orders, industrial_config)
```

---

## 💼 **Professional Features**

### 📊 **Comprehensive Analysis**

```python
from surface_optimizer.reporting import ReportGenerator
from surface_optimizer.utils.visualization import CuttingVisualizer

# Generate detailed reports
report_gen = ReportGenerator()
report_gen.create_efficiency_report(result)
report_gen.create_waste_analysis(result)
report_gen.export_cutting_plan(result, format='xlsx')

# Create visual layouts
visualizer = CuttingVisualizer()
visualizer.create_cutting_layout(result, title="Production Layout")
visualizer.create_efficiency_chart(result)
```

### 🔧 **Material-Specific Configurations**

```python
# Furniture manufacturing (wood grain considerations)
furniture_config = OptimizationConfig(
    respect_grain_direction=True,
    edge_banding_allowance=2.0,
    minimize_crosscuts=True
)

# Glass cutting (no rotation, stress considerations)
glass_config = OptimizationConfig(
    allow_rotation=False,
    edge_margin=5.0,
    minimize_stress_concentration=True
)

# Metal fabrication (thermal expansion, cutting path)
metal_config = OptimizationConfig(
    thermal_expansion_factor=0.001,
    optimize_cutting_path=True,
    cutting_width=3.5  # Plasma cutting
)
```

### 🎯 **Geometry Handling**

```python
from surface_optimizer.core.geometry import Rectangle, Circle, Polygon

# Complex shape support
orders = [
    Order("RECT_001", Rectangle(400, 300), 5),
    Order("CIRCLE_001", Circle(radius=150), 3),
    Order("POLYGON_001", Polygon([(0,0), (100,0), (50,100)]), 2)
]

# Custom validation
config.validate_geometry = True
config.check_minimum_distances = True
config.ensure_accessible_cuts = True
```

---

## 📈 **Performance Metrics**

### Efficiency Benchmarks

| Material Type | Average Efficiency | Typical Use Case |
|---------------|-------------------|------------------|
| **Wood Panels** | 85-92% | Furniture, cabinetry |
| **Metal Sheets** | 80-90% | HVAC, automotive |
| **Glass Sheets** | 75-85% | Windows, displays |
| **Fabric Rolls** | 82-88% | Apparel, upholstery |

### Computational Performance

| Problem Size | Algorithm | Processing Time |
|--------------|-----------|-----------------|
| 50 pieces | First Fit | < 1 second |
| 200 pieces | Best Fit | 2-5 seconds |
| 500 pieces | Genetic | 15-30 seconds |
| 1000+ pieces | Hybrid | 1-3 minutes |

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