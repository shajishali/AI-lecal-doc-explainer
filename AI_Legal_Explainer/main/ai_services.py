"""
AI Services for AI Legal Explainer
Handles document processing, summarization, clause detection, and risk analysis
"""

import os
import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import numpy as np

# Make AI library imports optional to avoid startup errors
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. AI summarization will use fallback methods.")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI library not available. Chat functionality will use fallback methods.")

from django.conf import settings
from .models import Document, Clause, RiskAnalysis, DocumentSummary, LegalTerm

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document text extraction and preprocessing"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.docx', '.txt']
    
    def extract_text(self, document: Document) -> str:
        """Extract text from uploaded document"""
        try:
            file_path = document.file.path
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.txt':
                return self._extract_text_from_txt(file_path)
            elif file_extension == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                return self._extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error extracting text from document {document.id}: {str(e)}")
            raise
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.error("PyPDF2 not installed. Please install it for PDF support.")
            raise
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.error("python-docx not installed. Please install it for DOCX support.")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep legal terms
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', '', text)
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text.strip()

class AISummarizer:
    """Handles AI-powered document summarization"""
    
    def __init__(self):
        self.model_name = "t5-base"
        self.tokenizer = None
        self.model = None
        self.summarizer = None
        
        if TRANSFORMERS_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load the T5 model for summarization"""
        try:
            model_path = settings.AI_MODEL_PATH / self.model_name
            if model_path.exists():
                self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                self.model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path))
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            self.summarizer = pipeline("summarization", model=self.model, tokenizer=self.tokenizer)
            logger.info("T5 model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading T5 model: {str(e)}")
            # Fallback to basic summarization
            self.summarizer = None
    
    def generate_summary(self, text: str, max_length: int = 400) -> Dict[str, str]:
        """Generate plain language summary of legal document"""
        try:
            if self.summarizer and TRANSFORMERS_AVAILABLE:
                # Use T5 model for summarization
                summary = self.summarizer(text, max_length=max_length, min_length=200, do_sample=False)
                plain_summary = summary[0]['summary_text']
            else:
                # Fallback to basic summarization
                plain_summary = self._basic_summarization(text, max_length)
            
            # Generate legal summary (more technical)
            legal_summary = self._generate_legal_summary(text)
            
            # Extract key points
            key_points = self._extract_key_points(text)
            
            return {
                'plain_language_summary': plain_summary,
                'legal_summary': legal_summary,
                'key_points': key_points,
                'word_count': len(plain_summary.split())
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # Return basic summary on error
            return {
                'plain_language_summary': self._basic_summarization(text, max_length),
                'legal_summary': '',
                'key_points': [],
                'word_count': 0
            }
    
    def _basic_summarization(self, text: str, max_length: int) -> str:
        """Basic summarization when AI model is not available"""
        sentences = text.split('.')
        summary_sentences = sentences[:5]  # Take first 5 sentences
        summary = '. '.join(summary_sentences) + '.'
        
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        
        return summary
    
    def _generate_legal_summary(self, text: str) -> str:
        """Generate more technical legal summary"""
        # This would be enhanced with legal domain knowledge
        return "Legal analysis summary would be generated here."
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from the document"""
        # Simple keyword-based extraction
        legal_keywords = [
            'contract', 'agreement', 'terms', 'conditions', 'obligations',
            'liability', 'indemnification', 'termination', 'renewal',
            'confidentiality', 'intellectual property', 'governing law'
        ]
        
        key_points = []
        sentences = text.split('.')
        
        for sentence in sentences[:10]:  # Check first 10 sentences
            for keyword in legal_keywords:
                if keyword.lower() in sentence.lower() and len(sentence.strip()) > 20:
                    key_points.append(sentence.strip())
                    break
                if len(key_points) >= 5:  # Limit to 5 key points
                    break
        
        return key_points[:5]

class ClauseDetector:
    """Detects legal clauses and assesses risk levels"""
    
    def __init__(self):
        self.clause_patterns = self._load_clause_patterns()
        self.risk_keywords = self._load_risk_keywords()
    
    def _load_clause_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for different clause types"""
        return {
            'penalty': [
                r'penalty.*\$\d+',
                r'fine.*\$\d+',
                r'late.*fee.*\$\d+',
                r'default.*\$\d+'
            ],
            'auto_renewal': [
                r'auto.*renew',
                r'automatic.*renewal',
                r'renew.*automatically',
                r'continue.*unless.*terminated'
            ],
            'termination': [
                r'terminate.*\d+\s*days',
                r'termination.*notice',
                r'cancel.*\d+\s*days',
                r'end.*agreement'
            ],
            'indemnification': [
                r'indemnify',
                r'indemnification',
                r'hold.*harmless',
                r'defend.*against'
            ],
            'liability': [
                r'limitation.*liability',
                r'liability.*limited',
                r'exclude.*liability',
                r'no.*liability'
            ],
            'confidentiality': [
                r'confidential',
                r'confidentiality',
                r'non.*disclosure',
                r'proprietary.*information'
            ]
        }
    
    def _load_risk_keywords(self) -> Dict[str, List[str]]:
        """Load keywords that indicate risk levels"""
        return {
            'high': [
                'penalty', 'fine', 'default', 'breach', 'termination',
                'indemnification', 'liability', 'damages', 'forfeit'
            ],
            'medium': [
                'renewal', 'modification', 'amendment', 'assignment',
                'governing law', 'jurisdiction', 'dispute resolution'
            ],
            'low': [
                'definitions', 'scope', 'purpose', 'background',
                'recitals', 'witness', 'signature'
            ]
        }
    
    def detect_clauses(self, text: str) -> List[Dict]:
        """Detect clauses in the document text"""
        clauses = []
        
        for clause_type, patterns in self.clause_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    clause_text = match.group(0)
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Calculate risk score
                    risk_score = self._calculate_risk_score(clause_text, clause_type)
                    risk_level = self._determine_risk_level(risk_score)
                    
                    # Generate plain language explanation
                    plain_explanation = self._generate_clause_explanation(clause_text, clause_type)
                    
                    clauses.append({
                        'clause_type': clause_type,
                        'original_text': clause_text,
                        'start_position': start_pos,
                        'end_position': end_pos,
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'plain_language_summary': plain_explanation,
                        'risk_explanation': self._generate_risk_explanation(risk_score, clause_type)
                    })
        
        return clauses
    
    def _calculate_risk_score(self, clause_text: str, clause_type: str) -> float:
        """Calculate risk score for a clause (0.0 to 1.0)"""
        base_scores = {
            'penalty': 0.9,
            'indemnification': 0.8,
            'termination': 0.7,
            'auto_renewal': 0.6,
            'liability': 0.7,
            'confidentiality': 0.5
        }
        
        base_score = base_scores.get(clause_type, 0.5)
        
        # Adjust based on text content
        text_lower = clause_text.lower()
        
        # High risk indicators
        if any(word in text_lower for word in ['penalty', 'fine', 'default']):
            base_score += 0.1
        if any(word in text_lower for word in ['immediate', 'instant', 'without notice']):
            base_score += 0.1
        
        # Medium risk indicators
        if any(word in text_lower for word in ['reasonable', 'appropriate', 'standard']):
            base_score -= 0.1
        
        return min(1.0, max(0.0, base_score))
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score"""
        if risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_clause_explanation(self, clause_text: str, clause_type: str) -> str:
        """Generate plain language explanation of the clause"""
        explanations = {
            'penalty': 'This clause describes penalties or fines that may apply.',
            'auto_renewal': 'This clause allows the agreement to automatically renew.',
            'termination': 'This clause explains how the agreement can be ended.',
            'indemnification': 'This clause requires one party to protect another from losses.',
            'liability': 'This clause limits or excludes liability for damages.',
            'confidentiality': 'This clause protects sensitive information.'
        }
        
        return explanations.get(clause_type, 'This clause contains important legal terms.')
    
    def _generate_risk_explanation(self, risk_score: float, clause_type: str) -> str:
        """Generate explanation of why the clause is risky"""
        if risk_score >= 0.7:
            return f"This {clause_type.replace('_', ' ')} clause poses significant risks and should be carefully reviewed."
        elif risk_score >= 0.4:
            return f"This {clause_type.replace('_', ' ')} clause has moderate risks that should be considered."
        else:
            return f"This {clause_type.replace('_', ' ')} clause has minimal risks."

class RiskAnalyzer:
    """Analyzes overall risk of documents"""
    
    def __init__(self):
        self.risk_weights = {
            'high': 1.0,
            'medium': 0.6,
            'low': 0.2
        }
    
    def analyze_document_risk(self, clauses: List[Dict]) -> Dict:
        """Analyze overall risk of the document based on clauses"""
        if not clauses:
            return {
                'overall_risk_score': 0.0,
                'overall_risk_level': 'low',
                'high_risk_clauses_count': 0,
                'medium_risk_clauses_count': 0,
                'low_risk_clauses_count': 0,
                'analysis_summary': 'No significant risk clauses detected.'
            }
        
        # Count clauses by risk level
        risk_counts = {'high': 0, 'medium': 0, 'low': 0}
        total_weighted_score = 0.0
        
        for clause in clauses:
            risk_level = clause['risk_level']
            risk_counts[risk_level] += 1
            total_weighted_score += clause['risk_score'] * self.risk_weights[risk_level]
        
        # Calculate overall risk score
        if clauses:
            overall_risk_score = total_weighted_score / len(clauses)
        else:
            overall_risk_score = 0.0
        
        # Determine overall risk level
        if overall_risk_score >= 0.7 or risk_counts['high'] >= 3:
            overall_risk_level = 'high'
        elif overall_risk_score >= 0.4 or risk_counts['high'] >= 1:
            overall_risk_level = 'medium'
        else:
            overall_risk_level = 'low'
        
        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(risk_counts, overall_risk_level)
        
        return {
            'overall_risk_score': round(overall_risk_score, 3),
            'overall_risk_level': overall_risk_level,
            'high_risk_clauses_count': risk_counts['high'],
            'medium_risk_clauses_count': risk_counts['medium'],
            'low_risk_clauses_count': risk_counts['low'],
            'analysis_summary': analysis_summary
        }
    
    def _generate_analysis_summary(self, risk_counts: Dict[str, int], overall_level: str) -> str:
        """Generate human-readable analysis summary"""
        high_count = risk_counts['high']
        medium_count = risk_counts['medium']
        low_count = risk_counts['low']
        
        if overall_level == 'high':
            if high_count >= 3:
                return f"This document contains {high_count} high-risk clauses and poses significant legal risks. Professional legal review is strongly recommended."
            else:
                return f"This document contains {high_count} high-risk clauses and should be carefully reviewed by legal professionals."
        
        elif overall_level == 'medium':
            if high_count > 0:
                return f"This document contains {high_count} high-risk and {medium_count} medium-risk clauses. Legal review is recommended."
            else:
                return f"This document contains {medium_count} medium-risk clauses. Some legal review may be beneficial."
        
        else:
            return f"This document contains mostly low-risk clauses ({low_count} low, {medium_count} medium). Standard review procedures should be sufficient."

class ChatService:
    """Handles Q&A functionality using Google Gemini API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', '')
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            if not GEMINI_AVAILABLE:
                logger.warning("Google Generative AI library not available")
            elif not self.api_key:
                logger.warning("Google Gemini API key not configured")
    
    def generate_answer(self, question: str, document_context: str, clauses: List[Dict] = None) -> Dict:
        """Generate answer to user question about the document"""
        try:
            if not self.model:
                return self._fallback_answer(question)
            
            # Prepare context for the AI model
            context = self._prepare_context(document_context, clauses)
            
            # Create prompt
            prompt = f"""
            Context: {context}
            
            Question: {question}
            
            Please provide a clear, helpful answer about this legal document. 
            If you reference specific clauses, please cite them. 
            Always include a disclaimer that this is not legal advice.
            
            Answer:
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Calculate confidence (simplified)
            confidence_score = self._calculate_confidence(answer, question, context)
            
            # Extract sources
            sources = self._extract_sources(answer, clauses)
            
            return {
                'answer': answer,
                'confidence_score': confidence_score,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return self._fallback_answer(question)
    
    def _prepare_context(self, document_context: str, clauses: List[Dict] = None) -> str:
        """Prepare context for the AI model"""
        context = f"Document content: {document_context[:2000]}..."  # Limit context length
        
        if clauses:
            clause_info = []
            for clause in clauses[:5]:  # Limit to 5 most relevant clauses
                clause_info.append(f"Clause ({clause['clause_type']}): {clause['original_text'][:200]}...")
            
            context += f"\n\nKey clauses: {' '.join(clause_info)}"
        
        return context
    
    def _calculate_confidence(self, answer: str, question: str, context: str) -> float:
        """Calculate confidence score for the answer"""
        # Simple heuristic-based confidence calculation
        confidence = 0.7  # Base confidence
        
        # Increase confidence if answer is detailed
        if len(answer) > 100:
            confidence += 0.1
        
        # Increase confidence if answer references specific clauses
        if 'clause' in answer.lower() or 'section' in answer.lower():
            confidence += 0.1
        
        # Decrease confidence if answer is too generic
        if len(answer) < 50:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _extract_sources(self, answer: str, clauses: List[Dict] = None) -> List[str]:
        """Extract source references from the answer"""
        sources = []
        
        if clauses:
            # Look for clause references in the answer
            for clause in clauses:
                if clause['clause_type'] in answer.lower():
                    sources.append(f"Clause: {clause['clause_type']}")
        
        if not sources:
            sources.append("Document content")
        
        return sources
    
    def _fallback_answer(self, question: str) -> Dict:
        """Fallback answer when AI service is not available"""
        return {
            'answer': f"I'm sorry, I'm unable to process your question about '{question}' at the moment. Please try again later or contact support.",
            'confidence_score': 0.0,
            'sources': ['System message']
        }

class GlossaryService:
    """Handles legal glossary and term definitions"""
    
    def __init__(self):
        self.terms = self._load_default_terms()
    
    def _load_default_terms(self) -> List[Dict]:
        """Load default legal terms"""
        return [
            {
                'term': 'Indemnification',
                'definition': 'A contractual obligation where one party agrees to compensate another party for losses or damages.',
                'plain_language_explanation': 'This means one party promises to pay for any losses or damages that happen to the other party.',
                'category': 'Contract Terms'
            },
            {
                'term': 'Liability',
                'definition': 'Legal responsibility for one\'s actions or inactions that result in harm or damage to another party.',
                'plain_language_explanation': 'This is the legal responsibility you have when something goes wrong.',
                'category': 'Legal Concepts'
            },
            {
                'term': 'Termination',
                'definition': 'The act of ending or canceling a contract or agreement before its natural expiration.',
                'plain_language_explanation': 'This is how you can end an agreement before it\'s supposed to end.',
                'category': 'Contract Terms'
            },
            {
                'term': 'Auto-renewal',
                'definition': 'A provision in a contract that automatically extends the agreement for additional periods unless terminated.',
                'plain_language_explanation': 'This means the agreement will automatically continue unless you specifically stop it.',
                'category': 'Contract Terms'
            },
            {
                'term': 'Penalty',
                'definition': 'A financial consequence or fine imposed for violating the terms of a contract.',
                'plain_language_explanation': 'This is a fine or charge you have to pay if you break the agreement.',
                'category': 'Contract Terms'
            }
        ]
    
    def search_terms(self, query: str) -> List[Dict]:
        """Search for legal terms matching the query"""
        query_lower = query.lower()
        matching_terms = []
        
        for term in self.terms:
            if (query_lower in term['term'].lower() or 
                query_lower in term['definition'].lower() or
                query_lower in term['plain_language_explanation'].lower()):
                matching_terms.append(term)
        
        return matching_terms
    
    def get_term_definition(self, term: str) -> Optional[Dict]:
        """Get definition for a specific term"""
        for legal_term in self.terms:
            if legal_term['term'].lower() == term.lower():
                return legal_term
        return None
    
    def highlight_terms_in_text(self, text: str) -> str:
        """Highlight legal terms in text with tooltips"""
        highlighted_text = text
        
        for term in self.terms:
            term_pattern = re.compile(r'\b' + re.escape(term['term']) + r'\b', re.IGNORECASE)
            highlighted_text = term_pattern.sub(
                f'<span class="legal-term" title="{term["plain_language_explanation"]}">{term["term"]}</span>',
                highlighted_text
            )
        
        return highlighted_text
