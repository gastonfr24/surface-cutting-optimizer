# Configuración Avanzada de Algoritmos

## 📋 **OptimizationConfig - Referencia Completa**

La clase `OptimizationConfig` permite personalizar el comportamiento de todos los algoritmos de optimización. Esta guía cubre todas las opciones disponibles y sus casos de uso.

## 🚀 **Configuración Básica**

```python
from surface_optimizer.core.models import OptimizationConfig

# Configuración mínima (usa valores por defecto)
config = OptimizationConfig()

# Configuración básica personalizada
config = OptimizationConfig(
    allow_rotation=True,
    max_computation_time=30,
    precision_tolerance=0.001
)
```

## ⚙️ **Parámetros Generales**

### Comportamiento Básico
```python
config = OptimizationConfig(
    # Rotación de piezas
    allow_rotation=True,           # Permitir rotación de 90°
    
    # Límites de tiempo
    max_computation_time=60,       # Tiempo máximo en segundos
    
    # Precisión
    precision_tolerance=0.001,     # Tolerancia para cálculos de punto flotante
    
    # Ordenamiento
    sort_orders_by="area_desc",    # Ordenar órdenes: area_desc, area_asc, priority, none
    sort_stocks_by="cost_asc",     # Ordenar stocks: cost_asc, cost_desc, area_asc, area_desc
    
    # Validación
    validate_inputs=True,          # Validar entradas antes de optimizar
    strict_mode=False             # Modo estricto para errores
)
```

### Control de Calidad
```python
config = OptimizationConfig(
    # Objetivos de eficiencia
    target_efficiency=0.8,         # Parar si se alcanza esta eficiencia
    min_acceptable_efficiency=0.5,  # Eficiencia mínima aceptable
    
    # Manejo de órdenes
    allow_partial_fulfillment=False,  # Permitir cumplimiento parcial
    prioritize_orders=True,           # Respetar prioridades de órdenes
    group_by_material=True,           # Agrupar por tipo de material
    
    # Optimización de costos
    optimize_for_cost=True,           # Minimizar costos además de desperdicios
    cost_weight=0.3                  # Peso de costos vs eficiencia (0-1)
)
```

## 🧬 **Configuración para Algoritmo Genético**

### Auto-Escalado (Recomendado)
```python
config = OptimizationConfig(
    # Auto-escalado inteligente
    auto_scaling=True,              # Habilitar auto-escalado
    problem_size_threshold_small=50,  # ≤50 = problema pequeño
    problem_size_threshold_medium=200, # ≤200 = problema mediano
    
    # Parámetros auto-escalados se calculan automáticamente:
    # - population_size: 10-100 según tamaño
    # - generations: 20-200 según tamaño
    # - mutation_rate: 0.05-0.2 según convergencia
)
```

### Configuración Manual Completa
```python
config = OptimizationConfig(
    # Población
    population_size=50,             # Tamaño de población
    generations=100,                # Número máximo de generaciones
    
    # Operadores genéticos
    crossover_rate=0.8,            # Probabilidad de cruce (0-1)
    mutation_rate=0.1,             # Probabilidad de mutación (0-1)
    elite_percentage=0.2,          # Porcentaje de élite (0-1)
    
    # Selección
    selection_method="tournament",   # tournament, roulette, rank
    tournament_size=3,              # Tamaño de torneo (si aplica)
    
    # Convergencia
    convergence_threshold=0.01,     # Umbral de convergencia
    stagnation_limit=20,           # Generaciones sin mejora para parar
    
    # Inicialización
    initialization_strategy="mixed", # greedy, random, mixed
    seed_with_heuristics=True,      # Usar heurísticas en población inicial
    
    # Optimizaciones avanzadas
    parallel_evaluation=True,       # Evaluación paralela de individuos
    adaptive_parameters=True,       # Parámetros adaptativos
    early_stopping=True,           # Parada temprana inteligente
    
    # Diversidad
    maintain_diversity=True,        # Mantener diversidad en población
    diversity_threshold=0.1,        # Umbral mínimo de diversidad
    restart_on_stagnation=False    # Reiniciar población si se estanca
)
```

### Configuraciones Predefinidas por Escenario
```python
# Para desarrollo/testing (velocidad máxima)
config_fast = OptimizationConfig(
    population_size=10,
    generations=20,
    max_computation_time=5,
    target_efficiency=0.7
)

# Para producción (balance)
config_production = OptimizationConfig(
    auto_scaling=True,
    max_computation_time=30,
    target_efficiency=0.8,
    early_stopping=True
)

# Para investigación (máxima calidad)
config_research = OptimizationConfig(
    population_size=100,
    generations=500,
    max_computation_time=300,
    target_efficiency=0.95,
    convergence_threshold=0.001
)
```

## 🌡️ **Configuración para Simulated Annealing**

### Parámetros de Temperatura
```python
config = OptimizationConfig(
    # Temperatura inicial
    initial_temperature=1000,       # Temperatura de inicio
    
    # Enfriamiento
    cooling_rate=0.95,             # Tasa de enfriamiento (0-1)
    cooling_schedule="exponential", # exponential, linear, logarithmic
    
    # Temperatura final
    min_temperature=0.1,           # Temperatura mínima
    
    # Iteraciones
    max_iterations=10000,          # Iteraciones máximas
    iterations_per_temperature=100, # Iteraciones por nivel de temperatura
    
    # Aceptación
    acceptance_threshold=0.1        # Umbral de aceptación de soluciones peores
)
```

### Auto-Escalado para SA
```python
config = OptimizationConfig(
    auto_scaling=True,
    
    # Los siguientes se calculan automáticamente:
    # - initial_temperature: 100-2000 según complejidad
    # - max_iterations: 1000-50000 según tamaño
    # - cooling_rate: 0.9-0.99 según convergencia deseada
    
    max_computation_time=60,       # Límite de tiempo total
    target_efficiency=0.85         # Objetivo de eficiencia
)
```

## 📊 **Configuración de Reportes y Logging**

### Logging Detallado
```python
config = OptimizationConfig(
    # Logging
    enable_logging=True,           # Habilitar logs
    log_level="INFO",             # DEBUG, INFO, WARNING, ERROR
    log_to_file=True,             # Guardar logs en archivo
    log_directory="logs/",        # Directorio de logs
    
    # Progreso
    show_progress=True,           # Mostrar barra de progreso
    progress_update_interval=10,   # Actualizar cada N iteraciones
    
    # Métricas detalladas
    track_detailed_metrics=True,   # Métricas detalladas
    save_intermediate_results=False, # Guardar resultados intermedios
    
    # Debugging
    debug_mode=False,             # Modo debug con información extra
    validate_each_step=False      # Validar en cada paso (muy lento)
)
```

### Configuración de Visualización
```python
config = OptimizationConfig(
    # Generación automática de visualizaciones
    generate_visualization=True,    # Crear imágenes automáticamente
    visualization_format="png",    # png, pdf, svg
    visualization_dpi=300,         # Resolución de imágenes
    
    # Directorios de salida
    output_directory="results/",   # Directorio base de resultados
    images_directory="images/",    # Subdirectorio para imágenes
    reports_directory="reports/",  # Subdirectorio para reportes
    
    # Contenido de visualizaciones
    show_stock_ids=True,          # Mostrar IDs de stocks
    show_dimensions=True,         # Mostrar dimensiones
    show_efficiency_text=True,    # Mostrar texto de eficiencia
    color_by_order=True          # Colorear por orden
)
```

## 🎯 **Configuraciones Especializadas por Industria**

### Industria del Vidrio
```python
config_glass = OptimizationConfig(
    # Vidrio es frágil, minimizar cortes
    optimize_for_cost=True,
    cost_weight=0.5,
    
    # Precisión alta para medidas exactas
    precision_tolerance=0.1,
    
    # Sin rotación (patrones direccionales)
    allow_rotation=False,
    
    # Agrupar por grosor/tipo
    group_by_material=True,
    
    # Eficiencia alta necesaria
    target_efficiency=0.85
)
```

### Carpintería
```python
config_wood = OptimizationConfig(
    # Madera permite rotación
    allow_rotation=True,
    
    # Optimizar por costo de material
    optimize_for_cost=True,
    cost_weight=0.4,
    
    # Cumplimiento completo de órdenes
    allow_partial_fulfillment=False,
    
    # Tiempo razonable para producción
    max_computation_time=45,
    target_efficiency=0.8
)
```

### Metalmecánica
```python
config_metal = OptimizationConfig(
    # Precisión industrial alta
    precision_tolerance=0.01,
    
    # Material costoso, máxima eficiencia
    target_efficiency=0.9,
    optimize_for_cost=True,
    cost_weight=0.6,
    
    # Tiempo suficiente para optimización
    max_computation_time=120,
    
    # Validación estricta
    strict_mode=True,
    validate_inputs=True
)
```

### Textil/Confección
```python
config_textile = OptimizationConfig(
    # Patrones pueden rotarse
    allow_rotation=True,
    
    # Muchas piezas pequeñas
    sort_orders_by="area_desc",
    
    # Optimización rápida para volumen alto
    max_computation_time=15,
    target_efficiency=0.75,
    
    # Cumplimiento parcial aceptable
    allow_partial_fulfillment=True
)
```

## 🔍 **Validación y Debugging de Configuración**

### Validar Configuración
```python
def validate_config(config):
    """Validar que la configuración sea coherente"""
    issues = []
    
    if config.crossover_rate + config.mutation_rate > 1.0:
        issues.append("Suma de crossover_rate y mutation_rate > 1.0")
    
    if config.target_efficiency > 1.0:
        issues.append("target_efficiency no puede ser > 1.0")
    
    if config.population_size < 5:
        issues.append("population_size muy pequeño (mín. 5)")
    
    return issues

# Uso
issues = validate_config(config)
if issues:
    print("⚠️ Problemas de configuración:", issues)
```

### Configuración de Debugging
```python
config_debug = OptimizationConfig(
    # Máximo detalle para debugging
    debug_mode=True,
    log_level="DEBUG",
    track_detailed_metrics=True,
    validate_each_step=True,
    save_intermediate_results=True,
    
    # Parámetros pequeños para testing rápido
    population_size=10,
    generations=20,
    max_computation_time=10
)
```

## 🔗 **Referencias**

- **[Genetic Algorithm](advanced/genetic.md)** - Configuración específica de GA
- **[Simulated Annealing](advanced/simulated_annealing.md)** - Configuración específica de SA
- **[API Reference](../api/README.md)** - Documentación completa de OptimizationConfig
- **[Troubleshooting](troubleshooting.md)** - Solución de problemas de configuración 