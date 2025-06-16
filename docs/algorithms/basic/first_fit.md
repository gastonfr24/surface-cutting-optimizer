# First Fit Algorithm

## 📖 **Descripción General**

El algoritmo **First Fit** es una heurística greedy que resuelve el problema de corte de stock 2D colocando cada pieza en el **primer stock disponible** que tenga suficiente espacio. Es el algoritmo más simple y rápido de la librería.

## 🔬 **Características Técnicas**

- **Tipo**: Algoritmo greedy determinístico
- **Complejidad Temporal**: O(n × m) donde n = número de piezas, m = número de stocks
- **Complejidad Espacial**: O(1) adicional
- **Estrategia**: Primera posición disponible encontrada
- **Optimización**: Velocidad sobre eficiencia

## ⚡ **Ventajas y Desventajas**

### ✅ **Ventajas**
- **Ultra-rápido**: Ideal para prototipos y pruebas
- **Memoria mínima**: No requiere estructuras de datos complejas  
- **Determinístico**: Siempre produce el mismo resultado
- **Simple**: Fácil de entender y debuggear
- **Escalable**: Rendimiento predecible en problemas grandes

### ❌ **Desventajas**
- **Baja eficiencia**: No optimiza el uso del material
- **Dependiente del orden**: Resultado varía según orden de entrada
- **Sin lookahead**: No considera posiciones futuras
- **Desperdicios altos**: Puede dejar espacios inutilizables

## 🎯 **Casos de Uso Ideales**

### ✅ **Recomendado Para:**
- **Prototipado rápido** de soluciones
- **Baseline** para comparar otros algoritmos
- **Tiempo crítico** con restricciones < 100ms
- **Stocks abundantes** y económicos
- **Desarrollo y testing** de aplicaciones

### ❌ **No Recomendado Para:**
- **Producción industrial** con costos altos de material
- **Optimización final** de layouts comerciales
- **Stocks limitados** o costosos
- **Aplicaciones** que requieren máxima eficiencia

## 🔧 **Configuración y Uso**

### Uso Básico
```python
from surface_optimizer.algorithms.basic import FirstFitAlgorithm
from surface_optimizer.core.models import OptimizationConfig

# Crear algoritmo
algorithm = FirstFitAlgorithm()

# Configuración básica
config = OptimizationConfig(
    allow_rotation=True,
    precision_tolerance=0.001
)

# Ejecutar optimización
result = algorithm.optimize(stocks, orders, config)

print(f"Algoritmo: {result.algorithm_used}")
print(f"Eficiencia: {result.efficiency_percentage:.1f}%")
print(f"Piezas colocadas: {len(result.placed_shapes)}")
```

### Configuración Avanzada
```python
# Para máximo rendimiento
config = OptimizationConfig(
    allow_rotation=False,  # Sin rotación = más rápido
    precision_tolerance=1.0,  # Menor precisión = más rápido
    max_computation_time=0.1,  # Límite de tiempo
    early_termination=True  # Parar en primera solución
)

# Para mejor calidad (dentro de First Fit)
config = OptimizationConfig(
    allow_rotation=True,  # Explorar rotaciones
    precision_tolerance=0.001,  # Alta precisión
    sort_orders="area_desc",  # Ordenar por área descendente
    sort_stocks="area_asc"  # Stocks pequeños primero
)
```

## 📊 **Rendimiento y Benchmarks**

### Benchmarks Típicos

| Problema | Piezas | Stocks | Tiempo | Eficiencia | Stocks Usados |
|----------|--------|--------|--------|------------|---------------|
| Pequeño | 10-50 | 5-10 | 0.001s | 45-60% | 70-90% |
| Mediano | 100-500 | 10-50 | 0.01s | 40-55% | 60-80% |
| Grande | 1000+ | 50+ | 0.1s | 35-50% | 50-70% |

### Factores que Afectan el Rendimiento

**⬆️ Mejora eficiencia cuando:**
- Piezas similares en tamaño
- Stocks uniformes
- Orden de entrada optimizado
- Proporción alta de stocks vs piezas

**⬇️ Reduce eficiencia cuando:**
- Piezas muy variadas en tamaño
- Stocks heterogéneos  
- Orden aleatorio de entrada
- Pocas opciones de stock

## 🛠️ **Algoritmo Interno**

### Pseudocódigo
```
ALGORITHM FirstFit(stocks, orders):
    FOR each order in orders:
        FOR each piece in order.quantity:
            placed = False
            FOR each stock in stocks:
                IF CanPlace(piece, stock):
                    Place(piece, stock)
                    placed = True
                    BREAK
            IF NOT placed:
                AddToUnfulfilled(piece)
    RETURN result
```

### Estrategia de Colocación
1. **Escaneo izquierda-derecha, arriba-abajo**
2. **Primera posición válida** encontrada
3. **Sin backtracking** ni optimización local
4. **Verificación simple** de solapamiento

## 📈 **Casos de Prueba y Ejemplos**

### Ejemplo 1: Caso Ideal (Alta Eficiencia)
```python
# Piezas uniformes en stocks uniformes
orders = [
    {"width": 100, "height": 100, "quantity": 9}  # 9 cuadrados
]
stocks = [
    {"width": 300, "height": 300, "cost": 10}  # Caben exactamente 9
]

# Resultado esperado: ~100% eficiencia
result = algorithm.optimize(stocks, orders, config)
# Eficiencia: ~100%, Stocks: 1
```

### Ejemplo 2: Caso Problemático (Baja Eficiencia)
```python
# Piezas variadas que generan fragmentación
orders = [
    {"width": 250, "height": 150, "quantity": 1},  # Pieza grande
    {"width": 25, "height": 25, "quantity": 10}    # Piezas pequeñas
]
stocks = [
    {"width": 300, "height": 200, "cost": 15}
]

# Resultado esperado: ~40-50% eficiencia
result = algorithm.optimize(stocks, orders, config)
# Eficiencia: ~45%, fragmentación alta
```

### Ejemplo 3: Optimización del Orden de Entrada
```python
# Mejor resultado ordenando por área descendente
orders_sorted = sorted(orders, key=lambda x: x["width"] * x["height"], reverse=True)

result1 = algorithm.optimize(stocks, orders, config)        # Orden original
result2 = algorithm.optimize(stocks, orders_sorted, config) # Orden optimizado

print(f"Original: {result1.efficiency_percentage:.1f}%")
print(f"Ordenado: {result2.efficiency_percentage:.1f}%")
# Típicamente: Ordenado > Original en 5-15%
```

## 🔗 **Integration con Otros Componentes**

### Con Sistema de Reportes
```python
from surface_optimizer.reporting import ReportGenerator

# Generar reporte detallado
report = ReportGenerator()
report.generate_cutting_plan_report(result, format="html")
report.generate_algorithm_comparison([result], format="pdf")
```

### Con Validación
```python
from surface_optimizer.core.validators import ValidationResult

# Validar resultado
validator = ValidationResult()
validation = validator.validate_cutting_result(result)

if validation.has_overlaps:
    print("⚠️ Advertencia: Se detectaron solapamientos")
if validation.efficiency_below_threshold:
    print("💡 Sugerencia: Considere usar Best Fit o Genetic Algorithm")
```

## 📚 **Referencias y Lecturas Adicionales**

### Papers Académicos
- Johnson, D. S. (1973). "Near-optimal bin packing algorithms". MIT
- Coffman Jr, E. G., et al. (1984). "Bin packing: A survey". Operations Research
- Baker, B. S. (1985). "A new proof for the first-fit decreasing bin-packing algorithm"

### Libros Recomendados
- "Introduction to Algorithms" - Cormen, Leiserson, Rivest, Stein (Capítulo sobre Greedy Algorithms)
- "Algorithm Design" - Kleinberg, Tardos
- "Approximation Algorithms" - Vazirani

### Recursos Online
- [Cutting Stock Problem - Wikipedia](https://en.wikipedia.org/wiki/Cutting_stock_problem)
- [Bin Packing Algorithms - GeeksforGeeks](https://www.geeksforgeeks.org/bin-packing-problem-minimize-number-of-used-bins/)

## 🔄 **Ver También**

- **[Best Fit Algorithm](best_fit.md)** - Mejor alternativa con similar velocidad
- **[Bottom Left Algorithm](bottom_left.md)** - Más eficiente, algo más lento
- **[Genetic Algorithm](../advanced/genetic.md)** - Máxima eficiencia
- **[Comparación de Algoritmos](../README.md#comparación-de-rendimiento)** - Tabla comparativa completa 