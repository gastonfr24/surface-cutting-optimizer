"""
Error Handler for Surface Cutting Optimizer
==========================================

Provides centralized error handling, logging, and recovery mechanisms.
"""

import traceback
import sys
from typing import Optional, Dict, Any, Callable, Type
from functools import wraps
from contextlib import contextmanager

from ..core.exceptions import (
    SurfaceOptimizerError, 
    OptimizationError, 
    ValidationError,
    AlgorithmError,
    InvalidDimensionsError,
    InvalidShapeError,
    InsufficientStockError
)
from .logging import get_logger, OptimizationLogger


class ErrorHandler:
    """
    Centralized error handling for the Surface Cutting Optimizer
    
    Features:
    - Automatic error logging with context
    - Error recovery strategies
    - User-friendly error messages
    - Debug information capture
    - Error statistics tracking
    """
    
    def __init__(self, logger: Optional[OptimizationLogger] = None):
        self.logger = logger or get_logger()
        self.error_counts = {}
        self.last_errors = []
        self.max_error_history = 10
        
    def handle_error(self, 
                    error: Exception, 
                    context: Optional[Dict[str, Any]] = None,
                    operation: Optional[str] = None,
                    reraise: bool = True) -> Optional[Exception]:
        """
        Handle an error with logging and context
        
        Args:
            error: The exception that occurred
            context: Additional context information
            operation: Name of the operation that failed
            reraise: Whether to re-raise the exception
            
        Returns:
            The processed exception (if not re-raised)
        """
        
        error_type = type(error).__name__
        error_message = str(error)
        
        # Track error statistics
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Create error entry
        error_entry = {
            'type': error_type,
            'message': error_message,
            'operation': operation,
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        # Add to error history
        self.last_errors.append(error_entry)
        if len(self.last_errors) > self.max_error_history:
            self.last_errors.pop(0)
        
        # Log the error with appropriate level - with error handling for logger
        try:
            if isinstance(error, ValidationError):
                self.logger.warning(f"🔍 Validation Error in {operation or 'unknown operation'}: {error_message}")
                if context:
                    for key, value in context.items():
                        try:
                            self.logger.warning(f"   • {key}: {value}")
                        except:
                            pass  # Skip context logging if it fails
                        
            elif isinstance(error, AlgorithmError):
                self.logger.error(f"🤖 Algorithm Error in {operation or 'unknown operation'}: {error_message}")
                if context:
                    try:
                        self.logger.error(f"   Context: {context}")
                    except:
                        pass
                    
            elif isinstance(error, OptimizationError):
                self.logger.error(f"⚡ Optimization Error in {operation or 'unknown operation'}: {error_message}")
                if context:
                    try:
                        self.logger.error(f"   Context: {context}")
                    except:
                        pass
                    
            elif isinstance(error, (InvalidDimensionsError, InvalidShapeError)):
                self.logger.warning(f"📐 Input Error in {operation or 'unknown operation'}: {error_message}")
                
            elif isinstance(error, InsufficientStockError):
                self.logger.warning(f"📦 Stock Error in {operation or 'unknown operation'}: {error_message}")
                
            else:
                # Unexpected error
                self.logger.error(f"💥 Unexpected Error in {operation or 'unknown operation'}: {error_message}")
                try:
                    self.logger.debug(f"   Traceback: {traceback.format_exc()}")
                except:
                    pass
        except Exception:
            # If logging fails, continue silently - don't let logger errors crash the application
            pass
        
        if reraise:
            raise error
        
        return error
    
    def safe_execute(self, 
                    func: Callable, 
                    *args, 
                    operation: Optional[str] = None,
                    default_return: Any = None,
                    context: Optional[Dict[str, Any]] = None,
                    **kwargs) -> Any:
        """
        Execute a function safely with error handling
        
        Args:
            func: Function to execute
            *args: Function arguments
            operation: Name of the operation
            default_return: Value to return if function fails
            context: Additional context
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or default_return if failed
        """
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(
                e, 
                context=context,
                operation=operation or func.__name__,
                reraise=False
            )
            return default_return
    
    @contextmanager
    def error_context(self, operation: str, context: Optional[Dict[str, Any]] = None):
        """
        Context manager for error handling
        
        Usage:
            with error_handler.error_context("optimization", {"stocks": 5}):
                # code that might fail
                result = optimize()
        """
        
        try:
            yield
        except Exception as e:
            self.handle_error(e, context=context, operation=operation, reraise=True)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': dict(self.error_counts),
            'recent_errors': len(self.last_errors),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None
        }
    
    def clear_error_history(self):
        """Clear error history and statistics"""
        self.error_counts.clear()
        self.last_errors.clear()


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def handle_error(error: Exception, 
                context: Optional[Dict[str, Any]] = None,
                operation: Optional[str] = None,
                reraise: bool = True):
    """Quick error handling function"""
    return get_error_handler().handle_error(error, context, operation, reraise)


def safe_execute(func: Callable, 
                *args,
                operation: Optional[str] = None,
                default_return: Any = None,
                context: Optional[Dict[str, Any]] = None,
                **kwargs):
    """Quick safe execution function"""
    return get_error_handler().safe_execute(
        func, *args, 
        operation=operation,
        default_return=default_return,
        context=context,
        **kwargs
    )


def error_context(operation: str, context: Optional[Dict[str, Any]] = None):
    """Quick error context manager"""
    return get_error_handler().error_context(operation, context)


def with_error_handling(operation: Optional[str] = None, 
                       context: Optional[Dict[str, Any]] = None,
                       default_return: Any = None):
    """
    Decorator for automatic error handling
    
    Usage:
        @with_error_handling("optimization", {"algorithm": "best_fit"})
        def optimize_layout(stocks, orders):
            # code that might fail
            return result
    """
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return safe_execute(
                func, *args,
                operation=operation or func.__name__,
                default_return=default_return,
                context=context,
                **kwargs
            )
        return wrapper
    return decorator


def validate_with_recovery(validator_func: Callable, 
                          data: Any,
                          recovery_func: Optional[Callable] = None,
                          operation: str = "validation") -> bool:
    """
    Validate data with optional recovery
    
    Args:
        validator_func: Function that validates the data
        data: Data to validate
        recovery_func: Optional function to attempt recovery
        operation: Name of the validation operation
        
    Returns:
        True if validation passed (or recovery succeeded)
    """
    
    try:
        return validator_func(data)
    except ValidationError as e:
        if recovery_func:
            try:
                get_logger().warning(f"🔧 Attempting recovery for validation error: {e}")
                recovery_func(data)
                return validator_func(data)  # Try validation again
            except Exception as recovery_error:
                handle_error(
                    recovery_error,
                    context={"original_error": str(e), "data_type": type(data).__name__},
                    operation=f"{operation}_recovery",
                    reraise=False
                )
        
        handle_error(
            e,
            context={"data_type": type(data).__name__},
            operation=operation,
            reraise=True
        ) 