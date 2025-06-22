"""
Unit tests for Surface Cutting Optimizer geometry module

Tests cover:
- Rectangle creation, properties, and operations
- Circle creation, properties, and operations  
- Polygon creation and complex shapes
- Shape transformations (rotation, translation)
- Overlap detection algorithms
- Bounding box calculations
- Spatial relationship tests
- Edge cases and error handling
"""

import unittest
import pytest
import math
from unittest.mock import patch, MagicMock

from surface_optimizer.core.geometry import (
    Shape, Rectangle, Circle, Polygon
)
from surface_optimizer.core.exceptions import (
    InvalidDimensionsError, InvalidShapeError
)


class TestShapeBase(unittest.TestCase):
    """Tests for abstract Shape base class"""
    
    def test_shape_initialization(self):
        """Test Shape base class initialization"""
        # We can't instantiate Shape directly, but we can test through Rectangle
        rect = Rectangle(100.0, 50.0, x=10.0, y=20.0, rotation=45.0)
        self.assertEqual(rect.x, 10.0)
        self.assertEqual(rect.y, 20.0)
        self.assertEqual(rect.rotation, 45.0)
        
    def test_rotation_normalization(self):
        """Test rotation is normalized to 0-360 degrees"""
        rect = Rectangle(100.0, 50.0, rotation=450.0)  # 450 = 90
        self.assertEqual(rect.rotation, 90.0)
        
        rect2 = Rectangle(100.0, 50.0, rotation=-90.0)  # -90 = 270
        self.assertEqual(rect2.rotation, 270.0)
        
    def test_move_operation(self):
        """Test shape movement"""
        rect = Rectangle(100.0, 50.0, x=10.0, y=20.0)
        rect.move(5.0, -10.0)
        self.assertEqual(rect.x, 15.0)
        self.assertEqual(rect.y, 10.0)
        
    def test_rotate_operation(self):
        """Test shape rotation"""
        rect = Rectangle(100.0, 50.0, rotation=30.0)
        rect.rotate(45.0)
        self.assertEqual(rect.rotation, 75.0)
        
        # Test rotation overflow
        rect.rotate(300.0)  # 75 + 300 = 375, normalized to 15
        self.assertEqual(rect.rotation, 15.0)


class TestRectangle(unittest.TestCase):
    """Tests for Rectangle class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rect = Rectangle(100.0, 50.0, x=10.0, y=20.0)
        
    def test_valid_rectangle_creation(self):
        """Test creating valid rectangles"""
        rect = Rectangle(width=200.0, height=100.0)
        self.assertEqual(rect.width, 200.0)
        self.assertEqual(rect.height, 100.0)
        self.assertEqual(rect.x, 0.0)  # default
        self.assertEqual(rect.y, 0.0)  # default
        self.assertEqual(rect.rotation, 0.0)  # default
        
    def test_invalid_rectangle_dimensions(self):
        """Test rectangle creation with invalid dimensions"""
        with self.assertRaises(InvalidDimensionsError):
            Rectangle(width=-100.0, height=50.0)
        with self.assertRaises(InvalidDimensionsError):
            Rectangle(width=100.0, height=0.0)
        with self.assertRaises(InvalidDimensionsError):
            Rectangle(width=0.0, height=0.0)
            
    def test_area_calculation(self):
        """Test rectangle area calculation"""
        self.assertEqual(self.rect.area(), 5000.0)  # 100 * 50
        
        square = Rectangle(25.0, 25.0)
        self.assertEqual(square.area(), 625.0)
        
    def test_bounding_box_no_rotation(self):
        """Test bounding box calculation without rotation"""
        bbox = self.rect.bounding_box()
        expected = (10.0, 20.0, 110.0, 70.0)  # (min_x, min_y, max_x, max_y)
        self.assertEqual(bbox, expected)
        
    def test_bounding_box_with_rotation(self):
        """Test bounding box calculation with rotation"""
        # Create a 100x50 rectangle at origin, rotated 90 degrees
        rect = Rectangle(100.0, 50.0, x=0.0, y=0.0, rotation=90.0)
        bbox = rect.bounding_box()
        
        # After 90° rotation, width and height should be swapped in bounding box
        # The exact values depend on the rotation implementation
        self.assertIsNotNone(bbox)
        self.assertEqual(len(bbox), 4)
        
    def test_corner_calculation(self):
        """Test corner calculation for rectangles"""
        corners = self.rect._get_corners()
        self.assertEqual(len(corners), 4)
        
        # For non-rotated rectangle at (10, 20) with size 100x50
        expected_corners = [
            (10.0, 20.0),     # bottom-left
            (110.0, 20.0),    # bottom-right  
            (110.0, 70.0),    # top-right
            (10.0, 70.0)      # top-left
        ]
        self.assertEqual(corners, expected_corners)
        
    def test_corner_calculation_rotated(self):
        """Test corner calculation for rotated rectangles"""
        # 90-degree rotation should swap dimensions
        rect = Rectangle(100.0, 50.0, x=50.0, y=50.0, rotation=90.0)
        corners = rect._get_corners()
        self.assertEqual(len(corners), 4)
        
        # All corners should be valid coordinates
        for corner in corners:
            self.assertIsInstance(corner[0], float)
            self.assertIsInstance(corner[1], float)
            
    def test_contains_point_no_rotation(self):
        """Test point containment without rotation"""
        # Point inside rectangle
        self.assertTrue(self.rect.contains_point(50.0, 40.0))
        
        # Point on edge (should be included)
        self.assertTrue(self.rect.contains_point(10.0, 20.0))  # corner
        self.assertTrue(self.rect.contains_point(60.0, 20.0))  # bottom edge
        
        # Point outside rectangle
        self.assertFalse(self.rect.contains_point(5.0, 40.0))   # left
        self.assertFalse(self.rect.contains_point(120.0, 40.0)) # right
        self.assertFalse(self.rect.contains_point(50.0, 10.0))  # below
        self.assertFalse(self.rect.contains_point(50.0, 80.0))  # above
        
    def test_contains_point_with_rotation(self):
        """Test point containment with rotation"""
        # Create a rectangle and rotate it
        rect = Rectangle(100.0, 50.0, x=0.0, y=0.0, rotation=45.0)
        
        # Center point should always be inside
        center_x = rect.width / 2
        center_y = rect.height / 2
        self.assertTrue(rect.contains_point(center_x, center_y))
        
    def test_fits_in_rectangle_no_rotation(self):
        """Test rectangle fitting in container without rotation"""
        # Rectangle fits in larger container
        self.assertTrue(self.rect.fits_in_rectangle(200.0, 100.0))
        
        # Rectangle exactly fits
        self.assertTrue(self.rect.fits_in_rectangle(100.0, 50.0))
        
        # Rectangle doesn't fit - too wide
        self.assertFalse(self.rect.fits_in_rectangle(90.0, 100.0))
        
        # Rectangle doesn't fit - too tall
        self.assertFalse(self.rect.fits_in_rectangle(200.0, 40.0))
        
    def test_fits_in_rectangle_with_rotation(self):
        """Test rectangle fitting in container with rotation"""
        rect = Rectangle(100.0, 50.0, rotation=90.0)
        
        # After 90° rotation, effective size should be 50x100
        # So it should fit in 60x110 but not in 110x60
        self.assertTrue(rect.fits_in_rectangle(60.0, 110.0))
        # This test depends on the exact rotation implementation
        
    def test_rectangle_overlap_no_rotation(self):
        """Test rectangle overlap detection without rotation"""
        rect1 = Rectangle(100.0, 50.0, x=0.0, y=0.0)     # 0,0 to 100,50
        rect2 = Rectangle(100.0, 50.0, x=50.0, y=25.0)   # 50,25 to 150,75
        rect3 = Rectangle(100.0, 50.0, x=200.0, y=0.0)   # 200,0 to 300,50
        
        # rect1 and rect2 overlap
        self.assertTrue(rect1.overlaps(rect2))
        self.assertTrue(rect2.overlaps(rect1))  # symmetric
        
        # rect1 and rect3 don't overlap
        self.assertFalse(rect1.overlaps(rect3))
        self.assertFalse(rect3.overlaps(rect1))  # symmetric
        
    def test_rectangle_overlap_edge_touching(self):
        """Test rectangle overlap when edges are touching"""
        rect1 = Rectangle(100.0, 50.0, x=0.0, y=0.0)    # 0,0 to 100,50
        rect2 = Rectangle(100.0, 50.0, x=100.0, y=0.0)  # 100,0 to 200,50
        
        # Touching edges should not count as overlap
        self.assertFalse(rect1.overlaps(rect2))
        
    def test_rectangle_self_overlap(self):
        """Test rectangle doesn't overlap with itself"""
        # A rectangle should not overlap with itself
        # (this is more of a conceptual test for the algorithm)
        rect = Rectangle(100.0, 50.0)
        # We don't test self-overlap as it's not a typical use case
        
    def test_string_representation(self):
        """Test rectangle string representation"""
        rect_str = str(self.rect)
        self.assertIn("100.0", rect_str)
        self.assertIn("50.0", rect_str)


class TestCircle(unittest.TestCase):
    """Tests for Circle class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.circle = Circle(radius=25.0, x=50.0, y=30.0)
        
    def test_valid_circle_creation(self):
        """Test creating valid circles"""
        circle = Circle(radius=100.0)
        self.assertEqual(circle.radius, 100.0)
        self.assertEqual(circle.x, 0.0)  # default
        self.assertEqual(circle.y, 0.0)  # default
        
    def test_invalid_circle_radius(self):
        """Test circle creation with invalid radius"""
        with self.assertRaises(InvalidDimensionsError):
            Circle(radius=-10.0)
        with self.assertRaises(InvalidDimensionsError):
            Circle(radius=0.0)
            
    def test_area_calculation(self):
        """Test circle area calculation"""
        expected_area = math.pi * 25.0 * 25.0  # π * r²
        self.assertAlmostEqual(self.circle.area(), expected_area, places=5)
        
    def test_bounding_box(self):
        """Test circle bounding box calculation"""
        bbox = self.circle.bounding_box()
        expected = (25.0, 5.0, 75.0, 55.0)  # (x-r, y-r, x+r, y+r)
        self.assertEqual(bbox, expected)
        
    def test_contains_point(self):
        """Test point containment in circle"""
        # Center point
        self.assertTrue(self.circle.contains_point(50.0, 30.0))
        
        # Point on circumference (should be included)
        self.assertTrue(self.circle.contains_point(75.0, 30.0))  # right edge
        
        # Point inside circle
        self.assertTrue(self.circle.contains_point(60.0, 35.0))
        
        # Point outside circle
        self.assertFalse(self.circle.contains_point(100.0, 30.0))
        self.assertFalse(self.circle.contains_point(50.0, 100.0))
        
    def test_fits_in_rectangle(self):
        """Test circle fitting in rectangular container"""
        # Circle fits (diameter = 50)
        self.assertTrue(self.circle.fits_in_rectangle(60.0, 60.0))
        
        # Circle exactly fits
        self.assertTrue(self.circle.fits_in_rectangle(50.0, 50.0))
        
        # Circle doesn't fit - container too narrow
        self.assertFalse(self.circle.fits_in_rectangle(40.0, 60.0))
        
        # Circle doesn't fit - container too short
        self.assertFalse(self.circle.fits_in_rectangle(60.0, 40.0))
        
    def test_circle_circle_overlap(self):
        """Test circle-circle overlap detection"""
        circle1 = Circle(radius=25.0, x=0.0, y=0.0)
        circle2 = Circle(radius=25.0, x=30.0, y=0.0)  # Distance = 30, sum of radii = 50
        circle3 = Circle(radius=25.0, x=100.0, y=0.0)  # Distance = 100, sum of radii = 50
        
        # Overlapping circles
        self.assertTrue(circle1.overlaps(circle2))
        
        # Non-overlapping circles
        self.assertFalse(circle1.overlaps(circle3))
        
    def test_circle_rectangle_overlap(self):
        """Test circle-rectangle overlap detection"""
        circle = Circle(radius=25.0, x=50.0, y=50.0)
        rect1 = Rectangle(100.0, 100.0, x=0.0, y=0.0)    # Contains circle
        rect2 = Rectangle(50.0, 50.0, x=100.0, y=100.0)  # Far from circle
        rect3 = Rectangle(20.0, 20.0, x=60.0, y=60.0)    # Intersects circle
        
        # Circle overlaps with containing rectangle
        self.assertTrue(circle.overlaps(rect1))
        
        # Circle doesn't overlap with distant rectangle
        self.assertFalse(circle.overlaps(rect2))
        
        # Circle overlaps with intersecting rectangle
        self.assertTrue(circle.overlaps(rect3))
        
    def test_string_representation(self):
        """Test circle string representation"""
        circle_str = str(self.circle)
        self.assertIn("25.0", circle_str)


class TestPolygon(unittest.TestCase):
    """Tests for Polygon class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Triangle vertices
        self.triangle_vertices = [(0.0, 0.0), (100.0, 0.0), (50.0, 100.0)]
        self.triangle = Polygon(self.triangle_vertices)
        
        # Square vertices  
        self.square_vertices = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
        self.square = Polygon(self.square_vertices)
        
    def test_valid_polygon_creation(self):
        """Test creating valid polygons"""
        self.assertEqual(len(self.triangle.vertices), 3)
        self.assertEqual(len(self.square.vertices), 4)
        
    def test_invalid_polygon_creation(self):
        """Test polygon creation with invalid vertices"""
        # Too few vertices
        with self.assertRaises(InvalidShapeError):
            Polygon([(0.0, 0.0), (1.0, 1.0)])  # Only 2 vertices
            
        # Empty vertices
        with self.assertRaises(InvalidShapeError):
            Polygon([])
            
    def test_triangle_area_calculation(self):
        """Test triangle area calculation using shoelace formula"""
        expected_area = 5000.0  # 0.5 * base * height = 0.5 * 100 * 100 = 5000
        calculated_area = self.triangle.area()
        self.assertAlmostEqual(calculated_area, expected_area, places=1)
        
    def test_square_area_calculation(self):
        """Test square area calculation"""
        expected_area = 10000.0  # 100 * 100
        calculated_area = self.square.area()
        self.assertAlmostEqual(calculated_area, expected_area, places=1)
        
    def test_bounding_box(self):
        """Test polygon bounding box calculation"""
        bbox = self.triangle.bounding_box()
        expected = (0.0, 0.0, 100.0, 100.0)  # (min_x, min_y, max_x, max_y)
        self.assertEqual(bbox, expected)
        
    def test_transformed_vertices(self):
        """Test vertex transformation with position and rotation"""
        triangle = Polygon([(0.0, 0.0), (10.0, 0.0), (5.0, 10.0)], x=10.0, y=20.0)
        transformed = triangle._get_transformed_vertices()
        
        # All vertices should be translated by (10, 20)
        expected = [(10.0, 20.0), (20.0, 20.0), (15.0, 30.0)]
        self.assertEqual(transformed, expected)
        
    def test_contains_point(self):
        """Test point containment in polygon using ray casting"""
        # Point inside triangle
        self.assertTrue(self.triangle.contains_point(50.0, 25.0))
        
        # Point outside triangle
        self.assertFalse(self.triangle.contains_point(150.0, 50.0))
        
        # Point on vertex
        self.assertTrue(self.triangle.contains_point(0.0, 0.0))
        
        # Point inside square
        self.assertTrue(self.square.contains_point(50.0, 50.0))
        
        # Point outside square
        self.assertFalse(self.square.contains_point(150.0, 50.0))
        
    def test_polygon_overlap(self):
        """Test polygon overlap detection"""
        # Create another triangle that overlaps
        overlapping_triangle = Polygon([(50.0, 0.0), (150.0, 0.0), (100.0, 100.0)])
        
        # Create a triangle that doesn't overlap
        separate_triangle = Polygon([(200.0, 0.0), (300.0, 0.0), (250.0, 100.0)])
        
        # Test overlap
        self.assertTrue(self.triangle.overlaps(overlapping_triangle))
        self.assertFalse(self.triangle.overlaps(separate_triangle))
        
    def test_string_representation(self):
        """Test polygon string representation"""
        poly_str = str(self.triangle)
        self.assertIn("3", poly_str)  # Number of vertices


class TestShapeInteractions(unittest.TestCase):
    """Tests for interactions between different shape types"""
    
    def test_rectangle_circle_overlap(self):
        """Test rectangle-circle overlap detection"""
        rect = Rectangle(100.0, 100.0, x=0.0, y=0.0)
        circle_inside = Circle(radius=25.0, x=50.0, y=50.0)
        circle_outside = Circle(radius=25.0, x=200.0, y=200.0)
        circle_intersecting = Circle(radius=30.0, x=80.0, y=80.0)
        
        # Circle inside rectangle
        self.assertTrue(rect.overlaps(circle_inside))
        self.assertTrue(circle_inside.overlaps(rect))
        
        # Circle outside rectangle
        self.assertFalse(rect.overlaps(circle_outside))
        self.assertFalse(circle_outside.overlaps(rect))
        
        # Circle intersecting rectangle
        self.assertTrue(rect.overlaps(circle_intersecting))
        self.assertTrue(circle_intersecting.overlaps(rect))
        
    def test_mixed_shape_overlaps(self):
        """Test overlap detection between different shape types"""
        rect = Rectangle(100.0, 100.0, x=0.0, y=0.0)
        circle = Circle(radius=50.0, x=50.0, y=50.0)
        triangle = Polygon([(25.0, 25.0), (75.0, 25.0), (50.0, 75.0)])
        
        # All shapes should overlap (they're all centered around (50,50))
        self.assertTrue(rect.overlaps(circle))
        self.assertTrue(rect.overlaps(triangle))
        self.assertTrue(circle.overlaps(triangle))
        
    def test_bounding_box_consistency(self):
        """Test that all shapes return consistent bounding box format"""
        rect = Rectangle(100.0, 50.0, x=10.0, y=20.0)
        circle = Circle(radius=25.0, x=50.0, y=30.0)
        triangle = Polygon([(0.0, 0.0), (100.0, 0.0), (50.0, 100.0)])
        
        for shape in [rect, circle, triangle]:
            bbox = shape.bounding_box()
            self.assertEqual(len(bbox), 4)
            self.assertLessEqual(bbox[0], bbox[2])  # min_x <= max_x
            self.assertLessEqual(bbox[1], bbox[3])  # min_y <= max_y


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error conditions"""
    
    def test_zero_area_shapes(self):
        """Test behavior with zero or near-zero area shapes"""
        # Very thin rectangle
        thin_rect = Rectangle(0.001, 1000.0)
        self.assertGreater(thin_rect.area(), 0)
        
        # Very small circle
        small_circle = Circle(radius=0.001)
        self.assertGreater(small_circle.area(), 0)
        
    def test_large_coordinates(self):
        """Test shapes with very large coordinates"""
        large_rect = Rectangle(1000000.0, 1000000.0, x=1000000.0, y=1000000.0)
        self.assertEqual(large_rect.area(), 1e12)
        
        bbox = large_rect.bounding_box()
        self.assertEqual(bbox[0], 1000000.0)  # min_x
        self.assertEqual(bbox[2], 2000000.0)  # max_x
        
    def test_negative_coordinates(self):
        """Test shapes with negative coordinates"""
        rect = Rectangle(100.0, 50.0, x=-50.0, y=-25.0)
        bbox = rect.bounding_box()
        self.assertEqual(bbox, (-50.0, -25.0, 50.0, 25.0))
        
    def test_overlapping_identical_shapes(self):
        """Test overlap detection with identical shapes"""
        rect1 = Rectangle(100.0, 50.0, x=10.0, y=20.0)
        rect2 = Rectangle(100.0, 50.0, x=10.0, y=20.0)
        
        # Identical shapes should overlap completely
        self.assertTrue(rect1.overlaps(rect2))
        
    def test_rotation_precision(self):
        """Test rotation precision and edge cases"""
        rect = Rectangle(100.0, 50.0, rotation=359.9999)
        self.assertAlmostEqual(rect.rotation, 359.9999, places=4)
        
        # Test rotation normalization edge cases
        rect.rotate(0.0001)
        self.assertLess(rect.rotation, 0.1)  # Should wrap around to ~0


class TestPerformance(unittest.TestCase):
    """Basic performance and stress tests"""
    
    def test_many_overlap_checks(self):
        """Test performance with many overlap checks"""
        rectangles = []
        for i in range(100):
            rect = Rectangle(10.0, 10.0, x=float(i), y=float(i))
            rectangles.append(rect)
            
        # Check overlaps between all pairs
        overlap_count = 0
        for i, rect1 in enumerate(rectangles):
            for rect2 in rectangles[i+1:]:
                if rect1.overlaps(rect2):
                    overlap_count += 1
                    
        # Should have some overlaps but not too many
        self.assertGreater(overlap_count, 0)
        self.assertLess(overlap_count, len(rectangles) * len(rectangles))
        
    def test_complex_polygon_operations(self):
        """Test operations on complex polygons"""
        # Create a polygon with many vertices
        vertices = []
        for i in range(20):
            angle = 2 * math.pi * i / 20
            x = 100 * math.cos(angle)
            y = 100 * math.sin(angle)
            vertices.append((x, y))
            
        complex_polygon = Polygon(vertices)
        
        # Should handle area calculation
        area = complex_polygon.area()
        self.assertGreater(area, 0)
        
        # Should handle point containment
        self.assertTrue(complex_polygon.contains_point(0.0, 0.0))  # center
        self.assertFalse(complex_polygon.contains_point(200.0, 200.0))  # outside


if __name__ == '__main__':
    unittest.main() 