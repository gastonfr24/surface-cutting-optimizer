# 🧠 Algoritmos de Optimización

Surface Cutting Optimizer incluye **5 algoritmos especializados** para resolver el problema de corte de stock 2D, cada uno con características únicas adaptadas a diferentes escenarios de uso.

## 📋 **Resumen de Algoritmos**

| Algoritmo | Tipo | Velocidad | Eficiencia | Complejidad | Caso de Uso |
|-----------|------|-----------|------------|-------------|-------------|
| [First Fit](basic/first_fit.md) | Básico | ⚡⚡⚡⚡⚡ | ⭐⭐ | O(n×m) | Prototipado rápido |
| [Best Fit](basic/best_fit.md) | Básico | ⚡⚡⚡⚡ | ⭐⭐⭐ | O(n×m log m) | Balance velocidad/calidad |
| [Bottom Left](basic/bottom_left.md) | Básico | ⚡⚡⚡ | ⭐⭐⭐⭐ | O(n²) | Minimizar desperdicios |
| [Genetic Algorithm](advanced/genetic.md) | Avanzado | ⚡⚡ | ⭐⭐⭐⭐⭐ | O(g×p×n) | Máxima eficiencia |
| [Simulated Annealing](advanced/simulated_annealing.md) | Avanzado | ⚡ | ⭐⭐⭐⭐⭐ | O(i×n) | Problemas complejos |

**Leyenda**: ⚡ = Velocidad, ⭐ = Eficiencia

## 🎯 **Guía de Selección de Algoritmos**

### Para Desarrollo y Prototipado
```python
# Ultra-rápido para pruebas
algorithm = "first_fit"
```

### Para Producción con Balance
```python
# Buena relación velocidad/eficiencia
algorithm = "best_fit"
```

### Para Máxima Eficiencia
```python
# Mejor resultado, más tiempo de cómputo
algorithm = "genetic"
```

### Para Problemas Específicos
```python
# Minimizar desperdicios en esquinas
algorithm = "bottom_left"

# Problemas muy complejos o irregulares
algorithm = "simulated_annealing"
```

## 📊 **Comparación de Rendimiento**

### Benchmarks Típicos (1000 piezas, 50 stocks)

| Algoritmo | Tiempo | Eficiencia | Stocks Usados | Desperdicios |
|-----------|--------|------------|---------------|--------------|
| First Fit | 0.01s | 45-60% | Alto | 40-55% |
| Best Fit | 0.05s | 55-70% | Medio | 30-45% |
| Bottom Left | 0.2s | 65-75% | Medio-Bajo | 25-35% |
| Genetic | 2-10s | 75-90% | Bajo | 10-25% |
| Simulated Annealing | 5-30s | 80-95% | Muy Bajo | 5-20% |

*Resultados varían según el tipo de problema y configuración*

## 🔧 **Configuración Avanzada**

### Auto-Escalado Inteligente
Los algoritmos avanzados incluyen **auto-escalado automático** basado en la complejidad del problema:

```python
# El sistema detecta automáticamente:
# - Tamaño del problema (pequeño/mediano/grande)
# - Ajusta parámetros en tiempo real
# - Optimiza velocidad vs calidad

config = OptimizationConfig(
    auto_scaling=True,  # Habilitado por defecto
    max_computation_time=60,  # Límite de tiempo
    target_efficiency=0.8  # Eficiencia deseada
)
```

### Configuración Manual de Parámetros
```python
# Para control total sobre el comportamiento
config = OptimizationConfig(
    # Algoritmos genéticos
    population_size=50,
    generations=100,
    mutation_rate=0.1,
    
    # Recocido simulado
    initial_temperature=1000,
    cooling_rate=0.95,
    min_temperature=0.1,
    
    # Generales
    allow_rotation=True,
    precision_tolerance=0.001,
    parallel_processing=True
)
```

## 📖 **Documentación Detallada**

### Algoritmos Básicos
- **[First Fit](basic/first_fit.md)** - Algoritmo greedy ultra-rápido
- **[Best Fit](basic/best_fit.md)** - Optimización de ajuste óptimo
- **[Bottom Left](basic/bottom_left.md)** - Estrategia de empaquetado inferior-izquierda

### Algoritmos Avanzados
- **[Genetic Algorithm](advanced/genetic.md)** - Algoritmo evolutivo con auto-escalado
- **[Simulated Annealing](advanced/simulated_annealing.md)** - Optimización por recocido simulado

### Guías Complementarias
- **[Configuración](configuration.md)** - Parámetros y opciones avanzadas
- **[Benchmarks](benchmarks.md)** - Comparativas y casos de prueba
- **[Troubleshooting](troubleshooting.md)** - Solución de problemas comunes

## 🚀 **Inicio Rápido**

```python
from surface_optimizer import SurfaceOptimizer

# Crear optimizador
optimizer = SurfaceOptimizer()

# Datos de ejemplo
orders = [
    {"width": 100, "height": 50, "quantity": 10},
    {"width": 80, "height": 60, "quantity": 5}
]
stock = [
    {"width": 300, "height": 200, "cost": 25.0}
]

# Optimizar con algoritmo automático
result = optimizer.optimize(orders, stock)

# Optimizar con algoritmo específico
result = optimizer.optimize(orders, stock, algorithm='genetic')

# Ver resultados
print(f"Eficiencia: {result.efficiency_percentage:.1f}%")
print(f"Stocks utilizados: {result.total_stock_used}")
```

## 🔗 **Referencias**

- [Instalación y Configuración](../user/quick_start.md)
- [API Reference](../api/README.md)
- [Ejemplos Avanzados](../examples/README.md)
- [Contributing Guidelines](../CONTRIBUTING.md) 