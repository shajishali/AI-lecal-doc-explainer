"""
Performance Optimization Services for AI Legal Explainer
Implements Phase 3.3: Performance Optimization functionality
"""

import time
import logging
import json
import threading
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import connection, transaction
from django.conf import settings
import psutil
import gc
import asyncio

from .models import (
    PerformanceMetrics, Document, Clause, DocumentSummary,
    RiskAnalysis, LocalCache
)

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitors and tracks performance metrics"""
    
    def __init__(self):
        self.metrics_buffer = []
        self.buffer_size = 100
        self.monitoring_enabled = True
        self.start_time = timezone.now()
    
    def start_operation(self, feature_name: str, operation_type: str, 
                       user: Optional[Any] = None, session_id: str = None) -> str:
        """Start monitoring an operation and return operation ID"""
        if not self.monitoring_enabled:
            return None
        
        operation_id = f"{feature_name}_{operation_type}_{int(time.time())}"
        
        # Record start metrics
        start_metrics = {
            'operation_id': operation_id,
            'feature_name': feature_name,
            'operation_type': operation_type,
            'start_time': timezone.now(),
            'user': user,
            'session_id': session_id,
            'system_metrics': self._get_system_metrics()
        }
        
        self.metrics_buffer.append(start_metrics)
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, 
                     error_message: str = None, result_data: Dict = None) -> bool:
        """End monitoring an operation and save metrics"""
        if not self.monitoring_enabled:
            return False
        
        try:
            # Find start metrics
            start_metrics = None
            for i, metrics in enumerate(self.metrics_buffer):
                if metrics.get('operation_id') == operation_id:
                    start_metrics = metrics
                    del self.metrics_buffer[i]
                    break
            
            if not start_metrics:
                logger.warning(f"Operation {operation_id} not found in metrics buffer")
                return False
            
            # Calculate duration and system metrics
            end_time = timezone.now()
            duration = (end_time - start_metrics['start_time']).total_seconds() * 1000
            
            end_system_metrics = self._get_system_metrics()
            
            # Calculate resource usage
            resource_usage = self._calculate_resource_usage(
                start_metrics['system_metrics'], 
                end_system_metrics
            )
            
            # Save to database
            self._save_performance_metrics(
                feature_name=start_metrics['feature_name'],
                operation_type=start_metrics['operation_type'],
                start_time=start_metrics['start_time'],
                end_time=end_time,
                duration_ms=duration,
                success=success,
                error_message=error_message,
                resource_usage=resource_usage,
                user=start_metrics.get('user'),
                session_id=start_metrics.get('session_id')
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error ending operation {operation_id}: {e}")
            return False
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict(),
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def _calculate_resource_usage(self, start_metrics: Dict, end_metrics: Dict) -> Dict[str, Any]:
        """Calculate resource usage between start and end"""
        try:
            usage = {}
            
            # CPU usage (average)
            if 'cpu_percent' in start_metrics and 'cpu_percent' in end_metrics:
                usage['cpu_avg'] = (start_metrics['cpu_percent'] + end_metrics['cpu_percent']) / 2
            
            # Memory usage
            if 'memory_percent' in start_metrics and 'memory_percent' in end_metrics:
                usage['memory_avg'] = (start_metrics['memory_percent'] + end_metrics['memory_percent']) / 2
            
            # Network I/O
            if 'network_io' in start_metrics and 'network_io' in end_metrics:
                start_io = start_metrics['network_io']
                end_io = end_metrics['network_io']
                
                usage['bytes_sent'] = end_io.get('bytes_sent', 0) - start_io.get('bytes_sent', 0)
                usage['bytes_recv'] = end_io.get('bytes_recv', 0) - start_io.get('bytes_recv', 0)
            
            return usage
            
        except Exception as e:
            logger.error(f"Error calculating resource usage: {e}")
            return {}
    
    def _save_performance_metrics(self, **kwargs):
        """Save performance metrics to database"""
        try:
            PerformanceMetrics.objects.create(**kwargs)
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        try:
            since = timezone.now() - timedelta(hours=hours)
            
            metrics = PerformanceMetrics.objects.filter(
                start_time__gte=since
            )
            
            # Calculate averages
            total_operations = metrics.count()
            successful_operations = metrics.filter(success=True).count()
            failed_operations = total_operations - successful_operations
            
            # Average duration by operation type
            avg_durations = {}
            for op_type in metrics.values_list('operation_type', flat=True).distinct():
                type_metrics = metrics.filter(operation_type=op_type)
                avg_duration = type_metrics.aggregate(
                    avg_duration=models.Avg('duration_ms')
                )['avg_duration'] or 0
                avg_durations[op_type] = avg_duration
            
            # Success rate
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
            
            return {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'failed_operations': failed_operations,
                'success_rate': round(success_rate, 2),
                'average_durations': avg_durations,
                'time_period_hours': hours
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}

class ModelOptimizer:
    """Optimizes AI model inference performance"""
    
    def __init__(self):
        self.model_cache = {}
        self.inference_cache = {}
        self.batch_size = 4
        self.max_cache_size = 1000
    
    def optimize_model_loading(self, model_name: str, model_path: str) -> bool:
        """Optimize model loading with caching and lazy loading"""
        try:
            if model_name in self.model_cache:
                logger.info(f"Model {model_name} already loaded in cache")
                return True
            
            # Load model with optimization
            model = self._load_model_optimized(model_path)
            if model:
                self.model_cache[model_name] = model
                logger.info(f"Model {model_name} loaded and cached")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error optimizing model loading for {model_name}: {e}")
            return False
    
    def _load_model_optimized(self, model_path: str) -> Any:
        """Load model with optimization techniques"""
        try:
            # This would integrate with actual model loading
            # For now, return a placeholder
            return {'model_path': model_path, 'loaded_at': timezone.now()}
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    def optimize_inference(self, model_name: str, input_data: Any, 
                          batch_mode: bool = False) -> Tuple[Any, float]:
        """Optimize model inference with caching and batching"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(model_name, input_data)
            if cache_key in self.inference_cache:
                logger.info(f"Using cached inference result for {model_name}")
                return self.inference_cache[cache_key], 0.0
            
            # Perform inference
            if batch_mode and isinstance(input_data, list):
                result = self._batch_inference(model_name, input_data)
            else:
                result = self._single_inference(model_name, input_data)
            
            # Cache result
            self._cache_inference_result(cache_key, result)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000
            
            return result, duration
            
        except Exception as e:
            logger.error(f"Error in optimized inference: {e}")
            return None, 0.0
    
    def _generate_cache_key(self, model_name: str, input_data: Any) -> str:
        """Generate cache key for inference results"""
        import hashlib
        
        # Create a hash of the input data
        data_str = str(input_data)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{model_name}_{hash_obj.hexdigest()}"
    
    def _single_inference(self, model_name: str, input_data: Any) -> Any:
        """Perform single inference"""
        # This would integrate with actual model inference
        # For now, return placeholder
        return f"inference_result_{model_name}_{hash(str(input_data))}"
    
    def _batch_inference(self, model_name: str, input_data: List[Any]) -> List[Any]:
        """Perform batch inference for better performance"""
        results = []
        
        # Process in batches
        for i in range(0, len(input_data), self.batch_size):
            batch = input_data[i:i + self.batch_size]
            batch_results = [self._single_inference(model_name, item) for item in batch]
            results.extend(batch_results)
        
        return results
    
    def _cache_inference_result(self, cache_key: str, result: Any):
        """Cache inference result with size management"""
        # Check cache size
        if len(self.inference_cache) >= self.max_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(self.inference_cache.keys())[:100]
            for key in oldest_keys:
                del self.inference_cache[key]
        
        self.inference_cache[cache_key] = result
    
    def clear_model_cache(self):
        """Clear model cache to free memory"""
        self.model_cache.clear()
        self.inference_cache.clear()
        gc.collect()
        logger.info("Model cache cleared")

class CacheOptimizer:
    """Optimizes caching strategies for better performance"""
    
    def __init__(self):
        self.cache_stats = {}
        self.adaptive_cache = {}
        self.cache_hit_threshold = 0.7
    
    def optimize_cache_strategy(self, cache_key: str, data: Any, 
                              access_pattern: str = 'random') -> bool:
        """Optimize caching strategy based on access patterns"""
        try:
            # Determine optimal cache strategy
            if access_pattern == 'frequent':
                strategy = 'persistent'
                ttl = timedelta(hours=24)
            elif access_pattern == 'moderate':
                strategy = 'temporary'
                ttl = timedelta(hours=6)
            else:
                strategy = 'short_term'
                ttl = timedelta(hours=1)
            
            # Store in local cache
            cache_entry, created = LocalCache.objects.get_or_create(
                cache_key=cache_key,
                defaults={
                    'cache_data': data,
                    'cache_type': 'optimized_cache',
                    'expires_at': timezone.now() + ttl
                }
            )
            
            if not created:
                cache_entry.cache_data = data
                cache_entry.expires_at = timezone.now() + ttl
                cache_entry.save()
            
            # Update cache statistics
            self._update_cache_stats(cache_key, strategy)
            
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing cache strategy: {e}")
            return False
    
    def _update_cache_stats(self, cache_key: str, strategy: str):
        """Update cache usage statistics"""
        if cache_key not in self.cache_stats:
            self.cache_stats[cache_key] = {
                'access_count': 0,
                'strategy': strategy,
                'last_accessed': timezone.now()
            }
        
        self.cache_stats[cache_key]['access_count'] += 1
        self.cache_stats[cache_key]['last_accessed'] = timezone.now()
    
    def get_cache_performance_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        try:
            total_entries = LocalCache.objects.count()
            expired_entries = LocalCache.objects.filter(
                expires_at__lt=timezone.now()
            ).count()
            
            # Calculate hit rate from statistics
            total_accesses = sum(stats['access_count'] for stats in self.cache_stats.values())
            cache_hits = sum(1 for stats in self.cache_stats.values() if stats['access_count'] > 1)
            
            hit_rate = (cache_hits / len(self.cache_stats) * 100) if self.cache_stats else 0
            
            return {
                'total_cache_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'cache_hit_rate': round(hit_rate, 2),
                'total_accesses': total_accesses,
                'average_accesses_per_entry': round(total_accesses / len(self.cache_stats), 2) if self.cache_stats else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting cache performance metrics: {e}")
            return {}
    
    def adaptive_cache_cleanup(self):
        """Perform adaptive cache cleanup based on usage patterns"""
        try:
            # Remove rarely accessed entries
            current_time = timezone.now()
            cleanup_threshold = current_time - timedelta(hours=12)
            
            entries_to_cleanup = []
            for cache_key, stats in self.cache_stats.items():
                if (stats['last_accessed'] < cleanup_threshold and 
                    stats['access_count'] < 2):
                    entries_to_cleanup.append(cache_key)
            
            # Remove from database
            if entries_to_cleanup:
                LocalCache.objects.filter(
                    cache_key__in=entries_to_cleanup
                ).delete()
                
                # Remove from stats
                for key in entries_to_cleanup:
                    del self.cache_stats[key]
                
                logger.info(f"Cleaned up {len(entries_to_cleanup)} rarely accessed cache entries")
            
            return len(entries_to_cleanup)
            
        except Exception as e:
            logger.error(f"Error in adaptive cache cleanup: {e}")
            return 0

class DatabaseOptimizer:
    """Optimizes database queries and performance"""
    
    def __init__(self):
        self.query_cache = {}
        self.connection_pool = {}
    
    def optimize_query(self, model_class, filters: Dict = None, 
                      select_related: List[str] = None, 
                      prefetch_related: List[str] = None) -> Any:
        """Optimize database query with proper select_related and prefetch_related"""
        try:
            queryset = model_class.objects.all()
            
            # Apply filters
            if filters:
                queryset = queryset.filter(**filters)
            
            # Optimize related field loading
            if select_related:
                queryset = queryset.select_related(*select_related)
            
            if prefetch_related:
                queryset = queryset.prefetch_related(*prefetch_related)
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            return model_class.objects.none()
    
    def bulk_operations(self, model_class, operations: List[Dict], 
                       operation_type: str = 'create') -> bool:
        """Perform bulk database operations for better performance"""
        try:
            if operation_type == 'create':
                model_class.objects.bulk_create([
                    model_class(**op) for op in operations
                ])
            elif operation_type == 'update':
                model_class.objects.bulk_update([
                    model_class(**op) for op in operations
                ], fields=list(operations[0].keys()))
            
            logger.info(f"Bulk {operation_type} completed for {len(operations)} records")
            return True
            
        except Exception as e:
            logger.error(f"Error in bulk {operation_type}: {e}")
            return False
    
    def get_database_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            with connection.cursor() as cursor:
                # Get query count
                cursor.execute("SHOW STATUS LIKE 'Questions'")
                total_queries = cursor.fetchone()[1]
                
                # Get slow query count
                cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
                slow_queries = cursor.fetchone()[1]
                
                # Get connection count
                cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                active_connections = cursor.fetchone()[1]
                
                return {
                    'total_queries': total_queries,
                    'slow_queries': slow_queries,
                    'active_connections': active_connections,
                    'slow_query_percentage': round((int(slow_queries) / int(total_queries) * 100), 2) if int(total_queries) > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting database performance metrics: {e}")
            return {}
    
    def optimize_database_connections(self):
        """Optimize database connection usage"""
        try:
            # Close idle connections
            connection.close()
            
            # Reset connection pool if needed
            if hasattr(connection, 'reset_queries'):
                connection.reset_queries()
            
            logger.info("Database connections optimized")
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing database connections: {e}")
            return False

class PerformanceAnalyzer:
    """Analyzes performance data and provides insights"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.cache_optimizer = CacheOptimizer()
        self.database_optimizer = DatabaseOptimizer()
    
    def analyze_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        try:
            # Get performance summary
            performance_summary = self.performance_monitor.get_performance_summary(hours)
            
            # Get cache metrics
            cache_metrics = self.cache_optimizer.get_cache_performance_metrics()
            
            # Get database metrics
            db_metrics = self.database_optimizer.get_database_performance_metrics()
            
            # Analyze trends
            trends = self._identify_performance_trends(performance_summary, cache_metrics, db_metrics)
            
            return {
                'performance_summary': performance_summary,
                'cache_metrics': cache_metrics,
                'database_metrics': db_metrics,
                'trends': trends,
                'recommendations': self._generate_recommendations(trends)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {}
    
    def _identify_performance_trends(self, performance_summary: Dict, 
                                   cache_metrics: Dict, db_metrics: Dict) -> Dict[str, Any]:
        """Identify performance trends and patterns"""
        trends = {
            'performance_degradation': False,
            'cache_efficiency': 'good',
            'database_efficiency': 'good',
            'bottlenecks': []
        }
        
        # Check for performance degradation
        if performance_summary.get('success_rate', 100) < 95:
            trends['performance_degradation'] = True
            trends['bottlenecks'].append('Low success rate')
        
        # Check cache efficiency
        cache_hit_rate = cache_metrics.get('cache_hit_rate', 0)
        if cache_hit_rate < 60:
            trends['cache_efficiency'] = 'poor'
            trends['bottlenecks'].append('Low cache hit rate')
        elif cache_hit_rate < 80:
            trends['cache_efficiency'] = 'fair'
        
        # Check database efficiency
        slow_query_percentage = db_metrics.get('slow_query_percentage', 0)
        if slow_query_percentage > 5:
            trends['database_efficiency'] = 'poor'
            trends['bottlenecks'].append('High slow query rate')
        elif slow_query_percentage > 2:
            trends['database_efficiency'] = 'fair'
        
        return trends
    
    def _generate_recommendations(self, trends: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if trends['performance_degradation']:
            recommendations.append("Investigate failed operations and improve error handling")
        
        if trends['cache_efficiency'] == 'poor':
            recommendations.append("Review cache invalidation strategy and increase cache size")
        
        if trends['database_efficiency'] == 'poor':
            recommendations.append("Optimize database queries and consider indexing improvements")
        
        if not trends['bottlenecks']:
            recommendations.append("Performance is optimal - continue monitoring")
        
        return recommendations
    
    def generate_performance_report(self, hours: int = 24) -> str:
        """Generate human-readable performance report"""
        try:
            analysis = self.analyze_performance_trends(hours)
            
            report = f"""
Performance Report - Last {hours} Hours
=====================================

Performance Summary:
- Total Operations: {analysis.get('performance_summary', {}).get('total_operations', 0)}
- Success Rate: {analysis.get('performance_summary', {}).get('success_rate', 0)}%
- Failed Operations: {analysis.get('performance_summary', {}).get('failed_operations', 0)}

Cache Performance:
- Hit Rate: {analysis.get('cache_metrics', {}).get('cache_hit_rate', 0)}%
- Active Entries: {analysis.get('cache_metrics', {}).get('active_entries', 0)}

Database Performance:
- Slow Query Rate: {analysis.get('database_metrics', {}).get('slow_query_percentage', 0)}%
- Active Connections: {analysis.get('database_metrics', {}).get('active_connections', 0)}

Performance Trends:
- Overall Status: {'Degraded' if analysis.get('trends', {}).get('performance_degradation') else 'Good'}
- Cache Efficiency: {analysis.get('trends', {}).get('cache_efficiency', 'Unknown').title()}
- Database Efficiency: {analysis.get('trends', {}).get('database_efficiency', 'Unknown').title()}

Bottlenecks Identified:
{chr(10).join(f"- {bottleneck}" for bottleneck in analysis.get('trends', {}).get('bottlenecks', []))}

Recommendations:
{chr(10).join(f"- {rec}" for rec in analysis.get('recommendations', []))}
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return f"Error generating performance report: {e}"
