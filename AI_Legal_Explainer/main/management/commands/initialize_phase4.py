"""
Django management command to initialize Phase 4 data and setup.

Usage:
    python manage.py initialize_phase4
    python manage.py initialize_phase4 --force
    python manage.py initialize_phase4 --user username
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from main.models import (
    SecurityAudit, ComplianceRecord, DataRetentionPolicy,
    UserConsent, PrivacyPolicy, TestResult, QualityMetric,
    PerformanceTest, SecurityTest, Documentation, TrainingMaterial,
    UserGuide, SupportTicket, ProductionEnvironment, MonitoringAlert,
    BackupRecord, UserOnboarding
)
from main.security_services import SecurityManager
from main.testing_services import TestSuite, QualityAssurance
from main.production_services import ProductionManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize Phase 4 data and setup for AI Legal Explainer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reinitialization of all Phase 4 data',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Initialize Phase 4 data for a specific user',
        )

    def handle(self, *args, **options):
        force = options['force']
        user_filter = options['user']

        try:
            self.stdout.write(
                self.style.SUCCESS('Starting Phase 4 initialization...')
            )

            if force:
                self.stdout.write('Force mode enabled - clearing existing data...')
                self._clear_phase4_data()

            # Initialize security and compliance
            self._initialize_security_compliance()

            # Initialize testing and quality assurance
            self._initialize_testing_qa()

            # Initialize documentation and training
            self._initialize_documentation_training()

            # Initialize production management
            self._initialize_production_management()

            # Initialize user-specific data if specified
            if user_filter:
                self._initialize_user_data(user_filter)

            self.stdout.write(
                self.style.SUCCESS('Phase 4 initialization completed successfully!')
            )

        except Exception as e:
            logger.error(f"Error during Phase 4 initialization: {e}")
            raise CommandError(f'Phase 4 initialization failed: {e}')

    def _clear_phase4_data(self):
        """Clear existing Phase 4 data."""
        try:
            # Clear all Phase 4 models
            SecurityAudit.objects.all().delete()
            ComplianceRecord.objects.all().delete()
            DataRetentionPolicy.objects.all().delete()
            UserConsent.objects.all().delete()
            PrivacyPolicy.objects.all().delete()
            TestResult.objects.all().delete()
            QualityMetric.objects.all().delete()
            PerformanceTest.objects.all().delete()
            SecurityTest.objects.all().delete()
            Documentation.objects.all().delete()
            TrainingMaterial.objects.all().delete()
            UserGuide.objects.all().delete()
            SupportTicket.objects.all().delete()
            ProductionEnvironment.objects.all().delete()
            MonitoringAlert.objects.all().delete()
            BackupRecord.objects.all().delete()
            UserOnboarding.objects.all().delete()

            self.stdout.write('Existing Phase 4 data cleared.')

        except Exception as e:
            logger.error(f"Error clearing Phase 4 data: {e}")
            raise

    def _initialize_security_compliance(self):
        """Initialize security and compliance data."""
        try:
            self.stdout.write('Initializing security and compliance...')

            # Create data retention policies
            retention_policies = [
                {
                    'data_type': 'user_data',
                    'retention_period_days': 2555,  # 7 years
                    'retention_reason': 'Legal compliance and business operations',
                    'disposal_method': 'secure_deletion'
                },
                {
                    'data_type': 'document_data',
                    'retention_period_days': 1825,  # 5 years
                    'retention_reason': 'Legal document retention requirements',
                    'disposal_method': 'secure_deletion'
                },
                {
                    'data_type': 'analytics_data',
                    'retention_period_days': 1095,  # 3 years
                    'retention_reason': 'Business analytics and improvement',
                    'disposal_method': 'anonymization'
                },
                {
                    'data_type': 'audit_logs',
                    'retention_period_days': 2555,  # 7 years
                    'retention_reason': 'Security and compliance auditing',
                    'disposal_method': 'archival'
                },
                {
                    'data_type': 'system_logs',
                    'retention_period_days': 365,  # 1 year
                    'retention_reason': 'System troubleshooting and monitoring',
                    'disposal_method': 'secure_deletion'
                },
                {
                    'data_type': 'backup_data',
                    'retention_period_days': 30,  # 30 days
                    'retention_reason': 'Disaster recovery and business continuity',
                    'disposal_method': 'secure_deletion'
                }
            ]

            for policy_data in retention_policies:
                DataRetentionPolicy.objects.get_or_create(
                    data_type=policy_data['data_type'],
                    defaults=policy_data
                )

            # Create initial privacy policy
            privacy_policy, created = PrivacyPolicy.objects.get_or_create(
                version='1.0',
                defaults={
                    'title': 'AI Legal Explainer Privacy Policy',
                    'content': self._get_default_privacy_policy(),
                    'language': 'en',
                    'effective_date': timezone.now(),
                    'is_active': True
                }
            )

            if created:
                self.stdout.write('Created default privacy policy.')

            # Create initial compliance records
            regulations = ['GDPR', 'PDPA']
            for regulation in regulations:
                ComplianceRecord.objects.get_or_create(
                    regulation=regulation,
                    defaults={
                        'compliance_status': 'under_review',
                        'requirements': self._get_regulation_requirements(regulation),
                        'gaps': 'Initial assessment pending',
                        'action_plan': 'Compliance assessment required'
                    }
                )

            self.stdout.write('Security and compliance initialization completed.')

        except Exception as e:
            logger.error(f"Error initializing security and compliance: {e}")
            raise

    def _initialize_testing_qa(self):
        """Initialize testing and quality assurance data."""
        try:
            self.stdout.write('Initializing testing and quality assurance...')

            # Create initial quality metrics
            quality_metrics = [
                {
                    'metric_name': 'test_coverage',
                    'metric_type': 'test_coverage',
                    'metric_value': 0.0,
                    'target_value': 80.0,
                    'unit': 'percentage',
                    'trend': 'unknown'
                },
                {
                    'metric_name': 'test_pass_rate',
                    'metric_type': 'test_coverage',
                    'metric_value': 0.0,
                    'target_value': 95.0,
                    'unit': 'percentage',
                    'trend': 'unknown'
                },
                {
                    'metric_name': 'performance_score',
                    'metric_type': 'performance',
                    'metric_value': 0.0,
                    'target_value': 85.0,
                    'unit': 'percentage',
                    'trend': 'unknown'
                },
                {
                    'metric_name': 'security_score',
                    'metric_type': 'security',
                    'metric_value': 0.0,
                    'target_value': 95.0,
                    'unit': 'percentage',
                    'trend': 'unknown'
                },
                {
                    'metric_name': 'code_quality_score',
                    'metric_type': 'code_quality',
                    'metric_value': 0.0,
                    'target_value': 85.0,
                    'unit': 'percentage',
                    'trend': 'unknown'
                }
            ]

            for metric_data in quality_metrics:
                QualityMetric.objects.get_or_create(
                    metric_name=metric_data['metric_name'],
                    defaults=metric_data
                )

            self.stdout.write('Testing and QA initialization completed.')

        except Exception as e:
            logger.error(f"Error initializing testing and QA: {e}")
            raise

    def _initialize_documentation_training(self):
        """Initialize documentation and training data."""
        try:
            self.stdout.write('Initializing documentation and training...')

            # Create initial documentation
            documentation_items = [
                {
                    'title': 'Getting Started Guide',
                    'content': self._get_getting_started_guide(),
                    'doc_type': 'user_guide',
                    'language': 'en',
                    'version': '1.0',
                    'is_published': True
                },
                {
                    'title': 'API Documentation',
                    'content': self._get_api_documentation(),
                    'doc_type': 'api_documentation',
                    'language': 'en',
                    'version': '1.0',
                    'is_published': True
                },
                {
                    'title': 'Deployment Guide',
                    'content': self._get_deployment_guide(),
                    'doc_type': 'deployment_guide',
                    'language': 'en',
                    'version': '1.0',
                    'is_published': True
                }
            ]

            for doc_data in documentation_items:
                Documentation.objects.get_or_create(
                    title=doc_data['title'],
                    defaults=doc_data
                )

            # Create initial training materials
            training_materials = [
                {
                    'title': 'Introduction to AI Legal Explainer',
                    'content': self._get_intro_training_content(),
                    'material_type': 'step_by_step',
                    'difficulty_level': 'beginner',
                    'estimated_duration': 15,
                    'language': 'en',
                    'is_active': True
                },
                {
                    'title': 'Advanced Document Analysis',
                    'content': self._get_advanced_training_content(),
                    'material_type': 'step_by_step',
                    'difficulty_level': 'intermediate',
                    'estimated_duration': 30,
                    'language': 'en',
                    'is_active': True
                }
            ]

            for material_data in training_materials:
                TrainingMaterial.objects.get_or_create(
                    title=material_data['title'],
                    defaults=material_data
                )

            self.stdout.write('Documentation and training initialization completed.')

        except Exception as e:
            logger.error(f"Error initializing documentation and training: {e}")
            raise

    def _initialize_production_management(self):
        """Initialize production management data."""
        try:
            self.stdout.write('Initializing production management...')

            # Create production environment
            production_env, created = ProductionEnvironment.objects.get_or_create(
                environment_name='production',
                defaults={
                    'environment_type': 'production',
                    'status': 'active',
                    'infrastructure_details': {
                        'web_server': 'Django',
                        'database': 'MySQL',
                        'cache': 'Redis',
                        'monitoring': 'Enabled'
                    },
                    'monitoring_enabled': True,
                    'alerting_enabled': True,
                    'backup_enabled': True
                }
            )

            if created:
                self.stdout.write('Created production environment.')

            # Create initial monitoring alert
            MonitoringAlert.objects.get_or_create(
                alert_name='System Initialization',
                defaults={
                    'alert_type': 'custom',
                    'severity': 'info',
                    'message': 'Phase 4 system initialization completed successfully',
                    'status': 'resolved',
                    'resolved_at': timezone.now()
                }
            )

            self.stdout.write('Production management initialization completed.')

        except Exception as e:
            logger.error(f"Error initializing production management: {e}")
            raise

    def _initialize_user_data(self, username):
        """Initialize Phase 4 data for a specific user."""
        try:
            self.stdout.write(f'Initializing Phase 4 data for user: {username}')

            user = User.objects.get(username=username)

            # Create user onboarding records
            onboarding_stages = [
                'welcome', 'profile_setup', 'feature_tour',
                'first_document', 'training_completed', 'onboarding_completed'
            ]

            for stage in onboarding_stages:
                UserOnboarding.objects.get_or_create(
                    user=user,
                    onboarding_stage=stage,
                    defaults={
                        'stage_completed': stage == 'welcome',
                        'completion_date': timezone.now() if stage == 'welcome' else None
                    }
                )

            # Create user consent records
            consent_types = [
                'data_processing', 'marketing', 'analytics',
                'third_party', 'cookies', 'location'
            ]

            for consent_type in consent_types:
                UserConsent.objects.get_or_create(
                    user=user,
                    consent_type=consent_type,
                    consent_version='1.0',
                    defaults={
                        'granted': True,
                        'consent_text': self._get_consent_text(consent_type),
                        'granted_at': timezone.now()
                    }
                )

            self.stdout.write(f'User data initialization completed for {username}.')

        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist.')
        except Exception as e:
            logger.error(f"Error initializing user data: {e}")
            raise

    def _get_default_privacy_policy(self):
        """Get default privacy policy content."""
        return """
        # Privacy Policy for AI Legal Explainer

        This privacy policy describes how AI Legal Explainer collects, uses, and protects your personal information.

        ## Information We Collect
        - Personal information (name, email, etc.)
        - Document content you upload
        - Usage analytics and preferences
        - Technical information about your device

        ## How We Use Your Information
        - To provide legal document analysis services
        - To improve our services
        - To communicate with you about updates
        - To ensure security and compliance

        ## Data Protection
        - All data is encrypted in transit and at rest
        - We implement strict access controls
        - Regular security audits are conducted
        - Compliance with GDPR and PDPA regulations

        ## Your Rights
        - Right to access your data
        - Right to correct inaccurate data
        - Right to delete your data
        - Right to withdraw consent
        - Right to data portability

        ## Contact Information
        For privacy-related questions, please contact our privacy team.
        """

    def _get_regulation_requirements(self, regulation):
        """Get requirements for a specific regulation."""
        if regulation == 'GDPR':
            return {
                'data_processing': 'Lawful basis required',
                'user_rights': 'Right to access, rectification, erasure',
                'consent': 'Explicit consent required',
                'data_retention': 'Limited retention periods',
                'breach_notification': '72-hour notification requirement'
            }
        elif regulation == 'PDPA':
            return {
                'data_processing': 'Consent or legitimate interest required',
                'user_rights': 'Right to access and correction',
                'consent': 'Consent required for processing',
                'data_retention': 'Reasonable retention periods',
                'breach_notification': 'Notification to PDPC required'
            }
        else:
            return {}

    def _get_getting_started_guide(self):
        """Get getting started guide content."""
        return """
        # Getting Started with AI Legal Explainer

        Welcome to AI Legal Explainer! This guide will help you get started with analyzing legal documents.

        ## Step 1: Create an Account
        - Sign up with your email address
        - Verify your email
        - Complete your profile

        ## Step 2: Upload Your First Document
        - Click "Upload Document" button
        - Select your legal document (PDF, DOCX, or TXT)
        - Wait for processing to complete

        ## Step 3: Review Analysis
        - Read the plain-language summary
        - Check risk indicators
        - Review identified clauses
        - Use the Q&A feature for specific questions

        ## Step 4: Explore Features
        - Try the what-if simulation
        - Check the glossary for legal terms
        - Use multilingual features if available

        ## Need Help?
        - Check our FAQ section
        - Contact support if you have questions
        - Review training materials for advanced features
        """

    def _get_api_documentation(self):
        """Get API documentation content."""
        return """
        # API Documentation

        The AI Legal Explainer API provides programmatic access to our services.

        ## Authentication
        - API key required for all requests
        - Include in Authorization header
        - Rate limiting: 100 requests per hour

        ## Endpoints

        ### Document Analysis
        POST /api/analyze/
        - Upload and analyze legal documents
        - Returns summary and risk analysis

        ### Q&A
        POST /api/qa/
        - Ask questions about legal documents
        - Returns AI-generated answers

        ### User Management
        GET /api/user/profile/
        - Get user profile information
        - Requires authentication

        ## Response Format
        All API responses are in JSON format with standard HTTP status codes.

        ## Error Handling
        - 400: Bad Request
        - 401: Unauthorized
        - 429: Rate Limited
        - 500: Internal Server Error
        """

    def _get_deployment_guide(self):
        """Get deployment guide content."""
        return """
        # Deployment Guide

        This guide covers deploying AI Legal Explainer to production.

        ## Prerequisites
        - Python 3.8+
        - MySQL 8.0+
        - Redis 6.0+
        - Nginx or Apache

        ## Installation Steps

        ### 1. Clone Repository
        ```bash
        git clone https://github.com/your-org/ai-legal-explainer.git
        cd ai-legal-explainer
        ```

        ### 2. Install Dependencies
        ```bash
        pip install -r requirements_phase4.txt
        ```

        ### 3. Configure Environment
        - Copy .env.example to .env
        - Set database credentials
        - Configure API keys
        - Set production settings

        ### 4. Database Setup
        ```bash
        python manage.py migrate
        python manage.py initialize_phase4
        ```

        ### 5. Collect Static Files
        ```bash
        python manage.py collectstatic
        ```

        ### 6. Start Services
        ```bash
        gunicorn AI_Legal_Explainer.wsgi:application
        ```

        ## Production Considerations
        - Use HTTPS
        - Set up monitoring
        - Configure backups
        - Enable logging
        - Set up CI/CD pipeline
        """

    def _get_intro_training_content(self):
        """Get introduction training content."""
        return """
        # Introduction to AI Legal Explainer

        Welcome to your first training session! This module covers the basics.

        ## What is AI Legal Explainer?
        AI Legal Explainer is an intelligent tool that helps you understand legal documents by:
        - Converting complex legal language to plain English
        - Identifying potential risks and issues
        - Highlighting important clauses
        - Answering your questions about the document

        ## Key Benefits
        - Save time reading legal documents
        - Understand risks before signing
        - Get answers to specific questions
        - Learn legal terminology

        ## Getting Started
        - Upload your first document
        - Read the summary
        - Ask questions using the chat feature
        - Review risk indicators

        ## Practice Exercise
        Try uploading a simple legal document and practice using each feature.
        """

    def _get_advanced_training_content(self):
        """Get advanced training content."""
        return """
        # Advanced Document Analysis

        This module covers advanced features for power users.

        ## Advanced Features
        - What-if simulations
        - Clause comparison
        - Risk pattern analysis
        - Custom glossary entries

        ## Best Practices
        - Use specific questions for better answers
        - Compare multiple documents
        - Track changes over time
        - Export analysis reports

        ## Troubleshooting
        - Common issues and solutions
        - Performance optimization
        - Error handling
        - Support resources

        ## Advanced Exercise
        Upload a complex contract and practice using all advanced features.
        """

    def _get_consent_text(self, consent_type):
        """Get consent text for a specific consent type."""
        consent_texts = {
            'data_processing': 'I consent to the processing of my personal data for the purpose of providing legal document analysis services.',
            'marketing': 'I consent to receive marketing communications about new features and updates.',
            'analytics': 'I consent to the use of analytics and tracking to improve service quality.',
            'third_party': 'I consent to the sharing of my data with third-party service providers.',
            'cookies': 'I consent to the use of cookies for essential website functionality.',
            'location': 'I consent to the collection and processing of my location data.'
        }
        return consent_texts.get(consent_type, 'I consent to the specified data processing.')
