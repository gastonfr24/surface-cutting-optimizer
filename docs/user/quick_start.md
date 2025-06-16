# Guía de Inicio Rápido

🚀 **Empezar con Surface Cutting Optimizer en 5 minutos**

## 📦 Instalación

```bash
pip install surface-cutting-optimizer
```

## 💡 Concepto Básico

**Surface Cutting Optimizer** resuelve el problema de: *"Tengo materiales de ciertos tamaños y necesito cortar piezas específicas. ¿Cómo optimizo el corte para minimizar desperdicio?"*

## 🎯 Ejemplo Básico

### 1. Importar la librería
```python
from surface_optimizer import Optimizer, Stock, Order
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.models import MaterialType, Priority
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
```

### 2. Definir materiales disponibles (Stock)
```python
# Tengo estas láminas de vidrio disponibles
stocks = [
    Stock("Vidrio-1", 2000, 1000, 6.0, MaterialType.GLASS, 100.0),
    Stock("Vidrio-2", 2000, 1000, 6.0, MaterialType.GLASS, 100.0),
    Stock("Metal-1", 1500, 1200, 3.0, MaterialType.METAL, 150.0)
]
```

### 3. Definir pedidos que necesito cortar
```python
# Necesito cortar estas piezas
orders = [
    Order("Ventana-1", Rectangle(800, 600), quantity=2, priority=Priority.HIGH, 
          material_type=MaterialType.GLASS, notes="Ventana principal"),
    
    Order("Puerta-1", Rectangle(600, 400), quantity=1, priority=Priority.MEDIUM,
          material_type=MaterialType.GLASS, notes="Puerta cristal"),
    
    Order("Placa-1", Rectangle(400, 300), quantity=3, priority=Priority.LOW,
          material_type=MaterialType.METAL, notes="Placas decorativas")
]
```

### 4. Optimizar el corte
```python
# Configurar y ejecutar optimización
optimizer = Optimizer()
optimizer.set_algorithm(BottomLeftAlgorithm())

result = optimizer.optimize(stocks, orders)
```

### 5. Ver resultados
```python
print(f"📊 Resultados:")
print(f"• Láminas usadas: {result.total_stock_used}")
print(f"• Pedidos cumplidos: {result.total_orders_fulfilled}/{len(orders)}")
print(f"• Eficiencia: {result.efficiency_percentage:.1f}%")
print(f"• Tiempo: {result.computation_time:.3f} segundos")

# Ver pedidos no cumplidos
if result.unfulfilled_orders:
    print(f"\n⚠️ No se pudieron cumplir:")
    for order in result.unfulfilled_orders:
        print(f"  • {order.id}: {order.shape}")
```

## 📈 Visualizar Resultados

```python
from surface_optimizer.utils.visualization import visualize_cutting_plan

# Mostrar plan de corte gráficamente
visualize_cutting_plan(result, stocks)
```

## 🎨 Ejemplo Completo

```python
from surface_optimizer import Optimizer, Stock, Order
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.models import MaterialType, Priority, OptimizationConfig
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.utils.visualization import visualize_cutting_plan

def main():
    # 1. Materiales disponibles
    stocks = [
        Stock("Madera-1", 2440, 1220, 18.0, MaterialType.WOOD, 80.0, "Almacén A"),
        Stock("Metal-1", 1500, 1000, 3.0, MaterialType.METAL, 120.0, "Almacén B")
    ]
    
    # 2. Pedidos a cortar
    orders = [
        Order("Mesa", Rectangle(1200, 800), 1, Priority.URGENT, MaterialType.WOOD),
        Order("Patas", Rectangle(100, 700), 4, Priority.HIGH, MaterialType.WOOD),
        Order("Refuerzo", Rectangle(400, 200), 2, Priority.MEDIUM, MaterialType.METAL),
        Order("Esquinas", Circle(50), 8, Priority.LOW, MaterialType.METAL)
    ]
    
    # 3. Configurar optimización
    config = OptimizationConfig(
        allow_rotation=True,      # Permitir rotar piezas
        cutting_width=3.0,        # 3mm de grosor de corte
        prioritize_orders=True    # Respetar prioridades
    )
    
    optimizer = Optimizer(config)
    optimizer.set_algorithm(BottomLeftAlgorithm())
    
    # 4. Optimizar
    result = optimizer.optimize(stocks, orders)
    
    # 5. Mostrar resultados
    print(f"🎯 Optimización completada!")
    print(f"📊 Eficiencia: {result.efficiency_percentage:.1f}%")
    print(f"📦 Láminas usadas: {result.total_stock_used}")
    print(f"✅ Pedidos cumplidos: {result.total_orders_fulfilled}/{len(orders)}")
    
    # 6. Visualizar (opcional)
    visualize_cutting_plan(result, stocks)

if __name__ == "__main__":
    main()
```

## 🎛️ Configuración Básica

```python
from surface_optimizer.core.models import OptimizationConfig

config = OptimizationConfig(
    allow_rotation=True,           # ¿Permitir rotar piezas?
    cutting_width=3.0,            # Grosor del corte (mm)
    min_waste_size=100.0,         # Tamaño mínimo útil de desperdicio
    max_computation_time=30.0,    # Tiempo máximo de cálculo (seg)
    prioritize_orders=True        # ¿Respetar prioridades?
)
```

## 🔍 Casos de Uso Comunes

### **Vidriería**
```python
# Materiales típicos de vidriería
stocks = [Stock("Cristal-6mm", 3210, 2250, 6.0, MaterialType.GLASS, 25.50)]
orders = [Order("Ventana", Rectangle(1200, 800), 3, Priority.HIGH, MaterialType.GLASS)]
```

### **Carpintería** 
```python
# Tableros de madera estándar
stocks = [Stock("MDF-18mm", 2440, 1220, 18.0, MaterialType.WOOD, 35.00)]
orders = [Order("Estante", Rectangle(800, 300), 4, Priority.MEDIUM, MaterialType.WOOD)]
```

### **Metalurgia**
```python
# Láminas de acero
stocks = [Stock("Acero-3mm", 2000, 1000, 3.0, MaterialType.METAL, 85.00)]
orders = [Order("Placa", Rectangle(400, 200), 10, Priority.HIGH, MaterialType.METAL)]
```

### **Textil**
```python
# Rollos de tela
stocks = [Stock("Algodón", 1500, 1000, 2.0, MaterialType.FABRIC, 12.00)]
orders = [Order("Patrón-A", Rectangle(600, 400), 5, Priority.URGENT, MaterialType.FABRIC)]
```

## ✅ Próximos Pasos

1. **Experimenta** con diferentes tamaños y materiales
2. **Prueba algoritmos** diferentes para comparar resultados
3. **Visualiza** los planes de corte generados
4. **Optimiza configuración** según tus necesidades específicas
5. **Revisa casos de test** conocidos para entender capacidades

## 🔗 Enlaces Útiles

- **[Casos de Uso Detallados](use_cases.md)** - Ejemplos específicos por industria
- **[FAQ](faq.md)** - Preguntas frecuentes
- **[API Reference](../ai/api_reference.md)** - Documentación completa
- **[Ejemplos Avanzados](../examples/)** - Casos más complejos

---

**💡 Tip**: Empieza con casos simples y ve aumentando la complejidad gradualmente. La librería incluye casos de test con soluciones óptimas conocidas para que puedas validar tus resultados. 