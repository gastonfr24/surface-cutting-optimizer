#!/usr/bin/env python3
"""
🧪 Test Smart Algorithm Selection
================================

Compara el enfoque anterior (FirstFit hardcoded) vs nueva selección automática
"""

from surface_optimizer import optimize, compare_algorithms
from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm

def test_old_vs_new_approach():
    """Compara eficiencia del enfoque anterior vs nuevo"""
    
    print("🧪 TEST: Enfoque Anterior vs Selección Automática")
    print("=" * 60)
    
    # Datos de prueba (mismo que demo simple)
    stocks = [
        Stock("PANEL_001", 1200, 800, material_type=MaterialType.METAL, cost_per_unit=25.50),
        Stock("PANEL_002", 1200, 800, material_type=MaterialType.METAL, cost_per_unit=25.50),
        Stock("PANEL_003", 1000, 600, material_type=MaterialType.METAL, cost_per_unit=18.75),
        Stock("PANEL_004", 800, 600, material_type=MaterialType.METAL, cost_per_unit=15.00)
    ]
    
    orders = [
        Order("ORDER_A", Rectangle(300, 200), quantity=1, priority=Priority.HIGH, material_type=MaterialType.METAL),
        Order("ORDER_B", Rectangle(400, 250), quantity=2, priority=Priority.MEDIUM, material_type=MaterialType.METAL),
        Order("ORDER_C", Rectangle(150, 100), quantity=3, priority=Priority.HIGH, material_type=MaterialType.METAL),
        Order("ORDER_D", Rectangle(350, 180), quantity=1, priority=Priority.MEDIUM, material_type=MaterialType.METAL),
        Order("ORDER_E", Rectangle(200, 120), quantity=2, priority=Priority.LOW, material_type=MaterialType.METAL)
    ]
    
    config = OptimizationConfig(
        allow_rotation=True,
        prioritize_orders=True,
        cutting_width=3.0
    )
    
    print("📊 PROBLEMA:")
    total_pieces = sum(order.quantity for order in orders)
    print(f"   • Paneles: {len(stocks)}")
    print(f"   • Órdenes: {len(orders)} ({total_pieces} piezas)")
    
    print("\n🔴 ENFOQUE ANTERIOR (FirstFit hardcoded):")
    print("-" * 45)
    
    # Método anterior - FirstFit hardcoded
    optimizer_old = Optimizer(config)
    optimizer_old.set_algorithm(FirstFitAlgorithm())
    result_old = optimizer_old.optimize(stocks, orders)
    
    print(f"   ✅ Eficiencia: {result_old.efficiency_percentage:.1f}%")
    print(f"   ⏱️  Tiempo: {result_old.computation_time:.3f}s")
    print(f"   📦 Paneles usados: {result_old.total_stock_used}")
    
    print("\n🟢 ENFOQUE NUEVO (Selección Automática):")
    print("-" * 47)
    
    # Método nuevo - Selección automática
    result_new = optimize(stocks, orders, priority='balanced', config=config)
    
    print(f"   ✅ Eficiencia: {result_new.efficiency_percentage:.1f}%")
    print(f"   ⏱️  Tiempo: {result_new.computation_time:.3f}s")
    print(f"   📦 Paneles usados: {result_new.total_stock_used}")
    
    # Comparación
    efficiency_improvement = result_new.efficiency_percentage - result_old.efficiency_percentage
    time_ratio = result_new.computation_time / result_old.computation_time if result_old.computation_time > 0 else 1
    
    print("\n📈 COMPARACIÓN:")
    print("-" * 15)
    print(f"   📊 Mejora en eficiencia: {efficiency_improvement:+.1f}%")
    print(f"   ⏱️  Ratio de tiempo: {time_ratio:.1f}x")
    
    if efficiency_improvement > 0:
        print(f"   🎉 ¡MEJORA! La selección automática es {efficiency_improvement:.1f}% más eficiente")
    elif efficiency_improvement == 0:
        print(f"   ⚖️  Misma eficiencia, pero con selección inteligente")
    else:
        print(f"   ⚠️  Eficiencia menor por {abs(efficiency_improvement):.1f}%")
    
    return {
        'old_efficiency': result_old.efficiency_percentage,
        'new_efficiency': result_new.efficiency_percentage,
        'improvement': efficiency_improvement,
        'old_time': result_old.computation_time,
        'new_time': result_new.computation_time
    }


def test_different_priorities():
    """Prueba diferentes prioridades de optimización"""
    
    print("\n\n🎯 TEST: Diferentes Prioridades de Optimización")
    print("=" * 50)
    
    # Problema más complejo
    stocks = [
        Stock("LARGE_001", 2000, 1000, material_type=MaterialType.METAL),
        Stock("LARGE_002", 2000, 1000, material_type=MaterialType.METAL),
        Stock("MEDIUM_001", 1500, 800, material_type=MaterialType.METAL)
    ]
    
    orders = [
        Order("BIG_A", Rectangle(800, 600), quantity=2, material_type=MaterialType.METAL),
        Order("BIG_B", Rectangle(700, 500), quantity=2, material_type=MaterialType.METAL),
        Order("MID_A", Rectangle(400, 300), quantity=4, material_type=MaterialType.METAL),
        Order("MID_B", Rectangle(350, 250), quantity=3, material_type=MaterialType.METAL),
        Order("SMALL_A", Rectangle(200, 150), quantity=6, material_type=MaterialType.METAL)
    ]
    
    priorities = ['speed', 'balanced', 'quality', 'maximum']
    results = {}
    
    for priority in priorities:
        print(f"\n🔸 Prioridad: {priority.upper()}")
        print("-" * 25)
        
        result = optimize(stocks, orders, priority=priority)
        
        results[priority] = {
            'efficiency': result.efficiency_percentage,
            'time': result.computation_time,
            'algorithm': result.metadata['algorithm_selection']['selected_algorithm']
        }
        
        print(f"   Algoritmo: {result.metadata['algorithm_selection']['selected_algorithm']}")
        print(f"   Eficiencia: {result.efficiency_percentage:.1f}%")
        print(f"   Tiempo: {result.computation_time:.3f}s")
    
    # Resumen
    print(f"\n🏆 RESUMEN DE PRIORIDADES:")
    print("-" * 30)
    
    best_efficiency = max(results.items(), key=lambda x: x[1]['efficiency'])
    fastest = min(results.items(), key=lambda x: x[1]['time'])
    
    print(f"🥇 Mejor eficiencia: {best_efficiency[0]} ({best_efficiency[1]['efficiency']:.1f}%)")
    print(f"⚡ Más rápido: {fastest[0]} ({fastest[1]['time']:.3f}s)")
    
    return results


def test_algorithm_comparison():
    """Compara todos los algoritmos en el mismo problema"""
    
    print("\n\n📊 TEST: Comparación Completa de Algoritmos")
    print("=" * 45)
    
    # Problema desafiante
    stocks = [
        Stock("TEST_001", 1200, 800),
        Stock("TEST_002", 1000, 600)
    ]
    
    orders = [
        Order("T1", Rectangle(400, 300), quantity=2),
        Order("T2", Rectangle(350, 250), quantity=3),
        Order("T3", Rectangle(200, 150), quantity=4),
        Order("T4", Rectangle(180, 120), quantity=2),
        Order("T5", Rectangle(160, 100), quantity=3)
    ]
    
    results = compare_algorithms(stocks, orders)
    
    return results


def main():
    """Ejecutar todas las pruebas"""
    
    print("🚀 INICIANDO TESTS DE SELECCIÓN INTELIGENTE")
    print("=" * 70)
    
    # Test 1: Comparar enfoque anterior vs nuevo
    test1_results = test_old_vs_new_approach()
    
    # Test 2: Diferentes prioridades
    test2_results = test_different_priorities()
    
    # Test 3: Comparación completa
    test3_results = test_algorithm_comparison()
    
    print("\n\n🎉 TESTS COMPLETADOS")
    print("=" * 25)
    print("✅ Se creó la función de selección automática")
    print("✅ Se probaron diferentes prioridades")
    print("✅ Se compararon todos los algoritmos")
    
    if test1_results['improvement'] > 0:
        print(f"🎯 RESULTADO PRINCIPAL: {test1_results['improvement']:.1f}% mejora en eficiencia")
    else:
        print("⚠️  La mejora depende del problema específico")


if __name__ == "__main__":
    main() 