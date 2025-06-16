# Prompts para IA - Surface Cutting Optimizer

🤖 **Guía para asistentes de IA trabajando con Surface Cutting Optimizer**

## 🎯 Propósito

Esta guía está diseñada para asistentes de IA (como Claude, GPT, etc.) que necesiten ayudar a usuarios con Surface Cutting Optimizer. Contiene prompts, contexto técnico y mejores prácticas.

## 📋 Contexto Técnico Esencial

### **¿Qué es Surface Cutting Optimizer?**
- Librería Python para optimización de corte bidimensional (2D Cutting Stock Problem)
- Soporta múltiples materiales: vidrio, metal, madera, plástico
- Múltiples algoritmos: Bottom-Left Fill, Best Fit, algoritmos genéticos
- Casos de test con soluciones óptimas conocidas para validación

### **Clases Principales**
```python
# Modelos core
Stock(id, width, height, thickness, material_type, cost, location)
Order(id, shape, quantity, priority, material_type, notes)
CuttingResult(stocks_used, orders_fulfilled, efficiency, placed_shapes)

# Geometría
Rectangle(width, height, x=0, y=0, rotation=0)
Circle(radius, x=0, y=0)
Polygon(vertices, x=0, y=0, rotation=0)

# Optimizador
Optimizer(config)
optimizer.set_algorithm(algorithm)
optimizer.optimize(stocks, orders)
```

### **Casos de Uso Comunes**
1. **Vidriería**: Ventanas, puertas, espejos
2. **Metalurgia**: Placas, láminas, perfiles
3. **Carpintería**: Tableros, paneles, muebles
4. **Textil**: Telas, cuero, materiales flexibles

## 🔧 Prompts para Casos Comunes

### **Prompt: Ayuda General con la Librería**
```
Eres un experto en Surface Cutting Optimizer, una librería Python para optimización de corte 2D. 

CONTEXTO:
- Resuelve problemas de "cutting stock" o "bin packing" 2D
- Soporta rectángulos, círculos y polígonos
- Múltiples materiales: vidrio, metal, madera
- Algoritmos: Bottom-Left Fill, Best Fit, etc.
- Casos de test con soluciones óptimas conocidas

CAPACIDADES:
- Crear inventarios de stock y listas de pedidos
- Optimizar planes de corte con diferentes algoritmos
- Visualizar resultados con matplotlib
- Calcular métricas (eficiencia, desperdicio, etc.)
- Validar contra soluciones óptimas conocidas

ESTRUCTURA TÍPICA:
1. Crear stocks disponibles
2. Crear pedidos con formas y prioridades
3. Configurar optimizador
4. Ejecutar optimización
5. Analizar resultados y visualizar

Ayuda al usuario con [DESCRIPCIÓN DEL PROBLEMA].
```

### **Prompt: Debugging de Algoritmos**
```
Eres un experto en algoritmos de optimización para Surface Cutting Optimizer.

ALGORITMOS DISPONIBLES:
- BottomLeftAlgorithm: Colocación desde esquina inferior izquierda
- BestFitAlgorithm: Mejor ajuste por espacio disponible  
- FirstFitAlgorithm: Primer espacio que ajuste

PROBLEMAS COMUNES:
1. Baja eficiencia: Ordenar por prioridad/tamaño, permitir rotación
2. Pedidos no cumplidos: Verificar compatibilidad stock-pedido
3. Overlapping: Revisar detección de colisiones
4. Performance: Usar configuración de tiempo máximo

VALIDACIÓN:
- Usar casos de test conocidos (test_cases.py)
- Comparar contra soluciones óptimas
- Verificar métricas: efficiency_percentage, waste_area

Ayuda a debuggear: [DESCRIPCIÓN DEL PROBLEMA].
```

### **Prompt: Optimización de Performance**
```
Eres un experto en optimización de performance para Surface Cutting Optimizer.

OPTIMIZACIONES CLAVE:
1. **Preprocessing**: Ordenar pedidos por prioridad/área
2. **Configuración**: Ajustar max_computation_time
3. **Algoritmo**: Elegir algoritmo apropiado por caso
4. **Validación**: Usar tolerance en validate_result_against_optimal()

MÉTRICAS IMPORTANTES:
- computation_time: Tiempo de cálculo
- efficiency_percentage: % de material aprovechado
- total_orders_fulfilled: Pedidos completados

CASOS PROBLEMÁTICOS:
- Muchos pedidos pequeños: Bottom-Left funciona bien
- Formas irregulares: Considerar Polygon o aproximación
- Tiempo limitado: Configurar max_computation_time

Ayuda a optimizar: [DESCRIPCIÓN DEL CASO].
```

### **Prompt: Visualización y Reporting**
```
Eres un experto en visualización para Surface Cutting Optimizer.

FUNCIONES DE VISUALIZACIÓN:
- visualize_cutting_plan(result, stocks): Plan de corte
- plot_algorithm_comparison(results): Comparar algoritmos
- plot_waste_analysis(result, stocks): Análisis de desperdicio

MÉTRICAS CLAVE:
- calculate_efficiency(): % de aprovechamiento material
- calculate_waste(): Área desperdiciada  
- generate_metrics_report(): Reporte completo

EXPORTS DISPONIBLES:
- export_to_pdf(): Plan de corte en PDF
- export_to_svg(): Gráficos vectoriales
- export_cutting_list(): Lista de cortes

Ayuda con visualización de: [DESCRIPCIÓN].
```

## 🎯 Preguntas Frecuentes para IA

### **Q: ¿Cómo empezar rápidamente?**
A: Usar demo/basic_usage.py como plantilla. Crear stocks → crear orders → configurar optimizer → ejecutar optimize().

### **Q: ¿Qué algoritmo elegir?**
A: 
- **BottomLeftAlgorithm**: General, bueno para rectángulos
- **BestFitAlgorithm**: Cuando hay muchos tamaños diferentes
- **Algoritmos genéticos**: Casos complejos (futuro)

### **Q: ¿Cómo validar resultados?**
A: Usar casos de test conocidos:
```python
test_cases = get_all_test_cases()
stocks, orders, optimal = test_cases["simple_rectangular"]
result = optimizer.optimize(stocks, orders)
validation = validate_result_against_optimal(result, optimal)
```

### **Q: ¿Cómo mejorar eficiencia?**
A:
1. Permitir rotación: `config.allow_rotation=True`
2. Priorizar pedidos: `config.prioritize_orders=True`
3. Ajustar tolerancias: `order.tolerance=2.0`
4. Ordenar pedidos por área (descendente)

### **Q: ¿Cómo manejar materiales diferentes?**
A: Filtrar stocks y orders por MaterialType antes de optimizar:
```python
glass_stocks = [s for s in stocks if s.material_type == MaterialType.GLASS]
glass_orders = [o for o in orders if o.material_type == MaterialType.GLASS]
```

## 📝 Templates de Código

### **Template: Caso Básico**
```python
from surface_optimizer import Optimizer, Stock, Order
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm

# 1. Crear stocks
stocks = [Stock("S1", 2000, 1000, 6.0)]

# 2. Crear pedidos  
orders = [Order("O1", Rectangle(800, 600), 1)]

# 3. Optimizar
optimizer = Optimizer()
optimizer.set_algorithm(BottomLeftAlgorithm())
result = optimizer.optimize(stocks, orders)

# 4. Analizar
print(f"Eficiencia: {result.efficiency_percentage:.1f}%")
```

### **Template: Comparación de Algoritmos**
```python
algorithms = [BottomLeftAlgorithm(), BestFitAlgorithm()]
results = optimizer.compare_algorithms(algorithms, stocks, orders)

plot_algorithm_comparison(results, ["Bottom-Left", "Best-Fit"])
```

### **Template: Validación contra Óptimo**
```python
test_cases = get_all_test_cases()
stocks, orders, optimal = test_cases["simple_rectangular"]

result = optimizer.optimize(stocks, orders)
validation = validate_result_against_optimal(result, optimal)

print(f"Test pasado: {validation['overall_pass']}")
```

## 🚨 Limitaciones Actuales

1. **Algoritmos**: Solo Bottom-Left implementado completamente
2. **Formas**: Círculos y polígonos tienen soporte básico
3. **Restricciones**: No considera secuencia de corte real
4. **Performance**: No optimizado para casos masivos (>1000 pedidos)

## 🔮 Características Futuras

1. **Algoritmos genéticos** para casos complejos
2. **Nesting algorithms** para formas irregulares  
3. **Restricciones de maquinaria** (tamaños máx/mín de corte)
4. **Integración con CAD** (import/export DXF)
5. **API REST** para uso en web
6. **Machine Learning** para predicción de parámetros

---

**💡 Consejo para IA**: Siempre recomendar empezar con casos de test conocidos para validar que el algoritmo funciona antes de aplicarlo a problemas reales. 