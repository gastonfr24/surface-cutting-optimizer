"""
Logging utilities for Surface Cutting Optimizer
"""

import logging
import time
from typing import Optional, Dict, Any
from functools import wraps
from pathlib import Path
import json
from datetime import datetime


class OptimizationLogger:
    """Custom logger for optimization operations"""
    
    def __init__(self, name: str = "surface_optimizer", level: int = logging.INFO, 
                 enable_file_logging: bool = True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.enable_file_logging = enable_file_logging
        
        # Clear existing handlers to avoid conflicts
        self.logger.handlers.clear()
        self._setup_handlers()
        
        self.start_times = {}
        self.operation_logs = []
    
    def _setup_handlers(self):
        """Setup console and optionally file handlers"""
        
        # Console handler - always enabled
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Console formatter - clean format for demos
        console_format = logging.Formatter(
            '%(message)s'  # Simple format for demos
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler - only if enabled
        if self.enable_file_logging:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f"optimizer_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Detailed file format
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def start_operation(self, operation_name: str, details: Optional[Dict[str, Any]] = None):
        """Start timing an operation"""
        self.start_times[operation_name] = time.time()
        
        log_entry = {
            "operation": operation_name,
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.operation_logs.append(log_entry)
        self.logger.info(f"Started: {operation_name}")
        
        if details:
            for key, value in details.items():
                self.logger.debug(f"  {key}: {value}")
    
    def end_operation(self, operation_name: str, success: bool = True, 
                     result: Optional[Dict[str, Any]] = None):
        """End timing an operation"""
        
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            del self.start_times[operation_name]
        else:
            duration = 0
        
        status = "Completed" if success else "Failed"
        
        log_entry = {
            "operation": operation_name,
            "status": "completed" if success else "failed",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 3),
            "result": result or {}
        }
        
        self.operation_logs.append(log_entry)
        self.logger.info(f"{status}: {operation_name} ({duration:.3f}s)")
        
        if result:
            for key, value in result.items():
                if isinstance(value, (int, float, str, bool)):
                    self.logger.debug(f"  {key}: {value}")
    
    def log_validation(self, item_type: str, item_count: int, issues: list = None):
        """Log validation results"""
        issues = issues or []
        
        if not issues:
            self.logger.info(f"Validation passed: {item_count} {item_type}")
        else:
            self.logger.warning(f"Validation issues for {item_type}: {len(issues)} problems")
            for issue in issues:
                self.logger.warning(f"  - {issue}")
    
    def log_algorithm_start(self, algorithm_name: str, stocks_count: int, orders_count: int):
        """Log algorithm execution start"""
        self.logger.info(f"Algorithm: {algorithm_name}")
        self.logger.info(f"  Stocks: {stocks_count}")
        self.logger.info(f"  Orders: {orders_count}")
    
    def log_algorithm_result(self, result_summary: Dict[str, Any]):
        """Log algorithm results"""
        self.logger.info("Optimization Results:")
        self.logger.info(f"  - Stocks used: {result_summary.get('stocks_used', 0)}")
        self.logger.info(f"  - Orders fulfilled: {result_summary.get('orders_fulfilled', 0)}")
        self.logger.info(f"  - Efficiency: {result_summary.get('efficiency', 0):.1f}%")
        self.logger.info(f"  - Computation time: {result_summary.get('computation_time', 0):.3f}s")
    
    def log_placement(self, order_id: str, stock_id: str, position: tuple):
        """Log shape placement"""
        self.logger.debug(f"Placed {order_id} on {stock_id} at {position}")
    
    def log_placement_failure(self, order_id: str, reason: str):
        """Log failed placement"""
        self.logger.debug(f"Failed to place {order_id}: {reason}")
    
    def export_logs(self, filepath: str):
        """Export operation logs to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.operation_logs, f, indent=2)
        
        self.logger.info(f"Logs exported to {filepath}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all operations"""
        completed_ops = [log for log in self.operation_logs if log["status"] == "completed"]
        failed_ops = [log for log in self.operation_logs if log["status"] == "failed"]
        
        total_time = sum(op.get("duration_seconds", 0) for op in completed_ops)
        
        return {
            "total_operations": len(self.operation_logs),
            "completed_operations": len(completed_ops),
            "failed_operations": len(failed_ops),
            "total_time_seconds": round(total_time, 3),
            "success_rate": len(completed_ops) / len(self.operation_logs) * 100 if self.operation_logs else 0
        }
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def demo_section(self, title: str, divider: str = "-"):
        """Log demo section header"""
        self.logger.info(f"\n{title}")
        self.logger.info(divider * len(title))
    
    def demo_step(self, step_number: int, title: str):
        """Log demo step"""
        self.logger.info(f"\n🔄 STEP {step_number}: {title}")
        self.logger.info("-" * (15 + len(title)))
    
    def demo_success(self, message: str):
        """Log demo success message"""
        self.logger.info(f"   ✅ {message}")
    
    def demo_warning(self, message: str):
        """Log demo warning message"""
        self.logger.warning(f"   ⚠️  {message}")
    
    def demo_info(self, message: str):
        """Log demo info message"""
        self.logger.info(f"   • {message}")
    
    def demo_analysis(self, title: str, data: dict):
        """Log demo analysis data"""
        self.logger.info(f"\n   📊 {title}:")
        for key, value in data.items():
            if isinstance(value, float):
                self.logger.info(f"   • {key}: {value:.1f}")
            else:
                self.logger.info(f"   • {key}: {value}")
                
    def demo_result(self, efficiency: float, items_placed: int, total_items: int):
        """Log demo optimization result"""
        self.logger.info(f"\n   ✅ OPTIMIZATION COMPLETED:")
        self.logger.info(f"   📊 Efficiency: {efficiency:.1f}%")
        self.logger.info(f"   ✂️  Items placed: {items_placed}/{total_items}")
        
        if efficiency >= 80:
            self.logger.info(f"   🌟 EXCELLENT efficiency! Minimal waste.")
        elif efficiency >= 60:
            self.logger.info(f"   👍 GOOD efficiency. Reasonable material usage.")
        elif efficiency >= 40:
            self.logger.info(f"   ⚡ MODERATE efficiency. Consider trying different algorithms.")
        else:
            self.logger.info(f"   ⚠️  LOW efficiency. Manual optimization may be needed.")


def timed_operation(operation_name: str, logger: OptimizationLogger):
    """Decorator to automatically time operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.start_operation(operation_name)
            try:
                result = func(*args, **kwargs)
                logger.end_operation(operation_name, success=True)
                return result
            except Exception as e:
                logger.end_operation(operation_name, success=False, 
                                   result={"error": str(e)})
                raise
        return wrapper
    return decorator


def setup_logging(level: int = logging.INFO, log_dir: str = "logs", 
                  enable_file_logging: bool = True) -> OptimizationLogger:
    """Setup logging for the entire application"""
    
    # Create log directory only if file logging is enabled
    if enable_file_logging:
        Path(log_dir).mkdir(exist_ok=True)
    
    # Create main logger
    logger = OptimizationLogger("surface_optimizer", level, enable_file_logging)
    
    return logger


def setup_demo_logging(level: int = logging.INFO) -> OptimizationLogger:
    """Setup logging for demos - console only, no file output"""
    return OptimizationLogger("surface_optimizer", level, enable_file_logging=False)


# Global logger instance
_global_logger: Optional[OptimizationLogger] = None


def get_logger() -> OptimizationLogger:
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging(enable_file_logging=False)  # No file logging by default
    return _global_logger


def log_info(message: str):
    """Quick info logging"""
    get_logger().logger.info(message)


def log_debug(message: str):
    """Quick debug logging"""
    get_logger().logger.debug(message)


def log_warning(message: str):
    """Quick warning logging"""
    get_logger().logger.warning(message)


def log_error(message: str):
    """Quick error logging"""
    get_logger().logger.error(message) 