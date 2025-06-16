"""
Surface Cutting Optimizer Library
=================================

Librería para optimización de corte de superficies bidimensionales.

Funciona con múltiples materiales: vidrio, metal, madera, plástico, tela, etc.

Características principales:
- Múltiples algoritmos de optimización
- Soporte para formas regulares e irregulares
- Visualización de resultados
- Métricas detalladas de eficiencia
- Casos de test con resultados conocidos
"""

__version__ = "1.0.0-beta"
__author__ = "Surface Cutting Team"

# Importaciones principales
from .core.models import Stock, Order, CuttingResult
from .core.optimizer import Optimizer
from .utils.visualization import visualize_cutting_plan
from .utils.metrics import calculate_efficiency, calculate_waste

__all__ = [
    "Stock",
    "Order", 
    "CuttingResult",
    "Optimizer",
    "visualize_cutting_plan",
    "calculate_efficiency",
    "calculate_waste"
] 