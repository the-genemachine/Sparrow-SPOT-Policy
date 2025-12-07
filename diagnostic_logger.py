"""
Sparrow SPOT Scale™ Diagnostic Logger
v8.4.2

Comprehensive logging system for debugging and troubleshooting.
Creates separate logs for different purposes without interfering with main pipeline.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import traceback
from functools import wraps
import time


class DiagnosticLogger:
    """
    Multi-level logging system for Sparrow SPOT Scale™
    
    Creates three separate log files:
    1. debug_trace.log - Detailed technical information
    2. errors.log - Errors and exceptions only
    3. performance.json - Timing and metrics
    """
    
    def __init__(self, output_dir=None, session_name=None):
        """
        Initialize diagnostic logger.
        
        Args:
            output_dir: Directory for log files (defaults to logs/ subdirectory)
            session_name: Name for this logging session (defaults to timestamp)
        """
        self.session_name = session_name or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(output_dir) if output_dir else Path("logs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_data = {
            'session': self.session_name,
            'start_time': datetime.now().isoformat(),
            'stages': [],
            'errors': []
        }
        self.stage_timers = {}
        
        # Setup loggers
        self._setup_debug_logger()
        self._setup_error_logger()
        
        self.debug("Diagnostic logging initialized", session=self.session_name)
    
    def _setup_debug_logger(self):
        """Setup detailed debug trace logger."""
        self.debug_logger = logging.getLogger('sparrow_debug')
        self.debug_logger.setLevel(logging.DEBUG)
        self.debug_logger.handlers.clear()
        
        # File handler for debug trace
        debug_file = self.output_dir / 'debug_trace.log'
        debug_handler = logging.FileHandler(debug_file, mode='a', encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        
        # Detailed format with timestamp, level, component, message
        debug_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        debug_handler.setFormatter(debug_format)
        self.debug_logger.addHandler(debug_handler)
    
    def _setup_error_logger(self):
        """Setup error-only logger."""
        self.error_logger = logging.getLogger('sparrow_errors')
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.handlers.clear()
        
        # File handler for errors only
        error_file = self.output_dir / 'errors.log'
        error_handler = logging.FileHandler(error_file, mode='a', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Include full traceback in error format
        error_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s\n%(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_format)
        self.error_logger.addHandler(error_handler)
    
    def debug(self, message, **kwargs):
        """Log debug information with optional context."""
        context = ' | '.join(f"{k}={v}" for k, v in kwargs.items())
        full_message = f"{message} | {context}" if context else message
        self.debug_logger.debug(full_message)
    
    def info(self, message, **kwargs):
        """Log informational message."""
        context = ' | '.join(f"{k}={v}" for k, v in kwargs.items())
        full_message = f"{message} | {context}" if context else message
        self.debug_logger.info(full_message)
    
    def warning(self, message, **kwargs):
        """Log warning message."""
        context = ' | '.join(f"{k}={v}" for k, v in kwargs.items())
        full_message = f"{message} | {context}" if context else message
        self.debug_logger.warning(full_message)
    
    def error(self, message, exception=None, **kwargs):
        """
        Log error with optional exception traceback.
        
        Args:
            message: Error description
            exception: Exception object (will extract traceback)
            **kwargs: Additional context
        """
        context = ' | '.join(f"{k}={v}" for k, v in kwargs.items())
        full_message = f"{message} | {context}" if context else message
        
        if exception:
            tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            full_message += f"\n\nTraceback:\n{tb}"
        
        self.error_logger.error(full_message)
        self.debug_logger.error(full_message)
        
        # Track in performance data
        self.performance_data['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'exception_type': type(exception).__name__ if exception else None
        })
    
    def log_import(self, module_name, success=True, error=None):
        """Log module import attempt."""
        if success:
            self.debug(f"Module import successful: {module_name}")
        else:
            self.error(f"Module import failed: {module_name}", exception=error)
    
    def log_config(self, config_name, value):
        """Log configuration setting."""
        self.debug(f"Configuration: {config_name}", value=value)
    
    def log_file_operation(self, operation, filepath, size=None, success=True):
        """Log file I/O operations."""
        context = {'operation': operation, 'path': filepath}
        if size:
            context['size'] = f"{size:,} bytes"
        
        if success:
            self.debug(f"File {operation} successful", **context)
        else:
            self.warning(f"File {operation} failed", **context)
    
    def log_subprocess(self, command, cwd=None, exit_code=None):
        """Log subprocess execution."""
        self.debug(
            "Subprocess executed",
            command=' '.join(command) if isinstance(command, list) else command,
            cwd=cwd or 'current',
            exit_code=exit_code if exit_code is not None else 'running'
        )
    
    def log_model_call(self, model_name, operation, tokens=None, duration=None):
        """Log AI model API calls."""
        context = {'model': model_name, 'operation': operation}
        if tokens:
            context['tokens'] = tokens
        if duration:
            context['duration'] = f"{duration:.2f}s"
        
        self.debug("Model API call", **context)
    
    def start_stage(self, stage_name):
        """Start timing a pipeline stage."""
        self.stage_timers[stage_name] = time.time()
        self.debug(f"Stage started: {stage_name}")
    
    def end_stage(self, stage_name, details=None):
        """End timing a pipeline stage."""
        if stage_name in self.stage_timers:
            duration = time.time() - self.stage_timers[stage_name]
            
            stage_data = {
                'name': stage_name,
                'duration': round(duration, 2),
                'timestamp': datetime.now().isoformat()
            }
            if details:
                stage_data['details'] = details
            
            self.performance_data['stages'].append(stage_data)
            self.debug(f"Stage completed: {stage_name}", duration=f"{duration:.2f}s")
            del self.stage_timers[stage_name]
    
    def log_memory(self, component, usage_mb):
        """Log memory usage."""
        self.debug(f"Memory usage: {component}", memory_mb=f"{usage_mb:.1f}")
    
    def save_performance_report(self):
        """Save performance metrics to JSON file."""
        self.performance_data['end_time'] = datetime.now().isoformat()
        
        # Calculate total duration
        if 'start_time' in self.performance_data:
            start = datetime.fromisoformat(self.performance_data['start_time'])
            end = datetime.fromisoformat(self.performance_data['end_time'])
            self.performance_data['total_duration'] = (end - start).total_seconds()
        
        perf_file = self.output_dir / 'performance.json'
        with open(perf_file, 'w') as f:
            json.dump(self.performance_data, f, indent=2)
        
        self.debug("Performance report saved", file=str(perf_file))
    
    def finalize(self):
        """Finalize logging session and save performance data."""
        self.save_performance_report()
        self.debug("Diagnostic logging session ended")


def log_function_call(logger):
    """
    Decorator to automatically log function calls with timing.
    
    Usage:
        @log_function_call(diagnostic_logger)
        def my_function(arg1, arg2):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            logger.debug(f"Function called: {func_name}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"Function completed: {func_name}", duration=f"{duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function failed: {func_name}",
                    exception=e,
                    duration=f"{duration:.3f}s"
                )
                raise
        
        return wrapper
    return decorator


# Singleton instance for global access
_global_logger = None

def get_logger(output_dir=None, session_name=None):
    """Get or create global diagnostic logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = DiagnosticLogger(output_dir, session_name)
    return _global_logger


def reset_logger():
    """Reset global logger (useful for testing)."""
    global _global_logger
    if _global_logger:
        _global_logger.finalize()
    _global_logger = None
