# 🧪 Surface Cutting Optimizer - Test Suite

Modern pytest-based test suite organized by test types and functionality.

## 📁 Test Organization

### **Structured by Test Types**

```
test/
├── 📁 unit/                    # Unit tests - Fast, isolated
│   ├── test_geometry.py        # Geometry classes and calculations
│   └── __init__.py
├── 📁 integration/             # Integration tests - Component interaction
│   ├── test_algorithms.py      # Algorithm functionality and interfaces
│   ├── test_overlap_detection.py # Critical overlap prevention
│   └── __init__.py
├── 📁 performance/             # Performance tests - Benchmarks and scaling
│   ├── test_performance.py     # Speed, memory, and scaling tests
│   └── __init__.py
├── 📁 validation/              # Industry validation - Real-world comparison
│   ├── test_supervised_validation.py # Industry benchmark validation
│   ├── README.md               # Validation documentation
│   └── __init__.py
├── 📁 data/                    # Test data and fixtures
│   ├── test_cases.py           # Reusable test cases and data
│   └── __init__.py
└── 📄 __init__.py              # Main test package
```

## 🎯 Test Categories

### **🔧 Unit Tests** (`test/unit/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 1 second each)
- **Coverage**: High coverage of edge cases
- **Examples**: Geometry calculations, shape validation

```bash
# Run only unit tests
pytest test/unit/ -v
```

### **🔗 Integration Tests** (`test/integration/`)
- **Purpose**: Test component interactions and workflows
- **Speed**: Moderate (1-5 seconds each)
- **Coverage**: End-to-end functionality
- **Examples**: Algorithm execution, overlap detection

```bash
# Run only integration tests
pytest test/integration/ -v
```

### **⚡ Performance Tests** (`test/performance/`)
- **Purpose**: Benchmark speed, memory, and scaling
- **Speed**: Variable (5-30 seconds)
- **Coverage**: Performance characteristics
- **Examples**: Algorithm speed, memory usage, large problems

```bash
# Run only performance tests
pytest test/performance/ -v

# Run with benchmarking
pytest test/performance/ --benchmark-only
```

### **🏭 Validation Tests** (`test/validation/`)
- **Purpose**: Compare against real-world industry solutions
- **Speed**: Slow (30+ seconds)
- **Coverage**: Business value validation
- **Examples**: Furniture, glass, metal, textile industry cases

```bash
# Run only validation tests
pytest test/validation/ -v

# Run validation with detailed output
pytest test/validation/ -v -s
```

## 🚀 Running Tests

### **Quick Commands**

```bash
# All tests
pytest

# Fast tests only (unit + integration)
pytest test/unit/ test/integration/

# By category
pytest test/unit/           # Unit tests
pytest test/integration/    # Integration tests  
pytest test/performance/    # Performance tests
pytest test/validation/     # Validation tests

# With coverage
pytest --cov=surface_optimizer --cov-report=html

# Parallel execution
pytest -n auto
```

### **Development Workflow**

```bash
# During development (fast feedback)
pytest test/unit/ test/integration/ -x --tb=short

# Before commit (comprehensive)
pytest --cov=surface_optimizer --cov-fail-under=80

# Release testing (complete validation)
pytest test/ -v
```

## 📊 Test Configuration

Uses `pytest.ini` with:
- **Coverage**: 80% minimum requirement
- **Markers**: Organized test categories
- **Parallel**: Support for parallel execution
- **Reports**: HTML, XML, and terminal coverage

## 🔍 Finding Tests

### **By Functionality**
```bash
# Geometry-related tests
pytest test/unit/test_geometry.py

# Algorithm tests
pytest test/integration/test_algorithms.py

# Overlap detection
pytest test/integration/test_overlap_detection.py

# Performance benchmarks
pytest test/performance/test_performance.py
```

### **By Test Type**
```bash
# Quick unit tests
pytest test/unit/

# Full integration testing
pytest test/integration/

# Performance analysis
pytest test/performance/

# Industry validation
pytest test/validation/
```

## 📈 Benefits of This Structure

### **1. Clear Separation of Concerns**
- ✅ **Unit**: Fast, isolated component testing
- ✅ **Integration**: Real workflow testing
- ✅ **Performance**: Speed and scaling analysis
- ✅ **Validation**: Business value verification

### **2. Flexible Execution**
- 🚀 **Development**: Run only unit/integration for speed
- 📊 **CI/CD**: Run unit/integration in pipeline
- 🔍 **Analysis**: Run performance for optimization
- 💼 **Validation**: Run validation for business cases

### **3. Easy Maintenance**
- 📁 **Organized**: Each test type in its own directory
- 🔍 **Discoverable**: Easy to find relevant tests
- 📝 **Documented**: Clear purpose for each category
- 🎯 **Focused**: Each test file has single responsibility

## 🛠️ Adding New Tests

### **Choosing the Right Category**

| Test Type | When to Use | Example |
|-----------|-------------|---------|
| **Unit** | Testing individual functions/classes | `Rectangle.area()` calculation |
| **Integration** | Testing component interaction | Algorithm + Optimizer workflow |
| **Performance** | Testing speed/memory/scaling | Algorithm with 1000 orders |
| **Validation** | Testing against real data | Furniture industry benchmark |

### **File Naming Convention**
- `test_*.py` - All test files start with `test_`
- Descriptive names: `test_geometry.py`, `test_algorithms.py`
- Group related functionality in same file

### **Import Patterns**
```python
# For tests in subdirectories
from test.data.test_cases import get_all_test_cases
from surface_optimizer.core.models import Stock, Order

# Use relative imports sparingly, prefer absolute
```

## 📞 Help & Support

1. **Test Structure Questions**: Check this README
2. **pytest Issues**: See [pytest documentation](https://docs.pytest.org/)
3. **Performance Testing**: Check `test/performance/test_performance.py` examples
4. **Validation Testing**: Check `test/validation/README.md` 