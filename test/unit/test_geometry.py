#!/usr/bin/env python3
"""
Modern pytest-based tests for geometry classes

Uses pytest fixtures, parametrization, and modern testing patterns.
"""

import pytest
import math
from typing import Tuple, List

from surface_optimizer.core.geometry import Rectangle, Circle, Polygon
from surface_optimizer.core.exceptions import InvalidDimensionsError, InvalidShapeError


# Fixtures for common test data
@pytest.fixture
def basic_rectangle():
    """Basic rectangle for testing"""
    return Rectangle(100, 50)


@pytest.fixture
def positioned_rectangle():
    """Rectangle with specific position"""
    return Rectangle(100, 50, x=10, y=20)


@pytest.fixture
def basic_circle():
    """Basic circle for testing"""
    return Circle(50)


@pytest.fixture
def positioned_circle():
    """Circle with specific position"""
    return Circle(50, x=100, y=200)


@pytest.fixture
def basic_polygon():
    """Basic square polygon for testing"""
    return Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])


# Rectangle Tests
class TestRectangle:
    """Test Rectangle geometry class"""
    
    def test_rectangle_creation(self, basic_rectangle):
        """Test basic rectangle creation"""
        assert basic_rectangle.width == 100
        assert basic_rectangle.height == 50
        assert basic_rectangle.x == 0
        assert basic_rectangle.y == 0
        assert basic_rectangle.rotation == 0
    
    def test_rectangle_with_position(self, positioned_rectangle):
        """Test rectangle creation with position"""
        assert positioned_rectangle.x == 10
        assert positioned_rectangle.y == 20
    
    @pytest.mark.parametrize("width,height,should_raise", [
        (0, 50, True),      # Zero width
        (-10, 50, True),    # Negative width
        (100, -5, True),    # Negative height
        (100, 0, True),     # Zero height
        (100, 50, False),   # Valid dimensions
        (0.1, 0.1, False),  # Small valid dimensions
    ])
    def test_rectangle_validation(self, width, height, should_raise):
        """Test rectangle dimension validation"""
        if should_raise:
            with pytest.raises(InvalidDimensionsError):
                Rectangle(width, height)
        else:
            rect = Rectangle(width, height)
            assert rect.width == width
            assert rect.height == height
    
    def test_area_calculation(self, basic_rectangle):
        """Test area calculation"""
        assert basic_rectangle.area() == 5000
    
    @pytest.mark.parametrize("width,height,expected_area", [
        (100, 50, 5000),
        (10, 10, 100),
        (1, 1000, 1000),
        (0.5, 2, 1.0),
    ])
    def test_area_various_sizes(self, width, height, expected_area):
        """Test area calculation for various sizes"""
        rect = Rectangle(width, height)
        assert rect.area() == expected_area
    
    def test_bounding_box_no_rotation(self, positioned_rectangle):
        """Test bounding box without rotation"""
        bbox = positioned_rectangle.bounding_box()
        expected = (10, 20, 110, 70)
        assert bbox == expected
    
    @pytest.mark.parametrize("x,y,inside", [
        (50, 40, True),     # Point inside
        (10, 20, True),     # Point on bottom-left corner
        (110, 70, True),    # Point on top-right corner
        (60, 20, True),     # Point on bottom edge
        (110, 45, True),    # Point on right edge
        (5, 40, False),     # Point left of rectangle
        (120, 40, False),   # Point right of rectangle
        (50, 10, False),    # Point below rectangle
        (50, 80, False),    # Point above rectangle
    ])
    def test_contains_point(self, positioned_rectangle, x, y, inside):
        """Test point containment"""
        assert positioned_rectangle.contains_point(x, y) == inside
    
    @pytest.mark.parametrize("container_w,container_h,fits", [
        (100, 50, True),    # Fits exactly
        (150, 100, True),   # Fits with space
        (90, 50, False),    # Too narrow
        (100, 40, False),   # Too short
        (90, 40, False),    # Too small both ways
        (200, 200, True),   # Much larger container
    ])
    def test_fits_in_rectangle(self, basic_rectangle, container_w, container_h, fits):
        """Test if rectangle fits in container"""
        assert basic_rectangle.fits_in_rectangle(container_w, container_h) == fits
    
    def test_move(self, positioned_rectangle):
        """Test moving rectangle"""
        original_x, original_y = positioned_rectangle.x, positioned_rectangle.y
        positioned_rectangle.move(5, -3)
        assert positioned_rectangle.x == original_x + 5
        assert positioned_rectangle.y == original_y - 3
    
    @pytest.mark.parametrize("rotation,expected", [
        (90, 90),
        (180, 180),
        (270, 270),
        (360, 0),      # Full rotation
        (450, 90),     # > 360 degrees
        (-90, 270),    # Negative rotation
    ])
    def test_rotate(self, basic_rectangle, rotation, expected):
        """Test rotating rectangle"""
        basic_rectangle.rotate(rotation)
        assert basic_rectangle.rotation == expected


# Circle Tests
class TestCircle:
    """Test Circle geometry class"""
    
    def test_circle_creation(self, basic_circle):
        """Test basic circle creation"""
        assert basic_circle.radius == 50
        assert basic_circle.x == 0
        assert basic_circle.y == 0
    
    @pytest.mark.parametrize("radius,should_raise", [
        (0, True),      # Zero radius
        (-10, True),    # Negative radius
        (50, False),    # Valid radius
        (0.1, False),   # Small valid radius
    ])
    def test_circle_validation(self, radius, should_raise):
        """Test circle radius validation"""
        if should_raise:
            with pytest.raises(InvalidDimensionsError):
                Circle(radius)
        else:
            circle = Circle(radius)
            assert circle.radius == radius
    
    @pytest.mark.parametrize("radius,expected_area", [
        (10, math.pi * 100),
        (1, math.pi),
        (5, math.pi * 25),
    ])
    def test_area_calculation(self, radius, expected_area):
        """Test area calculation"""
        circle = Circle(radius)
        assert abs(circle.area() - expected_area) < 1e-10
    
    def test_bounding_box(self, positioned_circle):
        """Test bounding box calculation"""
        bbox = positioned_circle.bounding_box()
        expected = (50, 150, 150, 250)  # (100-50, 200-50, 100+50, 200+50)
        assert bbox == expected
    
    @pytest.mark.parametrize("x,y,inside", [
        (100, 200, True),   # Center point
        (150, 200, True),   # Point on edge (right)
        (100, 250, True),   # Point on edge (top)
        (130, 230, True),   # Point inside
        (160, 200, False),  # Point outside (right)
        (100, 260, False),  # Point outside (top)
        (170, 270, False),  # Point outside (diagonal)
    ])
    def test_contains_point(self, positioned_circle, x, y, inside):
        """Test point containment"""
        assert positioned_circle.contains_point(x, y) == inside
    
    @pytest.mark.parametrize("container_w,container_h,fits", [
        (100, 100, True),   # Fits exactly (diameter = 100)
        (150, 150, True),   # Fits with space
        (90, 100, False),   # Too narrow
        (100, 90, False),   # Too short
        (50, 50, False),    # Much too small
        (200, 200, True),   # Much larger container
    ])
    def test_fits_in_rectangle(self, basic_circle, container_w, container_h, fits):
        """Test if circle fits in rectangle"""
        assert basic_circle.fits_in_rectangle(container_w, container_h) == fits


# Polygon Tests
class TestPolygon:
    """Test Polygon geometry class"""
    
    def test_polygon_creation(self, basic_polygon):
        """Test basic polygon creation"""
        assert len(basic_polygon.vertices) == 4
        assert basic_polygon.vertices[0] == (0, 0)
        assert basic_polygon.vertices[2] == (100, 100)
    
    @pytest.mark.parametrize("vertices,should_raise", [
        ([(0, 0), (100, 0)], True),                    # Too few vertices
        ([(0, 0)], True),                              # Single vertex
        ([], True),                                    # Empty vertices
        ([(0, 0), (100, 0), (50, 100)], False),      # Valid triangle
        ([(0, 0), (100, 0), (100, 100), (0, 100)], False),  # Valid square
    ])
    def test_polygon_validation(self, vertices, should_raise):
        """Test polygon validation"""
        if should_raise:
            with pytest.raises(InvalidShapeError):
                Polygon(vertices)
        else:
            polygon = Polygon(vertices)
            assert len(polygon.vertices) == len(vertices)
    
    @pytest.mark.parametrize("vertices,expected_area", [
        ([(0, 0), (100, 0), (100, 100), (0, 100)], 10000),  # Square
        ([(0, 0), (100, 0), (50, 100)], 5000),              # Triangle
        ([(0, 0), (200, 0), (200, 50), (0, 50)], 10000),    # Rectangle
    ])
    def test_area_calculation(self, vertices, expected_area):
        """Test area calculation using shoelace formula"""
        polygon = Polygon(vertices)
        assert abs(polygon.area() - expected_area) < 1e-10
    
    def test_bounding_box(self):
        """Test bounding box calculation"""
        vertices = [(10, 20), (110, 20), (110, 70), (10, 70)]
        polygon = Polygon(vertices)
        bbox = polygon.bounding_box()
        expected = (10, 20, 110, 70)
        assert bbox == expected


# Integration Tests
@pytest.mark.integration
class TestGeometryIntegration:
    """Integration tests for geometry classes"""
    
    @pytest.mark.parametrize("shape_class,args", [
        (Rectangle, (100, 50)),
        (Circle, (25,)),
        (Polygon, ([(0, 0), (50, 0), (50, 50), (0, 50)],)),
    ])
    def test_shape_interface_consistency(self, shape_class, args):
        """Test that all shapes implement required interface"""
        shape = shape_class(*args)
        
        # All shapes should have these methods
        assert hasattr(shape, 'area')
        assert hasattr(shape, 'bounding_box')
        assert hasattr(shape, 'contains_point')
        
        # All methods should be callable
        assert callable(shape.area)
        assert callable(shape.bounding_box)
        assert callable(shape.contains_point)
        
        # Methods should return expected types
        assert isinstance(shape.area(), (int, float))
        assert isinstance(shape.bounding_box(), tuple)
        assert len(shape.bounding_box()) == 4
    
    def test_rectangle_circle_overlap_detection(self):
        """Test overlap detection between rectangle and circle"""
        rect = Rectangle(100, 100, x=0, y=0)
        circle = Circle(30, x=50, y=50)  # Circle inside rectangle
        
        # Circle center should be inside rectangle
        assert rect.contains_point(circle.x, circle.y)
        
        # Rectangle corners outside circle
        assert not circle.contains_point(0, 0)
        assert not circle.contains_point(100, 100)
    
    def test_shape_transformations(self):
        """Test shape transformations don't break invariants"""
        rect = Rectangle(100, 50, x=10, y=20)
        
        # Store original properties
        original_area = rect.area()
        original_width = rect.width
        original_height = rect.height
        
        # Move rectangle
        rect.move(100, 200)
        
        # Area and dimensions should be unchanged
        assert rect.area() == original_area
        assert rect.width == original_width
        assert rect.height == original_height
        
        # Position should be updated
        assert rect.x == 110
        assert rect.y == 220


# Performance Tests
@pytest.mark.performance
class TestGeometryPerformance:
    """Performance tests for geometry operations"""
    
    def test_area_calculation_performance(self):
        """Test that area calculations are fast"""
        import time
        
        # Create many shapes
        rectangles = [Rectangle(i, i+10) for i in range(1, 1001)]
        circles = [Circle(i) for i in range(1, 1001)]
        
        # Time area calculations
        start_time = time.time()
        for rect in rectangles:
            rect.area()
        for circle in circles:
            circle.area()
        elapsed = time.time() - start_time
        
        # Should be very fast (< 0.1 seconds for 2000 calculations)
        assert elapsed < 0.1
    
    def test_containment_check_performance(self):
        """Test that point containment checks are fast"""
        import time
        
        rect = Rectangle(1000, 1000)
        points = [(i, j) for i in range(0, 100, 10) for j in range(0, 100, 10)]
        
        start_time = time.time()
        for x, y in points:
            rect.contains_point(x, y)
        elapsed = time.time() - start_time
        
        # Should be very fast
        assert elapsed < 0.01


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--cov=surface_optimizer.core.geometry"]) 