"""
Phase 4 Views

This module provides views for Phase 4 features including security,
testing, documentation, and production management.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import (
    SecurityAudit, ComplianceRecord, DataRetentionPolicy,
    UserConsent, PrivacyPolicy, TestResult, QualityMetric,
    PerformanceTest, SecurityTest, Documentation, TrainingMaterial,
    UserGuide, SupportTicket, ProductionEnvironment, MonitoringAlert,
    BackupRecord, UserOnboarding
)
from .security_services import SecurityManager
from .testing_services import TestSuite, QualityAssurance
from .production_services import ProductionManager

logger = logging.getLogger(__name__)


# Security & Compliance Views

@staff_member_required
def security_dashboard(request):
    """Security dashboard view."""
    try:
        security_manager = SecurityManager()
        
        # Get recent security audits
        recent_audits = SecurityAudit.objects.all().order_by('-started_at')[:10]
        
        # Get compliance status
        compliance_status = security_manager.check_compliance()
        
        # Get active alerts
        active_alerts = MonitoringAlert.objects.filter(status='active').order_by('-created_at')[:5]
        
        context = {
            'recent_audits': recent_audits,
            'compliance_status': compliance_status,
            'active_alerts': active_alerts,
            'total_audits': SecurityAudit.objects.count(),
            'pending_audits': SecurityAudit.objects.filter(status='pending').count(),
            'critical_issues': SecurityAudit.objects.filter(severity='critical').count(),
        }
        
        return render(request, 'main/security_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in security dashboard: {e}")
        messages.error(request, f"Error loading security dashboard: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@staff_member_required
def run_security_audit(request):
    """Run security audit."""
    if request.method == 'POST':
        try:
            audit_type = request.POST.get('audit_type', 'security_scan')
            
            security_manager = SecurityManager()
            audit_result = security_manager.run_security_audit(audit_type)
            
            if audit_result['status'] == 'completed':
                messages.success(request, f"Security audit completed successfully. Severity: {audit_result['severity']}")
            else:
                messages.error(request, f"Security audit failed: {audit_result.get('error', 'Unknown error')}")
            
            return redirect('security_dashboard')
            
        except Exception as e:
            logger.error(f"Error running security audit: {e}")
            messages.error(request, f"Error running security audit: {e}")
            return redirect('security_dashboard')
    
    return redirect('security_dashboard')


@staff_member_required
def compliance_dashboard(request):
    """Compliance dashboard view."""
    try:
        # Get compliance records
        compliance_records = ComplianceRecord.objects.all().order_by('-last_assessment')
        
        # Get data retention policies
        retention_policies = DataRetentionPolicy.objects.filter(is_active=True)
        
        # Get user consent statistics
        consent_stats = UserConsent.objects.values('consent_type').annotate(
            granted_count=Count('id', filter=Q(granted=True)),
            total_count=Count('id')
        )
        
        context = {
            'compliance_records': compliance_records,
            'retention_policies': retention_policies,
            'consent_stats': consent_stats,
            'total_regulations': compliance_records.count(),
            'compliant_regulations': compliance_records.filter(compliance_status='compliant').count(),
        }
        
        return render(request, 'main/compliance_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in compliance dashboard: {e}")
        messages.error(request, f"Error loading compliance dashboard: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@login_required
def privacy_center(request):
    """User privacy center view."""
    try:
        user = request.user
        
        # Get user consents
        user_consents = UserConsent.objects.filter(user=user).order_by('-granted_at')
        
        # Get privacy policies
        privacy_policies = PrivacyPolicy.objects.filter(is_active=True).order_by('-effective_date')
        
        context = {
            'user_consents': user_consents,
            'privacy_policies': privacy_policies,
            'user': user,
        }
        
        return render(request, 'main/privacy_center.html', context)
        
    except Exception as e:
        logger.error(f"Error in privacy center: {e}")
        messages.error(request, f"Error loading privacy center: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def update_consent(request):
    """Update user consent."""
    try:
        data = json.loads(request.body)
        consent_type = data.get('consent_type')
        granted = data.get('granted', False)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        security_manager = SecurityManager()
        privacy_manager = security_manager.get_consent_manager()
        
        success = privacy_manager.record_consent(
            user_id=request.user.id,
            consent_type=consent_type,
            granted=granted,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        if success:
            return JsonResponse({'status': 'success', 'message': 'Consent updated successfully'})
        else:
            return JsonResponse({'error': 'Failed to update consent'}, status=400)
            
    except Exception as e:
        logger.error(f"Error updating consent: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# Testing & Quality Assurance Views

@staff_member_required
def testing_dashboard(request):
    """Testing dashboard view."""
    try:
        # Get recent test results
        recent_tests = TestResult.objects.all().order_by('-run_at')[:10]
        
        # Get quality metrics
        quality_metrics = QualityMetric.objects.all().order_by('-measurement_date')[:10]
        
        # Get performance test results
        performance_tests = PerformanceTest.objects.all().order_by('-run_at')[:5]
        
        # Get security test results
        security_tests = SecurityTest.objects.all().order_by('-run_at')[:5]
        
        context = {
            'recent_tests': recent_tests,
            'quality_metrics': quality_metrics,
            'performance_tests': performance_tests,
            'security_tests': security_tests,
            'total_tests': TestResult.objects.count(),
            'passed_tests': TestResult.objects.filter(status='passed').count(),
            'failed_tests': TestResult.objects.filter(status='failed').count(),
        }
        
        return render(request, 'main/testing_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in testing dashboard: {e}")
        messages.error(request, f"Error loading testing dashboard: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@staff_member_required
def run_test_suite(request):
    """Run comprehensive test suite."""
    if request.method == 'POST':
        try:
            test_suite = TestSuite()
            test_results = test_suite.run_all_tests()
            
            if test_results.get('status') != 'failed':
                messages.success(request, "Test suite completed successfully")
            else:
                messages.error(request, f"Test suite failed: {test_results.get('error', 'Unknown error')}")
            
            return redirect('testing_dashboard')
            
        except Exception as e:
            logger.error(f"Error running test suite: {e}")
            messages.error(request, f"Error running test suite: {e}")
            return redirect('testing_dashboard')
    
    return redirect('testing_dashboard')


@staff_member_required
def quality_assurance(request):
    """Quality assurance view."""
    try:
        qa = QualityAssurance()
        quality_report = qa.run_quality_check()
        
        context = {
            'quality_report': quality_report,
            'thresholds': quality_report.get('thresholds', {}),
            'quality_status': quality_report.get('quality_status', {}),
        }
        
        return render(request, 'main/quality_assurance.html', context)
        
    except Exception as e:
        logger.error(f"Error in quality assurance: {e}")
        messages.error(request, f"Error loading quality assurance: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


# Documentation & Training Views

@login_required
def documentation_portal(request):
    """Documentation portal view."""
    try:
        # Get documentation by type
        user_guides = Documentation.objects.filter(
            doc_type='user_guide',
            is_published=True
        ).order_by('-updated_at')
        
        api_docs = Documentation.objects.filter(
            doc_type='api_documentation',
            is_published=True
        ).order_by('-updated_at')
        
        deployment_guides = Documentation.objects.filter(
            doc_type='deployment_guide',
            is_published=True
        ).order_by('-updated_at')
        
        context = {
            'user_guides': user_guides,
            'api_docs': api_docs,
            'deployment_guides': deployment_guides,
        }
        
        return render(request, 'main/documentation_portal.html', context)
        
    except Exception as e:
        logger.error(f"Error in documentation portal: {e}")
        messages.error(request, f"Error loading documentation portal: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@login_required
def training_portal(request):
    """Training portal view."""
    try:
        # Get training materials by difficulty level
        beginner_materials = TrainingMaterial.objects.filter(
            difficulty_level='beginner',
            is_active=True
        ).order_by('title')
        
        intermediate_materials = TrainingMaterial.objects.filter(
            difficulty_level='intermediate',
            is_active=True
        ).order_by('title')
        
        advanced_materials = TrainingMaterial.objects.filter(
            difficulty_level='advanced',
            is_active=True
        ).order_by('title')
        
        context = {
            'beginner_materials': beginner_materials,
            'intermediate_materials': intermediate_materials,
            'advanced_materials': advanced_materials,
        }
        
        return render(request, 'main/training_portal.html', context)
        
    except Exception as e:
        logger.error(f"Error in training portal: {e}")
        messages.error(request, f"Error loading training portal: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@login_required
def support_portal(request):
    """Support portal view."""
    try:
        user = request.user
        
        # Get user's support tickets
        user_tickets = SupportTicket.objects.filter(user=user).order_by('-created_at')
        
        # Get all tickets (for staff)
        all_tickets = None
        if user.is_staff:
            all_tickets = SupportTicket.objects.all().order_by('-created_at')
        
        context = {
            'user_tickets': user_tickets,
            'all_tickets': all_tickets,
            'total_tickets': user_tickets.count(),
            'open_tickets': user_tickets.filter(status='open').count(),
        }
        
        return render(request, 'main/support_portal.html', context)
        
    except Exception as e:
        logger.error(f"Error in support portal: {e}")
        messages.error(request, f"Error loading support portal: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@login_required
def create_support_ticket(request):
    """Create support ticket."""
    if request.method == 'POST':
        try:
            subject = request.POST.get('subject')
            description = request.POST.get('description')
            ticket_type = request.POST.get('ticket_type')
            priority = request.POST.get('priority')
            
            if not all([subject, description, ticket_type, priority]):
                messages.error(request, "All fields are required")
                return redirect('support_portal')
            
            ticket = SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                description=description,
                ticket_type=ticket_type,
                priority=priority,
                status='open'
            )
            
            messages.success(request, f"Support ticket #{ticket.id} created successfully")
            return redirect('support_portal')
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            messages.error(request, f"Error creating support ticket: {e}")
            return redirect('support_portal')
    
    return redirect('support_portal')


# Production Management Views

@staff_member_required
def production_dashboard(request):
    """Production dashboard view."""
    try:
        production_manager = ProductionManager()
        production_status = production_manager.get_production_status()
        
        # Get production environment info
        environments = ProductionEnvironment.objects.all().order_by('environment_name')
        
        # Get recent backups
        recent_backups = BackupRecord.objects.all().order_by('-started_at')[:5]
        
        # Get active monitoring alerts
        active_alerts = MonitoringAlert.objects.filter(status='active').order_by('-created_at')[:10]
        
        context = {
            'production_status': production_status,
            'environments': environments,
            'recent_backups': recent_backups,
            'active_alerts': active_alerts,
            'total_backups': BackupRecord.objects.count(),
            'successful_backups': BackupRecord.objects.filter(status='completed').count(),
            'failed_backups': BackupRecord.objects.filter(status='failed').count(),
        }
        
        return render(request, 'main/production_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in production dashboard: {e}")
        messages.error(request, f"Error loading production dashboard: {e}")
        return render(request, 'main/error.html', {'error': str(e)})


@staff_member_required
def setup_monitoring(request):
    """Setup production monitoring."""
    if request.method == 'POST':
        try:
            production_manager = ProductionManager()
            monitoring_result = production_manager.setup_monitoring()
            
            if monitoring_result['status'] == 'success':
                messages.success(request, "Production monitoring setup completed successfully")
            else:
                messages.error(request, f"Monitoring setup failed: {monitoring_result.get('error', 'Unknown error')}")
            
            return redirect('production_dashboard')
            
        except Exception as e:
            logger.error(f"Error setting up monitoring: {e}")
            messages.error(request, f"Error setting up monitoring: {e}")
            return redirect('production_dashboard')
    
    return redirect('production_dashboard')


@staff_member_required
def create_backup(request):
    """Create production backup."""
    if request.method == 'POST':
        try:
            production_manager = ProductionManager()
            backup_result = production_manager.create_backup()
            
            if backup_result['status'] == 'success':
                messages.success(request, f"Backup created successfully: {backup_result['backup_name']}")
            else:
                messages.error(request, f"Backup failed: {backup_result.get('error', 'Unknown error')}")
            
            return redirect('production_dashboard')
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            messages.error(request, f"Error creating backup: {e}")
            return redirect('production_dashboard')
    
    return redirect('production_dashboard')


@staff_member_required
def setup_onboarding(request):
    """Setup user onboarding system."""
    if request.method == 'POST':
        try:
            production_manager = ProductionManager()
            onboarding_result = production_manager.setup_user_onboarding()
            
            if onboarding_result['status'] == 'success':
                messages.success(request, "User onboarding system setup completed successfully")
            else:
                messages.error(request, f"Onboarding setup failed: {onboarding_result.get('error', 'Unknown error')}")
            
            return redirect('production_dashboard')
            
        except Exception as e:
            logger.error(f"Error setting up onboarding: {e}")
            messages.error(request, f"Error setting up onboarding: {e}")
            return redirect('production_dashboard')
    
    return redirect('production_dashboard')


# API Views for Phase 4

@csrf_exempt
@require_http_methods(["GET"])
def api_security_status(request):
    """API endpoint for security status."""
    try:
        security_manager = SecurityManager()
        status = security_manager.check_compliance()
        
        return JsonResponse({
            'status': 'success',
            'data': status,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in security status API: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_testing_results(request):
    """API endpoint for testing results."""
    try:
        # Get recent test results
        recent_tests = TestResult.objects.all().order_by('-run_at')[:20]
        
        test_data = []
        for test in recent_tests:
            test_data.append({
                'id': str(test.id),
                'test_name': test.test_name,
                'test_type': test.test_type,
                'status': test.status,
                'execution_time': test.execution_time,
                'run_at': test.run_at.isoformat(),
            })
        
        return JsonResponse({
            'status': 'success',
            'data': test_data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in testing results API: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_production_status(request):
    """API endpoint for production status."""
    try:
        production_manager = ProductionManager()
        status = production_manager.get_production_status()
        
        return JsonResponse({
            'status': 'success',
            'data': status,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in production status API: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_health_check(request):
    """Health check endpoint for production monitoring."""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'database': 'connected',
            'timestamp': timezone.now().isoformat(),
            'version': '4.0.0'
        }
        
        # Check database connection
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['database'] = 'connected'
        except Exception:
            health_status['database'] = 'disconnected'
            health_status['status'] = 'unhealthy'
        
        # Check if application is responding
        health_status['application'] = 'responding'
        
        return JsonResponse(health_status)
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
