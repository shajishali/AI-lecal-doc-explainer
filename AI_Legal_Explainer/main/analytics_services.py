"""
Advanced Analytics Services for AI Legal Explainer
Implements Phase 3.4: Advanced Analytics functionality
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.contrib.auth.models import User

from .models import (
    Document, Clause, RiskAnalysis, DocumentSummary,
    PerformanceMetrics, UserLanguagePreference
)

logger = logging.getLogger(__name__)

class UserBehaviorTracker:
    """Tracks user behavior patterns and preferences"""
    
    def __init__(self):
        self.tracking_enabled = True
    
    def track_user_action(self, user: User, action: str, context: Dict = None):
        """Track a user action for analytics"""
        if not self.tracking_enabled:
            return
        
        try:
            # Store in performance metrics
            PerformanceMetrics.objects.create(
                user=user,
                feature_name=action,
                operation_type='user_action',
                start_time=timezone.now(),
                end_time=timezone.now(),
                duration_ms=0,
                success=True,
                resource_usage={'action_context': context or {}}
            )
        except Exception as e:
            logger.error(f"Error tracking user action: {e}")
    
    def get_user_behavior_summary(self, user: User, days: int = 30) -> Dict[str, Any]:
        """Get summary of user behavior patterns"""
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Get user's performance metrics
            metrics = PerformanceMetrics.objects.filter(
                user=user,
                start_time__gte=since
            )
            
            # Analyze behavior patterns
            feature_usage = metrics.values('feature_name').annotate(
                count=Count('id'),
                avg_duration=Avg('duration_ms')
            ).order_by('-count')
            
            # Get language preferences
            try:
                lang_pref = UserLanguagePreference.objects.get(user=user)
                preferred_language = lang_pref.preferred_language
            except UserLanguagePreference.DoesNotExist:
                preferred_language = 'en'
            
            return {
                'total_actions': metrics.count(),
                'feature_usage': list(feature_usage),
                'preferred_language': preferred_language,
                'active_days': metrics.dates('start_time', 'day').count(),
                'most_used_feature': feature_usage.first()['feature_name'] if feature_usage else None
            }
        except Exception as e:
            logger.error(f"Error getting user behavior summary: {e}")
            return {}

class DocumentAnalytics:
    """Analyzes document processing patterns and metrics"""
    
    def __init__(self):
        pass
    
    def get_document_processing_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get document processing statistics"""
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Document upload stats
            total_documents = Document.objects.filter(uploaded_at__gte=since).count()
            processed_documents = Document.objects.filter(
                uploaded_at__gte=since,
                is_processed=True
            ).count()
            
            # Document type distribution
            type_distribution = Document.objects.filter(
                uploaded_at__gte=since
            ).values('document_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Processing time analysis
            processing_times = DocumentProcessingLog.objects.filter(
                step='summarization',
                started_at__gte=since,
                processing_time__isnull=False
            ).aggregate(
                avg_time=Avg('processing_time'),
                min_time=models.Min('processing_time'),
                max_time=models.Max('processing_time')
            )
            
            return {
                'total_documents': total_documents,
                'processed_documents': processed_documents,
                'processing_rate': round((processed_documents / total_documents * 100), 2) if total_documents > 0 else 0,
                'type_distribution': list(type_distribution),
                'processing_times': processing_times
            }
        except Exception as e:
            logger.error(f"Error getting document processing stats: {e}")
            return {}
    
    def get_language_distribution(self, days: int = 30) -> Dict[str, Any]:
        """Get document language distribution"""
        try:
            since = timezone.now() - timedelta(days=days)
            
            language_stats = DocumentSummary.objects.filter(
                generated_at__gte=since
            ).values('language').annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'language_distribution': list(language_stats),
                'total_summaries': sum(item['count'] for item in language_stats)
            }
        except Exception as e:
            logger.error(f"Error getting language distribution: {e}")
            return {}

class RiskPatternAnalyzer:
    """Analyzes risk patterns and provides insights"""
    
    def __init__(self):
        pass
    
    def analyze_risk_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze risk patterns across documents"""
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Get all clauses from recent documents
            recent_docs = Document.objects.filter(uploaded_at__gte=since)
            clauses = Clause.objects.filter(document__in=recent_docs)
            
            # Risk level distribution
            risk_distribution = clauses.values('risk_level').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Clause type risk analysis
            clause_type_risk = clauses.values('clause_type', 'risk_level').annotate(
                count=Count('id')
            ).order_by('clause_type', '-count')
            
            # High-risk clause patterns
            high_risk_clauses = clauses.filter(risk_level='high')
            high_risk_patterns = high_risk_clauses.values('clause_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'total_clauses': clauses.count(),
                'risk_distribution': list(risk_distribution),
                'clause_type_risk': list(clause_type_risk),
                'high_risk_patterns': list(high_risk_patterns),
                'high_risk_percentage': round((high_risk_clauses.count() / clauses.count() * 100), 2) if clauses.count() > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error analyzing risk patterns: {e}")
            return {}
    
    def identify_common_risk_factors(self, days: int = 30) -> List[Dict[str, Any]]:
        """Identify common risk factors in documents"""
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Analyze high-risk clauses for common patterns
            high_risk_clauses = Clause.objects.filter(
                risk_level='high',
                document__uploaded_at__gte=since
            )
            
            risk_factors = []
            
            # Check for penalty clauses
            penalty_clauses = high_risk_clauses.filter(clause_type='penalty')
            if penalty_clauses.exists():
                risk_factors.append({
                    'factor': 'High penalty amounts',
                    'frequency': penalty_clauses.count(),
                    'risk_level': 'high',
                    'description': 'Documents contain clauses with significant financial penalties'
                })
            
            # Check for auto-renewal clauses
            auto_renewal_clauses = high_risk_clauses.filter(clause_type='auto_renewal')
            if auto_renewal_clauses.exists():
                risk_factors.append({
                    'factor': 'Auto-renewal terms',
                    'frequency': auto_renewal_clauses.count(),
                    'risk_level': 'high',
                    'description': 'Documents contain automatic renewal clauses that may trap users'
                })
            
            # Check for indemnification clauses
            indemnification_clauses = high_risk_clauses.filter(clause_type='indemnification')
            if indemnification_clauses.exists():
                risk_factors.append({
                    'factor': 'Broad indemnification',
                    'frequency': indemnification_clauses.count(),
                    'risk_level': 'high',
                    'description': 'Documents contain broad indemnification clauses'
                })
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error identifying risk factors: {e}")
            return []

class PredictiveRiskModel:
    """Provides predictive risk modeling capabilities"""
    
    def __init__(self):
        self.risk_weights = {
            'penalty': 0.3,
            'auto_renewal': 0.25,
            'indemnification': 0.2,
            'termination': 0.15,
            'liability': 0.1
        }
    
    def predict_document_risk(self, document: Document) -> Dict[str, Any]:
        """Predict overall risk for a document"""
        try:
            # Get document clauses
            clauses = document.clauses.all()
            
            if not clauses.exists():
                return {
                    'predicted_risk': 'low',
                    'confidence': 0.0,
                    'factors': []
                }
            
            # Calculate weighted risk score
            total_score = 0
            total_weight = 0
            risk_factors = []
            
            for clause in clauses:
                weight = self.risk_weights.get(clause.clause_type, 0.05)
                risk_score = clause.risk_score
                
                total_score += risk_score * weight
                total_weight += weight
                
                if risk_score > 0.7:
                    risk_factors.append({
                        'clause_type': clause.clause_type,
                        'risk_score': risk_score,
                        'weight': weight
                    })
            
            # Normalize score
            if total_weight > 0:
                normalized_score = total_score / total_weight
            else:
                normalized_score = 0
            
            # Determine risk level
            if normalized_score > 0.7:
                risk_level = 'high'
            elif normalized_score > 0.4:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            # Calculate confidence based on number of clauses
            confidence = min(0.9, 0.5 + (len(clauses) * 0.1))
            
            return {
                'predicted_risk': risk_level,
                'risk_score': round(normalized_score, 3),
                'confidence': round(confidence, 3),
                'factors': risk_factors,
                'clause_count': clauses.count()
            }
            
        except Exception as e:
            logger.error(f"Error predicting document risk: {e}")
            return {
                'predicted_risk': 'unknown',
                'confidence': 0.0,
                'factors': []
            }
    
    def get_risk_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get risk trends over time"""
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Get documents with risk analysis
            documents = Document.objects.filter(
                uploaded_at__gte=since,
                risk_analysis__isnull=False
            ).select_related('risk_analysis')
            
            # Calculate daily risk averages
            daily_risks = {}
            for doc in documents:
                date = doc.uploaded_at.date()
                if date not in daily_risks:
                    daily_risks[date] = []
                daily_risks[date].append(doc.risk_analysis.overall_risk_score)
            
            # Calculate daily averages
            daily_averages = {}
            for date, scores in daily_risks.items():
                daily_averages[date.isoformat()] = round(sum(scores) / len(scores), 3)
            
            # Calculate trend
            dates = sorted(daily_averages.keys())
            if len(dates) >= 2:
                first_avg = daily_averages[dates[0]]
                last_avg = daily_averages[dates[-1]]
                trend = 'increasing' if last_avg > first_avg else 'decreasing' if last_avg < first_avg else 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'daily_averages': daily_averages,
                'trend': trend,
                'total_documents': documents.count(),
                'average_risk_score': round(sum(doc.risk_analysis.overall_risk_score for doc in documents) / documents.count(), 3) if documents.count() > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting risk trends: {e}")
            return {}

class AnalyticsDashboard:
    """Main analytics dashboard service"""
    
    def __init__(self):
        self.user_tracker = UserBehaviorTracker()
        self.doc_analytics = DocumentAnalytics()
        self.risk_analyzer = RiskPatternAnalyzer()
        self.risk_predictor = PredictiveRiskModel()
    
    def get_comprehensive_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data"""
        try:
            return {
                'user_behavior': self.user_tracker.get_user_behavior_summary(None, days),
                'document_analytics': self.doc_analytics.get_document_processing_stats(days),
                'language_distribution': self.doc_analytics.get_language_distribution(days),
                'risk_patterns': self.risk_analyzer.analyze_risk_patterns(days),
                'risk_factors': self.risk_analyzer.identify_common_risk_factors(days),
                'risk_trends': self.risk_predictor.get_risk_trends(days),
                'generated_at': timezone.now().isoformat(),
                'time_period_days': days
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive analytics: {e}")
            return {}
    
    def generate_analytics_report(self, days: int = 30) -> str:
        """Generate human-readable analytics report"""
        try:
            analytics = self.get_comprehensive_analytics(days)
            
            report = f"""
Analytics Report - Last {days} Days
==================================

Document Processing:
- Total Documents: {analytics.get('document_analytics', {}).get('total_documents', 0)}
- Processing Rate: {analytics.get('document_analytics', {}).get('processing_rate', 0)}%
- Average Processing Time: {analytics.get('document_analytics', {}).get('processing_times', {}).get('avg_time', 0):.2f}s

Language Distribution:
{chr(10).join(f"- {item['language']}: {item['count']}" for item in analytics.get('language_distribution', {}).get('language_distribution', []))}

Risk Analysis:
- Total Clauses: {analytics.get('risk_patterns', {}).get('total_clauses', 0)}
- High Risk Percentage: {analytics.get('risk_patterns', {}).get('high_risk_percentage', 0)}%

Common Risk Factors:
{chr(10).join(f"- {factor['factor']}: {factor['description']}" for factor in analytics.get('risk_factors', []))}

Risk Trends:
- Overall Trend: {analytics.get('risk_trends', {}).get('trend', 'Unknown').title()}
- Average Risk Score: {analytics.get('risk_trends', {}).get('average_risk_score', 0)}

Generated: {analytics.get('generated_at', 'Unknown')}
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return f"Error generating analytics report: {e}"
