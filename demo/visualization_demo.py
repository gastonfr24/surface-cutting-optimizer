#!/usr/bin/env python3
"""
Demo de visualización - Surface Cutting Optimizer
Muestra todas las capacidades de visualización y gráficos
"""

import matplotlib.pyplot as plt
from surface_optimizer import Optimizer, Stock, Order
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.core.models import MaterialType, Priority, OptimizationConfig
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.utils.visualization import (
    visualize_cutting_plan, 
    plot_algorithm_comparison,
    plot_waste_analysis
)
from surface_optimizer.utils.test_cases import get_all_test_cases


def main():
    print("🎨 Surface Cutting Optimizer - Demo de Visualización")
    print("=" * 60)
    
    # Configurar para mostrar gráficos
    plt.style.use('default')
    
    # 1. Caso de ejemplo con diferentes materiales
    print("\n1. Creando caso de ejemplo...")
    stocks = [
        Stock("Metal-1", 1200, 800, 3.0, MaterialType.METAL, 150.0),
        Stock("Vidrio-1", 2000, 1000, 6.0, MaterialType.GLASS, 100.0),
        Stock("Madera-1", 2440, 1220, 18.0, MaterialType.WOOD, 80.0)
    ]
    
    orders = [
        Order("M1", Rectangle(400, 300), 2, Priority.HIGH, MaterialType.METAL, notes="Placas metálicas"),
        Order("M2", Rectangle(300, 200), 3, Priority.MEDIUM, MaterialType.METAL, notes="Piezas pequeñas"),
        Order("V1", Rectangle(800, 600), 1, Priority.URGENT, MaterialType.GLASS, notes="Ventana grande"),
        Order("V2", Rectangle(400, 400), 2, Priority.LOW, MaterialType.GLASS, notes="Ventanas cuadradas"),
        Order("W1", Rectangle(1200, 800), 1, Priority.HIGH, MaterialType.WOOD, notes="Panel principal"),
        Order("C1", Circle(150), 1, Priority.MEDIUM, MaterialType.METAL, notes="Mesa redonda")
    ]
    
    # 2. Optimizar con algoritmo
    print("\n2. Ejecutando optimización...")
    config = OptimizationConfig(allow_rotation=True, prioritize_orders=True)
    optimizer = Optimizer(config)
    optimizer.set_algorithm(BottomLeftAlgorithm())
    
    result = optimizer.optimize(stocks, orders)
    
    print(f"✓ Optimización completada:")
    print(f"  • Stocks usados: {result.total_stock_used}")
    print(f"  • Pedidos cumplidos: {result.total_orders_fulfilled}/{len(orders)}")
    print(f"  • Eficiencia: {result.efficiency_percentage:.1f}%")
    
    # 3. Visualización del plan de corte
    print("\n3. Generando visualización del plan de corte...")
    try:
        visualize_cutting_plan(result, stocks, save_path="cutting_plan.png")
        print("✓ Plan de corte guardado como 'cutting_plan.png'")
    except Exception as e:
        print(f"❌ Error en visualización: {e}")
    
    # 4. Análisis de desperdicio
    print("\n4. Generando análisis de desperdicio...")
    try:
        plot_waste_analysis(result, stocks, save_path="waste_analysis.png")
        print("✓ Análisis de desperdicio guardado como 'waste_analysis.png'")
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
    
    # 5. Comparación de algoritmos (simulada)
    print("\n5. Simulando comparación de algoritmos...")
    try:
        # Simular resultados de diferentes algoritmos
        results = [result]  # Solo tenemos uno por ahora
        algorithm_names = ["Bottom-Left Fill"]
        
        plot_algorithm_comparison(results, algorithm_names, save_path="algorithm_comparison.png")
        print("✓ Comparación guardada como 'algorithm_comparison.png'")
    except Exception as e:
        print(f"❌ Error en comparación: {e}")
    
    # 6. Casos de test con visualización
    print("\n6. Visualizando casos de test...")
    try:
        test_cases = get_all_test_cases()
        
        # Visualizar caso simple
        test_stocks, test_orders, optimal = test_cases["simple_rectangular"]
        test_result = optimizer.optimize(test_stocks, test_orders)
        
        visualize_cutting_plan(test_result, test_stocks, save_path="test_case_simple.png")
        print("✓ Caso de test simple visualizado como 'test_case_simple.png'")
        
        # Visualizar caso con rotación
        test_stocks2, test_orders2, optimal2 = test_cases["rotation_required"]
        test_result2 = optimizer.optimize(test_stocks2, test_orders2)
        
        visualize_cutting_plan(test_result2, test_stocks2, save_path="test_case_rotation.png")
        print("✓ Caso de rotación visualizado como 'test_case_rotation.png'")
        
    except Exception as e:
        print(f"❌ Error en casos de test: {e}")
    
    # 7. Mostrar estadísticas de todos los casos
    print("\n7. Estadísticas de casos de test:")
    all_test_cases = get_all_test_cases()
    
    for name, (stocks_t, orders_t, optimal_t) in all_test_cases.items():
        try:
            result_t = optimizer.optimize(stocks_t, orders_t)
            efficiency_diff = result_t.efficiency_percentage - optimal_t.get('efficiency_percentage', 0)
            
            print(f"  📊 {name}:")
            print(f"     • Eficiencia obtenida: {result_t.efficiency_percentage:.1f}%")
            print(f"     • Eficiencia óptima: {optimal_t.get('efficiency_percentage', 0):.1f}%")
            print(f"     • Diferencia: {efficiency_diff:+.1f}%")
            print(f"     • Pedidos cumplidos: {result_t.total_orders_fulfilled}/{len(orders_t)}")
        except Exception as e:
            print(f"     ❌ Error en {name}: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo de visualización completado!")
    print("\nArchivos generados:")
    print("• cutting_plan.png - Plan de corte principal")
    print("• waste_analysis.png - Análisis de desperdicio")
    print("• algorithm_comparison.png - Comparación de algoritmos")
    print("• test_case_simple.png - Caso de test simple")
    print("• test_case_rotation.png - Caso con rotación")
    print("\n💡 Tip: Abre los archivos PNG para ver los gráficos generados")


if __name__ == "__main__":
    main() 