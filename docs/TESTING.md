# 🧪 Surface Cutting Optimizer - Test Suite

Modern pytest-based test suite for comprehensive testing of the Surface Cutting Optimizer library.

## 📁 Test Structure

### **Core Test Files**

| File | Description | Type | Markers |
|------|-------------|------|---------|
| `test_algorithms.py` | Algorithm functionality and interface tests | Unit/Integration | `@pytest.mark.algorithm` |
| `test_geometry.py` | Geometry classes and spatial operations | Unit | `@pytest.mark.geometry` |
| `test_overlap_detection.py` | Critical overlap prevention tests | Integration | `@pytest.mark.real_world` |
| `test_performance.py` | Performance, scaling, and benchmarks | Performance | `@pytest.mark.performance` |
| `test_supervised_validation.py` | Real-world industry validation | Validation | `@pytest.mark.real_world` |

### **Test Data**
- `test_cases.py` - Reusable test data and validation functions
- `benchmark_suite.py` - Legacy benchmark suite (consider modernizing)

## 🚀 Running Tests

### **Basic Test Execution**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=surface_optimizer --cov-report=html

# Run specific test file
pytest test/test_algorithms.py

# Run with verbose output
pytest -v
```

### **Test Categories**

```bash
# Unit tests only
pytest -m "unit"

# Integration tests
pytest -m "integration" 

# Performance tests
pytest -m "performance"

# Real-world validation
pytest -m "real_world"

# Fast tests (exclude slow ones)
pytest -m "not slow"
```

### **Performance Testing**
```bash
# Run benchmarks only
pytest --benchmark-only

# Performance tests with detailed timing
pytest test/test_performance.py -v -s

# Memory usage analysis
pytest test/test_performance.py::TestMemoryUsage -v -s
```

### **Parallel Execution**
```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run specific number of workers
pytest -n 4
```

## 📊 Test Configuration

The test suite uses `pytest.ini` configuration with:

- **Coverage**: Minimum 80% coverage requirement
- **Markers**: Organized test categories
- **Timeouts**: 300 seconds max per test
- **Parallel**: Support for parallel execution
- **Reports**: HTML, XML, and terminal coverage reports

## 🎯 Test Categories Explained

### **Unit Tests** (`@pytest.mark.unit`)
- Test individual components in isolation
- Fast execution (< 1 second each)
- Mock external dependencies
- High coverage of edge cases

### **Integration Tests** (`@pytest.mark.integration`)
- Test component interactions
- Real algorithm execution
- End-to-end workflows
- Moderate execution time

### **Performance Tests** (`@pytest.mark.performance`)
- Benchmark algorithm speed
- Memory usage monitoring
- Scaling characteristics
- Resource limit testing

### **Real-World Tests** (`@pytest.mark.real_world`)
- Industry-validated test cases
- Known optimal solutions
- Actual manufacturing data
- Quality validation

### **Slow Tests** (`@pytest.mark.slow`)
- Tests taking > 5 seconds
- Large-scale problems
- Comprehensive scenarios
- Skip with `-m "not slow"`

## 🔧 Test Fixtures

### **Common Fixtures**
- `basic_config` - Standard optimization configuration
- `simple_stock` - Single stock for basic tests
- `simple_orders` - Basic order set
- `algorithm_instance` - Parametrized algorithm instances

### **Problem Size Fixtures**
- `small_problem` - 1 stock, 5 orders (fast testing)
- `medium_problem` - 3 stocks, 20 orders (realistic)
- `large_problem` - 5 stocks, 50 orders (stress testing)

## 📈 Coverage Requirements

- **Minimum Coverage**: 80%
- **Core Modules**: 90%+ (algorithms, geometry, models)
- **Critical Paths**: 100% (overlap detection, validation)
- **Performance**: Functional coverage (not coverage %)

## 🚨 Critical Tests

### **Must-Pass Tests**
1. **Overlap Detection** - Ensures no shape overlaps in solutions
2. **Algorithm Interface** - All algorithms implement required interface
3. **Geometry Validation** - Shape calculations are correct
4. **Memory Limits** - No memory leaks or excessive usage

### **Quality Indicators**
1. **Efficiency Benchmarks** - Algorithms meet efficiency targets
2. **Real-World Validation** - Match industry solutions
3. **Performance Scaling** - Reasonable scaling with problem size
4. **Resource Usage** - Stay within memory/time limits

## 🛠️ Development Workflow

### **Running Tests During Development**
```bash
# Quick test run (exclude slow tests)
pytest -m "not slow" --tb=short

# Test specific functionality
pytest test/test_algorithms.py::TestBasicFunctionality

# Watch mode (with pytest-watch)
pytest-watch

# Debug mode
pytest --pdb --pdb-trace
```

### **Before Committing**
```bash
# Full test suite with coverage
pytest --cov=surface_optimizer --cov-fail-under=80

# Check code quality
black surface_optimizer/ test/
flake8 surface_optimizer/ test/
mypy surface_optimizer/
```

### **Release Testing**
```bash
# Complete test suite including slow tests
pytest --cov=surface_optimizer --cov-report=html

# Performance regression check
pytest test/test_performance.py --benchmark-compare

# Real-world validation
pytest -m "real_world" -v -s
```

## 🎯 Best Practices

### **Writing Tests**
1. Use descriptive test names: `test_algorithm_handles_empty_input`
2. Follow AAA pattern: Arrange, Act, Assert
3. Use pytest fixtures for setup
4. Parametrize similar test cases
5. Add appropriate markers

### **Test Organization**
1. Group related tests in classes
2. Use fixtures for common setup
3. Keep tests independent
4. Test both success and failure cases
5. Include performance considerations

### **Assertions**
```python
# Good assertions
assert result.efficiency_percentage >= 80.0
assert len(result.placed_shapes) == expected_count

# With helpful messages
assert result.total_orders_fulfilled > 0, f"No orders fulfilled from {len(orders)} orders"
```

## 📚 Dependencies

### **Core Testing**
- `pytest` - Modern testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Advanced mocking

### **Performance Testing**
- `pytest-benchmark` - Performance benchmarking
- `pytest-xdist` - Parallel execution
- `memory-profiler` - Memory usage tracking
- `psutil` - System resource monitoring

### **Code Quality**
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## 🐛 Debugging Tests

### **Common Issues**
1. **Import errors** - Check PYTHONPATH and module structure
2. **Fixture not found** - Ensure fixture is in scope
3. **Slow tests** - Use `-m "not slow"` for development
4. **Memory issues** - Run memory tests individually

### **Debug Commands**
```bash
# Drop into debugger on failure
pytest --pdb

# Verbose output with prints
pytest -v -s

# Only show failed tests
pytest --tb=short --failed-first

# Run last failed tests only
pytest --lf
```

## 📞 Support

For test-related issues:
1. Check this README first
2. Review pytest documentation
3. Check existing test patterns
4. Create clear, minimal test cases 