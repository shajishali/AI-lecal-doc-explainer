"""
Phase 3 Views for AI Legal Explainer
Implements views for offline mode, transparency controls, performance optimization, and analytics
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
import logging

from .models import (
    Document, Clause, RiskAnalysis, DocumentSummary,
    PerformanceMetrics, LocalCache, OfflineFeature,
    TransparencyPreference, ConnectivityStatus
)
from .offline_services import OfflineModeManager
from .transparency_services import TransparencyManager
from .performance_services import PerformanceAnalyzer
from .analytics_services import AnalyticsDashboard

logger = logging.getLogger(__name__)

# Offline Mode Views
class OfflineModeViewSet(viewsets.ViewSet):
    """ViewSet for offline mode functionality"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.offline_manager = OfflineModeManager()
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get current offline mode status"""
        try:
            connectivity_status = self.offline_manager.connectivity_monitor.get_current_status()
            available_features = self.offline_manager.feature_manager.get_available_offline_features()
            
            return Response({
                'connectivity': connectivity_status,
                'available_offline_features': available_features,
                'offline_mode': not connectivity_status.get('is_online', True)
            })
        except Exception as e:
            logger.error(f"Error getting offline status: {e}")
            return Response({
                'error': f'Failed to get offline status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """Initialize offline mode system"""
        try:
            success = self.offline_manager.initialize_offline_mode()
            
            if success:
                return Response({
                    'message': 'Offline mode system initialized successfully',
                    'status': 'initialized'
                })
            else:
                return Response({
                    'error': 'Failed to initialize offline mode system'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error initializing offline mode: {e}")
            return Response({
                'error': f'Initialization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def offline_operation(self, request, pk=None):
        """Perform operation in offline mode"""
        try:
            document = get_object_or_404(Document, id=pk)
            operation_type = request.data.get('operation_type')
            
            if not operation_type:
                return Response({
                    'error': 'operation_type is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = self.offline_manager.handle_offline_operation(
                operation_type, document_id=str(document.id)
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error in offline operation: {e}")
            return Response({
                'error': f'Offline operation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Transparency Controls Views
class TransparencyControlsViewSet(viewsets.ViewSet):
    """ViewSet for transparency controls"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transparency_manager = None
    
    def _get_transparency_manager(self, request):
        """Get or create transparency manager for the request"""
        if not self.transparency_manager:
            self.transparency_manager = TransparencyManager(request.user if hasattr(request, 'user') else None)
        return self.transparency_manager
    
    @action(detail=False, methods=['get'])
    def preferences(self, request):
        """Get current transparency preferences"""
        try:
            transparency_manager = self._get_transparency_manager(request)
            
            if not transparency_manager.is_initialized():
                return Response({
                    'error': 'Transparency manager not properly initialized',
                    'details': 'User preferences could not be loaded'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            preferences = transparency_manager.get_preferences_summary()
            return Response(preferences)
        except Exception as e:
            logger.error(f"Error getting transparency preferences: {e}")
            return Response({
                'error': f'Failed to get preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_preferences(self, request):
        """Update transparency preferences"""
        try:
            transparency_manager = self._get_transparency_manager(request)
            success = transparency_manager.update_preferences(**request.data)
            
            if success:
                return Response({
                    'message': 'Preferences updated successfully',
                    'preferences': transparency_manager.get_preferences_summary()
                })
            else:
                return Response({
                    'error': 'Failed to update preferences'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return Response({
                'error': f'Update failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def reset_preferences(self, request):
        """Reset preferences to defaults"""
        try:
            transparency_manager = self._get_transparency_manager(request)
            success = transparency_manager.reset_to_defaults()
            
            if success:
                return Response({
                    'message': 'Preferences reset to defaults successfully',
                    'preferences': transparency_manager.get_preferences_summary()
                })
            else:
                return Response({
                    'error': 'Failed to reset preferences'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error resetting preferences: {e}")
            return Response({
                'error': f'Reset failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def generate_explanation(self, request):
        """Generate explanation with transparency controls"""
        try:
            content = request.data.get('content')
            content_type = request.data.get('content_type', 'general')
            context = request.data.get('context', {})
            
            if not content:
                return Response({
                    'error': 'content is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            transparency_manager = self._get_transparency_manager(request)
            explanation = transparency_manager.content_generator.generate_explanation(
                content, content_type, context
            )
            
            return Response({
                'explanation': explanation,
                'detail_level': transparency_manager.controller.get_current_detail_level()
            })
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return Response({
                'error': f'Explanation generation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Performance Optimization Views
class PerformanceOptimizationViewSet(viewsets.ViewSet):
    """ViewSet for performance optimization"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.performance_analyzer = PerformanceAnalyzer()
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get performance metrics"""
        try:
            hours = int(request.query_params.get('hours', 24))
            metrics = self.performance_analyzer.analyze_performance_trends(hours)
            return Response(metrics)
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return Response({
                'error': f'Failed to get metrics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Get performance report"""
        try:
            hours = int(request.query_params.get('hours', 24))
            report = self.performance_analyzer.generate_performance_report(hours)
            return Response({
                'report': report,
                'hours': hours
            })
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return Response({
                'error': f'Failed to generate report: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def optimize_cache(self, request):
        """Optimize cache performance"""
        try:
            cache_optimizer = self.performance_analyzer.cache_optimizer
            cleaned_count = cache_optimizer.adaptive_cache_cleanup()
            
            return Response({
                'message': f'Cache optimization completed',
                'cleaned_entries': cleaned_count
            })
        except Exception as e:
            logger.error(f"Error optimizing cache: {e}")
            return Response({
                'error': f'Cache optimization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def optimize_database(self, request):
        """Optimize database performance"""
        try:
            db_optimizer = self.performance_analyzer.database_optimizer
            success = db_optimizer.optimize_database_connections()
            
            if success:
                return Response({
                    'message': 'Database optimization completed successfully'
                })
            else:
                return Response({
                    'error': 'Database optimization failed'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return Response({
                'error': f'Database optimization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Advanced Analytics Views
class AdvancedAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for advanced analytics"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analytics_dashboard = AnalyticsDashboard()
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive analytics dashboard"""
        try:
            days = int(request.query_params.get('days', 30))
            analytics = self.analytics_dashboard.get_comprehensive_analytics(days)
            return Response(analytics)
        except Exception as e:
            logger.error(f"Error getting analytics dashboard: {e}")
            return Response({
                'error': f'Failed to get analytics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Get analytics report"""
        try:
            days = int(request.query_params.get('days', 30))
            report = self.analytics_dashboard.generate_analytics_report(days)
            return Response({
                'report': report,
                'days': days
            })
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return Response({
                'error': f'Failed to generate report: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def document_analytics(self, request, pk=None):
        """Get analytics for specific document"""
        try:
            document = get_object_or_404(Document, id=pk)
            
            # Get document-specific analytics
            analytics = {
                'document_id': str(document.id),
                'document_title': document.title,
                'upload_date': document.uploaded_at.isoformat(),
                'processing_status': document.is_processed,
                'clause_count': document.clauses.count(),
                'risk_analysis': None,
                'summary': None
            }
            
            # Add risk analysis if available
            if hasattr(document, 'risk_analysis'):
                analytics['risk_analysis'] = {
                    'overall_risk_score': document.risk_analysis.overall_risk_score,
                    'overall_risk_level': document.risk_analysis.overall_risk_level,
                    'clause_counts': {
                        'high': document.risk_analysis.high_risk_clauses_count,
                        'medium': document.risk_analysis.medium_risk_clauses_count,
                        'low': document.risk_analysis.low_risk_clauses_count,
                    }
                }
            
            # Add summary if available
            if hasattr(document, 'summary'):
                analytics['summary'] = {
                    'language': document.summary.language,
                    'word_count': document.summary.word_count,
                    'key_points_count': len(document.summary.key_points)
                }
            
            return Response(analytics)
            
        except Exception as e:
            logger.error(f"Error getting document analytics: {e}")
            return Response({
                'error': f'Failed to get document analytics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Traditional Django Views
@login_required
def offline_dashboard(request):
    """Offline mode dashboard view"""
    try:
        offline_manager = OfflineModeManager()
        connectivity_status = offline_manager.connectivity_monitor.get_current_status()
        available_features = offline_manager.feature_manager.get_available_offline_features()
        
        context = {
            'connectivity_status': connectivity_status,
            'available_features': available_features,
            'is_offline': not connectivity_status.get('is_online', True)
        }
        
        return render(request, 'main/offline_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in offline dashboard: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load offline dashboard: {str(e)}'
        })

@login_required
def transparency_controls(request):
    """Transparency controls interface view"""
    try:
        transparency_manager = TransparencyManager(request.user)
        preferences = transparency_manager.get_preferences_summary()
        
        context = {
            'preferences': preferences,
            'detail_levels': [
                'very_simple', 'simple', 'medium', 'detailed', 'legal_detailed'
            ]
        }
        
        return render(request, 'main/transparency_controls.html', context)
        
    except Exception as e:
        logger.error(f"Error in transparency controls: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load transparency controls: {str(e)}'
        })

@login_required
def performance_dashboard(request):
    """Performance optimization dashboard view"""
    try:
        performance_analyzer = PerformanceAnalyzer()
        hours = int(request.GET.get('hours', 24))
        metrics = performance_analyzer.analyze_performance_trends(hours)
        
        context = {
            'metrics': metrics,
            'hours': hours,
            'time_periods': [1, 6, 12, 24, 48, 72]
        }
        
        return render(request, 'main/performance_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in performance dashboard: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load performance dashboard: {str(e)}'
        })

@login_required
def analytics_dashboard(request):
    """Advanced analytics dashboard view"""
    try:
        analytics_dashboard = AnalyticsDashboard()
        days = int(request.GET.get('days', 30))
        analytics = analytics_dashboard.get_comprehensive_analytics(days)
        
        context = {
            'analytics': analytics,
            'days': days,
            'time_periods': [7, 14, 30, 60, 90]
        }
        
        return render(request, 'main/analytics_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in analytics dashboard: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load analytics dashboard: {str(e)}'
        })

# API endpoints for AJAX calls
@csrf_exempt
def api_offline_status(request):
    """API endpoint for offline status"""
    if request.method == 'GET':
        try:
            offline_manager = OfflineModeManager()
            status = offline_manager.connectivity_monitor.get_current_status()
            return JsonResponse(status)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_transparency_preferences(request):
    """API endpoint for transparency preferences"""
    if request.method == 'GET':
        try:
            user = request.user if request.user.is_authenticated else None
            transparency_manager = TransparencyManager(user)
            preferences = transparency_manager.get_preferences_summary()
            return JsonResponse(preferences)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    elif request.method == 'POST':
        try:
            user = request.user if request.user.is_authenticated else None
            transparency_manager = TransparencyManager(user)
            data = json.loads(request.body)
            success = transparency_manager.update_preferences(**data)
            
            if success:
                return JsonResponse({'message': 'Preferences updated successfully'})
            else:
                return JsonResponse({'error': 'Failed to update preferences'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_performance_metrics(request):
    """API endpoint for performance metrics"""
    if request.method == 'GET':
        try:
            hours = int(request.GET.get('hours', 24))
            performance_analyzer = PerformanceAnalyzer()
            metrics = performance_analyzer.analyze_performance_trends(hours)
            return JsonResponse(metrics)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_analytics_dashboard(request):
    """API endpoint for analytics dashboard"""
    if request.method == 'GET':
        try:
            days = int(request.GET.get('days', 30))
            analytics_dashboard = AnalyticsDashboard()
            analytics = analytics_dashboard.get_comprehensive_analytics(days)
            return JsonResponse(analytics)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
