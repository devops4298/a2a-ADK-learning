"""
Monitoring and observability utilities for Confluence Knowledge Agent.

Provides health checks, metrics, and monitoring capabilities following ADK best practices.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

from .config.settings import get_data_config, get_server_config
from .tools.knowledge_base import ConfluenceKnowledgeBase

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Comprehensive health checking for the Confluence Knowledge Agent.
    
    Monitors system resources, data availability, and service dependencies.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.data_config = get_data_config()
        self.server_config = get_server_config()
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health metrics.

        Returns:
            Dict containing system health information
        """
        try:
            if psutil is None:
                return {
                    "status": "degraded",
                    "error": "psutil not available - install with: pip install psutil",
                    "uptime_seconds": time.time() - self.start_time
                }

            # CPU and Memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "uptime_seconds": time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_data_health(self) -> Dict[str, Any]:
        """
        Check data availability and integrity.
        
        Returns:
            Dict containing data health information
        """
        try:
            data_dir = Path(self.data_config["data_dir"])
            index_file = data_dir / self.data_config["index_file"]
            
            # Check if data directory exists
            if not data_dir.exists():
                return {
                    "status": "unhealthy",
                    "error": f"Data directory not found: {data_dir}"
                }
            
            # Check if index file exists
            if not index_file.exists():
                return {
                    "status": "unhealthy", 
                    "error": f"Index file not found: {index_file}"
                }
            
            # Try to load knowledge base
            try:
                kb = ConfluenceKnowledgeBase(str(data_dir))
                stats = kb.get_stats()
                
                return {
                    "status": "healthy",
                    "documents_loaded": stats["total_documents"],
                    "spaces_available": stats["total_spaces"],
                    "data_directory": str(data_dir),
                    "last_checked": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                return {
                    "status": "degraded",
                    "error": f"Error loading knowledge base: {e}",
                    "data_directory": str(data_dir)
                }
                
        except Exception as e:
            logger.error(f"Error checking data health: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Check service-specific health.
        
        Returns:
            Dict containing service health information
        """
        try:
            from .config.settings import validate_config
            
            config_valid = validate_config()
            
            return {
                "status": "healthy" if config_valid else "degraded",
                "configuration_valid": config_valid,
                "server_config": {
                    "host": self.server_config["host"],
                    "port": self.server_config["port"],
                    "debug": self.server_config["debug"]
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error checking service health: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_comprehensive_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health check results.
        
        Returns:
            Dict containing all health check results
        """
        system_health = self.get_system_health()
        data_health = self.get_data_health()
        service_health = self.get_service_health()
        
        # Determine overall status
        statuses = [
            system_health.get("status", "unknown"),
            data_health.get("status", "unknown"),
            service_health.get("status", "unknown")
        ]
        
        if "error" in statuses:
            overall_status = "error"
        elif "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "system": system_health,
                "data": data_health,
                "service": service_health
            }
        }


class MetricsCollector:
    """
    Collect and track metrics for the Confluence Knowledge Agent.
    """
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.search_count = 0
        self.start_time = time.time()
    
    def increment_request_count(self):
        """Increment total request count."""
        self.request_count += 1
    
    def increment_error_count(self):
        """Increment error count."""
        self.error_count += 1
    
    def increment_search_count(self):
        """Increment search count."""
        self.search_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dict containing current metrics
        """
        uptime = time.time() - self.start_time
        
        return {
            "requests": {
                "total": self.request_count,
                "errors": self.error_count,
                "success_rate": (
                    (self.request_count - self.error_count) / self.request_count
                    if self.request_count > 0 else 1.0
                )
            },
            "searches": {
                "total": self.search_count
            },
            "uptime": {
                "seconds": uptime,
                "formatted": f"{uptime // 3600:.0f}h {(uptime % 3600) // 60:.0f}m {uptime % 60:.0f}s"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
