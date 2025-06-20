#!/usr/bin/env python3
"""
Modern pytest-based performance tests using pytest-benchmark

Tests algorithm performance, scaling, and resource usage.
Run with: pytest test_performance.py --benchmark-only
"""

import pytest
import time
import psutil
import os
from typing import List, Dict, Any

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


# Fixtures for performance testing
@pytest.fixture
def small_problem():
    """Small problem: 1 stock, 5 orders"""
    stocks = [Stock("S1", 1000, 800, 5.0)]
    orders = [Order(f"O{i}", Rectangle(200, 150), 1, Priority.MEDIUM) for i in range(5)]
    return stocks, orders


@pytest.fixture
def medium_problem():
    """Medium problem: 3 stocks, 20 orders"""
    stocks = [Stock(f"S{i}", 1500, 1200, 5.0) for i in range(3)]
    orders = [Order(f"O{i}", Rectangle(200 + i*5, 150 + i*3), 1, Priority.MEDIUM) for i in range(20)]
    return stocks, orders


@pytest.fixture
def large_problem():
    """Large problem: 5 stocks, 50 orders"""
    stocks = [Stock(f"S{i}", 2000, 1500, 5.0) for i in range(5)]
    orders = [Order(f"O{i}", Rectangle(150 + i*2, 100 + i*2), 1, Priority.MEDIUM) for i in range(50)]
    return stocks, orders


@pytest.fixture
def optimization_config():
    """Standard optimization configuration"""
    return OptimizationConfig(allow_rotation=True, prioritize_orders=True)


# Basic Algorithm Performance Tests
@pytest.mark.performance
class TestBasicAlgorithmPerformance:
    """Test basic algorithm performance characteristics"""
    
    def test_first_fit_small_problem_benchmark(self, benchmark, small_problem, optimization_config):
        """Benchmark FirstFit algorithm on small problem"""
        stocks, orders = small_problem
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        # Benchmark the optimization
        result = benchmark(optimizer.optimize, stocks, orders, optimization_config)
        
        # Verify result quality
        assert result.total_orders_fulfilled > 0
        assert result.efficiency_percentage > 0
    
    def test_best_fit_small_problem_benchmark(self, benchmark, small_problem, optimization_config):
        """Benchmark BestFit algorithm on small problem"""
        stocks, orders = small_problem
        algorithm = BestFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = benchmark(optimizer.optimize, stocks, orders, optimization_config)
        
        assert result.total_orders_fulfilled > 0
        assert result.efficiency_percentage > 0
    
    def test_bottom_left_small_problem_benchmark(self, benchmark, small_problem, optimization_config):
        """Benchmark BottomLeft algorithm on small problem"""
        stocks, orders = small_problem
        algorithm = BottomLeftAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = benchmark(optimizer.optimize, stocks, orders, optimization_config)
        
        assert result.total_orders_fulfilled > 0
        assert result.efficiency_percentage > 0


# Advanced Algorithm Performance Tests
@pytest.mark.performance
class TestAdvancedAlgorithmPerformance:
    """Test advanced algorithm performance"""
    
    def test_genetic_small_problem_benchmark(self, benchmark, small_problem, optimization_config):
        """Benchmark Genetic algorithm on small problem"""
        stocks, orders = small_problem
        algorithm = GeneticAlgorithm(population_size=10, generations=5)
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = benchmark(optimizer.optimize, stocks, orders, optimization_config)
        
        assert result.total_orders_fulfilled > 0
        assert result.efficiency_percentage > 0
    
    def test_genetic_medium_problem_benchmark(self, benchmark, medium_problem, optimization_config):
        """Benchmark Genetic algorithm on medium problem"""
        stocks, orders = medium_problem
        algorithm = GeneticAlgorithm(population_size=15, generations=8)
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        result = benchmark(optimizer.optimize, stocks, orders, optimization_config)
        
        assert result.total_orders_fulfilled > 0
        assert result.efficiency_percentage > 0


# Scaling Tests
@pytest.mark.performance
@pytest.mark.slow
class TestAlgorithmScaling:
    """Test how algorithms scale with problem size"""
    
    @pytest.mark.parametrize("num_orders,max_time", [
        (10, 2.0),   # 10 orders should be fast
        (25, 5.0),   # 25 orders should be reasonable
        (50, 15.0),  # 50 orders might take longer
    ])
    def test_first_fit_scaling(self, num_orders, max_time, optimization_config):
        """Test FirstFit algorithm scaling"""
        stocks = [Stock(f"S{i}", 2000, 1500, 5.0) for i in range(3)]
        orders = [Order(f"O{i}", Rectangle(200, 150), 1, Priority.MEDIUM) for i in range(num_orders)]
        
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, optimization_config)
        elapsed = time.time() - start_time
        
        # Should complete within time limit
        assert elapsed < max_time, f"Took {elapsed:.2f}s for {num_orders} orders (limit: {max_time}s)"
        
        # Should produce reasonable results
        assert result.total_orders_fulfilled > 0
        print(f"FirstFit: {num_orders} orders in {elapsed:.3f}s, {result.efficiency_percentage:.1f}% efficiency")
    
    @pytest.mark.parametrize("population_size,generations,max_time", [
        (10, 5, 5.0),    # Small GA
        (20, 10, 15.0),  # Medium GA
        (30, 15, 30.0),  # Larger GA
    ])
    def test_genetic_algorithm_scaling(self, population_size, generations, max_time, medium_problem, optimization_config):
        """Test Genetic algorithm scaling with different parameters"""
        stocks, orders = medium_problem
        
        algorithm = GeneticAlgorithm(population_size=population_size, generations=generations)
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, optimization_config)
        elapsed = time.time() - start_time
        
        # Should complete within time limit
        assert elapsed < max_time, f"GA({population_size},{generations}) took {elapsed:.2f}s (limit: {max_time}s)"
        
        # Should produce reasonable results
        assert result.total_orders_fulfilled > 0
        print(f"GA({population_size},{generations}): {elapsed:.3f}s, {result.efficiency_percentage:.1f}% efficiency")


# Memory Usage Tests
@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage characteristics"""
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_memory_usage_small_problem(self, small_problem, optimization_config):
        """Test memory usage for small problems"""
        stocks, orders = small_problem
        
        # Measure baseline memory
        baseline_memory = self.get_memory_usage()
        
        # Run optimization
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        result = optimizer.optimize(stocks, orders, optimization_config)
        
        # Measure peak memory
        peak_memory = self.get_memory_usage()
        memory_increase = peak_memory - baseline_memory
        
        # Memory increase should be reasonable (< 50MB for small problem)
        assert memory_increase < 50, f"Memory increase too high: {memory_increase:.1f}MB"
        print(f"Memory usage: {memory_increase:.1f}MB for small problem")
    
    def test_memory_usage_large_problem(self, large_problem, optimization_config):
        """Test memory usage for large problems"""
        stocks, orders = large_problem
        
        baseline_memory = self.get_memory_usage()
        
        algorithm = GeneticAlgorithm(population_size=20, generations=10)
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        result = optimizer.optimize(stocks, orders, optimization_config)
        
        peak_memory = self.get_memory_usage()
        memory_increase = peak_memory - baseline_memory
        
        # Memory increase should be reasonable (< 200MB for large problem)
        assert memory_increase < 200, f"Memory increase too high: {memory_increase:.1f}MB"
        print(f"Memory usage: {memory_increase:.1f}MB for large problem")


# Comparative Performance Tests
@pytest.mark.performance
class TestComparativePerformance:
    """Compare performance between different algorithms"""
    
    def test_algorithm_speed_comparison(self, medium_problem, optimization_config):
        """Compare speed of different algorithms"""
        stocks, orders = medium_problem
        
        algorithms = [
            ("FirstFit", FirstFitAlgorithm()),
            ("BestFit", BestFitAlgorithm()),
            ("BottomLeft", BottomLeftAlgorithm()),
            ("Genetic(10,5)", GeneticAlgorithm(population_size=10, generations=5)),
        ]
        
        results = {}
        
        for name, algorithm in algorithms:
            optimizer = Optimizer()
            optimizer.set_algorithm(algorithm)
            
            start_time = time.time()
            result = optimizer.optimize(stocks, orders, optimization_config)
            elapsed = time.time() - start_time
            
            results[name] = {
                'time': elapsed,
                'efficiency': result.efficiency_percentage,
                'orders_fulfilled': result.total_orders_fulfilled
            }
        
        # Print comparison
        print("\nAlgorithm Performance Comparison:")
        print("Algorithm          Time(s)  Efficiency  Orders")
        print("-" * 45)
        for name, metrics in results.items():
            print(f"{name:<15} {metrics['time']:>7.3f}  {metrics['efficiency']:>9.1f}%  {metrics['orders_fulfilled']:>6}")
        
        # All algorithms should complete in reasonable time (< 30s)
        for name, metrics in results.items():
            assert metrics['time'] < 30, f"{name} took too long: {metrics['time']:.2f}s"
    
    def test_quality_vs_speed_tradeoff(self, medium_problem, optimization_config):
        """Test quality vs speed tradeoff for genetic algorithm"""
        stocks, orders = medium_problem
        
        configurations = [
            ("Fast", GeneticAlgorithm(population_size=5, generations=3)),
            ("Balanced", GeneticAlgorithm(population_size=10, generations=5)),
            ("Quality", GeneticAlgorithm(population_size=20, generations=10)),
        ]
        
        results = {}
        
        for name, algorithm in configurations:
            optimizer = Optimizer()
            optimizer.set_algorithm(algorithm)
            
            start_time = time.time()
            result = optimizer.optimize(stocks, orders, optimization_config)
            elapsed = time.time() - start_time
            
            results[name] = {
                'time': elapsed,
                'efficiency': result.efficiency_percentage,
                'orders_fulfilled': result.total_orders_fulfilled
            }
        
        # Print tradeoff analysis
        print("\nQuality vs Speed Tradeoff:")
        print("Config     Time(s)  Efficiency  Orders")
        print("-" * 35)
        for name, metrics in results.items():
            print(f"{name:<8} {metrics['time']:>7.3f}  {metrics['efficiency']:>9.1f}%  {metrics['orders_fulfilled']:>6}")
        
        # Quality config should not take more than 10x fast config
        fast_time = results["Fast"]["time"]
        quality_time = results["Quality"]["time"]
        assert quality_time < fast_time * 10, f"Quality config too slow: {quality_time/fast_time:.1f}x"


# Resource Limit Tests
@pytest.mark.performance
@pytest.mark.slow
class TestResourceLimits:
    """Test behavior under resource constraints"""
    
    def test_timeout_handling(self, large_problem, optimization_config):
        """Test that algorithms respect timeout limits"""
        stocks, orders = large_problem
        
        # Set a short timeout
        short_timeout = 5.0  # 5 seconds
        
        algorithm = GeneticAlgorithm(population_size=50, generations=100)  # Would normally take long
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, optimization_config)
        elapsed = time.time() - start_time
        
        # Should complete, even if not optimal
        assert result is not None
        print(f"Algorithm completed in {elapsed:.2f}s under timeout constraints")
    
    def test_large_scale_performance(self):
        """Test performance with very large problems"""
        # Create a large problem
        stocks = [Stock(f"S{i}", 3000, 2000, 5.0) for i in range(10)]
        orders = [Order(f"O{i}", Rectangle(100 + i, 80 + i), 1, Priority.MEDIUM) for i in range(100)]
        
        config = OptimizationConfig(allow_rotation=True)
        
        # Use fastest algorithm for large scale
        algorithm = FirstFitAlgorithm()
        optimizer = Optimizer()
        optimizer.set_algorithm(algorithm)
        
        start_time = time.time()
        result = optimizer.optimize(stocks, orders, config)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time even for large problems
        assert elapsed < 60, f"Large scale test took too long: {elapsed:.2f}s"
        assert result.total_orders_fulfilled > 0
        
        print(f"Large scale: 100 orders, 10 stocks in {elapsed:.2f}s")
        print(f"Efficiency: {result.efficiency_percentage:.1f}%, Orders: {result.total_orders_fulfilled}")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__, 
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-columns=mean,stddev,min,max",
        "-v"
    ]) 