"""
Offline Mode Services for AI Legal Explainer
Implements Phase 3.1: Offline Mode functionality
"""

import requests
import time
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import threading
import queue
import os

from .models import (
    ConnectivityStatus, LocalCache, OfflineFeature, 
    PerformanceMetrics, Document, DocumentSummary, Clause
)

logger = logging.getLogger(__name__)

class ConnectivityMonitor:
    """Monitors connectivity status and manages offline mode"""
    
    def __init__(self):
        self.check_interval = 30  # seconds
        self.endpoints_to_check = [
            'https://www.google.com',
            'https://api.openai.com',
            'https://generativelanguage.googleapis.com',
        ]
        self.is_monitoring = False
        self.monitor_thread = None
        self.status_queue = queue.Queue()
    
    def start_monitoring(self):
        """Start background connectivity monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Connectivity monitoring started")
    
    def stop_monitoring(self):
        """Stop background connectivity monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("Connectivity monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                status = self.check_connectivity()
                self.status_queue.put(status)
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in connectivity monitoring: {e}")
                time.sleep(self.check_interval)
    
    def check_connectivity(self):
        """Check current connectivity status"""
        try:
            # Check multiple endpoints
            online_endpoints = 0
            total_endpoints = len(self.endpoints_to_check)
            
            for endpoint in self.endpoints_to_check:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        online_endpoints += 1
                except:
                    pass
            
            # Calculate connection quality
            if online_endpoints == total_endpoints:
                quality = 'excellent'
                is_online = True
            elif online_endpoints > total_endpoints * 0.7:
                quality = 'good'
                is_online = True
            elif online_endpoints > total_endpoints * 0.3:
                quality = 'fair'
                is_online = True
            elif online_endpoints > 0:
                quality = 'poor'
                is_online = True
            else:
                quality = 'offline'
                is_online = False
            
            # Update database
            status, created = ConnectivityStatus.objects.get_or_create(
                id=1,  # Single global status
                defaults={
                    'is_online': is_online,
                    'connection_quality': quality,
                    'api_endpoints_status': {
                        'online_count': online_endpoints,
                        'total_count': total_endpoints,
                        'last_check': timezone.now().isoformat()
                    }
                }
            )
            
            if not created:
                status.is_online = is_online
                status.connection_quality = quality
                status.api_endpoints_status = {
                    'online_count': online_endpoints,
                    'total_count': total_endpoints,
                    'last_check': timezone.now().isoformat()
                }
                
                # Update offline timestamp
                if not is_online and status.is_online:
                    status.offline_since = timezone.now()
                elif is_online and not status.is_online:
                    status.offline_since = None
                
                status.save()
            
            return {
                'is_online': is_online,
                'quality': quality,
                'online_endpoints': online_endpoints,
                'total_endpoints': total_endpoints
            }
            
        except Exception as e:
            logger.error(f"Error checking connectivity: {e}")
            return {
                'is_online': False,
                'quality': 'offline',
                'error': str(e)
            }
    
    def get_current_status(self):
        """Get current connectivity status from database"""
        try:
            status = ConnectivityStatus.objects.get(id=1)
            return {
                'is_online': status.is_online,
                'quality': status.connection_quality,
                'last_check': status.last_online_check,
                'offline_since': status.offline_since,
                'api_status': status.api_endpoints_status
            }
        except ConnectivityStatus.DoesNotExist:
            return self.check_connectivity()

class OfflineModeManager:
    """Manages offline mode features and fallbacks"""
    
    def __init__(self):
        self.connectivity_monitor = ConnectivityMonitor()
        self.cache_manager = LocalCacheManager()
        self.feature_manager = OfflineFeatureManager()
    
    def initialize_offline_mode(self):
        """Initialize offline mode system"""
        try:
            # Start connectivity monitoring
            self.connectivity_monitor.start_monitoring()
            
            # Initialize offline features
            self.feature_manager.initialize_features()
            
            # Preload essential data to cache
            self.cache_manager.preload_essential_data()
            
            logger.info("Offline mode system initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize offline mode: {e}")
            return False
    
    def is_feature_available_offline(self, feature_name):
        """Check if a specific feature is available offline"""
        try:
            feature = OfflineFeature.objects.get(feature_name=feature_name)
            if not feature.is_available_offline:
                return False
            
            # Check if we have local models/cache for this feature
            if feature.local_model_required:
                return self.cache_manager.has_local_model(feature_name)
            
            return True
        except OfflineFeature.DoesNotExist:
            return False
    
    def get_offline_fallback(self, feature_name):
        """Get offline fallback for a feature"""
        try:
            feature = OfflineFeature.objects.get(feature_name=feature_name)
            return feature.fallback_mode
        except OfflineFeature.DoesNotExist:
            return None
    
    def handle_offline_operation(self, operation_type, **kwargs):
        """Handle operations in offline mode"""
        try:
            # Check if operation can be performed offline
            if not self.is_feature_available_offline(operation_type):
                return {
                    'success': False,
                    'error': f'Feature {operation_type} not available offline',
                    'offline_mode': True
                }
            
            # Try to get from cache first
            cache_key = f"{operation_type}_{hash(str(kwargs))}"
            cached_result = self.cache_manager.get_cache(cache_key)
            
            if cached_result:
                return {
                    'success': True,
                    'data': cached_result,
                    'source': 'cache',
                    'offline_mode': True
                }
            
            # Perform offline operation
            if operation_type == 'document_summary':
                return self._offline_document_summary(**kwargs)
            elif operation_type == 'clause_detection':
                return self._offline_clause_detection(**kwargs)
            elif operation_type == 'risk_analysis':
                return self._offline_risk_analysis(**kwargs)
            elif operation_type == 'glossary_lookup':
                return self._offline_glossary_lookup(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation type: {operation_type}',
                    'offline_mode': True
                }
                
        except Exception as e:
            logger.error(f"Error in offline operation {operation_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'offline_mode': True
            }
    
    def _offline_document_summary(self, document_id):
        """Generate document summary using offline methods"""
        try:
            document = Document.objects.get(id=document_id)
            
            # Use cached summary if available
            if hasattr(document, 'summary'):
                return {
                    'success': True,
                    'data': {
                        'summary': document.summary.plain_language_summary,
                        'key_points': document.summary.key_points,
                        'source': 'cached_summary'
                    }
                }
            
            # Generate basic summary from text
            text = document.processed_text or document.original_text
            if text:
                # Simple text summarization (basic NLP)
                sentences = text.split('.')
                summary = '. '.join(sentences[:3]) + '.'
                
                return {
                    'success': True,
                    'data': {
                        'summary': summary,
                        'key_points': ['Basic offline summary generated'],
                        'source': 'offline_generated'
                    }
                }
            
            return {
                'success': False,
                'error': 'No text available for summary generation'
            }
            
        except Document.DoesNotExist:
            return {
                'success': False,
                'error': 'Document not found'
            }
    
    def _offline_clause_detection(self, document_id):
        """Detect clauses using offline methods"""
        try:
            document = Document.objects.get(id=document_id)
            
            # Use cached clauses if available
            clauses = document.clauses.all()
            if clauses.exists():
                return {
                    'success': True,
                    'data': {
                        'clauses': list(clauses.values()),
                        'source': 'cached_clauses'
                    }
                }
            
            # Basic offline clause detection using keywords
            text = document.processed_text or document.original_text
            if text:
                detected_clauses = self._basic_clause_detection(text)
                return {
                    'success': True,
                    'data': {
                        'clauses': detected_clauses,
                        'source': 'offline_detected'
                    }
                }
            
            return {
                'success': False,
                'error': 'No text available for clause detection'
            }
            
        except Document.DoesNotExist:
            return {
                'success': False,
                'error': 'Document not found'
            }
    
    def _basic_clause_detection(self, text):
        """Basic clause detection using keyword patterns"""
        clauses = []
        
        # Define keyword patterns for different clause types
        patterns = {
            'penalty': ['penalty', 'fine', 'damages', 'liquidated damages'],
            'auto_renewal': ['auto-renewal', 'automatic renewal', 'renewal'],
            'termination': ['termination', 'terminate', 'cancel', 'cancellation'],
            'indemnification': ['indemnify', 'indemnification', 'hold harmless'],
            'liability': ['liability', 'liable', 'responsibility', 'responsible'],
        }
        
        text_lower = text.lower()
        
        for clause_type, keywords in patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find position of keyword
                    pos = text_lower.find(keyword)
                    start_pos = max(0, pos - 100)
                    end_pos = min(len(text), pos + 200)
                    
                    clause_text = text[start_pos:end_pos]
                    
                    clauses.append({
                        'clause_type': clause_type,
                        'original_text': clause_text,
                        'start_position': start_pos,
                        'end_position': end_pos,
                        'risk_level': 'medium',  # Default risk level
                        'risk_score': 0.5,
                        'plain_language_summary': f'Contains {clause_type.replace("_", " ")} terms',
                        'risk_explanation': f'This clause contains {clause_type.replace("_", " ")} language'
                    })
                    break  # Only add one instance per clause type
        
        return clauses
    
    def _offline_risk_analysis(self, document_id):
        """Perform risk analysis using offline methods"""
        try:
            document = Document.objects.get(id=document_id)
            
            # Use cached risk analysis if available
            if hasattr(document, 'risk_analysis'):
                return {
                    'success': True,
                    'data': {
                        'overall_risk_score': document.risk_analysis.overall_risk_score,
                        'overall_risk_level': document.risk_analysis.overall_risk_level,
                        'clause_counts': {
                            'high': document.risk_analysis.high_risk_clauses_count,
                            'medium': document.risk_analysis.medium_risk_clauses_count,
                            'low': document.risk_analysis.low_risk_clauses_count,
                        },
                        'source': 'cached_analysis'
                    }
                }
            
            # Basic offline risk analysis
            clauses = document.clauses.all()
            if clauses.exists():
                risk_scores = [clause.risk_score for clause in clauses]
                avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
                
                # Determine risk level
                if avg_risk > 0.7:
                    risk_level = 'high'
                elif avg_risk > 0.4:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                return {
                    'success': True,
                    'data': {
                        'overall_risk_score': avg_risk,
                        'overall_risk_level': risk_level,
                        'clause_counts': {
                            'high': len([c for c in clauses if c.risk_level == 'high']),
                            'medium': len([c for c in clauses if c.risk_level == 'medium']),
                            'low': len([c for c in clauses if c.risk_level == 'low']),
                        },
                        'source': 'offline_calculated'
                    }
                }
            
            return {
                'success': False,
                'error': 'No clauses available for risk analysis'
            }
            
        except Document.DoesNotExist:
            return {
                'success': False,
                'error': 'Document not found'
            }
    
    def _offline_glossary_lookup(self, term):
        """Look up glossary terms offline"""
        try:
            # Try to get from cache first
            cache_key = f"glossary_{term.lower()}"
            cached_term = self.cache_manager.get_cache(cache_key)
            
            if cached_term:
                return {
                    'success': True,
                    'data': cached_term,
                    'source': 'cached_glossary'
                }
            
            # Try to get from database
            from .models import LegalTerm
            try:
                legal_term = LegalTerm.objects.get(term__iexact=term)
                return {
                    'success': True,
                    'data': {
                        'term': legal_term.term,
                        'definition': legal_term.definition,
                        'plain_language_explanation': legal_term.plain_language_explanation,
                        'examples': legal_term.examples,
                        'category': legal_term.category
                    },
                    'source': 'database'
                }
            except LegalTerm.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Term "{term}" not found in glossary'
                }
                
        except Exception as e:
            logger.error(f"Error in offline glossary lookup: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class LocalCacheManager:
    """Manages local caching for offline mode"""
    
    def __init__(self):
        self.cache_expiry = {
            'document_summary': timedelta(hours=24),
            'clause_analysis': timedelta(hours=12),
            'risk_assessment': timedelta(hours=12),
            'glossary_term': timedelta(days=7),
            'ai_model': timedelta(days=30),
            'user_preferences': timedelta(days=1),
        }
    
    def set_cache(self, key, data, cache_type, expires_in=None):
        """Set cache entry"""
        try:
            if expires_in is None:
                expires_in = self.cache_expiry.get(cache_type, timedelta(hours=1))
            
            expires_at = timezone.now() + expires_in
            
            cache_entry, created = LocalCache.objects.get_or_create(
                cache_key=key,
                defaults={
                    'cache_data': data,
                    'cache_type': cache_type,
                    'expires_at': expires_at
                }
            )
            
            if not created:
                cache_entry.cache_data = data
                cache_entry.expires_at = expires_at
                cache_entry.save()
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def get_cache(self, key):
        """Get cache entry"""
        try:
            cache_entry = LocalCache.objects.get(cache_key=key)
            
            # Check if expired
            if cache_entry.is_expired():
                cache_entry.delete()
                return None
            
            # Update access count and timestamp
            cache_entry.access_count += 1
            cache_entry.last_accessed = timezone.now()
            cache_entry.save()
            
            return cache_entry.cache_data
        except LocalCache.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        try:
            expired_entries = LocalCache.objects.filter(
                expires_at__lt=timezone.now()
            )
            count = expired_entries.count()
            expired_entries.delete()
            logger.info(f"Cleared {count} expired cache entries")
            return count
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0
    
    def preload_essential_data(self):
        """Preload essential data to cache for offline use"""
        try:
            # Preload recent documents
            recent_docs = Document.objects.filter(
                is_processed=True
            ).order_by('-uploaded_at')[:10]
            
            for doc in recent_docs:
                cache_key = f"document_{doc.id}"
                cache_data = {
                    'id': str(doc.id),
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'processed_text': doc.processed_text[:1000],  # First 1000 chars
                    'uploaded_at': doc.uploaded_at.isoformat()
                }
                
                self.set_cache(cache_key, cache_data, 'document_summary')
            
            # Preload glossary terms
            from .models import LegalTerm
            legal_terms = LegalTerm.objects.all()[:50]  # First 50 terms
            
            for term in legal_terms:
                cache_key = f"glossary_{term.term.lower()}"
                cache_data = {
                    'term': term.term,
                    'definition': term.definition,
                    'plain_language_explanation': term.plain_language_explanation
                }
                
                self.set_cache(cache_key, cache_data, 'glossary_term')
            
            logger.info("Essential data preloaded to cache")
            return True
        except Exception as e:
            logger.error(f"Error preloading essential data: {e}")
            return False
    
    def has_local_model(self, feature_name):
        """Check if local model is available for a feature"""
        # This would check for actual local model files
        # For now, return True if we have cached data
        cache_key = f"local_model_{feature_name}"
        return self.get_cache(cache_key) is not None

class OfflineFeatureManager:
    """Manages offline feature availability and configuration"""
    
    def __init__(self):
        self.default_features = [
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
    
    def initialize_features(self):
        """Initialize offline features in database"""
        try:
            for feature_config in self.default_features:
                OfflineFeature.objects.get_or_create(
                    feature_name=feature_config['feature_name'],
                    defaults=feature_config
                )
            
            logger.info("Offline features initialized")
            return True
        except Exception as e:
            logger.error(f"Error initializing offline features: {e}")
            return False
    
    def get_available_offline_features(self):
        """Get list of features available offline"""
        try:
            features = OfflineFeature.objects.filter(
                is_available_offline=True
            ).order_by('priority')
            
            return list(features.values())
        except Exception as e:
            logger.error(f"Error getting offline features: {e}")
            return []
    
    def update_feature_availability(self, feature_name, is_available):
        """Update feature availability"""
        try:
            feature = OfflineFeature.objects.get(feature_name=feature_name)
            feature.is_available_offline = is_available
            feature.save()
            return True
        except OfflineFeature.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error updating feature availability: {e}")
            return False
