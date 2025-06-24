"""
Advanced Report Generator for Surface Cutting Optimizer
Professional reporting with HTML, charts, and analytics
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import csv

from ..core.models import Stock, Order, CuttingResult, MaterialType, Priority
from ..utils.logging import get_logger


class ReportFormat(Enum):
    """Supported report formats"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    XML = "xml"
    MARKDOWN = "markdown"
    TXT = "txt"


class ReportLanguage(Enum):
    """Supported languages"""
    SPANISH = "es"
    ENGLISH = "en"
    FRENCH = "fr"
    PORTUGUESE = "pt"
    GERMAN = "de"
    ITALIAN = "it"
    CHINESE = "zh"
    JAPANESE = "ja"


class ReportUsage(Enum):
    """Report usage types"""
    CNC_MACHINE = "cnc"
    ACCOUNTING = "accounting"
    PRESENTATION = "presentation"
    AUDIT = "audit"
    PRODUCTION = "production"
    ENGINEERING = "engineering"
    MANAGEMENT = "management"
    QUALITY_CONTROL = "quality"
    CUSTOMER = "customer"
    REGULATORY = "regulatory"


class UnitSystem(Enum):
    """Measurement unit systems"""
    METRIC = "metric"      # mm, cm, m
    IMPERIAL = "imperial"  # inches, feet
    CUSTOM = "custom"      # user defined


class ComplianceStandard(Enum):
    """Industry compliance standards"""
    ISO_9001 = "iso_9001"
    ISO_14001 = "iso_14001"
    CE_MARKING = "ce_marking"
    ANSI = "ansi"
    DIN = "din"
    JIS = "jis"
    ASTM = "astm"
    OSHA = "osha"


@dataclass
class FilterCriteria:
    """Advanced filtering criteria for reports"""
    materials: Optional[List[MaterialType]] = None
    priorities: Optional[List[Priority]] = None
    min_area: Optional[float] = None  # mm²
    max_area: Optional[float] = None  # mm²
    min_efficiency: Optional[float] = None  # %
    max_efficiency: Optional[float] = None  # %
    stock_ids: Optional[List[str]] = None
    order_ids: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    customer_ids: Optional[List[str]] = None
    exclude_materials: Optional[List[MaterialType]] = None
    only_fulfilled: bool = False
    only_unfulfilled: bool = False


@dataclass
class CompanyInfo:
    """Company information for report headers"""
    name: str = "Your Company"
    logo_path: Optional[str] = None
    address: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    registration_number: str = ""
    tax_id: str = ""
    certifications: List[str] = field(default_factory=list)


@dataclass
class ProjectInfo:
    """Project information for reports"""
    name: str = "Optimization Project"
    code: str = ""
    description: str = ""
    client: str = ""
    manager: str = ""
    deadline: Optional[datetime] = None
    budget: Optional[float] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ReportConfig:
    """Advanced report configuration"""
    
    # Basic settings
    format: ReportFormat = ReportFormat.JSON
    language: ReportLanguage = ReportLanguage.ENGLISH
    usage: ReportUsage = ReportUsage.PRESENTATION
    
    # Customization
    company_info: Optional[CompanyInfo] = None
    project_info: Optional[ProjectInfo] = None
    
    # Filtering
    filters: Optional[FilterCriteria] = None
    
    # Standards and compliance
    unit_system: UnitSystem = UnitSystem.METRIC
    decimal_precision: int = 2
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    
    # Content options
    include_charts: bool = True
    include_recommendations: bool = True
    include_benchmarks: bool = True
    include_cost_analysis: bool = True
    include_cutting_instructions: bool = True
    include_material_details: bool = True
    include_timeline: bool = False
    include_photos: bool = False
    include_signatures: bool = False
    
    # Technical settings
    page_size: str = "A4"  # A4, Letter, A3, etc.
    orientation: str = "portrait"  # portrait, landscape
    font_family: str = "Arial"
    font_size: int = 11
    watermark: Optional[str] = None
    
    # Security and traceability
    include_qr_code: bool = False
    include_barcode: bool = False
    digital_signature: bool = False
    confidentiality_level: str = "public"  # public, internal, confidential, restricted
    
    # Export options
    compress_output: bool = False
    password_protect: bool = False
    password: Optional[str] = None
    
    def get_translations(self) -> Dict[str, str]:
        """Get translations for the selected language"""
        translations = {
            ReportLanguage.ENGLISH: {
                "title": "Cutting Optimization Report",
                "efficiency": "Efficiency",
                "cost": "Cost",
                "material": "Material",
                "recommendations": "Recommendations",
                "summary": "Summary",
                "details": "Details",
                "date": "Date",
                "generated_by": "Generated by",
                "page": "Page",
                "total_area": "Total Area",
                "waste": "Waste",
                "stocks_used": "Stocks Used",
                "orders_fulfilled": "Orders Fulfilled",
                "cutting_time": "Cutting Time",
                "algorithm": "Algorithm"
            },
            ReportLanguage.SPANISH: {
                "title": "Reporte de Optimización de Corte",
                "efficiency": "Eficiencia",
                "cost": "Costo",
                "material": "Material",
                "recommendations": "Recomendaciones",
                "summary": "Resumen",
                "details": "Detalles",
                "date": "Fecha",
                "generated_by": "Generado por",
                "page": "Página",
                "total_area": "Área Total",
                "waste": "Desperdicio",
                "stocks_used": "Paneles Usados",
                "orders_fulfilled": "Órdenes Cumplidas",
                "cutting_time": "Tiempo de Corte",
                "algorithm": "Algoritmo"
            },
            ReportLanguage.FRENCH: {
                "title": "Rapport d'Optimisation de Découpe",
                "efficiency": "Efficacité",
                "cost": "Coût",
                "material": "Matériau",
                "recommendations": "Recommandations",
                "summary": "Résumé",
                "details": "Détails",
                "date": "Date",
                "generated_by": "Généré par",
                "page": "Page",
                "total_area": "Surface Totale",
                "waste": "Perte",
                "stocks_used": "Stocks Utilisés",
                "orders_fulfilled": "Commandes Remplies",
                "cutting_time": "Temps de Découpe",
                "algorithm": "Algorithme"
            }
        }
        return translations.get(self.language, translations[ReportLanguage.ENGLISH])
    
    def convert_units(self, value_mm: float, unit_type: str = "length") -> tuple[float, str]:
        """Convert from mm to target unit system"""
        if self.unit_system == UnitSystem.IMPERIAL:
            if unit_type == "length":
                return value_mm / 25.4, "in"
            elif unit_type == "area":
                return value_mm / (25.4 * 25.4), "in²"
        elif self.unit_system == UnitSystem.METRIC:
            if unit_type == "length":
                return value_mm, "mm"
            elif unit_type == "area":
                return value_mm, "mm²"
        
        return value_mm, "mm"  # Default fallback


@dataclass
class CuttingReport:
    """Main cutting report structure"""
    title: str
    generation_date: datetime
    optimization_result: CuttingResult
    stocks: List[Stock]
    orders: List[Order]
    metadata: Dict[str, Any]


@dataclass  
class PerformanceReport:
    """Performance analysis report"""
    efficiency_metrics: Dict[str, float]
    cost_analysis: Dict[str, float]
    fulfillment_analysis: Dict[str, Any]
    waste_analysis: Dict[str, float]
    optimization_time: float
    
    
@dataclass
class MaterialReport:
    """Material utilization report"""
    material_breakdown: Dict[str, Dict[str, Any]]
    waste_by_material: Dict[str, float]
    cost_by_material: Dict[str, float]
    efficiency_by_material: Dict[str, float]


@dataclass
class CuttingCoordinatesReport:
    """Cutting coordinates report for CNC/cutting machines"""
    cutting_plan: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generation_date: datetime


@dataclass
class AdvancedAnalyticsReport:
    """Advanced analytics and insights report"""
    efficiency_grade: str
    cost_grade: str
    recommendations: List[str]
    performance_benchmarks: Dict[str, Any]
    optimization_insights: Dict[str, Any]
    improvement_suggestions: List[str]


class ReportGenerator:
    """Advanced report generator with multiple formats and analytics"""
    
    def __init__(self):
        self.logger = get_logger()
        
    def generate_cutting_report(self, result: CuttingResult, stocks: List[Stock], 
                               orders: List[Order], title: str = "Cutting Report") -> CuttingReport:
        """Generate main cutting report"""
        
        return CuttingReport(
            title=title,
            generation_date=datetime.now(),
            optimization_result=result,
            stocks=stocks,
            orders=orders,
            metadata={
                "total_stocks": len(stocks),
                "total_orders": len(orders),
                "efficiency": result.efficiency_percentage,
                "fulfillment_rate": result.fulfillment_rate
            }
        )
    
    def apply_filters(self, result: CuttingResult, stocks: List[Stock], 
                     orders: List[Order], filters: FilterCriteria) -> tuple[CuttingResult, List[Stock], List[Order]]:
        """Apply filtering criteria to data"""
        
        filtered_stocks = stocks.copy()
        filtered_orders = orders.copy()
        filtered_placed_shapes = result.placed_shapes.copy()
        
        # Filter by materials
        if filters.materials:
            filtered_stocks = [s for s in filtered_stocks if s.material_type in filters.materials]
            filtered_orders = [o for o in filtered_orders if o.material_type in filters.materials]
            filtered_placed_shapes = [ps for ps in filtered_placed_shapes 
                                    if any(s.id == ps.stock_id and s.material_type in filters.materials 
                                          for s in stocks)]
        
        # Filter by priorities
        if filters.priorities:
            filtered_orders = [o for o in filtered_orders if o.priority in filters.priorities]
            order_ids = {o.id for o in filtered_orders}
            filtered_placed_shapes = [ps for ps in filtered_placed_shapes 
                                    if ps.order_id.split('_')[0] in order_ids]
        
        # Filter by area
        if filters.min_area or filters.max_area:
            def area_filter(order):
                area = order.total_area
                if filters.min_area and area < filters.min_area:
                    return False
                if filters.max_area and area > filters.max_area:
                    return False
                return True
            
            filtered_orders = [o for o in filtered_orders if area_filter(o)]
        
        # Filter by stock IDs
        if filters.stock_ids:
            filtered_stocks = [s for s in filtered_stocks if s.id in filters.stock_ids]
            filtered_placed_shapes = [ps for ps in filtered_placed_shapes if ps.stock_id in filters.stock_ids]
        
        # Filter by order IDs
        if filters.order_ids:
            filtered_orders = [o for o in filtered_orders if o.id in filters.order_ids]
            order_ids_set = set(filters.order_ids)
            filtered_placed_shapes = [ps for ps in filtered_placed_shapes 
                                    if ps.order_id.split('_')[0] in order_ids_set]
        
        # Create filtered result
        filtered_result = CuttingResult(
            total_stock_used=len(set(ps.stock_id for ps in filtered_placed_shapes)),
            total_orders_fulfilled=len(set(ps.order_id.split('_')[0] for ps in filtered_placed_shapes)),
            total_waste_area=result.total_waste_area,
            efficiency_percentage=result.efficiency_percentage,
            placed_shapes=filtered_placed_shapes,
            unfulfilled_orders=result.unfulfilled_orders,
            algorithm_used=result.algorithm_used,
            computation_time=result.computation_time,
            metadata=result.metadata,
            optimization_date=result.optimization_date,
            total_cost=result.total_cost,
            estimated_cutting_time=result.estimated_cutting_time
        )
        
        return filtered_result, filtered_stocks, filtered_orders
    
    def generate_advanced_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                               config: ReportConfig, output_path: str) -> str:
        """
        Generate advanced report with full customization
        
        Args:
            result: Optimization result
            stocks: Stock materials
            orders: Orders list
            config: Report configuration
            output_path: Output file path
            
        Returns:
            Path to generated report
        """
        
        # Apply filters if specified
        if config.filters:
            result, stocks, orders = self.apply_filters(result, stocks, orders, config.filters)
        
        # Generate based on format
        if config.format == ReportFormat.HTML:
            return self._generate_html_report(result, stocks, orders, config, output_path)
        elif config.format == ReportFormat.PDF:
            return self._generate_pdf_report(result, stocks, orders, config, output_path)
        elif config.format == ReportFormat.EXCEL:
            return self._generate_excel_report(result, stocks, orders, config, output_path)
        elif config.format == ReportFormat.CSV:
            return self._generate_csv_report(result, stocks, orders, config, output_path)
        elif config.format == ReportFormat.XML:
            return self._generate_xml_report(result, stocks, orders, config, output_path)
        elif config.format == ReportFormat.MARKDOWN:
            return self._generate_markdown_report(result, stocks, orders, config, output_path)
        elif config.format == ReportFormat.TXT:
            return self._generate_txt_report(result, stocks, orders, config, output_path)
        else:  # JSON
            return self._generate_json_report(result, stocks, orders, config, output_path)
    
    def _generate_html_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                            config: ReportConfig, output_path: str) -> str:
        """Generate enhanced HTML report with full professional content"""
        
        # Use the comprehensive export_to_html method but adapt it to our config
        title_parts = []
        if config.company_info:
            title_parts.append(config.company_info.name)
        if config.project_info:
            title_parts.append(config.project_info.name)
        title_parts.append("Cutting Optimization Report")
        title = " - ".join(title_parts)
        
        # Generate all detailed reports
        perf_report = self.generate_performance_report(result)
        material_report = self.generate_material_report(result, stocks)
        coords_report = self.generate_cutting_coordinates_report(result, stocks)
        analytics_report = self.generate_advanced_analytics(result, stocks, orders)
        
        translations = config.get_translations()
        company = config.company_info or CompanyInfo()
        project = config.project_info or ProjectInfo()
        
        # Convert units function
        def format_value(value, unit_type="length"):
            converted, unit = config.convert_units(value, unit_type)
            return f"{converted:.{config.decimal_precision}f} {unit}"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="{config.language.value}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .company-info {{
            text-align: left;
        }}
        .company-name {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin: 0;
        }}
        .project-info {{
            text-align: right;
        }}
        .project-name {{
            font-size: 1.5em;
            font-weight: bold;
            color: #3498db;
            margin: 0;
        }}
        .confidentiality {{
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
            text-transform: uppercase;
            margin-top: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .section h2 {{
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.5em;
        }}
        .grade {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .grade-A {{ background-color: #27ae60; }}
        .grade-B {{ background-color: #2ecc71; }}
        .grade-C {{ background-color: #f39c12; }}
        .grade-D {{ background-color: #e74c3c; }}
        .grade-F {{ background-color: #c0392b; }}
        .recommendations {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 5px;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .table th, .table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .table th {{
            background-color: #34495e;
            color: white;
        }}
        .table tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart-placeholder {{
            background: #ecf0f1;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 5px;
            margin: 15px 0;
            color: #7f8c8d;
        }}
        .compliance {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 6em;
            color: rgba(0,0,0,0.05);
            z-index: -1;
            pointer-events: none;
        }}
        @media print {{
            .container {{ box-shadow: none; }}
            body {{ background: white; }}
        }}
    </style>
</head>
<body>
    {"<div class='watermark'>" + config.watermark + "</div>" if config.watermark else ""}
    
    <div class="container">
        <div class="header">
            <div class="company-info">
                <h1 class="company-name">{company.name}</h1>
                <p>{company.address}</p>
                {"<p>" + company.phone + " | " + company.email + "</p>" if company.phone or company.email else ""}
                {"<div class='confidentiality'>" + config.confidentiality_level.upper() + "</div>" if config.confidentiality_level != "public" else ""}
            </div>
            <div class="project-info">
                <h2 class="project-name">{project.name}</h2>
                <p>{translations['date']}: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                {"<p>Manager: " + project.manager + "</p>" if project.manager else ""}
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{result.efficiency_percentage:.1f}%</div>
                <div class="metric-label">{translations['efficiency']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result.fulfillment_rate:.1f}%</div>
                <div class="metric-label">Order Fulfillment</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{format_value(result.total_cost, 'cost')}</div>
                <div class="metric-label">{translations['cost']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result.computation_time:.3f}s</div>
                <div class="metric-label">Processing Time</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Performance Analysis</h2>
            <p><strong>Efficiency Grade:</strong> <span class="grade grade-{analytics_report.efficiency_grade}">{analytics_report.efficiency_grade}</span></p>
            <p><strong>Cost Grade:</strong> <span class="grade grade-{analytics_report.cost_grade}">{analytics_report.cost_grade}</span></p>
            <p><strong>Algorithm Used:</strong> {result.algorithm_used}</p>
            <p><strong>vs Industry Average:</strong> {analytics_report.performance_benchmarks['performance_vs_industry']:+.1f}% efficiency</p>
            
            <div class="chart-placeholder">
                📊 Efficiency Chart (Can be enhanced with Chart.js)
            </div>
        </div>
        
        <div class="section">
            <h2>Material Breakdown</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Material</th>
                        <th>Efficiency</th>
                        <th>Cost</th>
                        <th>Pieces</th>
                        <th>Waste</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add material data
        for material, efficiency in material_report.efficiency_by_material.items():
            cost = material_report.cost_by_material.get(material, 0)
            waste = material_report.waste_by_material.get(material, 0)
            pieces = material_report.material_breakdown.get(material, {}).get('pieces', 0)
            
            html_content += f"""
                    <tr>
                        <td>{material.title()}</td>
                        <td>{efficiency:.1f}%</td>
                        <td>{format_value(cost, 'cost')}</td>
                        <td>{pieces}</td>
                        <td>{waste:.1f}%</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
"""
        
        # Add compliance section if standards are specified
        if config.compliance_standards:
            html_content += f"""
        <div class="section">
            <h2>Compliance & Standards</h2>
            <div class="compliance">
                <h3>Applied Standards:</h3>
                <ul>
"""
            for standard in config.compliance_standards:
                html_content += f"<li>{standard.value.upper().replace('_', ' ')}</li>"
            
            html_content += """
                </ul>
            </div>
        </div>
"""
        
        # Add recommendations section
        html_content += f"""
        <div class="section">
            <h2>{translations['recommendations']}</h2>
            <div class="recommendations">
                <h3>Optimization Recommendations:</h3>
                <ul>
"""
        
        for rec in analytics_report.recommendations:
            html_content += f"<li>{rec}</li>"
        
        html_content += """
                </ul>
                <h3>Improvement Suggestions:</h3>
                <ul>
"""
        
        for suggestion in analytics_report.improvement_suggestions:
            html_content += f"<li>{suggestion}</li>"
        
        html_content += f"""
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>Cutting Summary</h2>
            <p><strong>Total Cuts:</strong> {coords_report.summary['total_cuts']}</p>
            <p><strong>Sheets Used:</strong> {coords_report.summary['sheets_used']}</p>
            <p><strong>Estimated Cut Time:</strong> {coords_report.summary['total_cut_time_min']:.1f} minutes</p>
            <p><strong>Total Perimeter:</strong> {coords_report.summary['total_perimeter_mm']:,.0f} mm</p>
        </div>
        
        <div class="section">
            <h2>Technical Details</h2>
            <p><strong>Generation Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Software:</strong> Surface Cutting Optimizer v1.0.0</p>
            <p><strong>Report Format:</strong> Advanced HTML Report</p>
            {"<p><strong>Document ID:</strong> " + str(hash(output_path))[:8] + "</p>" if config.include_qr_code else ""}
        </div>
        
        <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #7f8c8d;">
            <p>{translations['generated_by']} Surface Cutting Optimizer v1.0.0</p>
            <p>{translations['date']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def _generate_json_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                            config: ReportConfig, output_path: str) -> str:
        """Generate enhanced JSON report with customization"""
        
        translations = config.get_translations()
        company = config.company_info or CompanyInfo()
        project = config.project_info or ProjectInfo()
        
        # Build comprehensive report data
        report_data = {
            "metadata": {
                "title": f"{project.name} - {translations['title']}",
                "generation_date": datetime.now().isoformat(),
                "language": config.language.value,
                "unit_system": config.unit_system.value,
                "confidentiality": config.confidentiality_level,
                "company": {
                    "name": company.name,
                    "address": company.address,
                    "contact": {
                        "phone": company.phone,
                        "email": company.email,
                        "website": company.website
                    }
                },
                "project": {
                    "name": project.name,
                    "code": project.code,
                    "description": project.description,
                    "client": project.client,
                    "manager": project.manager,
                    "tags": project.tags
                }
            },
            "summary": {
                "efficiency_percentage": result.efficiency_percentage,
                "total_cost": result.total_cost,
                "stocks_used": result.total_stock_used,
                "orders_fulfilled": result.total_orders_fulfilled,
                "computation_time": result.computation_time,
                "algorithm": result.algorithm_used,
                "optimization_date": result.optimization_date.isoformat()
            }
        }
        
        # Add detailed sections based on config
        if config.include_cutting_instructions:
            coords_report = self.generate_cutting_coordinates_report(result, stocks)
            report_data["cutting_instructions"] = {
                "summary": coords_report.summary,
                "cutting_plan": coords_report.cutting_plan
            }
        
        if config.include_cost_analysis:
            perf_report = self.generate_performance_report(result)
            report_data["cost_analysis"] = perf_report.cost_analysis
        
        if config.include_material_details:
            material_report = self.generate_material_report(result, stocks)
            report_data["material_analysis"] = {
                "breakdown": material_report.material_breakdown,
                "efficiency_by_material": material_report.efficiency_by_material,
                "cost_by_material": material_report.cost_by_material
            }
        
        if config.include_recommendations:
            analytics = self.generate_advanced_analytics(result, stocks, orders)
            report_data["analytics"] = {
                "efficiency_grade": analytics.efficiency_grade,
                "cost_grade": analytics.cost_grade,
                "recommendations": analytics.recommendations,
                "insights": analytics.optimization_insights,
                "benchmarks": analytics.performance_benchmarks
            }
        
        # Add compliance information
        if config.compliance_standards:
            report_data["compliance"] = {
                "standards": [std.value for std in config.compliance_standards],
                "traceability": {
                    "document_id": str(hash(output_path))[:8],
                    "version": "1.0",
                    "audit_trail": f"Generated on {datetime.now().isoformat()}"
                }
            }
        
        # Save file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=config.decimal_precision, ensure_ascii=False)
        
        return str(output_file)
    
    def _generate_pdf_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                           config: ReportConfig, output_path: str) -> str:
        """Generate PDF report (requires reportlab)"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            # Create PDF
            doc = SimpleDocTemplate(str(output_path), pagesize=A4 if config.page_size == "A4" else letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            translations = config.get_translations()
            title = Paragraph(f"{config.project_info.name if config.project_info else 'Project'} - {translations['title']}", 
                            styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Summary table
            summary_data = [
                [translations['efficiency'], f"{result.efficiency_percentage:.1f}%"],
                [translations['cost'], f"${result.total_cost:.2f}"],
                [translations['stocks_used'], str(result.total_stock_used)],
                [translations['algorithm'], result.algorithm_used]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            doc.build(story)
            
            return str(output_path)
            
        except ImportError:
            # Fallback to HTML if reportlab not available
            html_path = output_path.replace('.pdf', '.html')
            return self._generate_html_report(result, stocks, orders, config, html_path)
    
    def _generate_xml_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                           config: ReportConfig, output_path: str) -> str:
        """Generate XML report"""
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        translations = config.get_translations()
        
        # Create root element
        root = ET.Element("cutting_optimization_report")
        root.set("version", "1.0")
        root.set("language", config.language.value)
        root.set("generated", datetime.now().isoformat())
        
        # Metadata
        metadata = ET.SubElement(root, "metadata")
        if config.company_info:
            company = ET.SubElement(metadata, "company")
            ET.SubElement(company, "name").text = config.company_info.name
            ET.SubElement(company, "address").text = config.company_info.address
        
        if config.project_info:
            project = ET.SubElement(metadata, "project")
            ET.SubElement(project, "name").text = config.project_info.name
            ET.SubElement(project, "code").text = config.project_info.code
        
        # Summary
        summary = ET.SubElement(root, "summary")
        ET.SubElement(summary, "efficiency").text = str(result.efficiency_percentage)
        ET.SubElement(summary, "total_cost").text = str(result.total_cost)
        ET.SubElement(summary, "stocks_used").text = str(result.total_stock_used)
        ET.SubElement(summary, "orders_fulfilled").text = str(result.total_orders_fulfilled)
        ET.SubElement(summary, "algorithm").text = result.algorithm_used
        ET.SubElement(summary, "computation_time").text = str(result.computation_time)
        
        # Cutting instructions if enabled
        if config.include_cutting_instructions:
            cutting = ET.SubElement(root, "cutting_instructions")
            coords_report = self.generate_cutting_coordinates_report(result, stocks)
            
            for cut in coords_report.cutting_plan:
                cut_elem = ET.SubElement(cutting, "cut")
                cut_elem.set("id", cut["cut_id"])
                ET.SubElement(cut_elem, "order_id").text = cut["order_id"]
                ET.SubElement(cut_elem, "stock_id").text = cut["stock_id"]
                ET.SubElement(cut_elem, "position_x").text = str(cut["position_x_mm"])
                ET.SubElement(cut_elem, "position_y").text = str(cut["position_y_mm"])
                ET.SubElement(cut_elem, "width").text = str(cut["width_mm"])
                ET.SubElement(cut_elem, "height").text = str(cut["height_mm"])
        
        # Compliance if standards specified
        if config.compliance_standards:
            compliance = ET.SubElement(root, "compliance")
            for standard in config.compliance_standards:
                std_elem = ET.SubElement(compliance, "standard")
                std_elem.text = standard.value
        
        # Pretty print and save
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return str(output_file)
    
    def _generate_markdown_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                                config: ReportConfig, output_path: str) -> str:
        """Generate Markdown report"""
        
        translations = config.get_translations()
        company = config.company_info or CompanyInfo()
        project = config.project_info or ProjectInfo()
        
        markdown_content = f"""# {project.name} - {translations['title']}

**{translations['generated_by']}:** Surface Cutting Optimizer v1.0.0  
**{translations['date']}:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Company:** {company.name}

## {translations['summary']}

| Metric | Value |
|--------|-------|
| {translations['efficiency']} | {result.efficiency_percentage:.1f}% |
| {translations['cost']} | ${result.total_cost:.2f} |
| {translations['stocks_used']} | {result.total_stock_used} |
| {translations['orders_fulfilled']} | {result.total_orders_fulfilled} |
| {translations['algorithm']} | {result.algorithm_used} |
| Computation Time | {result.computation_time:.3f}s |

"""
        
        # Add recommendations if enabled
        if config.include_recommendations:
            analytics = self.generate_advanced_analytics(result, stocks, orders)
            markdown_content += f"""## {translations['recommendations']}

"""
            for i, rec in enumerate(analytics.recommendations, 1):
                markdown_content += f"{i}. {rec}\n"
        
        # Add compliance if standards specified
        if config.compliance_standards:
            markdown_content += "\n## Compliance & Standards\n\n"
            for standard in config.compliance_standards:
                markdown_content += f"- {standard.value.upper().replace('_', ' ')}\n"
        
        # Add material details if enabled
        if config.include_material_details:
            material_report = self.generate_material_report(result, stocks)
            markdown_content += f"\n## {translations['material']} Analysis\n\n"
            markdown_content += "| Material | Efficiency | Cost | Waste |\n"
            markdown_content += "|----------|------------|------|-------|\n"
            
            for material, efficiency in material_report.efficiency_by_material.items():
                cost = material_report.cost_by_material.get(material, 0)
                waste = material_report.waste_by_material.get(material, 0)
                markdown_content += f"| {material.title()} | {efficiency:.1f}% | ${cost:.2f} | {waste:.1f}% |\n"
        
        # Save file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(output_file)
    
    def _generate_csv_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                           config: ReportConfig, output_path: str) -> str:
        """Generate CSV report package"""
        
        # Use existing CSV package functionality but with config
        base_path = Path(output_path).parent
        prefix = Path(output_path).stem
        
        return self.export_to_csv_package(result, stocks, orders, str(base_path), prefix)[0]
    
    def _generate_txt_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                           config: ReportConfig, output_path: str) -> str:
        """Generate plain text report"""
        
        translations = config.get_translations()
        company = config.company_info or CompanyInfo()
        project = config.project_info or ProjectInfo()
        
        txt_content = f"""{project.name.upper()} - {translations['title'].upper()}
{'=' * 60}

Company: {company.name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Language: {config.language.value.upper()}

{translations['summary'].upper()}:
{'-' * 20}
{translations['efficiency']}: {result.efficiency_percentage:.1f}%
{translations['cost']}: ${result.total_cost:.2f}
{translations['stocks_used']}: {result.total_stock_used}
{translations['orders_fulfilled']}: {result.total_orders_fulfilled}
{translations['algorithm']}: {result.algorithm_used}
Computation Time: {result.computation_time:.3f}s

"""
        
        # Add recommendations if enabled
        if config.include_recommendations:
            analytics = self.generate_advanced_analytics(result, stocks, orders)
            txt_content += f"{translations['recommendations'].upper()}:\n{'-' * 20}\n"
            for i, rec in enumerate(analytics.recommendations, 1):
                txt_content += f"{i}. {rec}\n"
            txt_content += "\n"
        
        # Add compliance if standards specified
        if config.compliance_standards:
            txt_content += "COMPLIANCE & STANDARDS:\n" + "-" * 20 + "\n"
            for standard in config.compliance_standards:
                txt_content += f"- {standard.value.upper().replace('_', ' ')}\n"
            txt_content += "\n"
        
        # Add footer
        txt_content += f"""
{'=' * 60}
Generated by Surface Cutting Optimizer v1.0.0
Document ID: {str(hash(output_path))[:8]}
Confidentiality: {config.confidentiality_level.upper()}
"""
        
        # Save file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        return str(output_file)
    
    def _generate_excel_report(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                             config: ReportConfig, output_path: str) -> str:
        """Generate Excel report with customization"""
        
        # Use existing Excel functionality but with config
        return self.export_to_excel(result, stocks, orders, output_path)
    
    def generate_performance_report(self, result: CuttingResult) -> PerformanceReport:
        """Generate enhanced performance analysis report"""
        
        return PerformanceReport(
            efficiency_metrics={
                "overall_efficiency": result.efficiency_percentage,
                "waste_percentage": result.waste_percentage,
                "material_utilization": result.efficiency_percentage,
                "computation_speed": 1000 / max(result.computation_time, 0.001),  # operations per second
                "fulfillment_rate": result.fulfillment_rate
            },
            cost_analysis={
                "total_cost": result.total_cost,
                "cost_per_area": result.cost_per_area,
                "cost_efficiency": result.efficiency_percentage / 100.0,
                "waste_cost": result.total_cost * result.waste_percentage / 100.0,
                "savings_potential": result.total_cost * (1 - result.efficiency_percentage / 100.0)
            },
            fulfillment_analysis={
                "fulfillment_rate": result.fulfillment_rate,
                "orders_fulfilled": result.total_orders_fulfilled,
                "orders_pending": len(result.unfulfilled_orders),
                "success_score": result.fulfillment_rate * result.efficiency_percentage / 100.0
            },
            waste_analysis={
                "waste_percentage": result.waste_percentage,
                "total_waste_cost": result.total_cost * result.waste_percentage / 100.0,
                "waste_area": result.total_waste_area,
                "recyclable_percentage": min(85.0, result.efficiency_percentage + 20)  # Estimated
            },
            optimization_time=result.computation_time
        )
    
    def generate_material_report(self, result: CuttingResult, stocks: List[Stock]) -> MaterialReport:
        """Generate enhanced material utilization report"""
        
        stock_dict = {stock.id: stock for stock in stocks}
        material_data = {}
        
        # Analyze by material
        for placed_shape in result.placed_shapes:
            stock = stock_dict.get(placed_shape.stock_id)
            if not stock:
                continue
                
            material = stock.material_type.value
            if material not in material_data:
                material_data[material] = {
                    'used_area': 0,
                    'total_area': 0,
                    'cost': 0,
                    'pieces': 0,
                    'stocks_used': set()
                }
            
            material_data[material]['used_area'] += placed_shape.shape.area()
            material_data[material]['pieces'] += 1
            material_data[material]['stocks_used'].add(stock.id)
        
        # Add stock data
        for stock in stocks:
            if any(ps.stock_id == stock.id for ps in result.placed_shapes):
                material = stock.material_type.value
                if material in material_data:
                    material_data[material]['total_area'] += stock.area
                    material_data[material]['cost'] += stock.total_cost
        
        # Convert sets to counts for serialization
        for material in material_data:
            material_data[material]['stocks_count'] = len(material_data[material]['stocks_used'])
            material_data[material]['stocks_used'] = list(material_data[material]['stocks_used'])
        
        # Calculate metrics
        waste_by_material = {}
        cost_by_material = {}
        efficiency_by_material = {}
        
        for material, data in material_data.items():
            efficiency = (data['used_area'] / data['total_area'] * 100) if data['total_area'] > 0 else 0
            waste = 100 - efficiency
            
            efficiency_by_material[material] = efficiency
            waste_by_material[material] = waste
            cost_by_material[material] = data['cost']
        
        return MaterialReport(
            material_breakdown=material_data,
            waste_by_material=waste_by_material,
            cost_by_material=cost_by_material,
            efficiency_by_material=efficiency_by_material
        )
    
    def generate_cutting_coordinates_report(self, result: CuttingResult, 
                                          stocks: List[Stock]) -> CuttingCoordinatesReport:
        """Generate enhanced cutting coordinates report for CNC/cutting machines"""
        
        cutting_plan = []
        
        for i, placed_shape in enumerate(result.placed_shapes, 1):
            # Get stock info
            stock = next((s for s in stocks if s.id == placed_shape.stock_id), None)
            
            cutting_plan.append({
                "cut_id": f"CUT_{i:03d}",
                "order_id": placed_shape.order_id.split('_')[0],  # Remove _1 suffix
                "stock_id": placed_shape.stock_id,
                "stock_material": stock.material_type.value if stock else "Unknown",
                "position_x_mm": round(placed_shape.shape.x, 1),
                "position_y_mm": round(placed_shape.shape.y, 1),
                "width_mm": round(placed_shape.shape.width, 1),
                "height_mm": round(placed_shape.shape.height, 1),
                "rotation_degrees": placed_shape.rotation_applied,
                "area_mm2": round(placed_shape.shape.area(), 1),
                "cutting_sequence": i,
                "end_x_mm": round(placed_shape.shape.x + placed_shape.shape.width, 1),
                "end_y_mm": round(placed_shape.shape.y + placed_shape.shape.height, 1),
                "perimeter_mm": round(2 * (placed_shape.shape.width + placed_shape.shape.height), 1),
                "estimated_cut_time_min": round(2 * (placed_shape.shape.width + placed_shape.shape.height) / 1000 * 0.5, 2)  # Estimate
            })
        
        total_cut_time = sum(cut['estimated_cut_time_min'] for cut in cutting_plan)
        total_perimeter = sum(cut['perimeter_mm'] for cut in cutting_plan)
        
        summary = {
            "total_cuts": len(cutting_plan),
            "efficiency": round(result.efficiency_percentage, 2),
            "waste": round(100 - result.efficiency_percentage, 2),
            "total_cost": round(result.total_cost, 2),
            "sheets_used": result.total_stock_used,
            "pieces_cut": result.total_orders_fulfilled,
            "total_cut_time_min": round(total_cut_time, 2),
            "total_perimeter_mm": round(total_perimeter, 1),
            "average_piece_area": round(sum(cut['area_mm2'] for cut in cutting_plan) / len(cutting_plan), 1) if cutting_plan else 0
        }
        
        return CuttingCoordinatesReport(
            cutting_plan=cutting_plan,
            summary=summary,
            generation_date=datetime.now()
        )
    
    def generate_advanced_analytics(self, result: CuttingResult, stocks: List[Stock], 
                                  orders: List[Order]) -> AdvancedAnalyticsReport:
        """Generate advanced analytics and recommendations"""
        
        # Calculate performance grades
        efficiency_grade = self._calculate_grade(result.efficiency_percentage, [40, 55, 70, 85])
        cost_efficiency = (result.efficiency_percentage / 100.0) * (result.fulfillment_rate / 100.0)
        cost_grade = self._calculate_grade(cost_efficiency * 100, [30, 50, 70, 85])
        
        # Generate recommendations
        recommendations = []
        improvement_suggestions = []
        
        if result.efficiency_percentage < 60:
            recommendations.append("Consider using a more advanced optimization algorithm")
            improvement_suggestions.append("Try genetic algorithm for better space utilization")
        
        if result.fulfillment_rate < 100:
            recommendations.append("Some orders remain unfulfilled - consider additional stock")
            improvement_suggestions.append("Optimize stock sizes for better order coverage")
        
        if result.computation_time > 5.0:
            recommendations.append("Optimization time is high - consider algorithm tuning")
            improvement_suggestions.append("Use faster algorithms for time-critical operations")
        
        if result.total_cost > 0:
            potential_savings = result.total_cost * (1 - result.efficiency_percentage / 100.0)
            if potential_savings > result.total_cost * 0.2:
                recommendations.append(f"High waste cost detected: ${potential_savings:.2f} in potential savings")
                improvement_suggestions.append("Focus on waste reduction strategies")
        
        # Performance benchmarks
        benchmarks = {
            "industry_average_efficiency": 65.0,
            "good_efficiency_threshold": 70.0,
            "excellent_efficiency_threshold": 85.0,
            "average_computation_time": 2.0,
            "target_fulfillment_rate": 95.0,
            "performance_vs_industry": result.efficiency_percentage - 65.0
        }
        
        # Optimization insights
        insights = {
            "dominant_material": self._get_dominant_material(stocks),
            "largest_order": max((order.total_area for order in orders), default=0),
            "smallest_order": min((order.total_area for order in orders), default=0),
            "order_size_variance": self._calculate_variance([order.total_area for order in orders]),
            "stock_utilization_balance": self._calculate_stock_balance(result, stocks),
            "algorithm_suitability": self._assess_algorithm_suitability(result, stocks, orders)
        }
        
        return AdvancedAnalyticsReport(
            efficiency_grade=efficiency_grade,
            cost_grade=cost_grade,
            recommendations=recommendations,
            performance_benchmarks=benchmarks,
            optimization_insights=insights,
            improvement_suggestions=improvement_suggestions
        )
    
    def export_to_html(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                      output_path: str, title: str = "Professional Cutting Report") -> str:
        """Export comprehensive HTML report with embedded charts"""
        
        # Generate all reports
        perf_report = self.generate_performance_report(result)
        material_report = self.generate_material_report(result, stocks)
        coords_report = self.generate_cutting_coordinates_report(result, stocks)
        analytics_report = self.generate_advanced_analytics(result, stocks, orders)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .date {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .section h2 {{
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.5em;
        }}
        .grade {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .grade-A {{ background-color: #27ae60; }}
        .grade-B {{ background-color: #2ecc71; }}
        .grade-C {{ background-color: #f39c12; }}
        .grade-D {{ background-color: #e74c3c; }}
        .grade-F {{ background-color: #c0392b; }}
        .recommendations {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 5px;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .table th, .table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .table th {{
            background-color: #34495e;
            color: white;
        }}
        .table tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart-placeholder {{
            background: #ecf0f1;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 5px;
            margin: 15px 0;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="date">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{result.efficiency_percentage:.1f}%</div>
                <div class="metric-label">Material Efficiency</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result.fulfillment_rate:.1f}%</div>
                <div class="metric-label">Order Fulfillment</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${result.total_cost:.2f}</div>
                <div class="metric-label">Total Cost</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result.computation_time:.3f}s</div>
                <div class="metric-label">Processing Time</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Performance Analysis</h2>
            <p><strong>Efficiency Grade:</strong> <span class="grade grade-{analytics_report.efficiency_grade}">{analytics_report.efficiency_grade}</span></p>
            <p><strong>Cost Grade:</strong> <span class="grade grade-{analytics_report.cost_grade}">{analytics_report.cost_grade}</span></p>
            <p><strong>Algorithm Used:</strong> {result.algorithm_used}</p>
            <p><strong>vs Industry Average:</strong> {analytics_report.performance_benchmarks['performance_vs_industry']:+.1f}% efficiency</p>
            
            <div class="chart-placeholder">
                📊 Efficiency Chart (Can be enhanced with Chart.js)
            </div>
        </div>
        
        <div class="section">
            <h2>Material Breakdown</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Material</th>
                        <th>Efficiency</th>
                        <th>Cost</th>
                        <th>Pieces</th>
                        <th>Waste</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add material data
        for material, efficiency in material_report.efficiency_by_material.items():
            cost = material_report.cost_by_material.get(material, 0)
            waste = material_report.waste_by_material.get(material, 0)
            pieces = material_report.material_breakdown.get(material, {}).get('pieces', 0)
            
            html_content += f"""
                    <tr>
                        <td>{material.title()}</td>
                        <td>{efficiency:.1f}%</td>
                        <td>${cost:.2f}</td>
                        <td>{pieces}</td>
                        <td>{waste:.1f}%</td>
                    </tr>
"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <div class="recommendations">
                <h3>Optimization Recommendations:</h3>
                <ul>
"""
        
        for rec in analytics_report.recommendations:
            html_content += f"<li>{rec}</li>"
        
        html_content += """
                </ul>
                <h3>Improvement Suggestions:</h3>
                <ul>
"""
        
        for suggestion in analytics_report.improvement_suggestions:
            html_content += f"<li>{suggestion}</li>"
        
        html_content += f"""
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>Cutting Summary</h2>
            <p><strong>Total Cuts:</strong> {coords_report.summary['total_cuts']}</p>
            <p><strong>Sheets Used:</strong> {coords_report.summary['sheets_used']}</p>
            <p><strong>Estimated Cut Time:</strong> {coords_report.summary['total_cut_time_min']:.1f} minutes</p>
            <p><strong>Total Perimeter:</strong> {coords_report.summary['total_perimeter_mm']:,.0f} mm</p>
        </div>
        
        <div class="section">
            <h2>Technical Details</h2>
            <p><strong>Generation Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Software:</strong> Surface Cutting Optimizer v1.0.0</p>
            <p><strong>Report Format:</strong> Advanced HTML Report</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def export_to_excel(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                       output_path: str) -> str:
        """Export comprehensive Excel report (requires openpyxl)"""
        
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            from openpyxl.chart import BarChart, Reference
            
            wb = openpyxl.Workbook()
            
            # Summary sheet
            ws_summary = wb.active
            ws_summary.title = "Summary"
            
            # Add headers and data
            ws_summary['A1'] = "Surface Cutting Optimizer Report"
            ws_summary['A1'].font = Font(size=16, bold=True)
            
            summary_data = [
                ["Metric", "Value"],
                ["Efficiency", f"{result.efficiency_percentage:.1f}%"],
                ["Fulfillment Rate", f"{result.fulfillment_rate:.1f}%"],
                ["Total Cost", f"${result.total_cost:.2f}"],
                ["Processing Time", f"{result.computation_time:.3f}s"],
                ["Algorithm", result.algorithm_used],
                ["Stocks Used", result.total_stock_used],
                ["Orders Fulfilled", result.total_orders_fulfilled]
            ]
            
            for row_idx, row_data in enumerate(summary_data, 3):
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws_summary.cell(row=row_idx, column=col_idx, value=value)
                    if row_idx == 3:  # Header row
                        cell.font = Font(bold=True)
                        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                        cell.font = Font(color="FFFFFF", bold=True)
            
            # Cutting coordinates sheet
            ws_coords = wb.create_sheet("Cutting Coordinates")
            coords_report = self.generate_cutting_coordinates_report(result, stocks)
            
            # Headers
            headers = ["Cut ID", "Order ID", "Stock ID", "Material", "X (mm)", "Y (mm)", 
                      "Width (mm)", "Height (mm)", "Area (mm²)", "Cut Time (min)"]
            
            for col_idx, header in enumerate(headers, 1):
                cell = ws_coords.cell(row=1, column=col_idx, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.font = Font(color="FFFFFF", bold=True)
            
            # Data
            for row_idx, cut_data in enumerate(coords_report.cutting_plan, 2):
                ws_coords.cell(row=row_idx, column=1, value=cut_data['cut_id'])
                ws_coords.cell(row=row_idx, column=2, value=cut_data['order_id'])
                ws_coords.cell(row=row_idx, column=3, value=cut_data['stock_id'])
                ws_coords.cell(row=row_idx, column=4, value=cut_data['stock_material'])
                ws_coords.cell(row=row_idx, column=5, value=cut_data['position_x_mm'])
                ws_coords.cell(row=row_idx, column=6, value=cut_data['position_y_mm'])
                ws_coords.cell(row=row_idx, column=7, value=cut_data['width_mm'])
                ws_coords.cell(row=row_idx, column=8, value=cut_data['height_mm'])
                ws_coords.cell(row=row_idx, column=9, value=cut_data['area_mm2'])
                ws_coords.cell(row=row_idx, column=10, value=cut_data['estimated_cut_time_min'])
            
            # Save file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            wb.save(output_file)
            
            return str(output_file)
            
        except ImportError:
            print("Warning: openpyxl not available. Cannot generate Excel report.")
            return ""
    
    def export_to_csv_package(self, result: CuttingResult, stocks: List[Stock], orders: List[Order],
                             output_dir: str, prefix: str = "cutting_report") -> List[str]:
        """Export multiple CSV files with different data views"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # 1. Cutting coordinates CSV
        coords_file = output_path / f"{prefix}_coordinates.csv"
        coords_report = self.generate_cutting_coordinates_report(result, stocks)
        
        with open(coords_file, 'w', newline='', encoding='utf-8') as f:
            if coords_report.cutting_plan:
                writer = csv.DictWriter(f, fieldnames=coords_report.cutting_plan[0].keys())
                writer.writeheader()
                writer.writerows(coords_report.cutting_plan)
        files_created.append(str(coords_file))
        
        # 2. Performance summary CSV
        perf_file = output_path / f"{prefix}_performance.csv"
        perf_report = self.generate_performance_report(result)
        
        perf_data = [
            {"Metric", "Value"},
            {"Overall Efficiency", f"{perf_report.efficiency_metrics['overall_efficiency']:.2f}%"},
            {"Waste Percentage", f"{perf_report.efficiency_metrics['waste_percentage']:.2f}%"},
            {"Total Cost", f"${perf_report.cost_analysis['total_cost']:.2f}"},
            {"Cost per Area", f"${perf_report.cost_analysis['cost_per_area']:.4f}/m²"},
            {"Fulfillment Rate", f"{perf_report.fulfillment_analysis['fulfillment_rate']:.1f}%"},
            {"Processing Time", f"{perf_report.optimization_time:.3f}s"}
        ]
        
        with open(perf_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(perf_data)
        files_created.append(str(perf_file))
        
        # 3. Material breakdown CSV
        material_file = output_path / f"{prefix}_materials.csv"
        material_report = self.generate_material_report(result, stocks)
        
        material_data = [["Material", "Efficiency %", "Cost", "Waste %", "Pieces"]]
        for material, efficiency in material_report.efficiency_by_material.items():
            cost = material_report.cost_by_material.get(material, 0)
            waste = material_report.waste_by_material.get(material, 0)
            pieces = material_report.material_breakdown.get(material, {}).get('pieces', 0)
            material_data.append([material, f"{efficiency:.1f}", f"{cost:.2f}", f"{waste:.1f}", pieces])
        
        with open(material_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(material_data)
        files_created.append(str(material_file))
        
        return files_created
    
    def _calculate_grade(self, value: float, thresholds: List[float]) -> str:
        """Calculate letter grade based on value and thresholds"""
        if value >= thresholds[3]: return "A"
        elif value >= thresholds[2]: return "B"
        elif value >= thresholds[1]: return "C"
        elif value >= thresholds[0]: return "D"
        else: return "F"
    
    def _get_dominant_material(self, stocks: List[Stock]) -> str:
        """Get the most common material type"""
        from collections import Counter
        materials = [stock.material_type.value for stock in stocks]
        if materials:
            return Counter(materials).most_common(1)[0][0]
        return "unknown"
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_stock_balance(self, result: CuttingResult, stocks: List[Stock]) -> float:
        """Calculate how balanced the stock utilization is"""
        if not stocks:
            return 0.0
        
        stock_dict = {stock.id: stock for stock in stocks}
        utilizations = []
        
        for stock in stocks:
            if any(ps.stock_id == stock.id for ps in result.placed_shapes):
                shapes_on_stock = [ps for ps in result.placed_shapes if ps.stock_id == stock.id]
                used_area = sum(ps.shape.area() for ps in shapes_on_stock)
                utilization = used_area / stock.area
                utilizations.append(utilization)
        
        if not utilizations:
            return 0.0
        
        # Lower variance means better balance
        return 1.0 / (1.0 + self._calculate_variance(utilizations))
    
    def _assess_algorithm_suitability(self, result: CuttingResult, stocks: List[Stock], 
                                    orders: List[Order]) -> str:
        """Assess if the algorithm used was suitable for the problem"""
        
        total_orders = len(orders)
        total_area = sum(order.total_area for order in orders)
        
        if total_orders <= 5 and result.efficiency_percentage > 70:
            return "Excellent - Simple problem, good efficiency"
        elif total_orders <= 20 and result.efficiency_percentage > 60:
            return "Good - Medium complexity handled well"
        elif total_orders > 20 and result.efficiency_percentage > 50:
            return "Acceptable - Complex problem with reasonable efficiency"
        elif result.efficiency_percentage < 40:
            return "Poor - Consider advanced algorithms"
        else:
            return "Average - Room for improvement"