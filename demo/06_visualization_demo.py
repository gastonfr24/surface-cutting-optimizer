#!/usr/bin/env python3
"""
Demo 6: Visualización Básica a Avanzada - ¡Súper Fácil! 🎨
========================================================

🎯 Muestra cómo crear IMÁGENES de tus planes de corte desde básico hasta avanzado

Lo que aprenderás:
• Cómo guardar automáticamente imágenes del plan
• Ver resultados interactivamente  
• Guardar con nombres personalizados
• 🆕 Parámetros avanzados: temas, calidad, formatos
• 🆕 Configuración profesional para diferentes usos
• 🆕 Organización en subcarpetas por tipo
• Todo con la nueva API simplificada

¡Perfecto para: Desde imágenes básicas hasta presentaciones profesionales!
"""

# ¡Solo una línea de import! 🎉
from surface_optimizer import Stock, Order, MaterialType, Priority, Rectangle, optimize

def crear_datos_ejemplo():
    """Datos súper simples para demostrar visualización"""
    
    print("📋 Creando datos de ejemplo...")
    
    # 1 panel simple
    stock = Stock(
        id="TABLERO_001", 
        width=1200, 
        height=800, 
        material_type=MaterialType.WOOD, 
        cost_per_unit=50.0
    )
    
    # 3 órdenes simples
    orders = [
        Order(id="MESA", shape=Rectangle(500, 300), quantity=1, priority=Priority.HIGH, material_type=MaterialType.WOOD),
        Order(id="ESTANTE", shape=Rectangle(200, 200), quantity=2, priority=Priority.MEDIUM, material_type=MaterialType.WOOD),
        Order(id="SOPORTE", shape=Rectangle(100, 100), quantity=2, priority=Priority.LOW, material_type=MaterialType.WOOD),
    ]
    
    print(f"✅ Panel: {stock.width}×{stock.height}mm")
    print(f"✅ Órdenes: {len(orders)} tipos ({sum(o.quantity for o in orders)} piezas)")
    
    return [stock], orders

def demo_basico_optimizacion():
    """Demo 1: Optimización básica"""
    
    print("\n" + "="*15 + " 🎯 Demo 1: Optimización Básica " + "="*15)
    
    # Crear datos
    stocks, orders = crear_datos_ejemplo()
    
    # Optimizar
    print("\n🚀 Optimizando...")
    result = optimize(stocks, orders)
    
    # Ver resultados
    print("\n📊 Resultados:")
    result.show()
    
    return result, stocks, orders

def demo_basico_visualizacion(result):
    """Demo 2: Visualización básica"""
    
    print("\n" + "="*15 + " 🖱️ Demo 2: Visualización Básica " + "="*15)
    
    print("\n🖱️ 1. Mostrando plan interactivo...")
    result.visualize()  # Sin archivo = muestra en ventana
    
    print("\n💾 2. Guardando imagen básica...")
    result.visualize("basico.png", "data/06_visualizations/01_basico")
    
    print("✅ Métodos básicos completados")

def demo_intermedio_formatos(result):
    """Demo 3: Diferentes formatos y calidades"""
    
    print("\n" + "="*15 + " 📷 Demo 3: Formatos y Calidad " + "="*15)
    
    print("\n📷 Generando diferentes formatos...")
    
    # 1. PNG alta calidad para impresión
    print("🖨️ PNG alta calidad (300 DPI)...")
    result.visualize("alta_calidad.png", "data/06_visualizations/02_formatos", 
                    dpi=300, format='png')
    
    # 2. JPG para web
    print("🌐 JPG para web (150 DPI)...")
    result.visualize("web_optimizado.jpg", "data/06_visualizations/02_formatos", 
                    dpi=150, format='jpg')
    
    # 3. PDF para documentos
    print("📄 PDF para documentos...")
    result.visualize("documento.pdf", "data/06_visualizations/02_formatos", 
                    format='pdf')
    
    # 4. SVG vectorial
    print("🎯 SVG vectorial...")
    result.visualize("vectorial.svg", "data/06_visualizations/02_formatos", 
                    format='svg')
    
    print("✅ Múltiples formatos generados")

def demo_avanzado_temas(result):
    """Demo 4: Temas profesionales"""
    
    print("\n" + "="*15 + " 🎨 Demo 4: Temas Profesionales " + "="*15)
    
    print("\n🎨 Probando diferentes temas...")
    
    # 1. Tema profesional
    print("💼 Tema profesional...")
    result.visualize("profesional.png", "data/06_visualizations/03_temas", 
                    theme='professional', dpi=200)
    
    # 2. Tema colorido
    print("🌈 Tema colorido...")
    result.visualize("colorido.png", "data/06_visualizations/03_temas", 
                    theme='colorful', dpi=200)
    
    # 3. Tema minimal
    print("⚪ Tema minimal...")
    result.visualize("minimal.png", "data/06_visualizations/03_temas", 
                    theme='minimal', dpi=200)
    
    # 4. Tema por defecto
    print("📋 Tema por defecto...")
    result.visualize("defecto.png", "data/06_visualizations/03_temas", 
                    theme='default', dpi=200)
    
    print("✅ Diferentes temas aplicados")

def demo_avanzado_configuracion(result):
    """Demo 5: Configuraciones avanzadas"""
    
    print("\n" + "="*15 + " ⚙️ Demo 5: Configuración Avanzada " + "="*15)
    
    print("\n⚙️ Configuraciones especializadas...")
    
    # 1. Para presentación ejecutiva
    print("👔 Para presentación ejecutiva...")
    result.visualize("presentacion_ejecutiva.png", "data/06_visualizations/04_configuraciones",
                    figsize=(16, 10),  # Tamaño grande
                    dpi=300,           # Alta calidad
                    theme='professional',
                    show_cost=True,    # Mostrar costos
                    show_grid=False,   # Sin grid para limpieza
                    layout_style='auto')
    
    # 2. Para documentación técnica
    print("📋 Para documentación técnica...")
    result.visualize("documentacion_tecnica.png", "data/06_visualizations/04_configuraciones",
                    theme='minimal',
                    show_efficiency=True,
                    show_dimensions=True,
                    show_labels=True,
                    grid_alpha=0.1)    # Grid muy sutil
    
    # 3. Para taller (imprimir)
    print("🔧 Para taller...")
    result.visualize("instrucciones_taller.png", "data/06_visualizations/04_configuraciones",
                    figsize=(12, 8),
                    dpi=200,
                    theme='colorful',  # Colores distintivos
                    show_labels=True,
                    show_dimensions=True,
                    grid_alpha=0.5)    # Grid visible
    
    # 4. Para archivo/backup
    print("💾 Para archivo...")
    result.visualize("archivo_completo.png", "data/06_visualizations/04_configuraciones",
                    show_cost=True,
                    show_efficiency=True,
                    show_dimensions=True,
                    show_labels=True)
    
    print("✅ Configuraciones especializadas completadas")

def demo_layout_avanzado(result):
    """Demo 6: Layouts avanzados"""
    
    print("\n" + "="*15 + " 📐 Demo 6: Layouts Avanzados " + "="*15)
    
    # Crear datos con múltiples paneles para mostrar layouts
    stocks_multi = [
        Stock(id="PANEL_A", width=1200, height=800, material_type=MaterialType.WOOD, cost_per_unit=50.0),
        Stock(id="PANEL_B", width=1000, height=600, material_type=MaterialType.METAL, cost_per_unit=80.0),
        Stock(id="PANEL_C", width=800, height=400, material_type=MaterialType.WOOD, cost_per_unit=30.0),
    ]
    
    orders_multi = [
        Order(id="PIEZA_A", shape=Rectangle(400, 300), quantity=1, priority=Priority.HIGH, material_type=MaterialType.WOOD),
        Order(id="PIEZA_B", shape=Rectangle(300, 200), quantity=1, priority=Priority.MEDIUM, material_type=MaterialType.METAL),
        Order(id="PIEZA_C", shape=Rectangle(200, 150), quantity=1, priority=Priority.LOW, material_type=MaterialType.WOOD),
    ]
    
    print("\n📐 Optimizando múltiples paneles...")
    result_multi = optimize(stocks_multi, orders_multi)
    
    print("\n📐 Probando diferentes layouts...")
    
    # 1. Layout automático
    print("🤖 Layout automático...")
    result_multi.visualize("layout_auto.png", "data/06_visualizations/05_layouts",
                          layout_style='auto')
    
    # 2. Layout en fila única
    print("➡️ Layout en fila única...")
    result_multi.visualize("layout_fila.png", "data/06_visualizations/05_layouts",
                          layout_style='single_row')
    
    # 3. Layout en grid
    print("🔲 Layout en grid...")
    result_multi.visualize("layout_grid.png", "data/06_visualizations/05_layouts",
                          layout_style='grid', max_cols=2)
    
    print("✅ Layouts avanzados completados")

def demo_casos_uso_reales():
    """Demo 7: Casos de uso reales"""
    
    print("\n" + "="*15 + " 🏭 Demo 7: Casos de Uso Reales " + "="*15)
    
    # Usar datos del demo básico
    stocks, orders = crear_datos_ejemplo()
    result = optimize(stocks, orders)
    
    print("\n🏭 Generando para casos de uso reales...")
    
    # 1. Para mostrar al cliente
    print("🤝 Para mostrar al cliente...")
    result.visualize("cliente_propuesta.png", "data/06_visualizations/06_casos_uso/cliente",
                    theme='professional',
                    show_cost=True,       # Cliente puede ver costos
                    show_efficiency=True,
                    show_labels=False,    # Sin etiquetas técnicas
                    dpi=200)
    
    # 2. Para operario de máquina
    print("⚙️ Para operario de máquina...")
    result.visualize("operario_instrucciones.png", "data/06_visualizations/06_casos_uso/operario",
                    theme='colorful',     # Colores distintivos
                    show_labels=True,     # Etiquetas para identificar
                    show_dimensions=True, # Medidas exactas
                    show_grid=True,       # Grid para ayudar
                    grid_alpha=0.4,       # Grid visible pero no molesto
                    dpi=200)
    
    # 3. Para reporte gerencial básico
    print("📊 Para reporte gerencial básico...")
    result.visualize("reporte_gerencial_basico.pdf", "data/06_visualizations/06_casos_uso/gerencia",
                    format='pdf',         # PDF para documentos
                    figsize=(12, 8),      # Tamaño documento
                    theme='professional',
                    show_cost=True,
                    show_efficiency=True,
                    dpi=300)
    
    # 4. Para reporte gerencial mejorado (con más info)
    print("📊 Para reporte gerencial mejorado...")
    result.visualize("reporte_gerencial_mejorado.pdf", "data/06_visualizations/06_casos_uso/gerencia",
                    format='pdf',         # PDF para documentos
                    figsize=(14, 10),     # Tamaño grande
                    theme='professional',
                    show_cost=True,
                    show_efficiency=True,
                    show_dimensions=True,
                    show_labels=True,
                    dpi=300)
    
    # 5. Para reporte visual AVANZADO (imagen + información detallada)
    print("📊 Para reporte visual AVANZADO...")
    result.management_report("reporte_visual_avanzado.pdf", "data/06_visualizations/06_casos_uso/gerencia",
                            figsize=(16, 12),    # Tamaño extra grande
                            dpi=300,             # Alta calidad
                            format='pdf',        # PDF profesional
                            theme='professional',
                            show_detailed_info=True)  # Panel con información completa
    
    # 6. Para documentación técnica
    print("📚 Para documentación técnica...")
    result.visualize("documentacion.svg", "data/06_visualizations/06_casos_uso/documentacion",
                    format='svg',         # SVG escalable
                    theme='minimal',      # Limpio para documentos
                    show_dimensions=True,
                    show_labels=True)
    
    print("✅ Casos de uso reales completados")

def demo_reportes_visuales_avanzados():
    """Demo 8: Reportes Visuales Avanzados - ¡Con información detallada!"""
    
    print("\n" + "="*15 + " 📊 Demo 8: Reportes Visuales Avanzados " + "="*15)
    
    # Usar datos del demo básico
    stocks, orders = crear_datos_ejemplo()
    result = optimize(stocks, orders)
    
    print("\n📊 REPORTES VISUALES AVANZADOS:")
    print("   • Combina imagen del plan de corte + panel de información")
    print("   • Métricas de eficiencia, costos y utilización")
    print("   • Información detallada de stocks y pedidos")
    print("   • Layout profesional para presentaciones ejecutivas")
    
    print("\n📊 Generando reportes visuales avanzados...")
    
    # 1. Reporte ejecutivo básico
    print("👔 Reporte ejecutivo básico...")
    result.management_report("ejecutivo_basico.pdf", "data/06_visualizations/08_reportes_avanzados",
                            figsize=(14, 10),        # Tamaño estándar
                            dpi=200,                 # Calidad media
                            format='pdf',
                            theme='professional',
                            show_detailed_info=True)
    
    # 2. Reporte ejecutivo completo de alta calidad
    print("👑 Reporte ejecutivo COMPLETO...")
    result.management_report("ejecutivo_completo.pdf", "data/06_visualizations/08_reportes_avanzados",
                            figsize=(16, 12),        # Tamaño grande
                            dpi=300,                 # Alta calidad para impresión
                            format='pdf',
                            theme='professional',
                            show_detailed_info=True)
    
    # 3. Reporte visual para presentación
    print("📺 Para presentación en pantalla...")
    result.management_report("presentacion.png", "data/06_visualizations/08_reportes_avanzados",
                            figsize=(20, 12),        # Muy ancho para proyector
                            dpi=150,                 # Calidad pantalla
                            format='png',
                            theme='professional',
                            show_detailed_info=True)
    
    # 4. Reporte compacto (sin información extra)
    print("📄 Reporte compacto...")
    result.management_report("compacto.pdf", "data/06_visualizations/08_reportes_avanzados",
                            figsize=(12, 8),         # Más pequeño
                            dpi=200,
                            format='pdf',
                            theme='professional',
                            show_detailed_info=False)  # Sin panel de información
    
    print("✅ Reportes visuales avanzados completados")
    
    print("\n💡 CARACTERÍSTICAS DE LOS REPORTES VISUALES:")
    print("   📊 Panel izquierdo: Plan de corte visual")
    print("   📋 Panel derecho: Información detallada")
    print("   📈 Métricas: Eficiencia, costos, tiempos")
    print("   📦 Stock: Utilización, materiales, proveedores")
    print("   📋 Pedidos: Cumplimiento, prioridades, clientes")
    print("   🎨 Layout: Optimizado para presentaciones")
    
    print("\n🎯 CASOS DE USO IDEALES:")
    print("   👔 Reportes ejecutivos y gerenciales")
    print("   📺 Presentaciones a clientes")
    print("   📊 Análisis de performance")
    print("   💰 Reportes de costos y eficiencia")
    print("   📋 Documentación de proyectos")

def mostrar_estructura_archivos():
    """Mostrar estructura final de archivos"""
    
    print("\n" + "="*15 + " 📁 Estructura de Archivos " + "="*15)
    
    print("\n📁 ESTRUCTURA ORGANIZADA:")
    estructura = """data/06_visualizations/
├── 01_basico/
│   └── basico.png
├── 02_formatos/
│   ├── alta_calidad.png (300 DPI)
│   ├── web_optimizado.jpg (150 DPI)
│   ├── documento.pdf
│   └── vectorial.svg
├── 03_temas/
│   ├── profesional.png
│   ├── colorido.png
│   ├── minimal.png
│   └── defecto.png
├── 04_configuraciones/
│   ├── presentacion_ejecutiva.png
│   ├── documentacion_tecnica.png
│   ├── instrucciones_taller.png
│   └── archivo_completo.png
├── 05_layouts/
│   ├── layout_auto.png
│   ├── layout_fila.png
│   └── layout_grid.png
├── 06_casos_uso/
│   ├── cliente/
│   │   └── cliente_propuesta.png
│   ├── operario/
│   │   └── operario_instrucciones.png
│   ├── gerencia/
│   │   ├── reporte_gerencial_basico.pdf
│   │   ├── reporte_gerencial_mejorado.pdf
│   │   └── reporte_visual_avanzado.pdf
│   └── documentacion/
│       └── documentacion.svg
└── 08_reportes_avanzados/
    ├── ejecutivo_basico.pdf
    ├── ejecutivo_completo.pdf
    ├── presentacion.png
    └── compacto.pdf"""
    
    print(estructura)

def mostrar_resumen():
    """Mostrar resumen de capacidades"""
    
    print("\n" + "="*15 + " 📊 Resumen de Capacidades " + "="*15)
    
    print("\n🎨 PARÁMETROS DISPONIBLES:")
    print("   📐 figsize: Tamaño de imagen (ancho, alto)")
    print("   🔍 dpi: Calidad (72=draft, 150=web, 300=print)")
    print("   📁 format: 'png', 'jpg', 'pdf', 'svg'")
    print("   🎨 theme: 'default', 'professional', 'colorful', 'minimal'")
    print("   📏 show_grid: True/False")
    print("   👁️ show_labels: True/False")
    print("   💰 show_cost: True/False")
    print("   📊 show_efficiency: True/False")
    print("   📐 layout_style: 'auto', 'grid', 'single_row'")
    
    print("\n🏭 CASOS DE USO:")
    print("   🤝 Cliente: theme='professional', show_cost=True, dpi=200")
    print("   ⚙️ Operario: theme='colorful', show_labels=True, grid_alpha=0.4")
    print("   📊 Gerencial: format='pdf', dpi=300, show_efficiency=True")
    print("   📚 Documentación: theme='minimal', format='svg', show_grid=False")
    
    print("\n📁 ORGANIZACIÓN PROFESIONAL:")
    print("   • Subcarpetas por tipo de demo")
    print("   • Nombres descriptivos de archivos")
    print("   • Separación por casos de uso")
    print("   • Fácil navegación y mantenimiento")
    
    print("\n💡 TIPS PROFESIONALES:")
    print("   • PNG para imágenes con transparencia")
    print("   • JPG para fotos y web (menor tamaño)")
    print("   • PDF para documentos profesionales")
    print("   • SVG para gráficos escalables")
    print("   • DPI 300+ para impresión, 150 para web")

def main():
    """Función principal"""
    
    print("🎯 Demo 6: Visualización Básica a Avanzada - ¡SÚPER SIMPLE!")
    print("="*64)
    print("📋 Desde imágenes básicas hasta presentaciones profesionales")
    print("🆕 Con organización en subcarpetas - ¡súper ordenado!")
    
    # Demo 1: Optimización básica
    result, stocks, orders = demo_basico_optimizacion()
    
    # Demo 2: Visualización básica
    demo_basico_visualizacion(result)
    
    # Demo 3: Formatos
    demo_intermedio_formatos(result)
    
    # Demo 4: Temas
    demo_avanzado_temas(result)
    
    # Demo 5: Configuraciones
    demo_avanzado_configuracion(result)
    
    # Demo 6: Layouts
    demo_layout_avanzado(result)
    
    # Demo 7: Casos reales
    demo_casos_uso_reales()
    
    # Demo 8: Reportes Visuales Avanzados
    demo_reportes_visuales_avanzados()
    
    # Información final
    mostrar_estructura_archivos()
    mostrar_resumen()
    
    print("\n✅ ¡Demo de visualización completada!")
    
    print("\n🎉 LO QUE APRENDISTE:")
    print("   • ✅ Visualización básica e interactiva")
    print("   • ✅ Múltiples formatos (PNG, JPG, PDF, SVG)")
    print("   • ✅ Calidades diferentes (72, 150, 300 DPI)")
    print("   • ✅ Temas profesionales (4 estilos)")
    print("   • ✅ Configuraciones especializadas")
    print("   • ✅ Layouts avanzados para múltiples paneles")
    print("   • ✅ Casos de uso profesionales reales")
    print("   • ✅ Reportes visuales avanzados (imagen + información)")
    print("   • ✅ Organización profesional en subcarpetas")
    
    print("\n🚀 ¡Ahora dominas la visualización profesional!")
    print("💡 Tip: Los archivos están organizados para fácil navegación")

if __name__ == "__main__":
    main() 