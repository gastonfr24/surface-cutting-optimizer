# 🏭 Surface Cutting Optimizer - DEMOS
**Demos Industriales para Optimización de Corte 2D**

Bienvenido a la colección completa de demos del Surface Cutting Optimizer. Cada demo está diseñado para mostrar diferentes aspectos y capacidades del sistema de optimización.

---

## 📋 ÍNDICE DE DEMOS

### 🎯 **DEMO 1: Ejemplo Básico con CSV**
- **Archivo**: `01_simple_csv_demo.py`
- **Propósito**: INTRODUCCIÓN AL SISTEMA con casos básicos
- **Duración**: ~30 segundos
- **Datos**: Archivo CSV simple con 3 órdenes y 2 paneles
- **Funcionalidades**: 
  - Lectura automática de archivos CSV
  - Optimización básica con algoritmo First Fit
  - Visualización automática de resultados
  - Métricas básicas de eficiencia
- **Ideal para**: Primeros pasos, validación del sistema, demos rápidos

---

### 🏢 **DEMO 2: Múltiples Materiales y Stocks**
- **Archivo**: `02_multi_stock_demo.py`
- **Propósito**: GESTIÓN MULTI-MATERIAL con diferentes tipos de paneles
- **Duración**: ~45 segundos
- **Datos**: 4 materiales diferentes, 15 órdenes, validación por material
- **Funcionalidades**:
  - Gestión de múltiples tipos de materiales (vidrio, metal, madera, plástico)
  - Validación automática material-panel
  - Análisis por tipo de material
  - Costos diferenciados por material
- **Ideal para**: Empresas con múltiples líneas de producción, fábricas diversificadas

---

### ⚠️ **DEMO 3: Gestión de Overflow**
- **Archivo**: `03_overflow_demo.py`
- **Propósito**: GESTIÓN DE CAPACIDAD INSUFICIENTE y órdenes no cumplidas
- **Duración**: ~1 minuto
- **Datos**: Escenario con demanda > capacidad de stock
- **Funcionalidades**:
  - Detección automática de overflow
  - Priorización de órdenes más importantes
  - Reportes de órdenes no cumplidas
  - Estrategias de optimización con limitaciones
- **Ideal para**: Planificación de producción, gestión de crisis, análisis de capacidad

---

### 🔥 **DEMO 4: Optimización por Prioridades**
- **Archivo**: `04_priority_sorting_demo.py`
- **Propósito**: GESTIÓN INTELIGENTE DE PRIORIDADES con múltiples criterios
- **Duración**: ~1 minuto
- **Datos**: Órdenes con diferentes niveles de prioridad y fechas límite
- **Funcionalidades**:
  - 4 niveles de prioridad (LOW, MEDIUM, HIGH, URGENT)
  - Algoritmos de ordenamiento inteligente
  - Gestión de fechas límite
  - Optimización orientada a urgencias
- **Ideal para**: Producción just-in-time, gestión de urgencias, planificación estratégica

---

### 📊 **DEMO 5: REPORTES DEFINITIVOS - Todos los Formatos** ⭐
- **Archivo**: `05_reports_and_charts_demo.py`
- **Propósito**: 🚀 **LA DEMO DEFINITIVA DE REPORTES** - Todos los formatos y configuraciones
- **Duración**: ~3 minutos
- **Datos**: Escenario complejo con múltiples materiales, prioridades y clientes
- **Funcionalidades**:
  - ✅ **8 FORMATOS**: HTML, PDF, Excel, CSV, XML, Markdown, JSON, TXT
  - ✅ **PARAMETRIZACIÓN SIMPLE**: Ejemplos progresivos de básico a avanzado
  - ✅ **4 IDIOMAS**: Español, Inglés, Francés, Portugués
  - ✅ **10 CASOS DE USO**: CNC, Contabilidad, Presentación, Auditoría, etc.
  - ✅ **PERSONALIZACIÓN TOTAL**: Empresa, proyectos, marcas de agua, compliance
  - ✅ **FILTROS AVANZADOS**: Material, prioridad, cliente, eficiencia
  - ✅ **7 EJEMPLOS CLAROS**: De básico a casos especiales
  - ✅ **HTML PROFESIONAL**: Diseño empresarial con CSS avanzado
  - ✅ **COMPLIANCE**: ISO 9001, ISO 14001, ANSI, ASTM, OSHA
  - ✅ **SEGURIDAD**: 4 niveles de confidencialidad
- **Archivos generados**: 15+ reportes en diferentes formatos
- **Ideal para**: ¡TODOS! Desde principiantes hasta empresas internacionales

---

## 🏗️ **DEMOS AVANZADOS** (Subdirectorio `/advanced/`)

### 🧬 **Algoritmos Híbridos**
- **Archivo**: `advanced/hybrid_optimization_demo.py`
- **Propósito**: Algoritmos de optimización avanzados con múltiples técnicas
- **Funcionalidades**: Algoritmos genéticos, recocido simulado, optimización híbrida

### 📈 **Análisis de Impacto**  
- **Archivo**: `advanced/impact_analysis_demo.py`
- **Propósito**: Análisis profundo del impacto de optimización en costos y eficiencia
- **Funcionalidades**: Análisis comparativo, métricas avanzadas, proyecciones

---

## 🚀 **CÓMO EJECUTAR LOS DEMOS**

### Opción 1: Demo Individual
```bash
cd demo
python 01_simple_csv_demo.py
```

### Opción 2: Demo Específico
```bash
python demo/05_reports_and_charts_demo.py
```

### Opción 3: Demo Rápido (Básico)
```bash
python demo/quick_example.py
```

---

## 📁 **ESTRUCTURA DE ARCHIVOS GENERADOS**

Cada demo genera archivos en su directorio correspondiente:

```
demo/data/
├── 01_simple/          # CSV básico
│   ├── results/         # Visualizaciones
│   ├── simple_orders.csv
│   └── simple_stock.csv
├── 02_multi/           # Multi-material
│   └── results/
└── 05_reports/         # ⭐ REPORTES DEFINITIVOS
    ├── 01_basicos/      # Reportes legacy (JSON)
    ├── 02_html/         # HTML profesionales
    ├── 03_oficiales/    # PDF, XML, Markdown
    ├── 04_datos/        # CSV, Excel
    ├── 05_multiidioma/  # Múltiples idiomas
    ├── 06_filtros/      # Filtros avanzados
    └── 07_especiales/   # Casos especiales
```

---

## 🎯 **PROGRESIÓN RECOMENDADA**

1. **Principiante**: Demo 1 → Demo 2 → Demo 3
2. **Intermedio**: Demo 4 → Demo 5 (ejemplos básicos)
3. **Avanzado**: Demo 5 (ejemplos avanzados) → Demos `/advanced/`
4. **Empresarial**: Demo 5 (casos especiales) + análisis personalizados

---

## 💡 **NOTAS IMPORTANTES**

- **Tiempo total**: ~10-15 minutos para todos los demos
- **Espacio requerido**: ~50MB para todos los archivos generados
- **Dependencias opcionales**: 
  - `openpyxl` para reportes Excel
  - `reportlab` para PDFs avanzados
  - `matplotlib` para visualizaciones (incluido)
- **Compatibilidad**: Windows, macOS, Linux
- **Python**: 3.8+ recomendado

---

## 🔧 **PERSONALIZACIÓN**

Cada demo puede ser modificado para:
- ✅ Cambiar algoritmos de optimización
- ✅ Ajustar parámetros de configuración  
- ✅ Modificar datos de entrada
- ✅ Personalizar formatos de salida
- ✅ Adaptar a casos de uso específicos

---

## 📞 **SOPORTE**

¿Preguntas sobre los demos?
- 📧 Revisa la documentación en `/docs/`
- 🐛 Reporta issues en GitHub
- 💬 Consulta ejemplos adicionales en `/test/`

---

¡Disfruta explorando las capacidades del Surface Cutting Optimizer! 🚀 