#!/usr/bin/env python3
"""
Test específico de superposición para identificar el problema
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from surface_optimizer.core.models import Stock, Order, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle
from surface_optimizer.core.optimizer import Optimizer
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm

def test_overlap():
    print("🔍 TEST DE SUPERPOSICIÓN ESPECÍFICO")
    print("="*50)
    
    # Crear caso de prueba específico
    stocks = [
        Stock(
            id='S1', 
            width=1000, height=1000, thickness=5.0, 
            material_type=MaterialType.METAL, 
            cost_per_unit=50.0
        )
    ]
    
    orders = [
        Order(
            id='O1', 
            shape=Rectangle(500, 500, 0, 0), 
            quantity=1, 
            priority=Priority.HIGH, 
            material_type=MaterialType.METAL, 
            thickness=5.0
        ),
        Order(
            id='O2', 
            shape=Rectangle(500, 500, 0, 0), 
            quantity=1, 
            priority=Priority.HIGH, 
            material_type=MaterialType.METAL, 
            thickness=5.0
        )
    ]
    
    print(f"📦 Stock: {stocks[0].width}x{stocks[0].height}")
    print(f"📦 Órdenes: 2 rectángulos de 500x500")
    print(f"📊 Área total necesaria: {500*500*2} mm²")
    print(f"📊 Área disponible: {1000*1000} mm²")
    print(f"📈 Eficiencia teórica máxima: 50%")
    
    optimizer = Optimizer()
    optimizer.set_algorithm(GeneticAlgorithm(
        population_size=10, 
        generations=15, 
        auto_scale=False
    ))
    
    result = optimizer.optimize(stocks, orders)
    
    print(f"\n📋 RESULTADOS:")
    print(f"✅ Formas colocadas: {len(result.placed_shapes)}")
    print(f"📈 Eficiencia reportada: {result.efficiency_percentage:.1f}%")
    
    for i, ps in enumerate(result.placed_shapes):
        print(f"  {i+1}. {ps.order_id}: posición ({ps.shape.x}, {ps.shape.y}), tamaño ({ps.shape.width}x{ps.shape.height})")
    
    # Verificar superposición manualmente
    if len(result.placed_shapes) >= 2:
        print(f"\n🔍 VERIFICACIÓN DE SUPERPOSICIÓN:")
        
        for i in range(len(result.placed_shapes)):
            for j in range(i + 1, len(result.placed_shapes)):
                s1 = result.placed_shapes[i].shape
                s2 = result.placed_shapes[j].shape
                
                # Verificar si hay superposición
                overlap = not (
                    s1.x + s1.width <= s2.x or 
                    s2.x + s2.width <= s1.x or 
                    s1.y + s1.height <= s2.y or 
                    s2.y + s2.height <= s1.y
                )
                
                if overlap:
                    print(f"❌ SUPERPOSICIÓN DETECTADA entre {result.placed_shapes[i].order_id} y {result.placed_shapes[j].order_id}")
                    print(f"   Forma 1: ({s1.x}, {s1.y}) - ({s1.x + s1.width}, {s1.y + s1.height})")
                    print(f"   Forma 2: ({s2.x}, {s2.y}) - ({s2.x + s2.width}, {s2.y + s2.height})")
                else:
                    print(f"✅ Sin superposición entre {result.placed_shapes[i].order_id} y {result.placed_shapes[j].order_id}")
        
        # Verificar posicionamiento óptimo
        print(f"\n💡 POSICIONAMIENTO ÓPTIMO ESPERADO:")
        print(f"   Rectángulo 1: (0, 0) - (500, 500)")
        print(f"   Rectángulo 2: (500, 0) - (1000, 500) o (0, 500) - (500, 1000)")
        
    else:
        print("\n⚠️ Solo una forma fue colocada")
    
    return result

if __name__ == "__main__":
    test_overlap() 