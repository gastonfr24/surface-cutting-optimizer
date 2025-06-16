"""
Geometric shapes and utilities for Surface Cutting Optimizer
"""

import math
from abc import ABC, abstractmethod
from typing import List, Tuple, Union
import numpy as np
from .exceptions import InvalidDimensionsError, InvalidShapeError


class Shape(ABC):
    """Abstract base class for all geometric shapes"""
    
    def __init__(self, x: float = 0, y: float = 0, rotation: float = 0):
        self.x = x
        self.y = y
        self.rotation = rotation % 360
    
    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape"""
        pass
    
    @abstractmethod
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Return bounding box as (min_x, min_y, max_x, max_y)"""
        pass
    
    @abstractmethod
    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside the shape"""
        pass
    
    @abstractmethod
    def overlaps(self, other: 'Shape') -> bool:
        """Check if this shape overlaps with another shape"""
        pass
    
    def move(self, dx: float, dy: float):
        """Move the shape by (dx, dy)"""
        self.x += dx
        self.y += dy
    
    def rotate(self, angle: float):
        """Rotate the shape by angle degrees"""
        self.rotation = (self.rotation + angle) % 360


class Rectangle(Shape):
    """Rectangle shape"""
    
    def __init__(self, width: float, height: float, x: float = 0, y: float = 0, rotation: float = 0):
        if width <= 0 or height <= 0:
            raise InvalidDimensionsError(f"Rectangle dimensions must be positive: {width}x{height}")
        
        super().__init__(x, y, rotation)
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Return bounding box considering rotation"""
        if self.rotation == 0:
            return (self.x, self.y, self.x + self.width, self.y + self.height)
        
        # For rotated rectangle, calculate all corners and find bounding box
        corners = self._get_corners()
        xs = [corner[0] for corner in corners]
        ys = [corner[1] for corner in corners]
        
        return (min(xs), min(ys), max(xs), max(ys))
    
    def _get_corners(self) -> List[Tuple[float, float]]:
        """Get the four corners of the rectangle considering rotation"""
        if self.rotation == 0:
            return [
                (self.x, self.y),
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)
            ]
        
        # Rotate around center
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        
        # Half dimensions
        hw = self.width / 2
        hh = self.height / 2
        
        # Rotation in radians
        rad = math.radians(self.rotation)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        # Calculate rotated corners
        corners = []
        for dx, dy in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
            # Rotate point around origin
            rx = dx * cos_r - dy * sin_r
            ry = dx * sin_r + dy * cos_r
            # Translate to rectangle center
            corners.append((cx + rx, cy + ry))
        
        return corners
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside rectangle"""
        if self.rotation == 0:
            return (self.x <= x <= self.x + self.width and 
                    self.y <= y <= self.y + self.height)
        
        # For rotated rectangle, transform point to local coordinate system
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        
        # Translate to origin
        px = x - cx
        py = y - cy
        
        # Rotate point by negative angle
        rad = math.radians(-self.rotation)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        local_x = px * cos_r - py * sin_r
        local_y = px * sin_r + py * cos_r
        
        # Check if in local rectangle bounds
        return (-self.width/2 <= local_x <= self.width/2 and 
                -self.height/2 <= local_y <= self.height/2)
    
    def fits_in_rectangle(self, container_width: float, container_height: float) -> bool:
        """Check if this rectangle fits in a container"""
        if self.rotation == 0:
            return (self.width <= container_width and 
                    self.height <= container_height)
        
        # For rotated rectangle, check both orientations
        bbox = self.bounding_box()
        bbox_width = bbox[2] - bbox[0]
        bbox_height = bbox[3] - bbox[1]
        
        return (bbox_width <= container_width and 
                bbox_height <= container_height)
    
    def overlaps(self, other: 'Shape') -> bool:
        """Check overlap using Separating Axis Theorem (SAT)"""
        if isinstance(other, Rectangle):
            return self._overlaps_rectangle(other)
        elif isinstance(other, Circle):
            return other.overlaps(self)  # Delegate to circle's implementation
        else:
            # Generic bounding box check for other shapes
            bbox1 = self.bounding_box()
            bbox2 = other.bounding_box()
            return not (bbox1[2] < bbox2[0] or bbox2[2] < bbox1[0] or
                       bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    
    def _overlaps_rectangle(self, other: 'Rectangle') -> bool:
        """Check overlap with another rectangle using SAT"""
        # Get corners of both rectangles
        corners1 = self._get_corners()
        corners2 = other._get_corners()
        
        # Get axes to test (edges of both rectangles)
        axes = []
        
        # Add axes from first rectangle
        for i in range(4):
            edge = (corners1[(i+1)%4][0] - corners1[i][0], 
                   corners1[(i+1)%4][1] - corners1[i][1])
            # Perpendicular to edge
            axis = (-edge[1], edge[0])
            # Normalize
            length = math.sqrt(axis[0]**2 + axis[1]**2)
            if length > 0:
                axes.append((axis[0]/length, axis[1]/length))
        
        # Add axes from second rectangle
        for i in range(4):
            edge = (corners2[(i+1)%4][0] - corners2[i][0], 
                   corners2[(i+1)%4][1] - corners2[i][1])
            # Perpendicular to edge
            axis = (-edge[1], edge[0])
            # Normalize
            length = math.sqrt(axis[0]**2 + axis[1]**2)
            if length > 0:
                axes.append((axis[0]/length, axis[1]/length))
        
        # Test each axis
        for axis in axes:
            # Project both rectangles onto axis
            proj1 = [corner[0] * axis[0] + corner[1] * axis[1] for corner in corners1]
            proj2 = [corner[0] * axis[0] + corner[1] * axis[1] for corner in corners2]
            
            min1, max1 = min(proj1), max(proj1)
            min2, max2 = min(proj2), max(proj2)
            
            # Check for separation
            if max1 < min2 or max2 < min1:
                return False  # Separating axis found
        
        return True  # No separating axis found, they overlap
    
    def __str__(self):
        return f"Rectangle({self.width}x{self.height} at {self.x},{self.y}, rot={self.rotation}°)"


class Circle(Shape):
    """Circle shape"""
    
    def __init__(self, radius: float, x: float = 0, y: float = 0):
        if radius <= 0:
            raise InvalidDimensionsError(f"Circle radius must be positive: {radius}")
        
        super().__init__(x, y, 0)  # Circles don't rotate
        self.radius = radius
    
    def area(self) -> float:
        return math.pi * self.radius ** 2
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        return (self.x - self.radius, self.y - self.radius,
                self.x + self.radius, self.y + self.radius)
    
    def contains_point(self, x: float, y: float) -> bool:
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance <= self.radius
    
    def fits_in_rectangle(self, container_width: float, container_height: float) -> bool:
        """Check if circle fits in rectangle"""
        return (2 * self.radius <= container_width and 
                2 * self.radius <= container_height)
    
    def overlaps(self, other: 'Shape') -> bool:
        """Check overlap with another shape"""
        if isinstance(other, Circle):
            # Circle-circle overlap
            distance = math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)
            return distance <= (self.radius + other.radius)
        
        elif isinstance(other, Rectangle):
            # Circle-rectangle overlap
            return self._overlaps_rectangle(other)
        
        else:
            # Generic bounding box check
            bbox1 = self.bounding_box()
            bbox2 = other.bounding_box()
            return not (bbox1[2] < bbox2[0] or bbox2[2] < bbox1[0] or
                       bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    
    def _overlaps_rectangle(self, rect: Rectangle) -> bool:
        """Check if circle overlaps with rectangle"""
        # Find closest point on rectangle to circle center
        rect_corners = rect._get_corners()
        
        # For rotated rectangle, this is complex. Use simplified approach:
        # Check if circle center is inside rectangle or if circle intersects any edge
        
        if rect.contains_point(self.x, self.y):
            return True
        
        # Check distance to each edge
        for i in range(4):
            p1 = rect_corners[i]
            p2 = rect_corners[(i+1) % 4]
            
            # Distance from circle center to line segment
            dist = self._point_to_segment_distance(self.x, self.y, p1[0], p1[1], p2[0], p2[1])
            
            if dist <= self.radius:
                return True
        
        return False
    
    def _point_to_segment_distance(self, px: float, py: float, 
                                 x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate distance from point to line segment"""
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return math.sqrt(A * A + B * B)
        
        param = dot / len_sq
        
        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D
        
        dx = px - xx
        dy = py - yy
        return math.sqrt(dx * dx + dy * dy)
    
    def __str__(self):
        return f"Circle(r={self.radius} at {self.x},{self.y})"


class Polygon(Shape):
    """Polygon shape defined by vertices"""
    
    def __init__(self, vertices: List[Tuple[float, float]], x: float = 0, y: float = 0, rotation: float = 0):
        if len(vertices) < 3:
            raise InvalidShapeError(f"Polygon must have at least 3 vertices, got {len(vertices)}")
        
        super().__init__(x, y, rotation)
        self.vertices = vertices
    
    def area(self) -> float:
        """Calculate area using shoelace formula"""
        n = len(self.vertices)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i][0] * self.vertices[j][1]
            area -= self.vertices[j][0] * self.vertices[i][1]
        
        return abs(area) / 2.0
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Get bounding box of polygon"""
        transformed_vertices = self._get_transformed_vertices()
        
        xs = [v[0] for v in transformed_vertices]
        ys = [v[1] for v in transformed_vertices]
        
        return (min(xs), min(ys), max(xs), max(ys))
    
    def _get_transformed_vertices(self) -> List[Tuple[float, float]]:
        """Get vertices transformed by position and rotation"""
        if self.rotation == 0:
            return [(v[0] + self.x, v[1] + self.y) for v in self.vertices]
        
        # Apply rotation and translation
        rad = math.radians(self.rotation)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        transformed = []
        for vx, vy in self.vertices:
            # Rotate
            rx = vx * cos_r - vy * sin_r
            ry = vx * sin_r + vy * cos_r
            # Translate
            transformed.append((rx + self.x, ry + self.y))
        
        return transformed
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside polygon using ray casting"""
        vertices = self._get_transformed_vertices()
        n = len(vertices)
        inside = False
        
        p1x, p1y = vertices[0]
        for i in range(1, n + 1):
            p2x, p2y = vertices[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def overlaps(self, other: 'Shape') -> bool:
        """Check overlap with another shape"""
        # Simplified: use bounding box check
        bbox1 = self.bounding_box()
        bbox2 = other.bounding_box()
        return not (bbox1[2] < bbox2[0] or bbox2[2] < bbox1[0] or
                   bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    
    def __str__(self):
        return f"Polygon({len(self.vertices)} vertices at {self.x},{self.y}, rot={self.rotation}°)" 