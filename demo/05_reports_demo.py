#!/usr/bin/env python3
"""
📊 DEMO 5: REPORTES DEFINITIVOS - Todos los Formatos y Configuraciones
=======================================================================

¡LA DEMO DEFINITIVA DE REPORTES! 🚀

Aprende TODOS los tipos de reportes disponibles:
✅ 8 FORMATOS: HTML, PDF, Excel, CSV, XML, Markdown, JSON, TXT
✅ PARAMETRIZACIÓN SIMPLE: Ejemplos claros y progresivos
✅ CASOS DE USO REALES: Cuándo usar cada formato
✅ PERSONALIZACIÓN TOTAL: Empresa, idioma, filtros, compliance

Duración: ~3 minutos
Archivos generados: 15+ reportes diferentes
"""

from surface_optimizer import (
    optimize, Stock, Order, Rectangle, MaterialType, Priority,
    ReportConfig, ReportFormat, ReportLanguage, ReportUsage, 
    UnitSystem, ComplianceStandard, FilterCriteria,
    CompanyInfo, ProjectInfo
)
from pathlib import Path
import os


def demo_setup():
    """Configuración de datos para todos los ejemplos"""
    print("📋 Configurando escenario de ejemplo...")
    
    # Stocks diversos
    stocks = [
        Stock("WOOD_A1", 2400, 1200, material_type=MaterialType.WOOD, cost_per_unit=45.50, thickness=18),
        Stock("METAL_B2", 2000, 1000, material_type=MaterialType.METAL, cost_per_unit=120.00, thickness=3),
        Stock("PLASTIC_C3", 3000, 1500, material_type=MaterialType.PLASTIC, cost_per_unit=65.75, thickness=10),
    ]
    
    # Órdenes con diferentes prioridades y clientes
    orders = [
        Order("ORD_001", Rectangle(400, 300), quantity=2, priority=Priority.HIGH, 
              material_type=MaterialType.WOOD, customer_id="CLIENTE_VIP"),
        Order("ORD_002", Rectangle(600, 400), quantity=1, priority=Priority.URGENT,
              material_type=MaterialType.METAL, customer_id="CLIENTE_PREMIUM"),
        Order("ORD_003", Rectangle(800, 600), quantity=3, priority=Priority.MEDIUM,
              material_type=MaterialType.PLASTIC, customer_id="CLIENTE_NORMAL"),
        Order("ORD_004", Rectangle(300, 200), quantity=4, priority=Priority.LOW,
              material_type=MaterialType.WOOD, customer_id="CLIENTE_VIP"),
    ]
    
    print(f"   📦 {len(stocks)} paneles | 📋 {len(orders)} órdenes ({sum(o.quantity for o in orders)} piezas)")
    return stocks, orders


def ejemplo_1_basico():
    """🎯 EJEMPLO 1: Reportes Básicos (Sin Configuración)"""
    print("\n" + "="*70)
    print("🎯 EJEMPLO 1: REPORTES BÁSICOS (Modo Legacy)")
    print("="*70)
    print("💡 Ideal para: Empezar rápido, compatibilidad con código existente")
    
    stocks, orders = demo_setup()
    
    # Optimización
    result = optimize(stocks, orders, priority='balanced')
    print(f"✅ Optimización: {result.efficiency_percentage:.1f}% eficiencia")
    
    output_dir = "demo/outputs/05_reports/01_basicos"
    
    print("\n📄 Generando reportes básicos...")
    
    # JSON básico (compatible con versión anterior)
    result.generate_report("json", "reporte_basico.json", output_dir)
    print("   ✅ JSON: Datos estructurados completos")
    
    # Coordenadas para CNC
    result.generate_report("coordinates", "coordenadas_cnc.json", output_dir)
    print("   ✅ Coordinates: Para máquinas CNC")
    
    # Performance
    result.generate_report("performance", "rendimiento.json", output_dir)
    print("   ✅ Performance: Métricas de eficiencia")
    
    # Material
    result.generate_report("material", "analisis_materiales.json", output_dir)
    print("   ✅ Material: Análisis por tipo de material")
    
    print("\n💡 Código usado:")
    print("   result.generate_report('json', 'archivo.json')")
    print("   result.generate_report('coordinates', 'cnc.json')")


def ejemplo_2_html_profesional():
    """🌐 EJEMPLO 2: Reportes HTML Profesionales"""
    print("\n" + "="*70)
    print("🌐 EJEMPLO 2: REPORTES HTML PROFESIONALES")
    print("="*70)
    print("💡 Ideal para: Presentaciones, dashboards web, reportes ejecutivos")
    
    stocks, orders = demo_setup()
    result = optimize(stocks, orders)
    
    output_dir = "demo/outputs/05_reports/02_html"
    
    print("\n🎨 Generando reportes HTML...")
    
    # --- HTML BÁSICO ---
    config_simple = ReportConfig(
        format=ReportFormat.HTML,
        language=ReportLanguage.SPANISH
    )
    
    result.generate_report(
        config=config_simple,
        save_path="html_basico.html",
        output_dir=output_dir
    )
    print("   ✅ HTML Básico: Diseño simple, español")
    
    # --- HTML EMPRESARIAL ---
    empresa_info = CompanyInfo(
        name="Cortes Industriales S.A.",
        address="Polígono Industrial, Madrid",
        phone="+34 91 555 0123",
        email="info@cortes-industriales.es"
    )
    
    proyecto_info = ProjectInfo(
        name="Optimización Q4 2024",
        code="PROJ-2024-Q4",
        client="Clientes Premium",
        manager="Carlos Rodríguez"
    )
    
    config_empresarial = ReportConfig(
        format=ReportFormat.HTML,
        language=ReportLanguage.SPANISH,
        usage=ReportUsage.PRESENTATION,
        company_info=empresa_info,
        project_info=proyecto_info,
        include_recommendations=True,
        confidentiality_level="internal",
        watermark="CONFIDENCIAL"
    )
    
    result.generate_report(
        config=config_empresarial,
        save_path="html_empresarial.html", 
        output_dir=output_dir
    )
    print("   ✅ HTML Empresarial: Info de empresa, marca de agua, recomendaciones")
    
    # --- HTML CON COMPLIANCE ---
    config_compliance = ReportConfig(
        format=ReportFormat.HTML,
        language=ReportLanguage.ENGLISH,
        usage=ReportUsage.AUDIT,
        company_info=empresa_info,
        compliance_standards=[ComplianceStandard.ISO_9001, ComplianceStandard.ISO_14001],
        include_qr_code=True,
        confidentiality_level="restricted"
    )
    
    result.generate_report(
        config=config_compliance,
        save_path="html_compliance.html",
        output_dir=output_dir
    )
    print("   ✅ HTML Compliance: ISO 9001/14001, QR code, inglés")
    
    print("\n💡 Código usado:")
    print("   config = ReportConfig(format=ReportFormat.HTML, language=ReportLanguage.SPANISH)")
    print("   result.generate_report(config=config, save_path='reporte.html')")


def ejemplo_3_documentos_oficiales():
    """📋 EJEMPLO 3: Documentos Oficiales (PDF, XML, Markdown)"""
    print("\n" + "="*70) 
    print("📋 EJEMPLO 3: DOCUMENTOS OFICIALES")
    print("="*70)
    print("💡 Ideal para: Auditorías, máquinas CNC, documentación técnica")
    
    stocks, orders = demo_setup()
    result = optimize(stocks, orders)
    
    output_dir = "demo/outputs/05_reports/03_oficiales"
    
    print("\n📄 Generando documentos oficiales...")
    
    # --- PDF AUDITORÍA ---
    config_pdf = ReportConfig(
        format=ReportFormat.PDF,
        language=ReportLanguage.SPANISH,
        usage=ReportUsage.AUDIT,
        compliance_standards=[ComplianceStandard.ISO_9001],
        include_signatures=True,
        confidentiality_level="restricted"
    )
    
    try:
        result.generate_report(
            config=config_pdf,
            save_path="auditoria_oficial.pdf",
            output_dir=output_dir
        )
        print("   ✅ PDF: Auditoría oficial con ISO 9001")
    except Exception as e:
        print(f"   ⚠️ PDF: Requiere reportlab ({e})")
    
    # --- XML PARA CNC ---
    config_xml = ReportConfig(
        format=ReportFormat.XML,
        language=ReportLanguage.ENGLISH,
        usage=ReportUsage.CNC_MACHINE,
        unit_system=UnitSystem.IMPERIAL,
        decimal_precision=3,
        include_cutting_instructions=True,
        filters=FilterCriteria(priorities=[Priority.HIGH, Priority.URGENT])
    )
    
    result.generate_report(
        config=config_xml,
        save_path="instrucciones_cnc.xml",
        output_dir=output_dir
    )
    print("   ✅ XML: Instrucciones CNC en pulgadas, alta precisión")
    
    # --- MARKDOWN TÉCNICO ---
    config_md = ReportConfig(
        format=ReportFormat.MARKDOWN,
        language=ReportLanguage.ENGLISH,
        usage=ReportUsage.ENGINEERING,
        include_material_details=True,
        include_cutting_instructions=True,
        compliance_standards=[ComplianceStandard.ANSI]
    )
    
    result.generate_report(
        config=config_md,
        save_path="documentacion_tecnica.md",
        output_dir=output_dir
    )
    print("   ✅ Markdown: Documentación técnica con ANSI")
    
    print("\n💡 Cuándo usar cada formato:")
    print("   PDF → Documentos oficiales, auditorías, contratos")
    print("   XML → Máquinas CNC, sistemas ERP, integración")
    print("   Markdown → Documentación técnica, GitHub, colaboración")


def ejemplo_4_datos_y_excel():
    """📊 EJEMPLO 4: Datos y Excel (CSV, Excel)"""
    print("\n" + "="*70)
    print("📊 EJEMPLO 4: DATOS Y EXCEL")
    print("="*70)
    print("💡 Ideal para: Análisis de datos, BI, contabilidad, Excel")
    
    stocks, orders = demo_setup()
    result = optimize(stocks, orders)
    
    output_dir = "demo/outputs/05_reports/04_datos"
    
    print("\n📈 Generando reportes de datos...")
    
    # --- CSV CONTABILIDAD ---
    config_csv = ReportConfig(
        format=ReportFormat.CSV,
        usage=ReportUsage.ACCOUNTING,
        include_cost_analysis=True,
        include_material_details=True,
        decimal_precision=2
    )
    
    result.generate_report(
        config=config_csv,
        save_path="contabilidad_paquete",
        output_dir=output_dir
    )
    print("   ✅ CSV: Paquete contable (coordenadas, materiales, performance)")
    
    # --- EXCEL GERENCIAL ---
    config_excel = ReportConfig(
        format=ReportFormat.EXCEL,
        language=ReportLanguage.SPANISH,
        usage=ReportUsage.MANAGEMENT,
        include_cost_analysis=True,
        include_material_details=True,
        include_recommendations=True
    )
    
    try:
        result.generate_report(
            config=config_excel,
            save_path="reporte_gerencial.xlsx",
            output_dir=output_dir
        )
        print("   ✅ Excel: Reporte gerencial multihojas")
    except Exception as e:
        print(f"   ⚠️ Excel: Requiere openpyxl ({e})")
    
    print("\n💡 Casos de uso:")
    print("   CSV → Business Intelligence, análisis de datos, importar a Excel")
    print("   Excel → Gerencia, contabilidad, análisis financiero")


def ejemplo_5_multiidioma():
    """🌍 EJEMPLO 5: Reportes Multiidioma"""
    print("\n" + "="*70)
    print("🌍 EJEMPLO 5: REPORTES MULTIIDIOMA")
    print("="*70)
    print("💡 Ideal para: Empresas internacionales, clientes extranjeros")
    
    stocks, orders = demo_setup()
    result = optimize(stocks, orders)
    
    output_dir = "demo/outputs/05_reports/05_multiidioma"
    
    print("\n🗣️ Generando reportes en múltiples idiomas...")
    
    idiomas = [
        (ReportLanguage.SPANISH, "es", "Español"),
        (ReportLanguage.ENGLISH, "en", "English"), 
        (ReportLanguage.FRENCH, "fr", "Français")
    ]
    
    for idioma, codigo, nombre in idiomas:
        config = ReportConfig(
            format=ReportFormat.HTML,
            language=idioma,
            usage=ReportUsage.CUSTOMER,
            include_cost_analysis=False,  # Ocultar costos internos
            confidentiality_level="public"
        )
        
        result.generate_report(
            config=config,
            save_path=f"reporte_cliente_{codigo}.html",
            output_dir=output_dir
        )
        print(f"   ✅ {nombre}: Reporte para cliente público")
    
    print("\n💡 Código multiidioma:")
    print("   for idioma in [ReportLanguage.SPANISH, ReportLanguage.ENGLISH]:")
    print("       config = ReportConfig(language=idioma)")


def ejemplo_6_filtros_avanzados():
    """🔍 EJEMPLO 6: Filtros Avanzados"""
    print("\n" + "="*70)
    print("🔍 EJEMPLO 6: FILTROS AVANZADOS")
    print("="*70)
    print("💡 Ideal para: Reportes específicos, control de calidad, análisis focalizados")
    
    stocks, orders = demo_setup()
    result = optimize(stocks, orders)
    
    output_dir = "demo/outputs/05_reports/06_filtros"
    
    print("\n🎯 Generando reportes con filtros...")
    
    # --- FILTRO POR MATERIAL ---
    filtro_metal = FilterCriteria(
        materials=[MaterialType.METAL],
        priorities=[Priority.HIGH, Priority.URGENT]
    )
    
    config_metal = ReportConfig(
        format=ReportFormat.TXT,
        usage=ReportUsage.QUALITY_CONTROL,
        filters=filtro_metal,
        include_material_details=True
    )
    
    result.generate_report(
        config=config_metal,
        save_path="control_calidad_metal.txt",
        output_dir=output_dir
    )
    print("   ✅ TXT: Solo metal de alta prioridad")
    
    # --- FILTRO POR CLIENTE ---
    filtro_vip = FilterCriteria(
        customer_ids=["CLIENTE_VIP", "CLIENTE_PREMIUM"],
        min_efficiency=50.0
    )
    
    config_vip = ReportConfig(
        format=ReportFormat.HTML,
        usage=ReportUsage.CUSTOMER,
        filters=filtro_vip,
        confidentiality_level="internal"
    )
    
    result.generate_report(
        config=config_vip,
        save_path="reporte_clientes_vip.html",
        output_dir=output_dir
    )
    print("   ✅ HTML: Solo clientes VIP con buena eficiencia")
    
    print("\n💡 Tipos de filtros disponibles:")
    print("   materials → Filtrar por tipo de material")
    print("   priorities → Solo ciertas prioridades")
    print("   customer_ids → Clientes específicos")
    print("   min_efficiency/max_efficiency → Rangos de eficiencia")
    print("   min_area/max_area → Rangos de área")


def ejemplo_7_casos_especiales():
    """⚙️ EJEMPLO 7: Casos Especiales y Personalizaciones"""
    print("\n" + "="*70)
    print("⚙️ EJEMPLO 7: CASOS ESPECIALES Y PERSONALIZACIONES")
    print("="*70)
    print("💡 Ideal para: Necesidades específicas, integración con sistemas")
    
    stocks, orders = demo_setup()
    result = optimize(stocks, orders)
    
    output_dir = "demo/outputs/05_reports/07_especiales"
    
    print("\n🔧 Generando casos especiales...")
    
    # --- SISTEMA IMPERIAL ---
    config_imperial = ReportConfig(
        format=ReportFormat.HTML,
        language=ReportLanguage.ENGLISH,
        unit_system=UnitSystem.IMPERIAL,
        decimal_precision=3,
        usage=ReportUsage.CNC_MACHINE
    )
    
    result.generate_report(
        config=config_imperial,
        save_path="reporte_pulgadas.html",
        output_dir=output_dir
    )
    print("   ✅ HTML: Sistema imperial (pulgadas)")
    
    # --- MÁXIMA SEGURIDAD ---
    config_seguro = ReportConfig(
        format=ReportFormat.PDF,
        usage=ReportUsage.REGULATORY,
        compliance_standards=[
            ComplianceStandard.ISO_9001,
            ComplianceStandard.ISO_14001,
            ComplianceStandard.OSHA
        ],
        confidentiality_level="restricted",
        watermark="TOP SECRET",
        include_qr_code=True,
        digital_signature=True
    )
    
    try:
        result.generate_report(
            config=config_seguro,
            save_path="documento_clasificado.pdf",
            output_dir=output_dir
        )
        print("   ✅ PDF: Máxima seguridad + múltiples compliance")
    except:
        print("   ⚠️ PDF: Requiere reportlab para máxima seguridad")
    
    # --- MINIMAL JSON ---
    config_minimal = ReportConfig(
        format=ReportFormat.JSON,
        include_charts=False,
        include_recommendations=False,
        include_cost_analysis=False,
        decimal_precision=1
    )
    
    result.generate_report(
        config=config_minimal,
        save_path="datos_minimos.json",
        output_dir=output_dir
    )
    print("   ✅ JSON: Solo datos esenciales")
    
    print("\n💡 Personalizaciones avanzadas:")
    print("   unit_system → METRIC (mm) o IMPERIAL (inches)")
    print("   decimal_precision → 0-10 decimales")
    print("   watermark → Texto de marca de agua")
    print("   compliance_standards → Lista de estándares")


def main():
    """Función principal del demo"""
    print("="*80)
    print("📊 DEMO 5: REPORTES DEFINITIVOS - Todos los Formatos")
    print("="*80)
    print("🚀 ¡La demo completa de TODOS los tipos de reportes disponibles!")
    print()
    print("📚 LO QUE APRENDERÁS:")
    print("   ✅ 8 formatos: HTML, PDF, Excel, CSV, XML, Markdown, JSON, TXT")
    print("   ✅ Parametrización simple y clara")
    print("   ✅ Casos de uso reales para cada formato")
    print("   ✅ Personalización: empresa, idiomas, filtros")
    print("   ✅ Compliance: ISO, ANSI, OSHA, etc.")
    print()
    
    # Crear directorio base
    base_dir = Path("demo/outputs/05_reports")
    base_dir.mkdir(exist_ok=True, parents=True)
    
    # Ejecutar todos los ejemplos
    ejemplo_1_basico()
    ejemplo_2_html_profesional()
    ejemplo_3_documentos_oficiales()
    ejemplo_4_datos_y_excel()
    ejemplo_5_multiidioma()
    ejemplo_6_filtros_avanzados()
    ejemplo_7_casos_especiales()
    
    # Resumen final
    print("\n" + "="*80)
    print("🎉 ¡DEMO COMPLETADA! - Resumen de Archivos Generados")
    print("="*80)
    
    # Contar archivos generados
    total_files = 0
    formats = {}
    
    for subdir in base_dir.iterdir():
        if subdir.is_dir():
            files = list(subdir.glob("*"))
            total_files += len(files)
            print(f"\n📁 {subdir.name}/")
            for file in files:
                ext = file.suffix.upper() or "DIR"
                formats[ext] = formats.get(ext, 0) + 1
                print(f"   📄 {file.name}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   📄 Total de archivos: {total_files}")
    print(f"   📁 Formatos:")
    for fmt, count in sorted(formats.items()):
        print(f"      {fmt}: {count} archivos")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"   1. Abre los archivos HTML en tu navegador")
    print(f"   2. Importa los CSV a Excel o Power BI")
    print(f"   3. Usa los XML para máquinas CNC")
    print(f"   4. Personaliza los ReportConfig para tus necesidades")
    print(f"   5. Integra en tu sistema de producción")
    
    print(f"\n📁 Todos los archivos en: {base_dir.absolute()}")
    print("\n🚀 ¡Ahora ya sabes generar CUALQUIER tipo de reporte!")


if __name__ == "__main__":
    main() 