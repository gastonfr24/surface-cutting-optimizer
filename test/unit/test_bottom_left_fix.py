#!/usr/bin/env python3
"""
🧪 Test for BottomLeft Algorithm Fixes
=====================================

Tests to reproduce bugs in BottomLeft algorithm and verify fixes.
"""

import unittest
import time

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm


class TestBottomLeftFix(unittest.TestCase):
    """Test fixes for BottomLeft algorithm"""
    
    def setUp(self):
        """Setup test data"""
        self.algorithm = BottomLeftAlgorithm()
        
        # Simple test case
        self.stocks = [
            Stock("S1", 1000, 800, material_type=MaterialType.METAL, cost_per_unit=5.0)
        ]
        
        self.orders = [
            Order("O1", Rectangle(200, 150), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL),
            Order("O2", Rectangle(180, 120), quantity=1, priority=Priority.MEDIUM, material_type=MaterialType.METAL)
        ]
        
        self.config = OptimizationConfig(
            allow_rotation=True,
            cutting_width=3.0,
            prioritize_orders=True
        )
    
    def test_basic_functionality(self):
        """Test that BottomLeft algorithm works without errors"""
        
        try:
            result = self.algorithm.optimize(self.stocks, self.orders, self.config)
            
            # Should not throw exceptions
            self.assertIsNotNone(result)
            self.assertEqual(result.algorithm_used, "bottom_left")
            self.assertGreaterEqual(result.efficiency_percentage, 0)
            self.assertGreaterEqual(result.total_stock_used, 0)
            
            print(f"✅ BottomLeft test passed:")
            print(f"   • Efficiency: {result.efficiency_percentage:.1f}%")
            print(f"   • Stocks used: {result.total_stock_used}")
            print(f"   • Orders fulfilled: {result.total_orders_fulfilled}")
            
        except Exception as e:
            self.fail(f"BottomLeft algorithm failed with error: {e}")
    
    def test_multiple_pieces(self):
        """Test with multiple pieces to ensure proper placement"""
        
        orders = [
            Order("O1", Rectangle(150, 100), quantity=3, priority=Priority.HIGH, material_type=MaterialType.METAL),
            Order("O2", Rectangle(120, 80), quantity=2, priority=Priority.MEDIUM, material_type=MaterialType.METAL)
        ]
        
        try:
            result = self.algorithm.optimize(self.stocks, orders, self.config)
            
            self.assertIsNotNone(result)
            self.assertGreater(len(result.placed_shapes), 0)
            
            # Check no overlaps
            placed_rectangles = []
            for ps in result.placed_shapes:
                if ps.stock_id == "S1":
                    rect = ps.shape
                    placed_rectangles.append((rect.x, rect.y, rect.x + rect.width, rect.y + rect.height))
            
            # Verify no overlaps
            for i, rect1 in enumerate(placed_rectangles):
                for j, rect2 in enumerate(placed_rectangles[i+1:], i+1):
                    x1_min, y1_min, x1_max, y1_max = rect1
                    x2_min, y2_min, x2_max, y2_max = rect2
                    
                    # Check if rectangles overlap
                    overlap = not (x1_max <= x2_min or x2_max <= x1_min or 
                                 y1_max <= y2_min or y2_max <= y1_min)
                    
                    self.assertFalse(overlap, f"Overlap detected between pieces {i} and {j}")
            
            print(f"✅ Multiple pieces test passed: {len(result.placed_shapes)} pieces placed")
            
        except Exception as e:
            self.fail(f"Multiple pieces test failed: {e}")
    
    def test_performance(self):
        """Test that algorithm completes in reasonable time"""
        
        start_time = time.time()
        result = self.algorithm.optimize(self.stocks, self.orders, self.config)
        elapsed = time.time() - start_time
        
        # Should complete quickly
        self.assertLess(elapsed, 1.0, "BottomLeft taking too long")
        self.assertGreater(result.efficiency_percentage, 0)
        
        print(f"✅ Performance test passed: {elapsed:.3f}s")
    
    def test_edge_cases(self):
        """Test edge cases that might cause errors"""
        
        # Empty orders
        empty_result = self.algorithm.optimize(self.stocks, [], self.config)
        self.assertEqual(len(empty_result.placed_shapes), 0)
        self.assertEqual(empty_result.efficiency_percentage, 0)
        
        # Orders that don't fit
        big_orders = [
            Order("BIG", Rectangle(2000, 1500), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL)
        ]
        
        big_result = self.algorithm.optimize(self.stocks, big_orders, self.config)
        self.assertEqual(len(big_result.placed_shapes), 0)
        self.assertEqual(len(big_result.unfulfilled_orders), 1)
        
        print("✅ Edge cases test passed")


if __name__ == '__main__':
    unittest.main() 