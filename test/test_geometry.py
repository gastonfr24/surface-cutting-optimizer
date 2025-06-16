#!/usr/bin/env python3
"""
Unit tests for geometry classes
"""

import unittest
import math
from surface_optimizer.core.geometry import Rectangle, Circle, Polygon
from surface_optimizer.core.exceptions import InvalidDimensionsError, InvalidShapeError


class TestRectangle(unittest.TestCase):
    """Test cases for Rectangle class"""
    
    def test_rectangle_creation(self):
        """Test basic rectangle creation"""
        rect = Rectangle(100, 50)
        self.assertEqual(rect.width, 100)
        self.assertEqual(rect.height, 50)
        self.assertEqual(rect.x, 0)
        self.assertEqual(rect.y, 0)
        self.assertEqual(rect.rotation, 0)
    
    def test_rectangle_with_position(self):
        """Test rectangle creation with position"""
        rect = Rectangle(100, 50, x=10, y=20)
        self.assertEqual(rect.x, 10)
        self.assertEqual(rect.y, 20)
    
    def test_invalid_dimensions(self):
        """Test that invalid dimensions raise exception"""
        with self.assertRaises(InvalidDimensionsError):
            Rectangle(0, 50)
        
        with self.assertRaises(InvalidDimensionsError):
            Rectangle(-10, 50)
        
        with self.assertRaises(InvalidDimensionsError):
            Rectangle(100, -5)
    
    def test_area_calculation(self):
        """Test area calculation"""
        rect = Rectangle(100, 50)
        self.assertEqual(rect.area(), 5000)
    
    def test_bounding_box_no_rotation(self):
        """Test bounding box without rotation"""
        rect = Rectangle(100, 50, x=10, y=20)
        bbox = rect.bounding_box()
        expected = (10, 20, 110, 70)
        self.assertEqual(bbox, expected)
    
    def test_contains_point(self):
        """Test point containment"""
        rect = Rectangle(100, 50, x=10, y=20)
        
        # Point inside
        self.assertTrue(rect.contains_point(50, 40))
        
        # Point on border
        self.assertTrue(rect.contains_point(10, 20))
        self.assertTrue(rect.contains_point(110, 70))
        
        # Point outside
        self.assertFalse(rect.contains_point(5, 40))
        self.assertFalse(rect.contains_point(120, 40))
        self.assertFalse(rect.contains_point(50, 10))
        self.assertFalse(rect.contains_point(50, 80))
    
    def test_fits_in_rectangle(self):
        """Test if rectangle fits in container"""
        rect = Rectangle(100, 50)
        
        # Fits exactly
        self.assertTrue(rect.fits_in_rectangle(100, 50))
        
        # Fits with space
        self.assertTrue(rect.fits_in_rectangle(150, 100))
        
        # Doesn't fit
        self.assertFalse(rect.fits_in_rectangle(90, 50))
        self.assertFalse(rect.fits_in_rectangle(100, 40))
    
    def test_move(self):
        """Test moving rectangle"""
        rect = Rectangle(100, 50, x=10, y=20)
        rect.move(5, -3)
        self.assertEqual(rect.x, 15)
        self.assertEqual(rect.y, 17)
    
    def test_rotate(self):
        """Test rotating rectangle"""
        rect = Rectangle(100, 50)
        rect.rotate(90)
        self.assertEqual(rect.rotation, 90)
        
        rect.rotate(270)
        self.assertEqual(rect.rotation, 0)  # 360 % 360 = 0


class TestCircle(unittest.TestCase):
    """Test cases for Circle class"""
    
    def test_circle_creation(self):
        """Test basic circle creation"""
        circle = Circle(50)
        self.assertEqual(circle.radius, 50)
        self.assertEqual(circle.x, 0)
        self.assertEqual(circle.y, 0)
    
    def test_invalid_radius(self):
        """Test that invalid radius raises exception"""
        with self.assertRaises(InvalidDimensionsError):
            Circle(0)
        
        with self.assertRaises(InvalidDimensionsError):
            Circle(-10)
    
    def test_area_calculation(self):
        """Test area calculation"""
        circle = Circle(10)
        expected_area = math.pi * 100
        self.assertAlmostEqual(circle.area(), expected_area, places=5)
    
    def test_bounding_box(self):
        """Test bounding box calculation"""
        circle = Circle(50, x=100, y=200)
        bbox = circle.bounding_box()
        expected = (50, 150, 150, 250)
        self.assertEqual(bbox, expected)
    
    def test_contains_point(self):
        """Test point containment"""
        circle = Circle(50, x=100, y=100)
        
        # Point at center
        self.assertTrue(circle.contains_point(100, 100))
        
        # Point on edge
        self.assertTrue(circle.contains_point(150, 100))
        self.assertTrue(circle.contains_point(100, 150))
        
        # Point inside
        self.assertTrue(circle.contains_point(130, 130))
        
        # Point outside
        self.assertFalse(circle.contains_point(160, 100))
        self.assertFalse(circle.contains_point(100, 160))
    
    def test_fits_in_rectangle(self):
        """Test if circle fits in rectangle"""
        circle = Circle(50)
        
        # Fits exactly
        self.assertTrue(circle.fits_in_rectangle(100, 100))
        
        # Fits with space
        self.assertTrue(circle.fits_in_rectangle(150, 150))
        
        # Doesn't fit
        self.assertFalse(circle.fits_in_rectangle(90, 100))
        self.assertFalse(circle.fits_in_rectangle(100, 90))


class TestPolygon(unittest.TestCase):
    """Test cases for Polygon class"""
    
    def test_polygon_creation(self):
        """Test basic polygon creation"""
        vertices = [(0, 0), (100, 0), (100, 50), (0, 50)]
        polygon = Polygon(vertices)
        self.assertEqual(len(polygon.vertices), 4)
    
    def test_invalid_polygon(self):
        """Test that invalid polygons raise exception"""
        # Too few vertices
        with self.assertRaises(InvalidShapeError):
            Polygon([(0, 0), (100, 0)])
    
    def test_area_calculation(self):
        """Test area calculation using shoelace formula"""
        # Square
        vertices = [(0, 0), (100, 0), (100, 100), (0, 100)]
        polygon = Polygon(vertices)
        self.assertEqual(polygon.area(), 10000)
        
        # Triangle
        vertices = [(0, 0), (100, 0), (50, 100)]
        polygon = Polygon(vertices)
        self.assertEqual(polygon.area(), 5000)
    
    def test_bounding_box(self):
        """Test bounding box calculation"""
        vertices = [(10, 20), (110, 20), (110, 70), (10, 70)]
        polygon = Polygon(vertices)
        bbox = polygon.bounding_box()
        expected = (10, 20, 110, 70)
        self.assertEqual(bbox, expected)


class TestShapeOverlaps(unittest.TestCase):
    """Test shape overlap detection"""
    
    def test_rectangle_overlap(self):
        """Test rectangle-rectangle overlap"""
        rect1 = Rectangle(100, 50, x=0, y=0)
        rect2 = Rectangle(100, 50, x=50, y=25)
        
        # Should overlap
        self.assertTrue(rect1.overlaps(rect2))
        self.assertTrue(rect2.overlaps(rect1))
        
        # No overlap
        rect3 = Rectangle(100, 50, x=150, y=0)
        self.assertFalse(rect1.overlaps(rect3))
        self.assertFalse(rect3.overlaps(rect1))
    
    def test_circle_overlap(self):
        """Test circle-circle overlap"""
        circle1 = Circle(50, x=0, y=0)
        circle2 = Circle(50, x=50, y=0)
        
        # Should overlap
        self.assertTrue(circle1.overlaps(circle2))
        
        # No overlap
        circle3 = Circle(50, x=150, y=0)
        self.assertFalse(circle1.overlaps(circle3))


if __name__ == '__main__':
    unittest.main() 