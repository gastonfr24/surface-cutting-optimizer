"""
Surface Cutting Optimizer - Advanced 2D Cutting Stock Library

Library for bidimensional surface cutting optimization.

Key Features:
- Multiple optimization algorithms
- Automatic parameter scaling  
- Result visualization
- Professional reporting
- Test cases with known results

Version: 1.0.0-beta
"""

from .core.optimizer import Optimizer as SurfaceOptimizer
from .core.models import OptimizationConfig, OptimizationResult
from .utils.visualization import CuttingVisualizer
from .reporting.report_generator import ReportGenerator

__version__ = "1.0.0-beta"
__author__ = "Surface Cutting Optimizer Team"
__license__ = "MIT"

# Package information
__title__ = "Surface Cutting Optimizer"
__description__ = "Advanced 2D cutting stock optimization library"
__url__ = "https://github.com/gastonfr24/surface-cutting-optimizer"

# Export main classes
__all__ = [
    "SurfaceOptimizer",
    "OptimizationConfig", 
    "OptimizationResult",
    "CuttingVisualizer",
    "ReportGenerator"
] 