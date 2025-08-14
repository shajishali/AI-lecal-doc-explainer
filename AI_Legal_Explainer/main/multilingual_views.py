"""
Multilingual Views for AI Legal Explainer
Handles language switching, translation, and multilingual content delivery
"""

from django.shortcuts import render
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

from .models import Document, DocumentSummary, LegalTerm, UserLanguagePreference
from .serializers import DocumentSerializer, DocumentSummarySerializer, LegalTermSerializer
from .multilingual_service import MultilingualService, LegalTermTranslator
from .ai_services import AISummarizer, GlossaryService

logger = logging.getLogger(__name__)

class MultilingualViewSet(viewsets.ViewSet):
    """ViewSet for multilingual functionality"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multilingual_service = MultilingualService()
        self.legal_translator = LegalTermTranslator()
    
    @action(detail=False, methods=['get'])
    def supported_languages(self, request):
        """Get list of supported languages"""
        try:
            languages = self.multilingual_service.get_supported_languages()
            return Response({
                'success': True,
                'languages': languages
            })
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def detect_language(self, request):
        """Detect language of input text"""
        try:
            text = request.data.get('text', '')
            if not text:
                return Response({
                    'success': False,
                    'error': 'Text is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            detected_language = self.multilingual_service.detect_language(text)
            language_name = self.multilingual_service.get_language_name(detected_language)
            
            return Response({
                'success': True,
                'detected_language': detected_language,
                'language_name': language_name,
                'confidence': 'high' if detected_language != 'en' else 'medium'
            })
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def translate_text(self, request):
        """Translate text to target language"""
        try:
            text = request.data.get('text', '')
            target_language = request.data.get('target_language', 'en')
            source_language = request.data.get('source_language', 'auto')
            
            if not text:
                return Response({
                    'success': False,
                    'error': 'Text is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not self.multilingual_service.validate_language_code(target_language):
                return Response({
                    'success': False,
                    'error': f'Unsupported target language: {target_language}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            translated_text = self.multilingual_service.translate_text(
                text, target_language, source_language
            )
            
            return Response({
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language
            })
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def document_summary(self, request, pk=None):
        """Get document summary in specified language"""
        try:
            document = Document.objects.get(pk=pk)
            language = request.query_params.get('language', 'en')
            
            if not self.multilingual_service.validate_language_code(language):
                language = 'en'
            
            # Get or create summary
            summary, created = DocumentSummary.objects.get_or_create(
                document=document,
                defaults={'language': 'en'}
            )
            
            if language == 'en':
                # Return existing English summary
                return Response({
                    'success': True,
                    'summary': DocumentSummarySerializer(summary).data,
                    'language': 'en'
                })
            
            # Generate summary in target language
            summarizer = AISummarizer()
            multilingual_summary = summarizer.generate_summary_in_language(
                document.processed_text or document.original_text,
                language
            )
            
            # Update multilingual summaries in the summary object
            if not summary.multilingual_summaries:
                summary.multilingual_summaries = {}
            summary.multilingual_summaries[language] = multilingual_summary
            summary.save()
            
            return Response({
                'success': True,
                'summary': multilingual_summary,
                'language': language,
                'translated': True
            })
            
        except Document.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting multilingual summary: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def legal_glossary(self, request):
        """Get legal glossary in specified language"""
        try:
            language = request.query_params.get('language', 'en')
            query = request.query_params.get('query', '')
            
            if not self.multilingual_service.validate_language_code(language):
                language = 'en'
            
            glossary_service = GlossaryService()
            
            if query:
                # Search for terms
                if language == 'en':
                    terms = glossary_service.search_terms(query)
                else:
                    terms = glossary_service.search_terms_multilingual(query, language)
            else:
                # Get all terms
                if language == 'en':
                    terms = glossary_service.terms
                else:
                    terms = glossary_service.get_multilingual_glossary(language)
            
            return Response({
                'success': True,
                'terms': terms,
                'language': language,
                'total_terms': len(terms)
            })
            
        except Exception as e:
            logger.error(f"Error getting legal glossary: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def set_language_preference(self, request):
        """Set user language preference"""
        try:
            language = request.data.get('language', 'en')
            
            if not self.multilingual_service.validate_language_code(language):
                return Response({
                    'success': False,
                    'error': f'Unsupported language: {language}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # For now, store in session (in production, this would be user-specific)
            request.session['preferred_language'] = language
            
            return Response({
                'success': True,
                'message': f'Language preference set to {language}',
                'language': language
            })
            
        except Exception as e:
            logger.error(f"Error setting language preference: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def get_language_preference(self, request):
        """Get current language preference"""
        try:
            language = request.session.get('preferred_language', 'en')
            
            return Response({
                'success': True,
                'language': language,
                'language_name': self.multilingual_service.get_language_name(language)
            })
            
        except Exception as e:
            logger.error(f"Error getting language preference: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Traditional Django views for multilingual functionality
def language_switcher(request):
    """Language switcher page"""
    multilingual_service = MultilingualService()
    languages = multilingual_service.get_supported_languages()
    
    context = {
        'languages': languages,
        'current_language': request.session.get('preferred_language', 'en')
    }
    
    return render(request, 'main/language_switcher.html', context)


def multilingual_glossary(request, language='en'):
    """Multilingual glossary page"""
    try:
        multilingual_service = MultilingualService()
        legal_translator = LegalTermTranslator()
        
        if not multilingual_service.validate_language_code(language):
            language = 'en'
        
        glossary_service = GlossaryService()
        terms = glossary_service.get_multilingual_glossary(language)
        
        context = {
            'terms': terms,
            'language': language,
            'language_name': multilingual_service.get_language_name(language),
            'supported_languages': multilingual_service.get_supported_languages()
        }
        
        return render(request, 'main/multilingual_glossary.html', context)
        
    except Exception as e:
        logger.error(f"Error in multilingual glossary view: {e}")
        return render(request, 'main/error.html', {'error': str(e)})
