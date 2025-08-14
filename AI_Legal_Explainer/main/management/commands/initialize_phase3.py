"""
Management command to initialize Phase 3 functionality
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from main.models import (
    OfflineFeature, ConnectivityStatus, TransparencyPreference,
    UserLanguagePreference, PerformanceMetrics
)
from main.offline_services import OfflineModeManager
from main.transparency_services import TransparencyManager
from main.performance_services import PerformanceAnalyzer
from main.analytics_services import AnalyticsDashboard
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize Phase 3 functionality including offline mode, transparency controls, and performance optimization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reinitialization even if data exists',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to initialize preferences for (default: all users)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Phase 3 initialization...')
        )
        
        try:
            # Initialize offline features
            self.initialize_offline_features(options['force'])
            
            # Initialize connectivity status
            self.initialize_connectivity_status(options['force'])
            
            # Initialize transparency preferences
            self.initialize_transparency_preferences(options['force'], options['user'])
            
            # Initialize language preferences
            self.initialize_language_preferences(options['force'], options['user'])
            
            # Initialize performance monitoring
            self.initialize_performance_monitoring(options['force'])
            
            # Initialize offline mode system
            self.initialize_offline_mode_system()
            
            self.stdout.write(
                self.style.SUCCESS('Phase 3 initialization completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Phase 3 initialization failed: {str(e)}')
            )
            logger.error(f'Phase 3 initialization failed: {e}')
            raise

    def initialize_offline_features(self, force=False):
        """Initialize offline features configuration"""
        self.stdout.write('Initializing offline features...')
        
        default_features = [
            {
                'feature_name': 'document_summary',
                'is_available_offline': True,
                'requires_internet': False,
                'fallback_mode': 'cached_summary',
                'local_model_required': False,
                'cache_strategy': 'persistent',
                'priority': 1
            },
            {
                'feature_name': 'clause_detection',
                'is_available_offline': True,
                'requires_internet': False,
                'fallback_mode': 'basic_detection',
                'local_model_required': False,
                'cache_strategy': 'persistent',
                'priority': 2
            },
            {
                'feature_name': 'risk_analysis',
                'is_available_offline': True,
                'requires_internet': False,
                'fallback_mode': 'cached_analysis',
                'local_model_required': False,
                'cache_strategy': 'persistent',
                'priority': 3
            },
            {
                'feature_name': 'glossary_lookup',
                'is_available_offline': True,
                'requires_internet': False,
                'fallback_mode': 'cached_glossary',
                'local_model_required': False,
                'cache_strategy': 'persistent',
                'priority': 4
            },
            {
                'feature_name': 'ai_chat',
                'is_available_offline': False,
                'requires_internet': True,
                'fallback_mode': 'cached_responses',
                'local_model_required': True,
                'cache_strategy': 'temporary',
                'priority': 5
            },
            {
                'feature_name': 'advanced_analysis',
                'is_available_offline': False,
                'requires_internet': True,
                'fallback_mode': 'basic_analysis',
                'local_model_required': True,
                'cache_strategy': 'temporary',
                'priority': 6
            }
        ]
        
        for feature_config in default_features:
            feature, created = OfflineFeature.objects.get_or_create(
                feature_name=feature_config['feature_name'],
                defaults=feature_config
            )
            
            if created:
                self.stdout.write(f'  Created offline feature: {feature.feature_name}')
            elif force:
                for key, value in feature_config.items():
                    setattr(feature, key, value)
                feature.save()
                self.stdout.write(f'  Updated offline feature: {feature.feature_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'  Offline features initialized: {OfflineFeature.objects.count()} features')
        )

    def initialize_connectivity_status(self, force=False):
        """Initialize connectivity status"""
        self.stdout.write('Initializing connectivity status...')
        
        if force or not ConnectivityStatus.objects.exists():
            status = ConnectivityStatus.objects.create(
                is_online=True,
                connection_quality='excellent',
                last_online_check=timezone.now(),
                offline_since=None,
                api_endpoints_status={
                    'online_count': 3,
                    'total_count': 3,
                    'last_check': timezone.now().isoformat()
                }
            )
            self.stdout.write('  Created connectivity status')
        else:
            self.stdout.write('  Connectivity status already exists')

    def initialize_transparency_preferences(self, force=False, username=None):
        """Initialize transparency preferences for users"""
        self.stdout.write('Initializing transparency preferences...')
        
        if username:
            users = User.objects.filter(username=username)
        else:
            users = User.objects.all()
        
        preferences_created = 0
        preferences_updated = 0
        
        for user in users:
            if force or not TransparencyPreference.objects.filter(user=user).exists():
                preference, created = TransparencyPreference.objects.get_or_create(
                    user=user,
                    defaults={
                        'explanation_detail_level': 'medium',
                        'show_confidence_scores': True,
                        'show_source_citations': True,
                        'show_technical_details': False,
                        'auto_adjust_complexity': True,
                        'preferred_explanation_style': 'conversational'
                    }
                )
                
                if created:
                    preferences_created += 1
                else:
                    preferences_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'  Transparency preferences: {preferences_created} created, {preferences_updated} updated')
        )

    def initialize_language_preferences(self, force=False, username=None):
        """Initialize language preferences for users"""
        self.stdout.write('Initializing language preferences...')
        
        if username:
            users = User.objects.filter(username=username)
        else:
            users = User.objects.all()
        
        preferences_created = 0
        preferences_updated = 0
        
        for user in users:
            if force or not UserLanguagePreference.objects.filter(user=user).exists():
                preference, created = UserLanguagePreference.objects.get_or_create(
                    user=user,
                    defaults={
                        'preferred_language': 'en',
                        'fallback_language': 'en',
                        'auto_translate': True
                    }
                )
                
                if created:
                    preferences_created += 1
                else:
                    preferences_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'  Language preferences: {preferences_created} created, {preferences_updated} updated')
        )

    def initialize_performance_monitoring(self, force=False):
        """Initialize performance monitoring system"""
        self.stdout.write('Initializing performance monitoring...')
        
        # Create initial performance metrics if none exist
        if force or not PerformanceMetrics.objects.exists():
            # Create a sample performance metric
            PerformanceMetrics.objects.create(
                feature_name='system_initialization',
                operation_type='initialization',
                start_time=timezone.now(),
                end_time=timezone.now(),
                duration_ms=100,
                success=True,
                resource_usage={'cpu_percent': 5.0, 'memory_percent': 10.0}
            )
            self.stdout.write('  Created initial performance metric')
        
        self.stdout.write('  Performance monitoring initialized')

    def initialize_offline_mode_system(self):
        """Initialize the offline mode system"""
        self.stdout.write('Initializing offline mode system...')
        
        try:
            offline_manager = OfflineModeManager()
            success = offline_manager.initialize_offline_mode()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('  Offline mode system initialized successfully')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('  Offline mode system initialization failed')
                )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  Offline mode system initialization error: {str(e)}')
            )
        
        self.stdout.write('  Offline mode system initialization completed')
