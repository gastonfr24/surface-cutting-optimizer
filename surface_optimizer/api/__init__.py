"""
Enterprise API Module for Surface Cutting Optimizer

Professional REST API for industrial cutting optimization with:
- RESTful endpoints for optimization requests  
- Real-time job tracking and monitoring
- Enterprise authentication and rate limiting
- OpenAPI/Swagger documentation
- Batch processing capabilities
"""

try:
    from .enterprise_api import create_app, run_server
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    create_app = None
    run_server = None

__all__ = ['create_app', 'run_server', 'API_AVAILABLE'] 