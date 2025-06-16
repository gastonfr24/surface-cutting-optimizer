"""
First Fit Algorithm for 2D Cutting Stock Problem
===============================================

El algoritmo First Fit es una heurística greedy que coloca cada pieza en el primer 
stock disponible que tenga suficiente espacio. Es uno de los algoritmos más simples 
y rápidos para el problema de corte de stock 2D.

Características Principales:
- Complejidad temporal: O(n*m) donde n=órdenes, m=stocks
- Complejidad espacial: O(1) adicional
- Estrategia: Greedy, primera opción disponible
- Rotación: Soporta rotación de 90° si está habilitada

Ventajas:
- Extremadamente rápido
- Memoria mínima requerida
- Implementación simple
- Bueno para problemas con muchos stocks similares

Desventajas:
- No optimiza la utilización del material
- Puede desperdiciar mucho espacio
- No considera el orden óptimo de colocación
- Resultado muy dependiente del orden de entrada

Casos de Uso Ideales:
- Prototipado rápido de soluciones
- Problemas con tiempo de cómputo muy limitado
- Stocks abundantes y económicos
- Como baseline para comparar otros algoritmos

Referencias:
- Johnson, D. S. (1973). "Near-optimal bin packing algorithms"
- Coffman Jr, E. G., et al. (1984). "Bin packing: A survey"

Ejemplo de Uso:
```python
from surface_optimizer.algorithms.basic import FirstFitAlgorithm

# Crear algoritmo
algorithm = FirstFitAlgorithm()

# Configurar
config = OptimizationConfig(
    allow_rotation=True,
    max_computation_time=1.0,
    precision_tolerance=0.001
)

# Optimizar
result = algorithm.optimize(stocks, orders, config)
print(f"Eficiencia: {result.efficiency_percentage:.1f}%")
```

Autor: Surface Cutting Optimizer Team
Licencia: MIT
Versión: 1.0.0-beta
"""

from typing import List, Tuple, Optional
from ...core.models import Stock, Order, CuttingResult, OptimizationConfig, PlacedShape
from ...core.geometry import can_fit_in_stock, place_shape_in_stock
from ..base import BaseAlgorithm
import logging

logger = logging.getLogger(__name__)


class FirstFitAlgorithm(BaseAlgorithm):
    """
    First Fit Algorithm para Optimización de Corte 2D
    
    Implementa el algoritmo First Fit que coloca cada pieza en el primer
    stock disponible que tenga suficiente espacio. Es una heurística greedy
    simple y eficiente en tiempo de cómputo.
    
    Attributes:
        name (str): Nombre del algoritmo "First Fit"
        description (str): Descripción detallada del algoritmo
        complexity (str): Complejidad temporal y espacial
        
    Methods:
        optimize: Ejecuta la optimización First Fit
        _try_place_shape: Intenta colocar una forma en un stock
        _find_best_position: Encuentra la mejor posición usando estrategia First Fit
        
    Example:
        >>> algorithm = FirstFitAlgorithm()
        >>> result = algorithm.optimize(stocks, orders, config)
        >>> print(f"Stocks utilizados: {result.total_stock_used}")
    """
    
    def __init__(self):
        """
        Inicializa el algoritmo First Fit.
        
        Configura los metadatos del algoritmo y prepara el estado inicial
        para la optimización.
        """
        super().__init__()
        self.name = "First Fit"
        self.description = """
        Algoritmo greedy que coloca cada pieza en el primer stock disponible
        con suficiente espacio. Optimizado para velocidad sobre eficiencia.
        """
        self.complexity = "Tiempo: O(n*m), Espacio: O(1)"
        
    def optimize(self, stocks: List[Stock], orders: List[Order], 
                config: OptimizationConfig) -> CuttingResult:
        """
        Ejecuta la optimización usando el algoritmo First Fit.
        
        El algoritmo procesa cada orden en secuencia y para cada pieza
        busca el primer stock que tenga espacio suficiente. Si encuentra
        espacio, coloca la pieza; si no, la marca como no cumplida.
        
        Args:
            stocks (List[Stock]): Lista de stocks disponibles para cortar
            orders (List[Order]): Lista de órdenes a cumplir
            config (OptimizationConfig): Configuración de optimización
            
        Returns:
            CuttingResult: Resultado con las piezas colocadas y métricas
            
        Raises:
            ValueError: Si los parámetros de entrada son inválidos
            
        Note:
            El algoritmo no garantiza la solución óptima, pero es muy rápido.
            Para mejores resultados de eficiencia, considere usar algoritmos
            más avanzados como Genetic Algorithm o Best Fit.
            
        Example:
            >>> config = OptimizationConfig(allow_rotation=True)
            >>> result = algorithm.optimize(stocks, orders, config)
            >>> if result.efficiency_percentage > 70:
            ...     print("Buena eficiencia alcanzada")
        """
        logger.info(f"Iniciando optimización First Fit")
        logger.info(f"Stocks: {len(stocks)}, Órdenes: {len(orders)}")
        
        # Inicializar resultado
        result = CuttingResult()
        result.algorithm_used = self.name
        result.algorithm_details = {
            "strategy": "First available position",
            "complexity": self.complexity,
            "rotation_enabled": config.allow_rotation
        }
        
        # Crear copias de trabajo
        available_stocks = stocks.copy()
        remaining_orders = []
        total_shapes_to_place = sum(order.quantity for order in orders)
        shapes_placed = 0
        
        # Procesar cada orden
        for order in orders:
            shapes_placed_for_order = 0
            
            # Intentar colocar cada pieza de la orden
            for i in range(order.quantity):
                placed = False
                
                # Buscar en todos los stocks disponibles (First Fit)
                for stock_idx, stock in enumerate(available_stocks):
                    placement = self._try_place_shape(order, stock, config)
                    
                    if placement:
                        # Colocar la pieza
                        placed_shape = PlacedShape(
                            x=placement[0],
                            y=placement[1], 
                            width=placement[2],
                            height=placement[3],
                            order_id=order.id,
                            stock_id=stock.id,
                            rotated=placement[4] if len(placement) > 4 else False
                        )
                        
                        result.placed_shapes.append(placed_shape)
                        shapes_placed_for_order += 1
                        shapes_placed += 1
                        placed = True
                        
                        logger.debug(f"Pieza colocada en stock {stock.id} en posición ({placement[0]}, {placement[1]})")
                        break
                
                if not placed:
                    logger.debug(f"No se pudo colocar pieza de orden {order.id}")
            
            # Actualizar órdenes restantes
            if shapes_placed_for_order < order.quantity:
                remaining_order = Order(
                    id=order.id,
                    width=order.width,
                    height=order.height,
                    quantity=order.quantity - shapes_placed_for_order,
                    material=order.material,
                    priority=order.priority
                )
                remaining_orders.append(remaining_order)
        
        # Calcular métricas
        result.unfulfilled_orders = remaining_orders
        result.total_stock_used = len([s for s in available_stocks if any(
            ps.stock_id == s.id for ps in result.placed_shapes
        )])
        result.total_orders_fulfilled = len(orders) - len(remaining_orders)
        
        # Calcular eficiencia
        if result.total_stock_used > 0:
            total_stock_area = sum(s.width * s.height for s in stocks[:result.total_stock_used])
            used_area = sum(ps.width * ps.height for ps in result.placed_shapes)
            result.efficiency_percentage = (used_area / total_stock_area) * 100
        else:
            result.efficiency_percentage = 0.0
        
        logger.info(f"Optimización completada:")
        logger.info(f"  - Piezas colocadas: {shapes_placed}/{total_shapes_to_place}")
        logger.info(f"  - Stocks utilizados: {result.total_stock_used}")
        logger.info(f"  - Eficiencia: {result.efficiency_percentage:.1f}%")
        
        return result
    
    def _try_place_shape(self, order: Order, stock: Stock, 
                        config: OptimizationConfig) -> Optional[Tuple[float, float, float, float, bool]]:
        """
        Intenta colocar una forma en un stock usando estrategia First Fit.
        
        Busca la primera posición disponible en el stock donde la pieza
        pueda ser colocada, opcionalmente probando con rotación.
        
        Args:
            order (Order): Orden que contiene las dimensiones de la pieza
            stock (Stock): Stock donde intentar colocar la pieza  
            config (OptimizationConfig): Configuración con opciones de rotación
            
        Returns:
            Optional[Tuple]: (x, y, width, height, rotated) si se puede colocar,
                           None si no hay espacio suficiente
                           
        Note:
            Este método implementa la estrategia "First Fit" buscando desde
            la esquina superior izquierda hacia la derecha y abajo.
        """
        # Obtener posiciones ocupadas en este stock
        occupied_positions = []
        # TODO: Implementar verificación de posiciones ocupadas
        
        # Probar sin rotación
        position = self._find_best_position(
            order.width, order.height, stock, occupied_positions
        )
        if position:
            return (position[0], position[1], order.width, order.height, False)
        
        # Probar con rotación si está habilitada
        if config.allow_rotation and order.width != order.height:
            position = self._find_best_position(
                order.height, order.width, stock, occupied_positions
            )
            if position:
                return (position[0], position[1], order.height, order.width, True)
        
        return None
    
    def _find_best_position(self, width: float, height: float, stock: Stock,
                           occupied_positions: List[Tuple[float, float, float, float]]
                          ) -> Optional[Tuple[float, float]]:
        """
        Encuentra la primera posición disponible (estrategia First Fit).
        
        Escanea el stock desde la esquina superior izquierda buscando
        la primera posición donde la pieza pueda ser colocada sin solaparse.
        
        Args:
            width (float): Ancho de la pieza a colocar
            height (float): Alto de la pieza a colocar
            stock (Stock): Stock donde buscar posición
            occupied_positions (List): Lista de áreas ya ocupadas
            
        Returns:
            Optional[Tuple[float, float]]: Posición (x, y) si se encuentra,
                                         None si no hay espacio
                                         
        Algorithm:
            1. Escanea desde (0,0) hacia la derecha
            2. Cuando llega al borde, baja una fila
            3. Verifica solapamiento con áreas ocupadas
            4. Retorna la primera posición válida encontrada
        """
        step_size = 1.0  # Precisión de búsqueda en unidades de material
        
        # Verificar si cabe en el stock
        if width > stock.width or height > stock.height:
            return None
        
        # Buscar posición disponible (First Fit - primera encontrada)
        for y in range(0, int(stock.height - height + 1), int(step_size)):
            for x in range(0, int(stock.width - width + 1), int(step_size)):
                # Verificar si esta posición está libre
                position_free = True
                for occ_x, occ_y, occ_w, occ_h in occupied_positions:
                    if (x < occ_x + occ_w and x + width > occ_x and
                        y < occ_y + occ_h and y + height > occ_y):
                        position_free = False
                        break
                
                if position_free:
                    return (float(x), float(y))
        
        return None 