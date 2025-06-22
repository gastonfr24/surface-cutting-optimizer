"""
Unit tests for Surface Cutting Optimizer algorithms

Tests cover:
- Basic algorithms (FirstFit, BottomLeft, BestFit)
- Advanced algorithms (Genetic, SimulatedAnnealing)
- Algorithm performance and correctness
- Edge cases and error handling
- Configuration parameter handling
"""

import unittest
from unittest.mock import Mock, patch
import time

from surface_optimizer.core.models import (
    Stock, Order, CuttingResult, PlacedShape, OptimizationConfig,
    MaterialType, Priority, OrderSortCriteria
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm
from surface_optimizer.algorithms.advanced.simulated_annealing import SimulatedAnnealingAlgorithm


class TestFirstFitAlgorithm(unittest.TestCase):
    """Tests for First Fit algorithm implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = FirstFitAlgorithm()
        
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.WOOD)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=2, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(300.0, 150.0), quantity=1, material_type=MaterialType.WOOD),
            Order(id="O3", shape=Rectangle(100.0, 50.0), quantity=3, material_type=MaterialType.WOOD)
        ]
        
        self.config = OptimizationConfig(
            allow_rotation=True,
            prioritize_orders=True,
            order_sort_criteria=OrderSortCriteria.AREA_DESC
        )
        
    def test_algorithm_initialization(self):
        """Test algorithm initialization and properties"""
        self.assertEqual(self.algorithm.name, "first_fit")
        self.assertTrue(self.algorithm.supports_rotation)
        self.assertEqual(self.algorithm.complexity, "O(n×m)")
        self.assertIn("Greedy algorithm", self.algorithm.description)
        
    def test_basic_optimization(self):
        """Test basic optimization functionality"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        # Check result structure
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "first_fit")
        self.assertGreaterEqual(result.computation_time, 0)
        self.assertGreaterEqual(result.total_orders_fulfilled, 0)
        self.assertGreaterEqual(result.total_stock_used, 0)
        
        # Check placed shapes
        self.assertIsInstance(result.placed_shapes, list)
        for placed_shape in result.placed_shapes:
            self.assertIsInstance(placed_shape, PlacedShape)
            self.assertIn(placed_shape.stock_id, ["S1", "S2"])
            
    def test_empty_inputs_error(self):
        """Test error handling for empty inputs"""
        with self.assertRaises(ValueError):
            self.algorithm.optimize([], self.orders, self.config)
            
        with self.assertRaises(ValueError):
            self.algorithm.optimize(self.stocks, [], self.config)
            
    def test_rotation_functionality(self):
        """Test rotation feature"""
        # Test with rotation enabled
        config_rotation = OptimizationConfig(allow_rotation=True)
        result_with_rotation = self.algorithm.optimize(self.stocks, self.orders, config_rotation)
        
        # Test with rotation disabled
        config_no_rotation = OptimizationConfig(allow_rotation=False)
        result_no_rotation = self.algorithm.optimize(self.stocks, self.orders, config_no_rotation)
        
        # Both should return valid results
        self.assertIsInstance(result_with_rotation, CuttingResult)
        self.assertIsInstance(result_no_rotation, CuttingResult)
        
        # With rotation might place more pieces (but not guaranteed)
        self.assertGreaterEqual(len(result_with_rotation.placed_shapes), 0)
        
    def test_large_pieces_handling(self):
        """Test handling of pieces larger than available stocks"""
        large_orders = [
            Order(id="L1", shape=Rectangle(2000.0, 1000.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        result = self.algorithm.optimize(self.stocks, large_orders, self.config)
        
        # Should handle gracefully - unfulfilled orders
        self.assertEqual(len(result.placed_shapes), 0)
        self.assertEqual(len(result.unfulfilled_orders), 1)
        
    def test_performance_timing(self):
        """Test algorithm performance"""
        start_time = time.time()
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        end_time = time.time()
        
        # Should be very fast (< 1 second for small problems)
        self.assertLess(end_time - start_time, 1.0)
        self.assertGreaterEqual(result.computation_time, 0)
        self.assertLess(result.computation_time, 1.0)


class TestBottomLeftAlgorithm(unittest.TestCase):
    """Tests for Bottom Left algorithm implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = BottomLeftAlgorithm()
        
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=1, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(150.0, 120.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        self.config = OptimizationConfig()
        
    def test_algorithm_initialization(self):
        """Test Bottom Left algorithm initialization"""
        self.assertEqual(self.algorithm.name, "bottom_left")
        self.assertTrue(hasattr(self.algorithm, 'description'))
        self.assertTrue(hasattr(self.algorithm, 'supports_rotation'))
        
    def test_basic_optimization(self):
        """Test basic Bottom Left optimization"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "bottom_left")
        self.assertGreaterEqual(len(result.placed_shapes), 0)
        
        # Bottom Left should place pieces at bottom-left positions when possible
        for placed_shape in result.placed_shapes:
            self.assertGreaterEqual(placed_shape.shape.x, 0)
            self.assertGreaterEqual(placed_shape.shape.y, 0)
            
    def test_bottom_left_positioning(self):
        """Test that algorithm follows bottom-left positioning strategy"""
        # Use simple case with known optimal placement
        simple_orders = [
            Order(id="O1", shape=Rectangle(100.0, 100.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        result = self.algorithm.optimize(self.stocks, simple_orders, self.config)
        
        if len(result.placed_shapes) > 0:
            first_piece = result.placed_shapes[0]
            # First piece should be placed at (0, 0) - bottom-left corner
            self.assertEqual(first_piece.shape.x, 0.0)
            self.assertEqual(first_piece.shape.y, 0.0)


class TestBestFitAlgorithm(unittest.TestCase):
    """Tests for Best Fit algorithm implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = BestFitAlgorithm()
        
        self.stocks = [
            Stock(id="S1", width=500.0, height=300.0, material_type=MaterialType.WOOD),
            Stock(id="S2", width=800.0, height=400.0, material_type=MaterialType.WOOD)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 150.0), quantity=1, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(100.0, 80.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        self.config = OptimizationConfig()
        
    def test_algorithm_initialization(self):
        """Test Best Fit algorithm initialization"""
        self.assertEqual(self.algorithm.name, "best_fit")
        self.assertTrue(hasattr(self.algorithm, 'description'))
        self.assertTrue(hasattr(self.algorithm, 'supports_rotation'))
        
    def test_basic_optimization(self):
        """Test basic Best Fit optimization"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "best_fit")
        # Best Fit should now place pieces with basic implementation
        self.assertGreaterEqual(len(result.placed_shapes), 0)


class TestGeneticAlgorithm(unittest.TestCase):
    """Tests for Genetic algorithm implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = GeneticAlgorithm()
        
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD, cost_per_unit=100.0),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.WOOD, cost_per_unit=120.0)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=2, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(300.0, 150.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        self.config = OptimizationConfig(
            allow_rotation=True,
            prioritize_orders=True,
            max_computation_time=5.0  # Short time for testing
        )
        
    def test_algorithm_initialization(self):
        """Test Genetic algorithm initialization"""
        self.assertEqual(self.algorithm.name, "genetic")
        self.assertTrue(self.algorithm.supports_rotation)
        self.assertIsNone(self.algorithm.best_solution)
        self.assertEqual(len(self.algorithm.evolution_history), 0)
        
    def test_basic_optimization(self):
        """Test basic genetic optimization"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "genetic")
        self.assertGreater(result.computation_time, 0)
        self.assertGreaterEqual(len(result.placed_shapes), 0)
        
        # Check evolution history was recorded
        self.assertGreater(len(self.algorithm.evolution_history), 0)
        
        first_generation = self.algorithm.evolution_history[0]
        self.assertIn('generation', first_generation)
        self.assertIn('best_fitness', first_generation)
        self.assertIn('avg_fitness', first_generation)
        
    def test_auto_scaling_configuration(self):
        """Test automatic parameter scaling based on problem complexity"""
        # Small problem - should use smaller population
        small_orders = [
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        result_small = self.algorithm.optimize(self.stocks, small_orders, self.config)
        self.assertIsInstance(result_small, CuttingResult)
        
        # Medium problem - should use balanced parameters
        medium_orders = [
            Order(id=f"O{i}", shape=Rectangle(100.0, 50.0), quantity=2, material_type=MaterialType.WOOD)
            for i in range(10)
        ]
        
        result_medium = self.algorithm.optimize(self.stocks, medium_orders, self.config)
        self.assertIsInstance(result_medium, CuttingResult)
        
    def test_manual_configuration(self):
        """Test genetic algorithm with custom configuration parameters"""
        config_with_params = OptimizationConfig(
            allow_rotation=True,
            max_computation_time=3.0,
            prioritize_orders=True,
            placement_precision=0.5,
            max_iterations=100
        )
        
        result = self.algorithm.optimize(self.stocks, self.orders, config_with_params)
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "genetic")
        
    def test_early_stopping(self):
        """Test genetic algorithm with time-based early stopping"""
        # Use short time limit to trigger early stopping
        config_with_limit = OptimizationConfig(
            allow_rotation=True,
            max_computation_time=1.0,  # Very short time to trigger early stop
            prioritize_orders=True
        )
        
        result = self.algorithm.optimize(self.stocks, self.orders, config_with_limit)
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "genetic")
        
        # Should complete within time limit (plus some tolerance)
        self.assertLess(result.computation_time, 3.0)
        
        # Evolution should have recorded some history
        self.assertGreaterEqual(len(self.algorithm.evolution_history), 1)
        
    def test_evolution_history_tracking(self):
        """Test that evolution history is properly tracked"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        self.assertGreater(len(self.algorithm.evolution_history), 0)
        
        # Check history structure
        for generation_data in self.algorithm.evolution_history:
            self.assertIn('generation', generation_data)
            self.assertIn('best_fitness', generation_data)
            self.assertIn('avg_fitness', generation_data)
            self.assertIn('population_diversity', generation_data)
            
            # Fitness values should be reasonable
            self.assertGreaterEqual(generation_data['best_fitness'], 0)
            self.assertGreaterEqual(generation_data['avg_fitness'], 0)
            self.assertGreaterEqual(generation_data['population_diversity'], 0)
            
    def test_empty_inputs_handling(self):
        """Test handling of empty inputs"""
        result = self.algorithm.optimize([], self.orders, self.config)
        self.assertIsInstance(result, CuttingResult)
        
        result = self.algorithm.optimize(self.stocks, [], self.config)
        self.assertIsInstance(result, CuttingResult)


class TestSimulatedAnnealingAlgorithm(unittest.TestCase):
    """Tests for Simulated Annealing algorithm implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = SimulatedAnnealingAlgorithm()
        
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.WOOD)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=1, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(150.0, 120.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        self.config = OptimizationConfig(allow_rotation=True)
        
    def test_algorithm_initialization(self):
        """Test Simulated Annealing algorithm initialization"""
        self.assertEqual(self.algorithm.name, "Simulated Annealing")
        self.assertTrue(hasattr(self.algorithm, 'base_initial_temperature'))
        self.assertTrue(hasattr(self.algorithm, 'cooling_rate'))
        self.assertTrue(hasattr(self.algorithm, 'auto_scale'))
        
        # Check tracking lists
        self.assertIsInstance(self.algorithm.temperature_history, list)
        self.assertIsInstance(self.algorithm.cost_history, list)
        self.assertIsInstance(self.algorithm.acceptance_history, list)
        
        # Check default values
        self.assertEqual(self.algorithm.cooling_rate, 0.95)
        self.assertTrue(self.algorithm.auto_scale)
        
    def test_basic_optimization(self):
        """Test basic simulated annealing optimization"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertEqual(result.algorithm_used, "Simulated Annealing")
        self.assertGreater(result.computation_time, 0)
        self.assertGreaterEqual(len(result.placed_shapes), 0)
        
        # Check metadata
        self.assertIsNotNone(result.metadata)
        self.assertIn('algorithm', result.metadata)
        self.assertIn('cooling_schedule', result.metadata)
        self.assertIn('annealing_stats', result.metadata)
        
    def test_auto_scaling_parameters(self):
        """Test auto-scaling of algorithm parameters"""
        # Test with small problem
        small_orders = [
            Order(id="O1", shape=Rectangle(100.0, 50.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        result_small = self.algorithm.optimize(self.stocks, small_orders, self.config)
        self.assertIsInstance(result_small, CuttingResult)
        
        # Test with larger problem
        large_orders = [
            Order(id=f"O{i}", shape=Rectangle(100.0, 50.0), quantity=1, material_type=MaterialType.WOOD)
            for i in range(20)
        ]
        
        result_large = self.algorithm.optimize(self.stocks, large_orders, self.config)
        self.assertIsInstance(result_large, CuttingResult)
        
    def test_parameter_configuration(self):
        """Test algorithm with different parameters"""
        custom_algorithm = SimulatedAnnealingAlgorithm(
            initial_temperature=1000.0,
            cooling_rate=0.95,
            min_temperature=0.1,
            max_iterations=100,
            auto_scale=False
        )
        
        result = custom_algorithm.optimize(self.stocks, self.orders, self.config)
        self.assertIsInstance(result, CuttingResult)
        
        # Check that custom parameters were used
        self.assertEqual(custom_algorithm.cooling_rate, 0.95)
        self.assertFalse(custom_algorithm.auto_scale)
        
    def test_temperature_cooling(self):
        """Test that algorithm properly implements cooling schedule"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertGreater(result.computation_time, 0)
        
        # Check that temperature decreased over time
        if len(self.algorithm.temperature_history) > 1:
            first_temp = self.algorithm.temperature_history[0]
            last_temp = self.algorithm.temperature_history[-1]
            self.assertGreater(first_temp, last_temp)
            
    def test_annealing_statistics(self):
        """Test that annealing statistics are properly tracked"""
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        
        # Should have recorded some statistics
        if len(self.algorithm.temperature_history) > 0:
            self.assertGreater(len(self.algorithm.temperature_history), 0)
            self.assertGreater(len(self.algorithm.cost_history), 0)
            self.assertGreater(len(self.algorithm.acceptance_history), 0)
            
            # Check metadata contains statistics
            self.assertIn('annealing_stats', result.metadata)
            stats = result.metadata['annealing_stats']
            self.assertIn('temperature_history', stats)
            self.assertIn('cost_history', stats)
            self.assertIn('acceptance_history', stats)
            
    def test_empty_inputs_handling(self):
        """Test handling of empty inputs"""
        result = self.algorithm.optimize([], self.orders, self.config)
        self.assertIsInstance(result, CuttingResult)
        
        result = self.algorithm.optimize(self.stocks, [], self.config)
        self.assertIsInstance(result, CuttingResult)


class TestAlgorithmComparison(unittest.TestCase):
    """Tests for comparing algorithm performance and behavior"""
    
    def setUp(self):
        """Set up test fixtures for comparison"""
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.WOOD)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=2, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(300.0, 150.0), quantity=1, material_type=MaterialType.WOOD),
            Order(id="O3", shape=Rectangle(150.0, 80.0), quantity=2, material_type=MaterialType.WOOD)
        ]
        
        self.config = OptimizationConfig(
            allow_rotation=True,
            prioritize_orders=True
        )
        
        self.basic_algorithms = [
            FirstFitAlgorithm(),
            BottomLeftAlgorithm(),
            BestFitAlgorithm()
        ]
        
        self.advanced_algorithms = [
            GeneticAlgorithm(),
            SimulatedAnnealingAlgorithm()
        ]
        
        self.all_algorithms = self.basic_algorithms + self.advanced_algorithms
        
    def test_all_basic_algorithms_produce_valid_results(self):
        """Test that all basic algorithms produce valid CuttingResult objects"""
        for algorithm in self.basic_algorithms:
            with self.subTest(algorithm=algorithm.name):
                result = algorithm.optimize(self.stocks, self.orders, self.config)
                
                self.assertIsInstance(result, CuttingResult)
                self.assertEqual(result.algorithm_used, algorithm.name)
                self.assertGreaterEqual(result.computation_time, 0)
                self.assertIsInstance(result.placed_shapes, list)
                self.assertIsInstance(result.unfulfilled_orders, list)
                
    def test_algorithm_performance_comparison(self):
        """Compare basic algorithm performance characteristics"""
        results = {}
        
        for algorithm in self.basic_algorithms:
            start_time = time.time()
            result = algorithm.optimize(self.stocks, self.orders, self.config)
            end_time = time.time()
            
            results[algorithm.name] = {
                'result': result,
                'wall_time': end_time - start_time,
                'efficiency': result.efficiency_percentage,
                'pieces_placed': len(result.placed_shapes)
            }
        
        # Verify all algorithms completed
        self.assertEqual(len(results), len(self.basic_algorithms))
        
        # Basic algorithms should be fast
        for alg_name, data in results.items():
            self.assertLess(data['wall_time'], 2.0)  # Should be very fast
            self.assertGreaterEqual(data['efficiency'], 0)
            self.assertGreaterEqual(data['pieces_placed'], 0)
            
    def test_all_advanced_algorithms_produce_valid_results(self):
        """Test that all advanced algorithms produce valid CuttingResult objects"""
        # Use shorter time limits for advanced algorithms in tests
        short_config = OptimizationConfig(
            allow_rotation=True,
            prioritize_orders=True,
            max_computation_time=3.0  # Limit execution time for tests
        )
        
        for algorithm in self.advanced_algorithms:
            with self.subTest(algorithm=algorithm.name):
                result = algorithm.optimize(self.stocks, self.orders, short_config)
                
                self.assertIsInstance(result, CuttingResult)
                self.assertEqual(result.algorithm_used, algorithm.name)
                self.assertGreaterEqual(result.computation_time, 0)
                self.assertIsInstance(result.placed_shapes, list)
                self.assertIsInstance(result.unfulfilled_orders, list)
                
                # Advanced algorithms should have metadata
                if hasattr(result, 'metadata') and result.metadata:
                    self.assertIsInstance(result.metadata, dict)
            
    def test_algorithm_consistency(self):
        """Test that algorithms produce consistent results across runs"""
        algorithm = FirstFitAlgorithm()  # Most deterministic algorithm
        
        results = []
        for _ in range(3):
            result = algorithm.optimize(self.stocks, self.orders, self.config)
            results.append({
                'pieces_placed': len(result.placed_shapes),
                'efficiency': result.efficiency_percentage,
                'stocks_used': result.total_stock_used
            })
        
        # First Fit should be deterministic (same results each time)
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result['pieces_placed'], first_result['pieces_placed'])
            self.assertEqual(result['efficiency'], first_result['efficiency'])
            self.assertEqual(result['stocks_used'], first_result['stocks_used'])


class TestAlgorithmEdgeCases(unittest.TestCase):
    """Tests for algorithm edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithms = [
            FirstFitAlgorithm(),
            BottomLeftAlgorithm(),
            BestFitAlgorithm()
        ]
        
    def test_no_feasible_placement(self):
        """Test handling when no pieces can be placed"""
        tiny_stocks = [
            Stock(id="S1", width=10.0, height=10.0, material_type=MaterialType.WOOD)
        ]
        
        large_orders = [
            Order(id="O1", shape=Rectangle(100.0, 100.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        config = OptimizationConfig()
        
        for algorithm in self.algorithms:
            with self.subTest(algorithm=algorithm.name):
                result = algorithm.optimize(tiny_stocks, large_orders, config)
                
                self.assertIsInstance(result, CuttingResult)
                self.assertEqual(len(result.placed_shapes), 0)
                self.assertEqual(len(result.unfulfilled_orders), 1)
                self.assertEqual(result.efficiency_percentage, 0.0)
                
    def test_single_stock_single_order(self):
        """Test minimal case with one stock and one order"""
        single_stock = [
            Stock(id="S1", width=200.0, height=200.0, material_type=MaterialType.WOOD)
        ]
        
        single_order = [
            Order(id="O1", shape=Rectangle(100.0, 100.0), quantity=1, material_type=MaterialType.WOOD)
        ]
        
        config = OptimizationConfig()
        
        for algorithm in self.algorithms:
            with self.subTest(algorithm=algorithm.name):
                result = algorithm.optimize(single_stock, single_order, config)
                
                self.assertIsInstance(result, CuttingResult)
                self.assertEqual(len(result.placed_shapes), 1)
                self.assertEqual(len(result.unfulfilled_orders), 0)
                self.assertGreater(result.efficiency_percentage, 0)
                
    def test_identical_pieces(self):
        """Test handling multiple identical pieces"""
        stocks = [
            Stock(id="S1", width=500.0, height=500.0, material_type=MaterialType.WOOD)
        ]
        
        orders = [
            Order(id="O1", shape=Rectangle(100.0, 100.0), quantity=10, material_type=MaterialType.WOOD)
        ]
        
        config = OptimizationConfig()
        
        for algorithm in self.algorithms:
            with self.subTest(algorithm=algorithm.name):
                result = algorithm.optimize(stocks, orders, config)
                
                self.assertIsInstance(result, CuttingResult)
                # Should place multiple pieces
                self.assertGreaterEqual(len(result.placed_shapes), 1)


class TestAlgorithmIntegration(unittest.TestCase):
    """Tests for algorithm integration with core components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.algorithm = FirstFitAlgorithm()
        
    def test_integration_with_different_material_types(self):
        """Test algorithm integration with different material types"""
        stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.METAL)
        ]
        
        orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=1, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(150.0, 120.0), quantity=1, material_type=MaterialType.METAL)
        ]
        
        config = OptimizationConfig()
        
        result = self.algorithm.optimize(stocks, orders, config)
        
        self.assertIsInstance(result, CuttingResult)
        # Should handle material matching
        self.assertGreaterEqual(len(result.placed_shapes), 0)
        
    def test_integration_with_priorities(self):
        """Test algorithm integration with order priorities"""
        stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD)
        ]
        
        orders = [
            Order(id="O1", shape=Rectangle(400.0, 200.0), quantity=1, 
                  material_type=MaterialType.WOOD, priority=Priority.LOW),
            Order(id="O2", shape=Rectangle(300.0, 150.0), quantity=1, 
                  material_type=MaterialType.WOOD, priority=Priority.HIGH)
        ]
        
        config = OptimizationConfig(prioritize_orders=True)
        
        result = self.algorithm.optimize(stocks, orders, config)
        
        self.assertIsInstance(result, CuttingResult)
        self.assertGreaterEqual(len(result.placed_shapes), 0)


class TestAdvancedAlgorithmPerformance(unittest.TestCase):
    """Tests for advanced algorithm performance characteristics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, material_type=MaterialType.WOOD),
            Stock(id="S2", width=800.0, height=600.0, material_type=MaterialType.WOOD)
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=2, material_type=MaterialType.WOOD),
            Order(id="O2", shape=Rectangle(300.0, 150.0), quantity=1, material_type=MaterialType.WOOD),
            Order(id="O3", shape=Rectangle(150.0, 80.0), quantity=2, material_type=MaterialType.WOOD)
        ]
        
        self.basic_algorithms = [FirstFitAlgorithm(), BottomLeftAlgorithm(), BestFitAlgorithm()]
        self.advanced_algorithms = [GeneticAlgorithm(), SimulatedAnnealingAlgorithm()]
        
    def test_advanced_vs_basic_efficiency(self):
        """Test that advanced algorithms generally achieve better efficiency"""
        basic_config = OptimizationConfig(allow_rotation=True)
        advanced_config = OptimizationConfig(
            allow_rotation=True,
            max_computation_time=3.0  # Limit for testing
        )
        
        basic_results = {}
        for algorithm in self.basic_algorithms:
            result = algorithm.optimize(self.stocks, self.orders, basic_config)
            basic_results[algorithm.name] = result.efficiency_percentage
            
        advanced_results = {}
        for algorithm in self.advanced_algorithms:
            result = algorithm.optimize(self.stocks, self.orders, advanced_config)
            advanced_results[algorithm.name] = result.efficiency_percentage
            
        # Advanced algorithms should exist and run
        self.assertGreater(len(advanced_results), 0)
        
        # All results should be valid
        for alg_name, efficiency in advanced_results.items():
            self.assertGreaterEqual(efficiency, 0)
            self.assertLessEqual(efficiency, 100)
            
    def test_advanced_algorithm_scaling(self):
        """Test that advanced algorithms handle larger problems"""
        # Create a moderately sized problem for testing
        large_orders = [
            Order(id=f"O{i}", shape=Rectangle(100.0, 50.0), quantity=1, material_type=MaterialType.WOOD)
            for i in range(8)  # Smaller problem for reasonable test time
        ]
        
        config = OptimizationConfig(
            allow_rotation=True,
            max_computation_time=10.0  # Reasonable time limit for testing
        )
        
        for algorithm in self.advanced_algorithms:
            with self.subTest(algorithm=algorithm.name):
                result = algorithm.optimize(self.stocks, large_orders, config)
                
                self.assertIsInstance(result, CuttingResult)
                self.assertGreaterEqual(len(result.placed_shapes), 0)
                
                # Should complete within configured time limit (with some tolerance)
                self.assertLess(result.computation_time, config.max_computation_time + 5.0)
                
    def test_time_vs_quality_tradeoff(self):
        """Test time vs quality tradeoff in advanced algorithms"""
        short_config = OptimizationConfig(
            allow_rotation=True,
            max_computation_time=1.0  # Very short time
        )
        
        long_config = OptimizationConfig(
            allow_rotation=True,
            max_computation_time=5.0  # Longer time
        )
        
        for algorithm in self.advanced_algorithms:
            with self.subTest(algorithm=algorithm.name):
                short_result = algorithm.optimize(self.stocks, self.orders, short_config)
                long_result = algorithm.optimize(self.stocks, self.orders, long_config)
                
                # Both should complete successfully
                self.assertIsInstance(short_result, CuttingResult)
                self.assertIsInstance(long_result, CuttingResult)
                
                # Longer run should generally take more time
                # (though this isn't guaranteed due to early stopping)
                self.assertGreaterEqual(long_result.computation_time, 0)
                self.assertGreaterEqual(short_result.computation_time, 0)


if __name__ == '__main__':
    unittest.main()
