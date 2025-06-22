"""
Core module for Surface Cutting Optimizer
Contains fundamental classes and utilities
"""

from .models import Stock, Order, CuttingResult, PlacedShape, MaterialType, Priority, OptimizationConfig, OrderSortCriteria
from .geometry import Shape, Rectangle, Circle, Polygon
from .optimizer import Optimizer
from .exceptions import (
    SurfaceOptimizerError,
    InvalidDimensionsError,
    InvalidShapeError,
    InsufficientStockError,
    OptimizationError
)

__all__ = [
    "Stock",
    "Order", 
    "CuttingResult",
    "PlacedShape",
    "MaterialType",
    "Priority",
    "OptimizationConfig",
    "OrderSortCriteria",
    "Shape",
    "Rectangle",
    "Circle", 
    "Polygon",
    "Optimizer",
    "SurfaceOptimizerError",
    "InvalidDimensionsError",
    "InvalidShapeError",
    "InsufficientStockError",
    "OptimizationError"
] 