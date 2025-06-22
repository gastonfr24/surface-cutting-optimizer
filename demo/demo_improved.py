#!/usr/bin/env python3
"""
🎯 Demo Mejorado: Comparación Antes vs Después
==============================================

Muestra la mejora en eficiencia usando selección automática de algoritmos
vs el enfoque anterior con FirstFit hardcoded.
"""

import pandas as pd
from pathlib import Path

# Nuevo enfoque - función de conveniencia
from surface_optimizer import optimize, compare_algorithms

# Enfoque anterior
from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm


def load_demo_data():
    """Cargar datos del demo original"""
    
    # Usar datos del demo simple
    data_path = Path(__file__).parent / "data" / "01_simple"
    
    try:
        # Cargar stocks desde CSV
        stock_df = pd.read_csv(data_path / "simple_stock.csv")
        stocks = [
            Stock(
                id=row['stock_id'],
                width=row['width'], 
                height=row['height'],
                material_type=MaterialType.METAL,
                cost_per_unit=row['cost']
            )
            for _, row in stock_df.iterrows()
        ]
        
        # Cargar orders desde CSV
        orders_df = pd.read_csv(data_path / "simple_orders.csv")
        orders = [
            Order(
                id=row['order_id'],
                shape=Rectangle(row['width'], row['height']),
                quantity=row['quantity'],
                priority=Priority.HIGH if row['priority'] == 'HIGH' else Priority.MEDIUM,
                material_type=MaterialType.METAL
            )
            for _, row in orders_df.iterrows()
        ]
        
        return stocks, orders
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return None, None


def demo_old_approach(stocks, orders):
    """Enfoque anterior: FirstFit hardcoded"""
    
    print("🔴 ENFOQUE ANTERIOR")
    print("=" * 25)
    print("🎯 Algoritmo: FirstFit (hardcoded)")
    print("📝 Configuración: Manual, sin optimización")
    
    # Configuración original
    config = OptimizationConfig(
        allow_rotation=True,
        prioritize_orders=True,
        cutting_width=3.0
    )
    
    # Optimizador original
    optimizer = Optimizer(config)
    optimizer.set_algorithm(FirstFitAlgorithm())
    
    # Ejecutar
    result = optimizer.optimize(stocks, orders)
    
    print(f"✅ Eficiencia: {result.efficiency_percentage:.1f}%")
    print(f"⏱️  Tiempo: {result.computation_time:.3f}s")
    print(f"📦 Paneles usados: {result.total_stock_used}")
    
    return result


def demo_new_approach(stocks, orders):
    """Nuevo enfoque: Selección automática inteligente"""
    
    print("\n🟢 ENFOQUE NUEVO")
    print("=" * 23)
    print("🤖 Algoritmo: Selección automática")
    print("📝 Configuración: Inteligente basada en problema")
    
    # Nueva función de conveniencia
    result = optimize(
        stocks, orders, 
        priority='balanced',  # Prioridad balanceada
        allow_rotation=True,
        prioritize_orders=True,
        cutting_width=3.0
    )
    
    print(f"✅ Eficiencia: {result.efficiency_percentage:.1f}%")
    print(f"⏱️  Tiempo: {result.computation_time:.3f}s")
    print(f"📦 Paneles usados: {result.total_stock_used}")
    print(f"🧠 Algoritmo elegido: {result.metadata['algorithm_selection']['selected_algorithm']}")
    
    return result


def demo_quality_focus(stocks, orders):
    """Enfoque enfocado en calidad máxima"""
    
    print("\n🔥 ENFOQUE CALIDAD MÁXIMA")
    print("=" * 32)
    print("🎯 Prioridad: Quality (mejor eficiencia)")
    
    try:
        result = optimize(
            stocks, orders, 
            priority='quality',  # Máxima calidad
            allow_rotation=True,
            prioritize_orders=True,
            cutting_width=3.0
        )
        
        print(f"✅ Eficiencia: {result.efficiency_percentage:.1f}%")
        print(f"⏱️  Tiempo: {result.computation_time:.3f}s")
        print(f"📦 Paneles usados: {result.total_stock_used}")
        print(f"🧠 Algoritmo elegido: {result.metadata['algorithm_selection']['selected_algorithm']}")
        
        return result
        
    except Exception as e:
        print(f"⚠️ Error con algoritmo quality: {str(e)[:60]}...")
        print("🔄 Fallback: Usando genetic algorithm...")
        
        # Fallback a genetic
        result = optimize(
            stocks, orders, 
            algorithm='genetic',  # Manual selection
            allow_rotation=True,
            prioritize_orders=True,
            cutting_width=3.0
        )
        
        print(f"✅ Eficiencia: {result.efficiency_percentage:.1f}%")
        print(f"⏱️  Tiempo: {result.computation_time:.3f}s")
        print(f"📦 Paneles usados: {result.total_stock_used}")
        print(f"🧠 Algoritmo elegido: genetic (fallback)")
        
        return result


def compare_all_approaches(stocks, orders):
    """Comparar todos los enfoques"""
    
    print("\n\n📊 COMPARACIÓN COMPLETA")
    print("=" * 30)
    
    results = compare_algorithms(stocks, orders, config=OptimizationConfig(
        allow_rotation=True,
        prioritize_orders=True,
        cutting_width=3.0
    ))
    
    return results


def main():
    """Demo principal"""
    
    print("🏭 Surface Cutting Optimizer v1.0.0 - Demo Mejorado")
    print("=" * 60)
    print("🎯 Objetivo: Mostrar mejoras con selección automática")
    
    # Cargar datos
    stocks, orders = load_demo_data()
    if not stocks or not orders:
        return
    
    print(f"\n📊 DATOS DEL PROBLEMA:")
    total_pieces = sum(order.quantity for order in orders)
    total_stock_area = sum(stock.area for stock in stocks)
    total_demand_area = sum(order.total_area for order in orders)
    utilization = (total_demand_area / total_stock_area * 100) if total_stock_area > 0 else 0
    
    print(f"   • Paneles disponibles: {len(stocks)}")
    print(f"   • Órdenes: {len(orders)} ({total_pieces} piezas)")
    print(f"   • Utilización teórica: {utilization:.1f}%")
    
    # Ejecutar demostraciones
    result_old = demo_old_approach(stocks, orders)
    result_new = demo_new_approach(stocks, orders)
    result_quality = demo_quality_focus(stocks, orders)
    
    # Comparación completa
    comparison = compare_all_approaches(stocks, orders)
    
    # Resumen final
    print("\n\n🎉 RESUMEN DE MEJORAS")
    print("=" * 25)
    
    improvement_new = result_new.efficiency_percentage - result_old.efficiency_percentage
    improvement_quality = result_quality.efficiency_percentage - result_old.efficiency_percentage
    
    print(f"📈 Enfoque nuevo vs anterior:")
    print(f"   • Mejora en eficiencia: {improvement_new:+.1f}%")
    print(f"   • Tiempo: {result_new.computation_time:.3f}s vs {result_old.computation_time:.3f}s")
    
    print(f"\n📈 Enfoque calidad vs anterior:")
    print(f"   • Mejora en eficiencia: {improvement_quality:+.1f}%")
    print(f"   • Tiempo: {result_quality.computation_time:.3f}s vs {result_old.computation_time:.3f}s")
    
    if improvement_new > 0 or improvement_quality > 0:
        print(f"\n🎯 CONCLUSIÓN: ¡La selección automática mejora la eficiencia!")
        if improvement_quality > improvement_new:
            print(f"   🏆 Mejor resultado: Enfoque calidad ({result_quality.efficiency_percentage:.1f}%)")
        else:
            print(f"   🏆 Mejor resultado: Enfoque nuevo ({result_new.efficiency_percentage:.1f}%)")
    else:
        print(f"\n📊 CONCLUSIÓN: Para este problema específico, todos los algoritmos")
        print(f"   dan resultados similares. La selección automática garantiza")
        print(f"   usar el algoritmo más apropiado sin conocimiento experto.")
    
    print(f"\n✨ BENEFICIOS ADICIONALES:")
    print(f"   ✅ API más simple (1 línea vs 6 líneas)")
    print(f"   ✅ Selección automática (no necesita conocimiento experto)")
    print(f"   ✅ Mejor rendimiento en tiempo (usa algoritmos más eficientes)")
    print(f"   ✅ Escalable (se adapta al tamaño del problema)")


if __name__ == "__main__":
    main() 