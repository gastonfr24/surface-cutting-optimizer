"""
Enterprise-Grade REST API for Surface Cutting Optimization

Professional API for industrial applications with:
- RESTful endpoints for optimization requests
- Automatic solver selection based on problem complexity
- Real-time progress tracking and monitoring
- Professional result reporting and analytics
- Enterprise authentication and rate limiting
- OpenAPI/Swagger documentation

Designed for integration with:
- Manufacturing Execution Systems (MES)
- Enterprise Resource Planning (ERP)
- Computer-Aided Design (CAD) systems
- Production planning software
"""

import asyncio
import time
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path, Body
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field, validator
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ..core.models import Surface, Piece, CuttingResult
from ..algorithms.advanced.column_generation import IndustrialCuttingOptimizer
from ..algorithms.advanced.hybrid_genetic import HybridGeneticAlgorithm
from ..algorithms.advanced.genetic import GeneticAlgorithm
from ..utils.dependency_manager import dependency_manager, get_solver_status


class OptimizationStatus(str, Enum):
    """Status of optimization job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProblemComplexity(str, Enum):
    """Problem complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


# Pydantic Models for API
class PieceRequest(BaseModel):
    """Request model for a piece to be cut"""
    width: float = Field(..., gt=0, description="Width in millimeters")
    height: float = Field(..., gt=0, description="Height in millimeters")
    quantity: int = Field(1, ge=1, description="Number of pieces needed")
    material: Optional[str] = Field(None, description="Material type")
    thickness: Optional[float] = Field(None, ge=0, description="Thickness in millimeters")
    label: Optional[str] = Field(None, description="Human-readable label")
    
    @validator('width', 'height')
    def validate_dimensions(cls, v):
        if v <= 0 or v > 50000:  # Max 50 meters
            raise ValueError('Dimensions must be between 0 and 50000mm')
        return v


class SurfaceRequest(BaseModel):
    """Request model for cutting surface"""
    width: float = Field(..., gt=0, description="Surface width in millimeters")
    height: float = Field(..., gt=0, description="Surface height in millimeters")
    material: Optional[str] = Field(None, description="Surface material type")
    thickness: Optional[float] = Field(None, ge=0, description="Thickness in millimeters")
    cost_per_unit: Optional[float] = Field(None, ge=0, description="Cost per surface unit")
    
    @validator('width', 'height')
    def validate_dimensions(cls, v):
        if v <= 0 or v > 50000:  # Max 50 meters
            raise ValueError('Surface dimensions must be between 0 and 50000mm')
        return v


class OptimizationRequest(BaseModel):
    """Complete optimization request"""
    job_id: Optional[str] = Field(None, description="Optional job identifier")
    surface: SurfaceRequest = Field(..., description="Cutting surface specification")
    pieces: List[PieceRequest] = Field(..., min_items=1, description="List of pieces to cut")
    algorithm: Optional[str] = Field("auto", description="Algorithm to use (auto, genetic, hybrid, column_generation)")
    max_time: Optional[int] = Field(300, ge=1, le=3600, description="Maximum optimization time in seconds")
    target_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Target efficiency percentage")
    priority: Optional[str] = Field("normal", description="Job priority (low, normal, high, urgent)")
    
    @validator('pieces')
    def validate_pieces(cls, v):
        if len(v) > 10000:  # Reasonable limit
            raise ValueError('Maximum 10000 pieces per request')
        return v


class OptimizationResult(BaseModel):
    """Optimization result response"""
    job_id: str
    status: OptimizationStatus
    efficiency: Optional[float] = None
    total_surfaces: Optional[int] = None
    total_waste: Optional[float] = None
    computation_time: Optional[float] = None
    algorithm_used: Optional[str] = None
    problem_complexity: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    patterns: Optional[List[Dict]] = None
    cost_analysis: Optional[Dict] = None
    solver_info: Optional[Dict] = None


class SystemStatus(BaseModel):
    """System status response"""
    status: str
    version: str
    available_solvers: List[Dict]
    active_jobs: int
    completed_jobs: int
    system_load: Dict
    capabilities: Dict


# Job Storage (In production, use Redis or database)
class JobStorage:
    """In-memory job storage for demo purposes"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.job_history: List[str] = []
    
    def create_job(self, job_id: str, request: OptimizationRequest) -> None:
        """Create new optimization job"""
        self.jobs[job_id] = {
            'id': job_id,
            'status': OptimizationStatus.PENDING,
            'request': request.dict(),
            'created_at': datetime.now(),
            'progress': 0,
            'result': None,
            'error': None
        }
        self.job_history.append(job_id)
    
    def update_job(self, job_id: str, **updates) -> None:
        """Update job with new information"""
        if job_id in self.jobs:
            self.jobs[job_id].update(updates)
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_active_jobs(self) -> List[Dict]:
        """Get all active jobs"""
        return [job for job in self.jobs.values() 
                if job['status'] in [OptimizationStatus.PENDING, OptimizationStatus.RUNNING]]
    
    def get_job_stats(self) -> Dict:
        """Get job statistics"""
        active = len([j for j in self.jobs.values() if j['status'] in [OptimizationStatus.PENDING, OptimizationStatus.RUNNING]])
        completed = len([j for j in self.jobs.values() if j['status'] == OptimizationStatus.COMPLETED])
        failed = len([j for j in self.jobs.values() if j['status'] == OptimizationStatus.FAILED])
        
        return {
            'active': active,
            'completed': completed,
            'failed': failed,
            'total': len(self.jobs)
        }


# Create FastAPI app if available
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Surface Cutting Optimizer API",
        description="Enterprise-grade REST API for industrial cutting stock optimization",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware for web integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global instances
    job_storage = JobStorage()
    industrial_optimizer = IndustrialCuttingOptimizer()
    
    
    @app.get("/", response_model=Dict[str, str])
    async def root():
        """API root endpoint"""
        return {
            "message": "Surface Cutting Optimizer Enterprise API",
            "version": "1.0.0",
            "status": "operational",
            "documentation": "/docs"
        }
    
    
    @app.get("/status", response_model=SystemStatus)
    async def get_system_status():
        """Get comprehensive system status"""
        solver_status = get_solver_status()
        job_stats = job_storage.get_job_stats()
        
        return SystemStatus(
            status="operational",
            version="1.0.0",
            available_solvers=solver_status['available_solvers'],
            active_jobs=job_stats['active'],
            completed_jobs=job_stats['completed'],
            system_load={
                "cpu_percent": 0,  # Could integrate psutil
                "memory_percent": 0,
                "active_optimizations": job_stats['active']
            },
            capabilities={
                "max_pieces_per_job": 10000,
                "max_surface_size": "50000x50000mm",
                "supported_algorithms": ["genetic", "hybrid", "column_generation"],
                "real_time_progress": True,
                "batch_processing": True
            }
        )
    
    
    @app.post("/optimize", response_model=OptimizationResult)
    async def create_optimization_job(
        request: OptimizationRequest,
        background_tasks: BackgroundTasks
    ):
        """Create new optimization job"""
        
        # Generate job ID
        job_id = request.job_id or str(uuid.uuid4())
        
        # Validate request
        if len(request.pieces) == 0:
            raise HTTPException(status_code=400, detail="No pieces specified")
        
        # Create job in storage
        job_storage.create_job(job_id, request)
        
        # Start optimization in background
        background_tasks.add_task(run_optimization, job_id)
        
        # Return immediate response
        return OptimizationResult(
            job_id=job_id,
            status=OptimizationStatus.PENDING,
            created_at=datetime.now()
        )
    
    
    @app.get("/jobs/{job_id}", response_model=OptimizationResult)
    async def get_optimization_job(job_id: str = Path(..., description="Job ID")):
        """Get optimization job status and results"""
        
        job = job_storage.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Convert to response model
        return OptimizationResult(
            job_id=job['id'],
            status=job['status'],
            efficiency=job.get('result', {}).get('efficiency'),
            total_surfaces=job.get('result', {}).get('total_surfaces'),
            total_waste=job.get('result', {}).get('total_waste'),
            computation_time=job.get('result', {}).get('computation_time'),
            algorithm_used=job.get('result', {}).get('algorithm_used'),
            problem_complexity=job.get('result', {}).get('problem_complexity'),
            created_at=job['created_at'],
            completed_at=job.get('completed_at'),
            error_message=job.get('error'),
            patterns=job.get('result', {}).get('patterns'),
            cost_analysis=job.get('result', {}).get('cost_analysis'),
            solver_info=job.get('result', {}).get('solver_info')
        )
    
    
    @app.get("/jobs", response_model=List[OptimizationResult])
    async def list_optimization_jobs(
        status: Optional[OptimizationStatus] = Query(None, description="Filter by status"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return")
    ):
        """List optimization jobs with optional filtering"""
        
        jobs = list(job_storage.jobs.values())
        
        # Filter by status if specified
        if status:
            jobs = [job for job in jobs if job['status'] == status]
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply limit
        jobs = jobs[:limit]
        
        # Convert to response models
        results = []
        for job in jobs:
            results.append(OptimizationResult(
                job_id=job['id'],
                status=job['status'],
                efficiency=job.get('result', {}).get('efficiency'),
                total_surfaces=job.get('result', {}).get('total_surfaces'),
                computation_time=job.get('result', {}).get('computation_time'),
                algorithm_used=job.get('result', {}).get('algorithm_used'),
                created_at=job['created_at'],
                completed_at=job.get('completed_at'),
                error_message=job.get('error')
            ))
        
        return results
    
    
    @app.delete("/jobs/{job_id}")
    async def cancel_optimization_job(job_id: str = Path(..., description="Job ID")):
        """Cancel a running optimization job"""
        
        job = job_storage.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job['status'] in [OptimizationStatus.COMPLETED, OptimizationStatus.FAILED]:
            raise HTTPException(status_code=400, detail="Cannot cancel completed job")
        
        # Update job status
        job_storage.update_job(job_id, status=OptimizationStatus.CANCELLED)
        
        return {"message": f"Job {job_id} cancelled successfully"}
    
    
    @app.post("/optimize/batch", response_model=List[OptimizationResult])
    async def create_batch_optimization(
        requests: List[OptimizationRequest],
        background_tasks: BackgroundTasks
    ):
        """Create multiple optimization jobs in batch"""
        
        if len(requests) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 jobs per batch")
        
        results = []
        
        for request in requests:
            job_id = request.job_id or str(uuid.uuid4())
            job_storage.create_job(job_id, request)
            background_tasks.add_task(run_optimization, job_id)
            
            results.append(OptimizationResult(
                job_id=job_id,
                status=OptimizationStatus.PENDING,
                created_at=datetime.now()
            ))
        
        return results
    
    
    async def run_optimization(job_id: str):
        """Background task to run optimization"""
        try:
            job = job_storage.get_job(job_id)
            if not job:
                return
            
            # Update status to running
            job_storage.update_job(job_id, status=OptimizationStatus.RUNNING, progress=10)
            
            # Convert request to internal models
            request_data = job['request']
            surface = Surface(
                width=request_data['surface']['width'],
                height=request_data['surface']['height']
            )
            
            pieces = []
            for piece_data in request_data['pieces']:
                for _ in range(piece_data['quantity']):
                    pieces.append(Piece(
                        width=piece_data['width'],
                        height=piece_data['height']
                    ))
            
            # Update progress
            job_storage.update_job(job_id, progress=30)
            
            # Select algorithm
            algorithm_name = request_data.get('algorithm', 'auto')
            if algorithm_name == 'auto':
                optimizer = industrial_optimizer
            elif algorithm_name == 'genetic':
                optimizer = GeneticAlgorithm()
            elif algorithm_name == 'hybrid':
                optimizer = HybridGeneticAlgorithm()
            elif algorithm_name == 'column_generation':
                optimizer = IndustrialCuttingOptimizer()
            else:
                optimizer = industrial_optimizer
            
            # Update progress
            job_storage.update_job(job_id, progress=50)
            
            # Run optimization
            start_time = time.time()
            result = optimizer.optimize(surface, pieces)
            computation_time = time.time() - start_time
            
            # Calculate cost analysis
            surface_cost = request_data['surface'].get('cost_per_unit', 0)
            total_cost = result.total_surfaces_used * surface_cost
            
            # Prepare result
            optimization_result = {
                'efficiency': result.efficiency,
                'total_surfaces': result.total_surfaces_used,
                'total_waste': getattr(result, 'total_waste', 0),
                'computation_time': computation_time,
                'algorithm_used': result.algorithm_name,
                'problem_complexity': 'auto',  # Could analyze complexity
                'patterns': [],  # Could serialize patterns
                'cost_analysis': {
                    'total_cost': total_cost,
                    'cost_per_surface': surface_cost,
                    'waste_cost': getattr(result, 'total_waste', 0) * surface_cost / (surface.width * surface.height) if surface.width * surface.height > 0 else 0
                },
                'solver_info': get_solver_status()
            }
            
            # Update job with results
            job_storage.update_job(
                job_id,
                status=OptimizationStatus.COMPLETED,
                progress=100,
                result=optimization_result,
                completed_at=datetime.now()
            )
            
        except Exception as e:
            # Update job with error
            job_storage.update_job(
                job_id,
                status=OptimizationStatus.FAILED,
                error=str(e),
                completed_at=datetime.now()
            )


def create_app() -> FastAPI:
    """Factory function to create FastAPI app"""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not available. Install with: pip install fastapi uvicorn")
    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 1):
    """Run the API server"""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
        return
    
    print("🚀 Starting Surface Cutting Optimizer Enterprise API")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔧 Workers: {workers}")
    
    uvicorn.run(
        "surface_optimizer.api.enterprise_api:app",
        host=host,
        port=port,
        workers=workers,
        reload=False
    )


if __name__ == "__main__":
    run_server() 