"""
Enhanced Views for AI Legal Explainer
Implements missing functionality: risk visualizations, what-if simulations, clause library
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
import logging

from .models import Document, Clause, RiskAnalysis
from .enhanced_ai_services import RiskVisualizer, WhatIfSimulator, ClauseLibraryService

logger = logging.getLogger(__name__)

class RiskVisualizationViewSet(viewsets.ViewSet):
    """ViewSet for risk visualization features"""
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get comprehensive risk visualization dashboard"""
        try:
            document = get_object_or_404(Document, id=pk)
            visualizer = RiskVisualizer()
            
            dashboard_data = visualizer.create_risk_dashboard(document)
            
            if 'error' in dashboard_data:
                return Response({
                    'error': dashboard_data['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'document_id': str(document.id),
                'document_title': document.title,
                'visualizations': dashboard_data
            })
            
        except Exception as e:
            logger.error(f"Error creating risk dashboard: {e}")
            return Response({
                'error': f'Dashboard creation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def risk_distribution(self, request, pk=None):
        """Get risk distribution chart"""
        try:
            document = get_object_or_404(Document, id=pk)
            visualizer = RiskVisualizer()
            
            clauses = document.clauses.all()
            if not clauses:
                return Response({
                    'error': 'No clauses available for visualization'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            chart_html = visualizer._create_risk_distribution_chart(clauses)
            
            return Response({
                'chart_html': chart_html,
                'clause_count': len(clauses)
            })
            
        except Exception as e:
            logger.error(f"Error creating risk distribution chart: {e}")
            return Response({
                'error': f'Chart creation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WhatIfSimulationViewSet(viewsets.ViewSet):
    """ViewSet for what-if simulation features"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def simulate_scenario(self, request):
        """Simulate a what-if scenario for a clause"""
        try:
            clause_id = request.data.get('clause_id')
            scenario_type = request.data.get('scenario_type')
            modifications = request.data.get('modifications', {})
            
            if not clause_id or not scenario_type:
                return Response({
                    'error': 'clause_id and scenario_type are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            clause = get_object_or_404(Clause, id=clause_id)
            simulator = WhatIfSimulator()
            
            simulation_result = simulator.simulate_scenario(clause, scenario_type, modifications)
            
            if 'error' in simulation_result:
                return Response({
                    'error': simulation_result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(simulation_result)
            
        except Exception as e:
            logger.error(f"Error simulating scenario: {e}")
            return Response({
                'error': f'Simulation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def available_scenarios(self, request):
        """Get list of available scenario types"""
        try:
            simulator = WhatIfSimulator()
            scenarios = []
            
            for scenario_id, scenario_data in simulator.scenario_templates.items():
                scenarios.append({
                    'id': scenario_id,
                    'name': scenario_data['name'],
                    'description': scenario_data['description'],
                    'parameters': scenario_data['parameters'],
                    'impact_areas': scenario_data['impact_areas']
                })
            
            return Response({
                'scenarios': scenarios
            })
            
        except Exception as e:
            logger.error(f"Error getting available scenarios: {e}")
            return Response({
                'error': f'Failed to get scenarios: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClauseLibraryViewSet(viewsets.ViewSet):
    """ViewSet for clause library and comparison features"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def compare_clauses(self, request):
        """Compare two clauses"""
        try:
            clause1_id = request.data.get('clause1_id')
            clause2_id = request.data.get('clause2_id')
            
            if not clause1_id or not clause2_id:
                return Response({
                    'error': 'Both clause1_id and clause2_id are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            clause1 = get_object_or_404(Clause, id=clause1_id)
            clause2 = get_object_or_404(Clause, id=clause2_id)
            
            library_service = ClauseLibraryService()
            comparison_result = library_service.compare_clauses(clause1, clause2)
            
            if 'error' in comparison_result:
                return Response({
                    'error': comparison_result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(comparison_result)
            
        except Exception as e:
            logger.error(f"Error comparing clauses: {e}")
            return Response({
                'error': f'Comparison failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def find_similar(self, request, pk=None):
        """Find clauses similar to a target clause"""
        try:
            target_clause = get_object_or_404(Clause, id=pk)
            threshold = float(request.query_params.get('threshold', 0.7))
            
            # Get all clauses from the same document
            all_clauses = list(target_clause.document.clauses.all())
            
            library_service = ClauseLibraryService()
            similar_clauses = library_service.find_similar_clauses(target_clause, all_clauses, threshold)
            
            return Response({
                'target_clause': {
                    'id': str(target_clause.id),
                    'type': target_clause.clause_type,
                    'text': target_clause.original_text[:100] + '...'
                },
                'similar_clauses': similar_clauses,
                'threshold': threshold
            })
            
        except Exception as e:
            logger.error(f"Error finding similar clauses: {e}")
            return Response({
                'error': f'Search failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """Get recommendations for improving a clause"""
        try:
            clause = get_object_or_404(Clause, id=pk)
            library_service = ClauseLibraryService()
            
            recommendations = library_service.get_clause_recommendations(clause)
            
            if 'error' in recommendations:
                return Response({
                    'error': recommendations['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(recommendations)
            
        except Exception as e:
            logger.error(f"Error getting clause recommendations: {e}")
            return Response({
                'error': f'Recommendations failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available clause templates"""
        try:
            library_service = ClauseLibraryService()
            templates = []
            
            for template_id, template_data in library_service.clause_templates.items():
                templates.append({
                    'id': template_id,
                    'name': template_data['name'],
                    'text': template_data['text'],
                    'risk_level': template_data['risk_level'],
                    'best_practice': template_data['best_practice'],
                    'jurisdiction': template_data['jurisdiction'],
                    'industry': template_data['industry']
                })
            
            return Response({
                'templates': templates
            })
            
        except Exception as e:
            logger.error(f"Error getting clause templates: {e}")
            return Response({
                'error': f'Failed to get templates: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Traditional Django views for enhanced functionality
def risk_dashboard_view(request, document_id):
    """Display risk visualization dashboard"""
    try:
        document = get_object_or_404(Document, id=document_id)
        visualizer = RiskVisualizer()
        
        dashboard_data = visualizer.create_risk_dashboard(document)
        
        context = {
            'document': document,
            'dashboard_data': dashboard_data,
            'has_error': 'error' in dashboard_data
        }
        
        return render(request, 'main/risk_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in risk dashboard view: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load risk dashboard: {str(e)}'
        })

def what_if_simulation_view(request, clause_id):
    """Display what-if simulation interface"""
    try:
        clause = get_object_or_404(Clause, id=clause_id)
        simulator = WhatIfSimulator()
        
        available_scenarios = []
        for scenario_id, scenario_data in simulator.scenario_templates.items():
            available_scenarios.append({
                'id': scenario_id,
                'name': scenario_data['name'],
                'description': scenario_data['description'],
                'parameters': scenario_data['parameters']
            })
        
        context = {
            'clause': clause,
            'available_scenarios': available_scenarios
        }
        
        return render(request, 'main/what_if_simulation.html', context)
        
    except Exception as e:
        logger.error(f"Error in what-if simulation view: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load simulation interface: {str(e)}'
        })

def clause_comparison_view(request, clause1_id, clause2_id):
    """Display clause comparison interface"""
    try:
        clause1 = get_object_or_404(Clause, id=clause1_id)
        clause2 = get_object_or_404(Clause, id=clause2_id)
        
        library_service = ClauseLibraryService()
        comparison_result = library_service.compare_clauses(clause1, clause2)
        
        context = {
            'clause1': clause1,
            'clause2': clause2,
            'comparison': comparison_result,
            'has_error': 'error' in comparison_result
        }
        
        return render(request, 'main/clause_comparison.html', context)
        
    except Exception as e:
        logger.error(f"Error in clause comparison view: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load comparison: {str(e)}'
        })

def clause_library_view(request):
    """Display clause library interface"""
    try:
        library_service = ClauseLibraryService()
        
        # Get all documents with clauses for library browsing
        documents_with_clauses = Document.objects.filter(clauses__isnull=False).distinct()
        
        context = {
            'documents': documents_with_clauses,
            'templates': library_service.clause_templates,
            'best_practices': library_service.best_practices
        }
        
        return render(request, 'main/clause_library.html', context)
        
    except Exception as e:
        logger.error(f"Error in clause library view: {e}")
        return render(request, 'main/error.html', {
            'error_message': f'Failed to load clause library: {str(e)}'
        })

# AJAX endpoints for dynamic functionality
@csrf_exempt
def ajax_simulate_scenario(request):
    """AJAX endpoint for what-if simulation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            clause_id = data.get('clause_id')
            scenario_type = data.get('scenario_type')
            modifications = data.get('modifications', {})
            
            if not clause_id or not scenario_type:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                })
            
            clause = get_object_or_404(Clause, id=clause_id)
            simulator = WhatIfSimulator()
            
            simulation_result = simulator.simulate_scenario(clause, scenario_type, modifications)
            
            if 'error' in simulation_result:
                return JsonResponse({
                    'success': False,
                    'error': simulation_result['error']
                })
            
            return JsonResponse({
                'success': True,
                'result': simulation_result
            })
            
        except Exception as e:
            logger.error(f"Error in AJAX simulation: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@csrf_exempt
def ajax_compare_clauses(request):
    """AJAX endpoint for clause comparison"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            clause1_id = data.get('clause1_id')
            clause2_id = data.get('clause2_id')
            
            if not clause1_id or not clause2_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                })
            
            clause1 = get_object_or_404(Clause, id=clause1_id)
            clause2 = get_object_or_404(Clause, id=clause2_id)
            
            library_service = ClauseLibraryService()
            comparison_result = library_service.compare_clauses(clause1, clause2)
            
            if 'error' in comparison_result:
                return JsonResponse({
                    'success': False,
                    'error': comparison_result['error']
                })
            
            return JsonResponse({
                'success': True,
                'result': comparison_result
            })
            
        except Exception as e:
            logger.error(f"Error in AJAX comparison: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
