"""
Phase 4 Documentation Services

This module provides comprehensive documentation management, training materials,
user guides, and support system services for the AI Legal Explainer application.
"""

import logging
import markdown
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import (
    Documentation, TrainingMaterial, UserGuide, SupportTicket
)

logger = logging.getLogger(__name__)


class DocumentationManager:
    """
    Comprehensive documentation management service.
    
    Handles documentation creation, management, publishing, and versioning.
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self.markdown_extensions = [
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.toc'
        ]
    
    def create_documentation(self, title: str, content: str, doc_type: str,
                           language: str = 'en', version: str = '1.0',
                           created_by: Optional[User] = None) -> Documentation:
        """
        Create new documentation.
        
        Args:
            title: Documentation title
            content: Documentation content (markdown)
            doc_type: Type of documentation
            language: Language code
            version: Version string
            created_by: User creating the documentation
            
        Returns:
            Created Documentation instance
        """
        try:
            with transaction.atomic():
                doc = Documentation.objects.create(
                    title=title,
                    content=content,
                    doc_type=doc_type,
                    language=language,
                    version=version,
                    created_by=created_by,
                    is_published=False
                )
                
                # Clear cache
                self._clear_documentation_cache(doc_type, language)
                
                logger.info(f"Created documentation: {title} ({doc_type})")
                return doc
                
        except Exception as e:
            logger.error(f"Error creating documentation: {e}")
            raise
    
    def update_documentation(self, doc_id: str, **kwargs) -> Documentation:
        """
        Update existing documentation.
        
        Args:
            doc_id: Documentation ID
            **kwargs: Fields to update
            
        Returns:
            Updated Documentation instance
        """
        try:
            with transaction.atomic():
                doc = Documentation.objects.get(id=doc_id)
                
                for field, value in kwargs.items():
                    if hasattr(doc, field):
                        setattr(doc, field, value)
                
                doc.save()
                
                # Clear cache
                self._clear_documentation_cache(doc.doc_type, doc.language)
                
                logger.info(f"Updated documentation: {doc.title}")
                return doc
                
        except Documentation.DoesNotExist:
            raise ValidationError(f"Documentation with ID {doc_id} not found")
        except Exception as e:
            logger.error(f"Error updating documentation: {e}")
            raise
    
    def publish_documentation(self, doc_id: str) -> Documentation:
        """
        Publish documentation.
        
        Args:
            doc_id: Documentation ID
            
        Returns:
            Published Documentation instance
        """
        try:
            doc = self.update_documentation(doc_id, is_published=True)
            logger.info(f"Published documentation: {doc.title}")
            return doc
        except Exception as e:
            logger.error(f"Error publishing documentation: {e}")
            raise
    
    def get_documentation(self, doc_type: Optional[str] = None,
                         language: str = 'en', published_only: bool = True) -> List[Documentation]:
        """
        Get documentation based on criteria.
        
        Args:
            doc_type: Type of documentation to filter by
            language: Language code
            published_only: Whether to return only published docs
            
        Returns:
            List of Documentation instances
        """
        try:
            cache_key = f"docs_{doc_type}_{language}_{published_only}"
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            queryset = Documentation.objects.filter(language=language)
            
            if doc_type:
                queryset = queryset.filter(doc_type=doc_type)
            
            if published_only:
                queryset = queryset.filter(is_published=True)
            
            docs = list(queryset.order_by('doc_type', 'title'))
            
            # Cache result
            cache.set(cache_key, docs, self.cache_timeout)
            
            return docs
            
        except Exception as e:
            logger.error(f"Error getting documentation: {e}")
            return []
    
    def generate_api_documentation(self) -> str:
        """
        Generate API documentation in markdown format.
        
        Returns:
            API documentation as markdown string
        """
        try:
            api_docs = """
# AI Legal Explainer API Documentation

## Overview
The AI Legal Explainer API provides programmatic access to legal document analysis services.

## Authentication
All API requests require authentication using API keys.

## Endpoints

### Document Analysis
- `POST /api/analyze/` - Upload and analyze legal documents
- `GET /api/documents/` - List user documents
- `GET /api/documents/{id}/` - Get document details

### Q&A System
- `POST /api/qa/` - Ask questions about documents
- `GET /api/chat-sessions/` - List chat sessions

### User Management
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile

### Analytics
- `GET /api/analytics/dashboard/` - Get analytics dashboard
- `GET /api/analytics/performance/` - Get performance metrics

## Response Format
All responses are in JSON format with standard HTTP status codes.

## Rate Limiting
- 100 requests per hour for standard users
- 1000 requests per hour for premium users

## Error Handling
Standard HTTP error codes with detailed error messages.
            """
            
            return api_docs.strip()
            
        except Exception as e:
            logger.error(f"Error generating API documentation: {e}")
            return "Error generating API documentation"
    
    def _clear_documentation_cache(self, doc_type: str, language: str):
        """Clear documentation cache for specific type and language."""
        cache_keys = [
            f"docs_{doc_type}_{language}_True",
            f"docs_{doc_type}_{language}_False",
            f"docs_None_{language}_True",
            f"docs_None_{language}_False"
        ]
        
        for key in cache_keys:
            cache.delete(key)


class TrainingManager:
    """
    Training materials management service.
    
    Handles creation, organization, and delivery of training materials.
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
    
    def create_training_material(self, title: str, content: str, material_type: str,
                                difficulty_level: str, estimated_duration: int,
                                language: str = 'en', created_by: Optional[User] = None) -> TrainingMaterial:
        """
        Create new training material.
        
        Args:
            title: Training material title
            content: Training content
            material_type: Type of training material
            difficulty_level: Difficulty level
            estimated_duration: Estimated duration in minutes
            language: Language code
            created_by: User creating the material
            
        Returns:
            Created TrainingMaterial instance
        """
        try:
            with transaction.atomic():
                material = TrainingMaterial.objects.create(
                    title=title,
                    content=content,
                    material_type=material_type,
                    difficulty_level=difficulty_level,
                    estimated_duration=estimated_duration,
                    language=language,
                    created_by=created_by,
                    is_active=True
                )
                
                # Clear cache
                self._clear_training_cache(language)
                
                logger.info(f"Created training material: {title}")
                return material
                
        except Exception as e:
            logger.error(f"Error creating training material: {e}")
            raise
    
    def get_training_path(self, user_level: str, language: str = 'en') -> List[TrainingMaterial]:
        """
        Get recommended training path for user level.
        
        Args:
            user_level: User's current level
            language: Language code
            
        Returns:
            List of TrainingMaterial instances in recommended order
        """
        try:
            cache_key = f"training_path_{user_level}_{language}"
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Define training progression
            progression = {
                'beginner': ['beginner', 'intermediate'],
                'intermediate': ['intermediate', 'advanced'],
                'advanced': ['advanced', 'expert'],
                'expert': ['expert']
            }
            
            levels = progression.get(user_level, ['beginner'])
            
            materials = TrainingMaterial.objects.filter(
                difficulty_level__in=levels,
                language=language,
                is_active=True
            ).order_by('difficulty_level', 'estimated_duration')
            
            result = list(materials)
            
            # Cache result
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting training path: {e}")
            return []
    
    def _clear_training_cache(self, language: str):
        """Clear training cache for specific language."""
        cache_keys = [
            f"training_path_beginner_{language}",
            f"training_path_intermediate_{language}",
            f"training_path_advanced_{language}",
            f"training_path_expert_{language}"
        ]
        
        for key in cache_keys:
            cache.delete(key)


class UserGuideManager:
    """
    User guide management service.
    
    Handles creation and management of user guides and tutorials.
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
    
    def create_user_guide(self, title: str, content: str, guide_type: str,
                          target_audience: str, language: str = 'en',
                          version: str = '1.0', created_by: Optional[User] = None) -> UserGuide:
        """
        Create new user guide.
        
        Args:
            title: Guide title
            content: Guide content
            guide_type: Type of guide
            target_audience: Target audience
            language: Language code
            version: Version string
            created_by: User creating the guide
            
        Returns:
            Created UserGuide instance
        """
        try:
            with transaction.atomic():
                guide = UserGuide.objects.create(
                    title=title,
                    content=content,
                    guide_type=guide_type,
                    target_audience=target_audience,
                    language=language,
                    version=version,
                    created_by=created_by,
                    is_published=False
                )
                
                # Clear cache
                self._clear_guide_cache(guide_type, target_audience, language)
                
                logger.info(f"Created user guide: {title}")
                return guide
                
        except Exception as e:
            logger.error(f"Error creating user guide: {e}")
            raise
    
    def get_guide_by_type(self, guide_type: str, target_audience: str,
                          language: str = 'en') -> Optional[UserGuide]:
        """
        Get user guide by type and target audience.
        
        Args:
            guide_type: Type of guide
            target_audience: Target audience
            language: Language code
            
        Returns:
            UserGuide instance or None
        """
        try:
            cache_key = f"guide_{guide_type}_{target_audience}_{language}"
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            guide = UserGuide.objects.filter(
                guide_type=guide_type,
                target_audience=target_audience,
                language=language,
                is_published=True
            ).order_by('-version').first()
            
            # Cache result
            cache.set(cache_key, guide, self.cache_timeout)
            
            return guide
            
        except Exception as e:
            logger.error(f"Error getting guide: {e}")
            return None
    
    def _clear_guide_cache(self, guide_type: str, target_audience: str, language: str):
        """Clear guide cache for specific criteria."""
        cache_key = f"guide_{guide_type}_{target_audience}_{language}"
        cache.delete(cache_key)


class SupportManager:
    """
    Support ticket management service.
    
    Handles creation, tracking, and resolution of support tickets.
    """
    
    def __init__(self):
        self.priority_weights = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'urgent': 4
        }
    
    def create_support_ticket(self, user: User, subject: str, description: str,
                             ticket_type: str, priority: str = 'medium') -> SupportTicket:
        """
        Create new support ticket.
        
        Args:
            user: User creating the ticket
            subject: Ticket subject
            description: Ticket description
            ticket_type: Type of ticket
            priority: Priority level
            
        Returns:
            Created SupportTicket instance
        """
        try:
            with transaction.atomic():
                ticket = SupportTicket.objects.create(
                    user=user,
                    subject=subject,
                    description=description,
                    ticket_type=ticket_type,
                    priority=priority,
                    status='open'
                )
                
                logger.info(f"Created support ticket: {subject} for user {user.username}")
                return ticket
                
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            raise
    
    def update_ticket_status(self, ticket_id: str, status: str,
                           assigned_to: Optional[User] = None,
                           resolution: Optional[str] = None) -> SupportTicket:
        """
        Update ticket status.
        
        Args:
            ticket_id: Ticket ID
            status: New status
            assigned_to: User assigned to ticket
            resolution: Resolution text
            
        Returns:
            Updated SupportTicket instance
        """
        try:
            with transaction.atomic():
                ticket = SupportTicket.objects.get(id=ticket_id)
                
                ticket.status = status
                if assigned_to:
                    ticket.assigned_to = assigned_to
                if resolution:
                    ticket.resolution = resolution
                
                if status == 'resolved':
                    ticket.resolved_at = timezone.now()
                
                ticket.save()
                
                logger.info(f"Updated ticket {ticket_id} status to {status}")
                return ticket
                
        except SupportTicket.DoesNotExist:
            raise ValidationError(f"Support ticket with ID {ticket_id} not found")
        except Exception as e:
            logger.error(f"Error updating ticket status: {e}")
            raise
    
    def get_user_tickets(self, user: User, status: Optional[str] = None) -> List[SupportTicket]:
        """
        Get tickets for a specific user.
        
        Args:
            user: User to get tickets for
            status: Filter by status
            
        Returns:
            List of SupportTicket instances
        """
        try:
            queryset = SupportTicket.objects.filter(user=user)
            
            if status:
                queryset = queryset.filter(status=status)
            
            return list(queryset.order_by('-created_at'))
            
        except Exception as e:
            logger.error(f"Error getting user tickets: {e}")
            return []
    
    def get_tickets_by_priority(self, priority: str = 'high') -> List[SupportTicket]:
        """
        Get tickets by priority level.
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            List of SupportTicket instances
        """
        try:
            tickets = SupportTicket.objects.filter(
                priority=priority,
                status__in=['open', 'in_progress']
            ).order_by('created_at')
            
            return list(tickets)
            
        except Exception as e:
            logger.error(f"Error getting tickets by priority: {e}")
            return []
    
    def get_ticket_statistics(self) -> Dict[str, Any]:
        """
        Get support ticket statistics.
        
        Returns:
            Dictionary with ticket statistics
        """
        try:
            total_tickets = SupportTicket.objects.count()
            open_tickets = SupportTicket.objects.filter(status='open').count()
            resolved_tickets = SupportTicket.objects.filter(status='resolved').count()
            
            # Calculate average resolution time
            resolved_tickets_with_time = SupportTicket.objects.filter(
                status='resolved',
                resolved_at__isnull=False
            )
            
            total_resolution_time = timedelta()
            count = 0
            
            for ticket in resolved_tickets_with_time:
                if ticket.created_at and ticket.resolved_at:
                    resolution_time = ticket.resolved_at - ticket.created_at
                    total_resolution_time += resolution_time
                    count += 1
            
            avg_resolution_time = total_resolution_time / count if count > 0 else timedelta()
            
            return {
                'total_tickets': total_tickets,
                'open_tickets': open_tickets,
                'resolved_tickets': resolved_tickets,
                'resolution_rate': (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                'avg_resolution_time_hours': avg_resolution_time.total_seconds() / 3600,
                'tickets_by_priority': self._get_tickets_by_priority_count(),
                'tickets_by_type': self._get_tickets_by_type_count()
            }
            
        except Exception as e:
            logger.error(f"Error getting ticket statistics: {e}")
            return {}
    
    def _get_tickets_by_priority_count(self) -> Dict[str, int]:
        """Get count of tickets by priority."""
        try:
            from django.db.models import Count
            return dict(
                SupportTicket.objects.values('priority').annotate(count=Count('id')).values_list('priority', 'count')
            )
        except Exception:
            return {}
    
    def _get_tickets_by_type_count(self) -> Dict[str, int]:
        """Get count of tickets by type."""
        try:
            from django.db.models import Count
            return dict(
                SupportTicket.objects.values('ticket_type').annotate(count=Count('id')).values_list('ticket_type', 'count')
            )
        except Exception:
            return {}


class DocumentationService:
    """
    Main documentation service that coordinates all documentation-related operations.
    """
    
    def __init__(self):
        self.doc_manager = DocumentationManager()
        self.training_manager = TrainingManager()
        self.guide_manager = UserGuideManager()
        self.support_manager = SupportManager()
    
    def get_comprehensive_help(self, user: User, language: str = 'en') -> Dict[str, Any]:
        """
        Get comprehensive help resources for a user.
        
        Args:
            user: User requesting help
            language: Language code
            
        Returns:
            Dictionary with help resources
        """
        try:
            # Get user's current onboarding stage
            from .models import UserOnboarding
            onboarding = UserOnboarding.objects.filter(
                user=user,
                onboarding_stage='onboarding_completed'
            ).first()
            
            user_level = 'beginner' if not onboarding else 'intermediate'
            
            return {
                'documentation': self.doc_manager.get_documentation(language=language),
                'training_materials': self.training_manager.get_training_path(user_level, language),
                'user_guides': self._get_relevant_guides(user, language),
                'support_tickets': self.support_manager.get_user_tickets(user),
                'faq': self._get_faq_content(language),
                'getting_started': self._get_getting_started_content(language)
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive help: {e}")
            return {}
    
    def _get_relevant_guides(self, user: User, language: str) -> List[UserGuide]:
        """Get relevant user guides for the user."""
        try:
            guides = []
            
            # Get guides for end users
            end_user_guides = self.guide_manager.get_guide_by_type('getting_started', 'end_user', language)
            if end_user_guides:
                guides.append(end_user_guides)
            
            # Get feature guides
            feature_guides = self.guide_manager.get_guide_by_type('feature_guide', 'end_user', language)
            if feature_guides:
                guides.append(feature_guides)
            
            return guides
            
        except Exception as e:
            logger.error(f"Error getting relevant guides: {e}")
            return []
    
    def _get_faq_content(self, language: str) -> str:
        """Get FAQ content for the specified language."""
        faq_content = {
            'en': """
# Frequently Asked Questions

## How do I upload a document?
Click the "Upload Document" button and select your file. Supported formats: PDF, DOCX, TXT.

## How accurate is the AI analysis?
Our AI models are trained on legal documents and provide high-accuracy analysis with risk identification.

## Can I use this for any legal document?
Yes, the system works with contracts, agreements, terms of service, and other legal documents.

## Is my data secure?
Yes, all data is encrypted and we comply with GDPR and PDPA regulations.

## How do I get help?
Use the support system or check our comprehensive documentation and training materials.
            """,
            'ta': """
# அடிக்கடி கேட்கப்படும் கேள்விகள்

## நான் எப்படி ஒரு ஆவணத்தை பதிவேற்றுவது?
"ஆவணத்தை பதிவேற்று" பொத்தானைக் கிளிக் செய்து உங்கள் கோப்பைத் தேர்ந்தெடுக்கவும். ஆதரிக்கப்படும் வடிவங்கள்: PDF, DOCX, TXT.

## AI பகுப்பாய்வு எவ்வளவு துல்லியமானது?
எங்கள் AI மாடல்கள் சட்ட ஆவணங்களில் பயிற்சி பெற்றவை மற்றும் அபாய அடையாளங்காட்டல் மூலம் உயர் துல்லிய பகுப்பாய்வை வழங்குகின்றன.
            """,
            'si': """
# නිතර අසන ප්‍රශ්න

## මම ලේඛනයක් උඩුගත කරන්නේ කෙසේද?
"ලේඛනය උඩුගත කරන්න" බොත්තම ක්ලික් කර ඔබේ ගොනුව තෝරන්න. සහාය වන ආකෘති: PDF, DOCX, TXT.

## AI විශ්ලේෂණය කෙතරම් නිවැරදිද?
අපගේ AI මොඩල් නීති ලේඛන මත පුහුණු වී ඇති අතර අවදානම් හඳුනාගැනීම සමඟ ඉහළ නිරවද්‍යතා විශ්ලේෂණය සපයයි.
            """
        }
        
        return faq_content.get(language, faq_content['en'])
    
    def _get_getting_started_content(self, language: str) -> str:
        """Get getting started content for the specified language."""
        getting_started_content = {
            'en': """
# Getting Started with AI Legal Explainer

## Welcome to AI Legal Explainer!
This powerful tool helps you understand complex legal documents in plain language.

## Quick Start Guide

### 1. Create Your Account
- Sign up with your email
- Verify your email address
- Complete your profile

### 2. Upload Your First Document
- Click "Upload Document"
- Choose your legal document (PDF, DOCX, or TXT)
- Wait for processing to complete

### 3. Review the Analysis
- Read the plain-language summary
- Check risk indicators
- Review identified clauses
- Use the Q&A feature for questions

### 4. Explore Advanced Features
- Try the what-if simulation
- Check the glossary for legal terms
- Use multilingual features

## Need Help?
- Check our FAQ section
- Review training materials
- Contact support if needed
            """,
            'ta': """
# AI சட்ட விளக்கத்துடன் தொடங்குதல்

## AI சட்ட விளக்கத்திற்கு வரவேற்கிறோம்!
இந்த சக்திவாய்ந்த கருவி சிக்கலான சட்ட ஆவணங்களை எளிய மொழியில் புரிந்துகொள்ள உதவுகிறது.

## விரைவு தொடக்க வழிகாட்டி

### 1. உங்கள் கணக்கை உருவாக்கவும்
- உங்கள் மின்னஞ்சலுடன் பதிவு செய்யவும்
- உங்கள் மின்னஞ்சல் முகவரியை சரிபார்க்கவும்
- உங்கள் சுயவிவரத்தை முடிக்கவும்
            """,
            'si': """
# AI නීති පැහැදිලි කිරීමෙන් ආරම්භ කිරීම

## AI නීති පැහැදිලි කිරීමට සාදරයෙන් පිළිගනිමු!
මෙම බලවත් මෙවලම සංකීර්ණ නීති ලේඛන සරල භාෂාවෙන් තේරුම් ගැනීමට ඔබට උදව් කරයි.

## ඉක්මන් ආරම්භ මාර්ගෝපදේශය

### 1. ඔබේ ගිණුම සාදන්න
- ඔබගේ විද්‍යුත් තැපෑල සමඟ ලියාපදිංචි වන්න
- ඔබගේ විද්‍යුත් තැපෑල සත්‍යාපිත කරන්න
- ඔබගේ පැතිකඩ සම්පූර්ණ කරන්න
            """
        }
        
        return getting_started_content.get(language, getting_started_content['en'])
