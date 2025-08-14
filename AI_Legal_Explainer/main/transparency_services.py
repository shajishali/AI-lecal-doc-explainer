"""
Transparency Controls Service for AI Legal Explainer
Implements Phase 3.2: Transparency Controls functionality
"""

import json
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.cache import cache

from .models import TransparencyPreference, UserLanguagePreference

logger = logging.getLogger(__name__)

class TransparencyController:
    """Manages transparency controls and explanation detail levels"""
    
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self.preferences = self._get_user_preferences()
        self.detail_levels = self._get_detail_levels()
    
    def _get_user_preferences(self) -> TransparencyPreference:
        """Get or create user transparency preferences"""
        if not self.user:
            logger.warning("No user provided to TransparencyController")
            return None
        
        try:
            preferences, created = TransparencyPreference.objects.get_or_create(
                user=self.user,
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
                logger.info(f"Created transparency preferences for user {self.user.username}")
            
            return preferences
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None
    
    def _get_detail_levels(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for different detail levels"""
        return {
            'very_simple': {
                'max_sentence_length': 15,
                'max_words_per_sentence': 10,
                'use_simple_vocabulary': True,
                'avoid_legal_terms': True,
                'include_examples': True,
                'use_analogies': True,
                'confidence_threshold': 0.8,
                'show_technical_details': False,
                'explanation_style': 'conversational'
            },
            'simple': {
                'max_sentence_length': 25,
                'max_words_per_sentence': 15,
                'use_simple_vocabulary': True,
                'avoid_legal_terms': False,
                'include_examples': True,
                'use_analogies': True,
                'confidence_threshold': 0.7,
                'show_technical_details': False,
                'explanation_style': 'conversational'
            },
            'medium': {
                'max_sentence_length': 35,
                'max_words_per_sentence': 20,
                'use_simple_vocabulary': False,
                'avoid_legal_terms': False,
                'include_examples': True,
                'use_analogies': False,
                'confidence_threshold': 0.6,
                'show_technical_details': False,
                'explanation_style': 'educational'
            },
            'detailed': {
                'max_sentence_length': 50,
                'max_words_per_sentence': 30,
                'use_simple_vocabulary': False,
                'avoid_legal_terms': False,
                'include_examples': True,
                'use_analogies': False,
                'confidence_threshold': 0.5,
                'show_technical_details': True,
                'explanation_style': 'educational'
            },
            'legal_detailed': {
                'max_sentence_length': 75,
                'max_words_per_sentence': 40,
                'use_simple_vocabulary': False,
                'avoid_legal_terms': False,
                'include_examples': True,
                'use_analogies': False,
                'confidence_threshold': 0.4,
                'show_technical_details': True,
                'explanation_style': 'formal'
            }
        }
    
    def get_current_detail_level(self) -> str:
        """Get current explanation detail level"""
        if self.preferences:
            return self.preferences.explanation_detail_level
        return 'medium'
    
    def get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences when user preferences are not available"""
        return {
            'explanation_detail_level': 'medium',
            'show_confidence_scores': True,
            'show_source_citations': True,
            'show_technical_details': False,
            'auto_adjust_complexity': True,
            'preferred_explanation_style': 'conversational'
        }
    
    def set_detail_level(self, level: str) -> bool:
        """Set explanation detail level"""
        if level not in self.detail_levels:
            return False
        
        if self.preferences:
            self.preferences.explanation_detail_level = level
            self.preferences.save()
            logger.info(f"User {self.user.username} set detail level to {level}")
            return True
        
        return False
    
    def get_level_config(self, level: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific detail level"""
        if level is None:
            level = self.get_current_detail_level()
        
        return self.detail_levels.get(level, self.detail_levels['medium'])
    
    def should_show_confidence_score(self, confidence: float) -> bool:
        """Determine if confidence score should be shown"""
        if not self.preferences or not self.preferences.show_confidence_scores:
            return False
        
        threshold = self.get_level_config()['confidence_threshold']
        return confidence >= threshold
    
    def should_show_source_citations(self) -> bool:
        """Determine if source citations should be shown"""
        return self.preferences and self.preferences.show_source_citations
    
    def should_show_technical_details(self) -> bool:
        """Determine if technical details should be shown"""
        if not self.preferences:
            return False
        
        return (self.preferences.show_technical_details or 
                self.get_level_config()['show_technical_details'])
    
    def get_explanation_style(self) -> str:
        """Get preferred explanation style"""
        if self.preferences:
            return self.preferences.preferred_explanation_style
        return 'conversational'

class ContentAdapter:
    """Adapts content based on transparency preferences"""
    
    def __init__(self, transparency_controller: TransparencyController):
        self.controller = transparency_controller
        self.simple_vocabulary = self._load_simple_vocabulary()
        self.legal_terms = self._load_legal_terms()
    
    def _load_simple_vocabulary(self) -> Dict[str, str]:
        """Load simple vocabulary replacements"""
        return {
            'hereinafter': 'from now on',
            'aforementioned': 'mentioned before',
            'whereas': 'while',
            'hereby': 'by this',
            'thereof': 'of that',
            'therein': 'in that',
            'thereby': 'by that',
            'whereby': 'by which',
            'notwithstanding': 'despite',
            'pursuant to': 'according to',
            'in accordance with': 'following',
            'subject to': 'depending on',
            'without prejudice to': 'without affecting',
            'mutatis mutandis': 'with necessary changes',
            'prima facie': 'at first sight',
            'bona fide': 'in good faith',
            'ad hoc': 'for this purpose',
            'de facto': 'in fact',
            'de jure': 'by law',
            'inter alia': 'among other things'
        }
    
    def _load_legal_terms(self) -> Dict[str, str]:
        """Load legal terms and their explanations"""
        return {
            'indemnification': 'protection against loss or damage',
            'liquidated damages': 'agreed-upon compensation',
            'force majeure': 'unforeseen circumstances',
            'arbitration': 'dispute resolution by neutral party',
            'jurisdiction': 'legal authority area',
            'governing law': 'law that applies to the contract',
            'breach': 'violation of contract terms',
            'remedy': 'solution for contract violation',
            'consideration': 'something of value exchanged',
            'covenant': 'promise in a contract'
        }
    
    def adapt_text(self, text: str, content_type: str = 'general') -> str:
        """Adapt text based on transparency preferences"""
        level_config = self.controller.get_level_config()
        
        # Apply sentence length limits
        if level_config['max_sentence_length']:
            text = self._limit_sentence_length(text, level_config['max_sentence_length'])
        
        # Apply vocabulary simplification
        if level_config['use_simple_vocabulary']:
            text = self._simplify_vocabulary(text)
        
        # Handle legal terms
        if level_config['avoid_legal_terms']:
            text = self._explain_legal_terms(text)
        else:
            text = self._add_legal_term_explanations(text)
        
        # Add examples if requested
        if level_config['include_examples']:
            text = self._add_examples(text, content_type)
        
        # Add analogies if requested
        if level_config['use_analogies']:
            text = self._add_analogies(text, content_type)
        
        return text
    
    def _limit_sentence_length(self, text: str, max_length: int) -> str:
        """Limit sentence length to specified maximum"""
        sentences = text.split('. ')
        adapted_sentences = []
        
        for sentence in sentences:
            if len(sentence) > max_length:
                # Split long sentences
                words = sentence.split()
                current_sentence = ""
                adapted_sentences.append(current_sentence)
                
                for word in words:
                    if len(current_sentence + " " + word) <= max_length:
                        current_sentence += (" " + word) if current_sentence else word
                    else:
                        if current_sentence:
                            adapted_sentences.append(current_sentence.strip())
                        current_sentence = word
                
                if current_sentence:
                    adapted_sentences.append(current_sentence.strip())
            else:
                adapted_sentences.append(sentence)
        
        return '. '.join(adapted_sentences)
    
    def _simplify_vocabulary(self, text: str) -> str:
        """Replace complex words with simpler alternatives"""
        for complex_word, simple_word in self.simple_vocabulary.items():
            text = text.replace(complex_word, simple_word)
            text = text.replace(complex_word.title(), simple_word.title())
        
        return text
    
    def _explain_legal_terms(self, text: str) -> str:
        """Replace legal terms with explanations"""
        for legal_term, explanation in self.legal_terms.items():
            text = text.replace(legal_term, explanation)
            text = text.replace(legal_term.title(), explanation.title())
        
        return text
    
    def _add_legal_term_explanations(self, text: str) -> str:
        """Add explanations for legal terms in parentheses"""
        for legal_term, explanation in self.legal_terms.items():
            if legal_term in text.lower():
                # Add explanation in parentheses
                text = text.replace(legal_term, f"{legal_term} ({explanation})")
                text = text.replace(legal_term.title(), f"{legal_term.title()} ({explanation})")
        
        return text
    
    def _add_examples(self, text: str, content_type: str) -> str:
        """Add examples based on content type"""
        examples = {
            'clause': {
                'penalty': 'For example, if you break this rule, you might have to pay $100.',
                'auto_renewal': 'For example, this contract will automatically continue every year unless you cancel it.',
                'termination': 'For example, either party can end this agreement with 30 days notice.'
            },
            'risk': {
                'high': 'For example, this is like signing up for a service that automatically charges your credit card.',
                'medium': 'For example, this is like agreeing to pay a fee if you cancel early.',
                'low': 'For example, this is like agreeing to give notice before ending the service.'
            }
        }
        
        # Add relevant examples based on content
        for category, category_examples in examples.items():
            for key, example in category_examples.items():
                if key in text.lower():
                    text += f" {example}"
                    break
        
        return text
    
    def _add_analogies(self, text: str, content_type: str) -> str:
        """Add analogies to make content more understandable"""
        analogies = {
            'clause': 'Think of this like reading the fine print on a contract.',
            'risk': 'This is like checking the weather before going on a trip.',
            'summary': 'This is like having someone explain a complex movie plot in simple terms.'
        }
        
        if content_type in analogies:
            text += f" {analogies[content_type]}"
        
        return text

class AdaptiveContentGenerator:
    """Generates adaptive content based on user preferences and context"""
    
    def __init__(self, transparency_controller: TransparencyController):
        self.controller = transparency_controller
        self.content_adapter = ContentAdapter(transparency_controller)
    
    def generate_explanation(self, 
                           content: str, 
                           content_type: str = 'general',
                           context: Optional[Dict[str, Any]] = None) -> str:
        """Generate explanation with appropriate detail level"""
        
        # Get current configuration
        level_config = self.controller.get_level_config()
        
        # Start with base content
        explanation = content
        
        # Adapt content based on preferences
        explanation = self.content_adapter.adapt_text(explanation, content_type)
        
        # Add confidence information if applicable
        if context and 'confidence' in context:
            confidence = context['confidence']
            if self.controller.should_show_confidence_score(confidence):
                explanation += f"\n\nConfidence Level: {confidence:.1%}"
        
        # Add source citations if applicable
        if context and 'sources' in context and self.controller.should_show_source_citations():
            sources = context['sources']
            if sources:
                explanation += "\n\nSources:"
                for source in sources[:3]:  # Limit to 3 sources
                    explanation += f"\n• {source}"
        
        # Add technical details if applicable
        if context and 'technical_details' in context and self.controller.should_show_technical_details():
            tech_details = context['technical_details']
            if tech_details:
                explanation += f"\n\nTechnical Details: {tech_details}"
        
        return explanation
    
    def generate_risk_explanation(self, 
                                risk_level: str, 
                                risk_score: float,
                                clause_text: str,
                                clause_type: str) -> str:
        """Generate risk explanation with appropriate detail"""
        
        level_config = self.controller.get_level_config()
        
        # Base explanations for different risk levels
        base_explanations = {
            'high': {
                'very_simple': 'This is a risky part of the contract. Be careful!',
                'simple': 'This clause has high risk. You should pay special attention to it.',
                'medium': 'This clause presents significant risk that requires careful consideration.',
                'detailed': 'This clause contains high-risk elements that could have substantial negative consequences.',
                'legal_detailed': 'This clause exhibits elevated risk characteristics that necessitate thorough legal review and potential modification.'
            },
            'medium': {
                'very_simple': 'This part has some risk. Think about it carefully.',
                'simple': 'This clause has moderate risk. You should understand it well.',
                'medium': 'This clause presents moderate risk that should be reviewed carefully.',
                'detailed': 'This clause contains moderate risk elements that require attention and understanding.',
                'legal_detailed': 'This clause demonstrates moderate risk characteristics that warrant careful consideration and potential negotiation.'
            },
            'low': {
                'very_simple': 'This part is mostly safe. It\'s okay.',
                'simple': 'This clause has low risk. It\'s generally safe to accept.',
                'medium': 'This clause presents minimal risk and is generally acceptable.',
                'detailed': 'This clause contains low-risk elements that pose minimal concerns.',
                'legal_detailed': 'This clause exhibits low-risk characteristics that are generally acceptable in standard contractual arrangements.'
            }
        }
        
        # Get base explanation
        detail_level = self.controller.get_current_detail_level()
        base_explanation = base_explanations[risk_level][detail_level]
        
        # Add clause-specific information
        if detail_level in ['detailed', 'legal_detailed']:
            explanation = f"{base_explanation} The clause relates to {clause_type.replace('_', ' ')} and contains the following text: '{clause_text[:100]}...'"
        else:
            explanation = base_explanation
        
        # Adapt the explanation
        explanation = self.content_adapter.adapt_text(explanation, 'risk')
        
        return explanation
    
    def generate_summary(self, 
                        document_text: str, 
                        summary_type: str = 'general',
                        max_length: Optional[int] = None) -> str:
        """Generate document summary with appropriate detail level"""
        
        level_config = self.controller.get_level_config()
        
        # Determine summary length based on detail level
        if max_length is None:
            length_multipliers = {
                'very_simple': 0.5,
                'simple': 0.7,
                'medium': 1.0,
                'detailed': 1.3,
                'legal_detailed': 1.5
            }
            base_length = 200  # Base summary length
            max_length = int(base_length * length_multipliers.get(level_config, 1.0))
        
        # Generate summary (this would integrate with AI summarization)
        # For now, create a simple summary
        sentences = document_text.split('.')
        summary = '. '.join(sentences[:3]) + '.'
        
        # Adapt the summary
        summary = self.content_adapter.adapt_text(summary, 'summary')
        
        # Truncate if necessary
        if len(summary) > max_length:
            summary = summary[:max_length-3] + '...'
        
        return summary

class TransparencyManager:
    """Main manager for transparency controls"""
    
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self.controller = TransparencyController(user)
        self.content_generator = AdaptiveContentGenerator(self.controller)
    
    @property
    def preferences(self):
        """Convenience property to access user preferences"""
        return self.controller.preferences if self.controller else None
    
    def is_initialized(self) -> bool:
        """Check if the manager is properly initialized"""
        return (self.controller is not None and 
                self.controller.preferences is not None)
    
    def update_preferences(self, **kwargs) -> bool:
        """Update user transparency preferences"""
        if not self.controller.preferences:
            return False
        
        try:
            for key, value in kwargs.items():
                if hasattr(self.controller.preferences, key):
                    setattr(self.controller.preferences, key, value)
            
            self.controller.preferences.save()
            logger.info(f"Updated transparency preferences for user {self.user.username}")
            return True
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False
    
    def get_preferences_summary(self) -> Dict[str, Any]:
        """Get summary of current preferences"""
        if not self.controller.preferences:
            # Return default preferences if user preferences are not available
            return self.controller.get_default_preferences()
        
        return {
            'detail_level': self.controller.preferences.explanation_detail_level,
            'show_confidence': self.controller.preferences.show_confidence_scores,
            'show_sources': self.controller.preferences.show_source_citations,
            'show_technical': self.controller.preferences.show_technical_details,
            'auto_adjust': self.controller.preferences.auto_adjust_complexity,
            'style': self.controller.preferences.preferred_explanation_style
        }
    
    def reset_to_defaults(self) -> bool:
        """Reset preferences to default values"""
        if not self.controller.preferences:
            return False
        
        try:
            self.controller.preferences.explanation_detail_level = 'medium'
            self.controller.preferences.show_confidence_scores = True
            self.controller.preferences.show_source_citations = True
            self.controller.preferences.show_technical_details = False
            self.controller.preferences.auto_adjust_complexity = True
            self.controller.preferences.preferred_explanation_style = 'conversational'
            self.controller.preferences.save()
            
            logger.info(f"Reset preferences to defaults for user {self.user.username}")
            return True
        except Exception as e:
            logger.error(f"Error resetting preferences: {e}")
            return False
