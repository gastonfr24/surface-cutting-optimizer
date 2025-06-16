"""
Export utilities for Surface Cutting Optimizer
Export results to various formats (PDF, Excel, HTML)
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from ..core.models import Stock, Order, CuttingResult
from ..utils.logging import get_logger


class PDFExporter:
    """Export reports to PDF format"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def export_report(self, tables: Dict[str, pd.DataFrame], 
                     output_file: str) -> bool:
        """Export tables to PDF"""
        try:
            # Placeholder for PDF export
            # Would use libraries like reportlab or weasyprint
            self.logger.logger.info(f"PDF export to {output_file} (placeholder)")
            return True
        except Exception as e:
            self.logger.logger.error(f"PDF export failed: {e}")
            return False


class ExcelExporter:
    """Export reports to Excel format"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def export_report(self, tables: Dict[str, pd.DataFrame], 
                     output_file: str) -> bool:
        """Export tables to Excel with multiple sheets"""
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for sheet_name, df in tables.items():
                    if df is not None and not df.empty:
                        # Clean sheet name for Excel
                        clean_name = sheet_name.replace('_', ' ').title()[:31]
                        df.to_excel(writer, sheet_name=clean_name, index=False)
            
            self.logger.logger.info(f"Excel export successful: {output_file}")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Excel export failed: {e}")
            return False


class HTMLExporter:
    """Export reports to HTML format"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def export_report(self, tables: Dict[str, pd.DataFrame], 
                     output_file: str, title: str = "Cutting Report") -> bool:
        """Export tables to HTML report"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #666; margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; font-weight: bold; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .summary {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <div class="summary">
                    <p>Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Total tables: {len(tables)}</p>
                </div>
            """
            
            for table_name, df in tables.items():
                if df is not None and not df.empty:
                    clean_name = table_name.replace('_', ' ').title()
                    html_content += f"<h2>{clean_name}</h2>\n"
                    html_content += df.to_html(index=False, classes='data-table')
                    html_content += "\n"
            
            html_content += """
            </body>
            </html>
            """
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.logger.info(f"HTML export successful: {output_file}")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"HTML export failed: {e}")
            return False 