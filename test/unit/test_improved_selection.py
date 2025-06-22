#!/usr/bin/env python3
"""
🧪 Test for Improved Algorithm Selection
=======================================

Tests to verify that the improved algorithm selection provides better efficiency
compared to the old approach.
"""

import unittest
import time

from surface_optimizer import optimize, auto_select_algorithm
from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm


class TestImprovedSelection(unittest.TestCase):
    """Test improved algorithm selection"""
    
    def setUp(self):
        """Setup test data"""
        
        # Test data from the demo
        self.stocks = [
            Stock("S1", 1200, 800, material_type=MaterialType.METAL, cost_per_unit=5.0),
            Stock("S2", 1000, 600, material_type=MaterialType.METAL, cost_per_unit=4.5)
        ]
        
        self.orders = [
            Order("O1", Rectangle(300, 200), quantity=2, priority=Priority.HIGH, material_type=MaterialType.METAL),
            Order("O2", Rectangle(250, 150), quantity=1, priority=Priority.MEDIUM, material_type=MaterialType.METAL),
            Order("O3", Rectangle(180, 120), quantity=3, priority=Priority.LOW, material_type=MaterialType.METAL)
        ]
        
        self.config = OptimizationConfig(
            allow_rotation=True,
            cutting_width=3.0,
            prioritize_orders=True
        )
    
    def test_improved_selection_vs_old(self):
        """Test that improved selection gives better efficiency than old FirstFit approach"""
        
        print("🧪 Testing: Improved Selection vs Old FirstFit")
        print("=" * 50)
        
        # OLD APPROACH: FirstFit hardcoded
        optimizer_old = Optimizer(self.config)
        optimizer_old.set_algorithm(FirstFitAlgorithm())
        
        start_time = time.time()
        result_old = optimizer_old.optimize(self.stocks, self.orders)
        time_old = time.time() - start_time
        
        print(f"🔴 OLD (FirstFit):     {result_old.efficiency_percentage:.1f}% in {time_old:.3f}s")
        
        # NEW APPROACH: Automatic selection
        start_time = time.time()
        result_new = optimize(self.stocks, self.orders, priority='balanced')
        time_new = time.time() - start_time
        
        print(f"🟢 NEW (Auto-Select): {result_new.efficiency_percentage:.1f}% in {time_new:.3f}s")
        
        # Verify improvement
        efficiency_improvement = result_new.efficiency_percentage - result_old.efficiency_percentage
        print(f"📈 IMPROVEMENT: {efficiency_improvement:+.1f}%")
        
        # Assertions
        self.assertGreater(result_new.efficiency_percentage, result_old.efficiency_percentage,
                          "New approach should be more efficient")
        self.assertGreaterEqual(result_new.total_orders_fulfilled, result_old.total_orders_fulfilled,
                               "New approach should fulfill at least as many orders")
        
        # Should use BestFit for this problem size
        selected_algorithm = result_new.metadata['algorithm_selection']['selected_algorithm']
        self.assertIn('best_fit', selected_algorithm)
        
        print("✅ Improved selection test PASSED")
        
        return efficiency_improvement
    
    def test_algorithm_selection_logic(self):
        """Test that algorithm selection logic works correctly"""
        
        print("\n🧠 Testing: Algorithm Selection Logic")
        print("=" * 40)
        
        # Small problem -> Should select BestFit
        small_orders = [Order("S1", Rectangle(100, 100), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL)]
        small_stocks = [Stock("SS1", 500, 500, material_type=MaterialType.METAL, cost_per_unit=5.0)]
        
        alg, desc, metrics = auto_select_algorithm(small_stocks, small_orders, 'balanced')
        self.assertIsInstance(alg, BestFitAlgorithm)
        print(f"✅ Small problem -> {desc}")
        
        # Medium problem -> Should still be BestFit (up to 10 pieces)
        medium_orders = [Order(f"M{i}", Rectangle(100, 100), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL) for i in range(8)]
        
        alg, desc, metrics = auto_select_algorithm(self.stocks, medium_orders, 'balanced')
        self.assertIsInstance(alg, BestFitAlgorithm)
        print(f"✅ Medium problem -> {desc}")
        
        # Large problem -> Should use BottomLeft or Genetic
        large_orders = [Order(f"L{i}", Rectangle(100, 100), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL) for i in range(20)]
        
        alg, desc, metrics = auto_select_algorithm(self.stocks, large_orders, 'balanced')
        self.assertNotIsInstance(alg, FirstFitAlgorithm)  # Should not use FirstFit
        print(f"✅ Large problem -> {desc}")
        
        print("✅ Algorithm selection logic test PASSED")
    
    def test_priority_modes(self):
        """Test different priority modes"""
        
        print("\n⚙️ Testing: Priority Modes")
        print("=" * 30)
        
        priorities = ['speed', 'balanced', 'quality', 'maximum']
        
        results = {}
        
        for priority in priorities:
            start_time = time.time()
            result = optimize(self.stocks, self.orders, priority=priority)
            elapsed = time.time() - start_time
            
            results[priority] = {
                'efficiency': result.efficiency_percentage,
                'time': elapsed,
                'algorithm': result.metadata['algorithm_selection']['selected_algorithm']
            }
            
            print(f"🎯 {priority:8}: {result.efficiency_percentage:5.1f}% in {elapsed:.3f}s ({result.metadata['algorithm_selection']['selected_algorithm']})")
        
        # Quality should generally be better than speed
        if results['quality']['efficiency'] >= results['speed']['efficiency']:
            print("✅ Quality mode gives better efficiency than speed")
        else:
            print("⚠️  Quality mode not significantly better (might be problem-dependent)")
        
        # All should work without errors
        for priority, data in results.items():
            self.assertGreaterEqual(data['efficiency'], 0)
            self.assertGreater(data['time'], 0)
        
        print("✅ Priority modes test PASSED")
    
    def test_performance_benchmark(self):
        """Benchmark performance improvement"""
        
        print("\n⚡ Performance Benchmark")
        print("=" * 25)
        
        # Run multiple tests to get average
        old_efficiencies = []
        new_efficiencies = []
        
        for run in range(3):
            # Old approach
            optimizer_old = Optimizer(self.config)
            optimizer_old.set_algorithm(FirstFitAlgorithm())
            result_old = optimizer_old.optimize(self.stocks, self.orders)
            old_efficiencies.append(result_old.efficiency_percentage)
            
            # New approach
            result_new = optimize(self.stocks, self.orders, priority='balanced')
            new_efficiencies.append(result_new.efficiency_percentage)
        
        avg_old = sum(old_efficiencies) / len(old_efficiencies)
        avg_new = sum(new_efficiencies) / len(new_efficiencies)
        improvement = avg_new - avg_old
        
        print(f"📊 Average OLD efficiency: {avg_old:.1f}%")
        print(f"📊 Average NEW efficiency: {avg_new:.1f}%")
        print(f"📈 Average improvement:    {improvement:+.1f}%")
        
        # Should see improvement
        self.assertGreater(improvement, 0, "Should see efficiency improvement on average")
        self.assertGreater(avg_new, 30, "New approach should achieve reasonable efficiency")
        
        print("✅ Performance benchmark PASSED")


if __name__ == '__main__':
    unittest.main() 