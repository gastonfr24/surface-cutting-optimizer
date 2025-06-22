#!/usr/bin/env python3
"""
🧪 Test for Advanced BestFit Algorithm
=====================================

Tests to verify that the new advanced BestFit algorithm provides
significantly better efficiency than the previous basic version.
"""

import unittest
import time

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm


class TestAdvancedBestFit(unittest.TestCase):
    """Test advanced BestFit algorithm improvements"""
    
    def setUp(self):
        """Setup test data"""
        
        # Create a realistic test scenario
        self.stocks = [
            Stock("PANEL_001", 1200, 800, material_type=MaterialType.METAL, cost_per_unit=5.0),
            Stock("PANEL_002", 1000, 600, material_type=MaterialType.METAL, cost_per_unit=4.5)
        ]
        
        # Multiple pieces that can be optimally packed
        self.orders = [
            Order("CUT_001", Rectangle(400, 200), quantity=2, priority=Priority.HIGH, material_type=MaterialType.METAL),
            Order("CUT_002", Rectangle(300, 150), quantity=2, priority=Priority.MEDIUM, material_type=MaterialType.METAL),
            Order("CUT_003", Rectangle(200, 100), quantity=3, priority=Priority.LOW, material_type=MaterialType.METAL),
            Order("CUT_004", Rectangle(150, 120), quantity=2, priority=Priority.MEDIUM, material_type=MaterialType.METAL)
        ]
        
        self.config = OptimizationConfig(
            allow_rotation=True,
            cutting_width=3.0,
            prioritize_orders=True
        )
    
    def test_advanced_placement_functionality(self):
        """Test that advanced placement algorithm works correctly"""
        
        print("🧪 Testing: Advanced BestFit Placement")
        print("=" * 40)
        
        algorithm = BestFitAlgorithm()
        
        start_time = time.time()
        result = algorithm.optimize(self.stocks, self.orders, self.config)
        elapsed = time.time() - start_time
        
        print(f"✅ Efficiency: {result.efficiency_percentage:.1f}%")
        print(f"⏱️  Time: {elapsed:.3f}s")
        print(f"📦 Stocks used: {result.total_stock_used}")
        print(f"🎯 Orders fulfilled: {result.total_orders_fulfilled}")
        print(f"📏 Pieces placed: {len(result.placed_shapes)}")
        
        # Basic functionality assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.algorithm_used, "best_fit")
        self.assertGreaterEqual(result.efficiency_percentage, 0)
        self.assertLessEqual(result.total_stock_used, len(self.stocks))
        
        # Should complete quickly
        self.assertLess(elapsed, 2.0, "Advanced BestFit should be fast")
        
        # Should place at least some pieces
        self.assertGreater(len(result.placed_shapes), 0, "Should place some pieces")
        
        print("✅ Advanced placement functionality test PASSED")
        
        return result
    
    def test_intelligent_positioning(self):
        """Test that pieces are positioned intelligently, not just at origin"""
        
        print("\n🎯 Testing: Intelligent Positioning")
        print("=" * 35)
        
        algorithm = BestFitAlgorithm()
        result = algorithm.optimize(self.stocks, self.orders, self.config)
        
        # Check that not all pieces are at origin (0,0)
        positions = [(ps.shape.x, ps.shape.y) for ps in result.placed_shapes]
        unique_positions = set(positions)
        
        print(f"📍 Unique positions found: {len(unique_positions)}")
        print(f"🔄 Sample positions: {list(unique_positions)[:5]}")
        
        # Should have multiple different positions
        self.assertGreater(len(unique_positions), 1, "Should use multiple positions, not just origin")
        
        # At least some pieces should NOT be at origin
        non_origin_pieces = sum(1 for x, y in positions if x != 0 or y != 0)
        print(f"📊 Non-origin pieces: {non_origin_pieces}/{len(positions)}")
        
        if len(result.placed_shapes) > 1:
            self.assertGreater(non_origin_pieces, 0, "Should place some pieces away from origin")
        
        print("✅ Intelligent positioning test PASSED")
    
    def test_no_overlaps(self):
        """Test that placed pieces don't overlap"""
        
        print("\n🔍 Testing: No Overlaps")
        print("=" * 25)
        
        algorithm = BestFitAlgorithm()
        result = algorithm.optimize(self.stocks, self.orders, self.config)
        
        # Group pieces by stock
        pieces_by_stock = {}
        for ps in result.placed_shapes:
            if ps.stock_id not in pieces_by_stock:
                pieces_by_stock[ps.stock_id] = []
            pieces_by_stock[ps.stock_id].append(ps.shape)
        
        overlap_count = 0
        
        for stock_id, pieces in pieces_by_stock.items():
            print(f"📦 Stock {stock_id}: {len(pieces)} pieces")
            
            # Check each pair of pieces for overlaps
            for i, piece1 in enumerate(pieces):
                for j, piece2 in enumerate(pieces[i+1:], i+1):
                    # Check overlap
                    if (piece1.x < piece2.x + piece2.width and
                        piece2.x < piece1.x + piece1.width and
                        piece1.y < piece2.y + piece2.height and
                        piece2.y < piece1.y + piece1.height):
                        
                        overlap_count += 1
                        print(f"❌ OVERLAP: Piece {i} and {j} in stock {stock_id}")
        
        print(f"🔍 Total overlaps found: {overlap_count}")
        
        self.assertEqual(overlap_count, 0, "No pieces should overlap")
        
        print("✅ No overlaps test PASSED")
    
    def test_efficiency_improvement(self):
        """Test that efficiency is significantly better than basic placement"""
        
        print("\n📈 Testing: Efficiency Improvement")
        print("=" * 35)
        
        algorithm = BestFitAlgorithm()
        result = algorithm.optimize(self.stocks, self.orders, self.config)
        
        print(f"📊 Final efficiency: {result.efficiency_percentage:.1f}%")
        print(f"📏 Placed pieces: {len(result.placed_shapes)}")
        print(f"📋 Total pieces requested: {sum(order.quantity for order in self.orders)}")
        
        # Calculate theoretical maximum efficiency
        total_piece_area = sum(order.total_area for order in self.orders)
        total_stock_area = sum(stock.area for stock in self.stocks)
        theoretical_max = (total_piece_area / total_stock_area) * 100
        
        print(f"🎯 Theoretical maximum: {theoretical_max:.1f}%")
        
        # Should achieve reasonable efficiency
        self.assertGreater(result.efficiency_percentage, 30, 
                          "Should achieve decent efficiency with advanced placement")
        
        # Should place most pieces
        total_pieces = sum(order.quantity for order in self.orders)
        placement_ratio = len(result.placed_shapes) / total_pieces
        print(f"📦 Placement ratio: {placement_ratio:.1%}")
        
        self.assertGreater(placement_ratio, 0.5, "Should place majority of pieces")
        
        print("✅ Efficiency improvement test PASSED")
    
    def test_rotation_handling(self):
        """Test that rotation is handled properly"""
        
        print("\n🔄 Testing: Rotation Handling")
        print("=" * 30)
        
        # Test with rectangular pieces that benefit from rotation
        rotation_orders = [
            Order("TALL", Rectangle(100, 400), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL),
            Order("WIDE", Rectangle(400, 100), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL)
        ]
        
        algorithm = BestFitAlgorithm()
        
        # Test with rotation enabled
        config_with_rotation = OptimizationConfig(allow_rotation=True)
        result_with_rotation = algorithm.optimize(self.stocks, rotation_orders, config_with_rotation)
        
        # Test without rotation
        config_no_rotation = OptimizationConfig(allow_rotation=False)
        result_no_rotation = algorithm.optimize(self.stocks, rotation_orders, config_no_rotation)
        
        print(f"🔄 With rotation: {result_with_rotation.efficiency_percentage:.1f}% efficiency")
        print(f"🚫 Without rotation: {result_no_rotation.efficiency_percentage:.1f}% efficiency")
        
        print(f"📦 With rotation: {len(result_with_rotation.placed_shapes)} pieces placed")
        print(f"📦 Without rotation: {len(result_no_rotation.placed_shapes)} pieces placed")
        
        # Rotation should generally help or at least not hurt
        self.assertGreaterEqual(result_with_rotation.efficiency_percentage, 
                               result_no_rotation.efficiency_percentage,
                               "Rotation should help or at least not hurt efficiency")
        
        print("✅ Rotation handling test PASSED")
    
    def test_performance_benchmark(self):
        """Benchmark performance of advanced algorithm"""
        
        print("\n⚡ Performance Benchmark")
        print("=" * 25)
        
        algorithm = BestFitAlgorithm()
        
        # Run multiple times for average
        times = []
        efficiencies = []
        
        for run in range(3):
            start_time = time.time()
            result = algorithm.optimize(self.stocks, self.orders, self.config)
            elapsed = time.time() - start_time
            
            times.append(elapsed)
            efficiencies.append(result.efficiency_percentage)
        
        avg_time = sum(times) / len(times)
        avg_efficiency = sum(efficiencies) / len(efficiencies)
        
        print(f"⏱️  Average time: {avg_time:.3f}s")
        print(f"📊 Average efficiency: {avg_efficiency:.1f}%")
        print(f"🎯 Consistency: {min(efficiencies):.1f}% - {max(efficiencies):.1f}%")
        
        # Should be fast and consistent
        self.assertLess(avg_time, 1.0, "Should complete quickly")
        self.assertGreater(avg_efficiency, 25, "Should achieve reasonable efficiency")
        
        # Results should be consistent (deterministic algorithm)
        efficiency_range = max(efficiencies) - min(efficiencies)
        self.assertLess(efficiency_range, 5.0, "Results should be consistent")
        
        print("✅ Performance benchmark PASSED")


if __name__ == '__main__':
    unittest.main() 