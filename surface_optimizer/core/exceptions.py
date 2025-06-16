"""
Custom exceptions for Surface Cutting Optimizer
"""


class SurfaceOptimizerError(Exception):
    """Base exception for all surface cutting optimizer errors"""
    pass


class InvalidDimensionsError(SurfaceOptimizerError):
    """Raised when dimensions are invalid (negative, zero, etc.)"""
    pass


class InvalidShapeError(SurfaceOptimizerError):
    """Raised when a shape is invalid or malformed"""
    pass


class InsufficientStockError(SurfaceOptimizerError):
    """Raised when there's not enough stock to fulfill orders"""
    pass


class OptimizationError(SurfaceOptimizerError):
    """Raised when optimization process fails"""
    pass


class AlgorithmError(SurfaceOptimizerError):
    """Raised when an algorithm encounters an error"""
    pass


class ValidationError(SurfaceOptimizerError):
    """Raised when validation fails"""
    pass 