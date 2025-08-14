"""
Multilingual Service for AI Legal Explainer
Handles language detection, translation, and multilingual text processing
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

class MultilingualService:
    """Service for handling multilingual support including Tamil and Sinhala"""
    
    def __init__(self):
        self.supported_languages = ['en', 'ta', 'si']
        self.default_language = 'en'
        self.translation_service = None
        self.language_detector = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize language detection and translation services"""
        try:
            # Initialize language detection
            from langdetect import detect, DetectorFactory
            DetectorFactory.seed = 0  # For consistent results
            self.language_detector = detect
            
            # Initialize translation service
            from googletrans import Translator
            self.translation_service = Translator()
            
            logger.info("Multilingual services initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Translation services not available: {e}")
            self.translation_service = None
            self.language_detector = None
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        if not self.language_detector or not text.strip():
            return self.default_language
        
        try:
            detected_lang = self.language_detector(text[:1000])  # Use first 1000 chars for detection
            
            # Map detected language codes to our supported languages
            lang_mapping = {
                'en': 'en',
                'ta': 'ta',
                'si': 'si',
                'sin': 'si',  # Alternative Sinhala code
                'tam': 'ta',  # Alternative Tamil code
            }
            
            detected_lang = lang_mapping.get(detected_lang, self.default_language)
            logger.info(f"Detected language: {detected_lang}")
            return detected_lang
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return self.default_language
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> str:
        """Translate text to target language"""
        if not self.translation_service or not text.strip():
            return text
        
        if target_language == source_language or target_language not in self.supported_languages:
            return text
        
        try:
            # Handle Tamil and Sinhala language codes for Google Translate
            lang_codes = {
                'ta': 'ta',  # Tamil
                'si': 'si',  # Sinhala
                'en': 'en',  # English
            }
            
            target_code = lang_codes.get(target_language, 'en')
            source_code = 'auto' if source_language == 'auto' else lang_codes.get(source_language, 'en')
            
            translation = self.translation_service.translate(
                text, 
                dest=target_code, 
                src=source_code
            )
            
            translated_text = translation.text
            logger.info(f"Translated text from {source_code} to {target_code}")
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            'en': 'English',
            'ta': 'Tamil',
            'si': 'Sinhala',
        }
        return language_names.get(language_code, 'Unknown')
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages with codes and names"""
        return [
            {'code': 'en', 'name': 'English', 'native_name': 'English'},
            {'code': 'ta', 'name': 'Tamil', 'native_name': 'தமிழ்'},
            {'code': 'si', 'name': 'Sinhala', 'native_name': 'සිංහල'},
        ]
    
    def process_multilingual_text(self, text: str, target_language: str = 'en') -> Dict[str, str]:
        """Process text in multiple languages and return translations"""
        if not text.strip():
            return {}
        
        # Detect source language
        source_language = self.detect_language(text)
        
        # If source language is already target language, no translation needed
        if source_language == target_language:
            return {
                'original': text,
                'translated': text,
                'source_language': source_language,
                'target_language': target_language,
                'translation_needed': False
            }
        
        # Translate to target language
        translated_text = self.translate_text(text, target_language, source_language)
        
        return {
            'original': text,
            'translated': translated_text,
            'source_language': source_language,
            'target_language': target_language,
            'translation_needed': True
        }
    
    def create_multilingual_summary(self, summary: str, languages: List[str] = None) -> Dict[str, str]:
        """Create multilingual versions of a summary"""
        if not languages:
            languages = self.supported_languages
        
        multilingual_summary = {}
        
        for lang in languages:
            if lang == 'en':
                multilingual_summary[lang] = summary
            else:
                translated = self.translate_text(summary, lang, 'en')
                multilingual_summary[lang] = translated
        
        return multilingual_summary
    
    def validate_language_code(self, language_code: str) -> bool:
        """Validate if a language code is supported"""
        return language_code in self.supported_languages
    
    def get_language_script_info(self, language_code: str) -> Dict[str, str]:
        """Get information about language scripts and writing systems"""
        script_info = {
            'en': {
                'script': 'Latin',
                'direction': 'ltr',
                'font_family': 'Arial, sans-serif'
            },
            'ta': {
                'script': 'Tamil',
                'direction': 'ltr',
                'font_family': 'Latha, Arial Unicode MS, sans-serif'
            },
            'si': {
                'script': 'Sinhala',
                'direction': 'ltr',
                'font_family': 'Iskoola Pota, Arial Unicode MS, sans-serif'
            }
        }
        return script_info.get(language_code, script_info['en'])


class LegalTermTranslator:
    """Specialized translator for legal terminology"""
    
    def __init__(self):
        self.multilingual_service = MultilingualService()
        self.legal_terms = self._load_legal_terms()
    
    def _load_legal_terms(self) -> Dict[str, Dict[str, str]]:
        """Load legal terms with translations"""
        return {
            'contract': {
                'en': 'Contract',
                'ta': 'ஒப்பந்தம்',
                'si': 'කොන්ත්‍රාත්තුව'
            },
            'agreement': {
                'en': 'Agreement',
                'ta': 'ஒப்பந்தம்',
                'si': 'එකඟතාවය'
            },
            'liability': {
                'en': 'Liability',
                'ta': 'பொறுப்பு',
                'si': 'වගකීම'
            },
            'indemnification': {
                'en': 'Indemnification',
                'ta': 'பாதுகாப்பு',
                'si': 'රක්ෂාව'
            },
            'termination': {
                'en': 'Termination',
                'ta': 'முடிவு',
                'si': 'අවසන් කිරීම'
            },
            'penalty': {
                'en': 'Penalty',
                'ta': 'பரிகாரம்',
                'si': 'දඩය'
            },
            'breach': {
                'en': 'Breach',
                'ta': 'மீறல்',
                'si': 'ලංකිරීම'
            },
            'damages': {
                'en': 'Damages',
                'ta': 'சேதம்',
                'si': 'හානි'
            }
        }
    
    def translate_legal_term(self, term: str, target_language: str) -> str:
        """Translate a legal term to target language"""
        if target_language not in self.multilingual_service.supported_languages:
            return term
        
        # Check if we have a direct translation
        if term.lower() in self.legal_terms:
            return self.legal_terms[term.lower()].get(target_language, term)
        
        # Fallback to general translation
        return self.multilingual_service.translate_text(term, target_language, 'en')
    
    def get_legal_glossary(self, language: str) -> Dict[str, str]:
        """Get legal glossary in specified language"""
        if language not in self.multilingual_service.supported_languages:
            language = 'en'
        
        glossary = {}
        for term, translations in self.legal_terms.items():
            glossary[term] = translations.get(language, translations['en'])
        
        return glossary
