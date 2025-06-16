#!/usr/bin/env python3
"""
Ejemplo básico de uso de Surface Cutting Optimizer
Demuestra las funcionalidades principales de la librería
"""

from surface_optimizer import Optimizer, Stock, Order
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.models import MaterialType, Priority, OptimizationConfig
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.utils.visualization import visualize_cutting_plan, plot_algorithm_comparison
from surface_optimizer.utils.metrics import generate_metrics_report
from surface_optimizer.utils.test_cases import get_all_test_cases, validate_result_against_optimal


def main():
    print("🔧 Surface Cutting Optimizer - Ejemplo Básico")
    print("=" * 50)
    
    # 1. Crear inventario de materiales disponibles
    print("\n1. Creando inventario de materiales...")
    stocks = [
        Stock("S1", 2000, 1000, 6.0, MaterialType.GLASS, 100.0, "Almacén A"),
        Stock("S2", 2000, 1000, 6.0, MaterialType.GLASS, 100.0, "Almacén A"), 
        Stock("S3", 1500, 1200, 8.0, MaterialType.METAL, 150.0, "Almacén B"),
        Stock("S4", 2440, 1220, 18.0, MaterialType.WOOD, 80.0, "Almacén C")
    ]
    
    for stock in stocks:
        print(f"  ✓ {stock}")
    
    # 2. Crear lista de pedidos
    print("\n2. Creando pedidos de corte...")
    orders = [
        Order("O1", Rectangle(800, 600), quantity=2, priority=Priority.HIGH, 
              material_type=MaterialType.GLASS, notes="Ventana principal"),
        Order("O2", Rectangle(600, 400), quantity=1, priority=Priority.MEDIUM,
              material_type=MaterialType.GLASS, notes="Puerta lateral"),
        Order("O3", Rectangle(400, 300), quantity=3, priority=Priority.LOW,
              material_type=MaterialType.GLASS, notes="Ventanas pequeñas"),
        Order("O4", Circle(200), quantity=1, priority=Priority.URGENT,
              material_type=MaterialType.METAL, notes="Mesa redonda"),
        Order("O5", Rectangle(1200, 800), quantity=1, priority=Priority.MEDIUM,
              material_type=MaterialType.WOOD, notes="Panel de madera")
    ]
    
    for order in orders:
        print(f"  ✓ {order}")
    
    # 3. Configurar optimizador
    print("\n3. Configurando optimizador...")
    config = OptimizationConfig(
        allow_rotation=True,
        cutting_width=3.0,
        min_waste_size=100.0,
        max_computation_time=30.0,
        prioritize_orders=True
    )
    
    optimizer = Optimizer(config)
    optimizer.set_algorithm(BottomLeftAlgorithm())
    print(f"  ✓ Algoritmo: {optimizer.algorithm}")
    print(f"  ✓ Configuración: Rotación={config.allow_rotation}, Prioridad={config.prioritize_orders}")
    
    # 4. Ejecutar optimización
    print("\n4. Ejecutando optimización...")
    try:
        result = optimizer.optimize(stocks, orders)
        print("  ✓ Optimización completada!")
        
        # Mostrar resultados
        print(f"\n📊 Resultados:")
        print(f"  • Stocks utilizados: {result.total_stock_used}")
        print(f"  • Pedidos cumplidos: {result.total_orders_fulfilled}/{len(orders)}")
        print(f"  • Eficiencia: {result.efficiency_percentage:.1f}%")
        print(f"  • Tiempo de cálculo: {result.computation_time:.3f} segundos")
        print(f"  • Algoritmo: {result.algorithm_used}")
        
        # Pedidos no cumplidos
        if result.unfulfilled_orders:
            print(f"\n⚠️ Pedidos no cumplidos:")
            for order in result.unfulfilled_orders:
                print(f"  • {order.id}: {order.shape}")
        
        # 5. Generar reporte detallado
        print("\n5. Generando métricas detalladas...")
        metrics = generate_metrics_report(result, stocks, orders)
        print("  📈 Métricas completas:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"    {key}: {value:.2f}")
            else:
                print(f"    {key}: {value}")
        
        # 6. Visualización (comentada para no mostrar gráficos en ejemplo básico)
        print("\n6. Visualización disponible:")
        print("  • visualize_cutting_plan(result, stocks)  # Plan de corte")
        print("  • plot_algorithm_comparison(results)      # Comparación de algoritmos")
        
        # Mostrar formas colocadas
        if result.placed_shapes:
            print(f"\n📋 Formas colocadas ({len(result.placed_shapes)}):")
            for placed in result.placed_shapes:
                print(f"  • {placed}")
        
    except Exception as e:
        print(f"  ❌ Error en optimización: {e}")
        return
    
    # 7. Probar caso de test conocido
    print("\n7. Probando caso de test con solución óptima conocida...")
    try:
        test_cases = get_all_test_cases()
        test_stocks, test_orders, optimal_solution = test_cases["simple_rectangular"]
        
        print(f"  📝 Caso de test: {optimal_solution['description']}")
        print(f"  🎯 Solución óptima esperada:")
        print(f"    • Stocks: {optimal_solution['total_stock_used']}")
        print(f"    • Eficiencia: {optimal_solution['efficiency_percentage']}%")
        print(f"    • Pedidos: {optimal_solution['total_orders_fulfilled']}")
        
        # Ejecutar en caso de test
        test_result = optimizer.optimize(test_stocks, test_orders)
        
        # Validar resultado
        validation = validate_result_against_optimal(test_result, optimal_solution)
        
        print(f"\n  🧪 Resultado del algoritmo:")
        print(f"    • Stocks: {test_result.total_stock_used}")
        print(f"    • Eficiencia: {test_result.efficiency_percentage:.1f}%")
        print(f"    • Pedidos: {test_result.total_orders_fulfilled}")
        
        print(f"\n  ✅ Validación:")
        for check, passed in validation.items():
            status = "✓" if passed else "✗"
            print(f"    {status} {check}: {'PASS' if passed else 'FAIL'}")
        
        overall_status = "✅ ÉXITO" if validation['overall_pass'] else "❌ FALLO"
        print(f"\n  {overall_status}: Test general")
        
    except Exception as e:
        print(f"  ❌ Error en caso de test: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Ejemplo completado! La arquitectura funciona correctamente.")
    print("\nPróximos pasos:")
    print("• Implementar algoritmos más sofisticados")
    print("• Añadir soporte para formas irregulares")
    print("• Optimizar rendimiento para casos grandes")
    print("• Integrar con sistemas ERP existentes")


if __name__ == "__main__":
    main() 