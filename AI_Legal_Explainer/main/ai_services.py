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

# Simplified imports - remove heavy AI libraries
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
            
            logger.info(f"Extracting text from {file_extension} file: {file_path}")
            
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
            # Return a fallback text instead of crashing
            return f"Error extracting text: {str(e)}. Please check the file format."
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Failed to read TXT file {file_path}: {str(e)}")
                return f"Error reading text file: {str(e)}"
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        else:
                            logger.warning(f"Page {page_num + 1} returned no text")
                    except Exception as page_error:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {str(page_error)}")
                        continue
            
            if not text.strip():
                return "PDF file appears to be empty or contains no extractable text."
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
            
        except ImportError:
            logger.error("PyPDF2 not installed. Please install it for PDF support.")
            return "PDF processing not available. Please install PyPDF2."
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return f"Error processing PDF: {str(e)}"
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            
            if not text.strip():
                return "DOCX file appears to be empty or contains no text."
            
            logger.info(f"Successfully extracted {len(text)} characters from DOCX")
            return text
            
        except ImportError:
            logger.error("python-docx not installed. Please install it for DOCX support.")
            return "DOCX processing not available. Please install python-docx."
        except Exception as e:
            logger.error(f"Error processing DOCX {file_path}: {str(e)}")
            return f"Error processing DOCX: {str(e)}"
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        try:
            if not text or len(text.strip()) < 10:
                return "Document contains insufficient text for analysis."
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            # Remove special characters but keep legal terms
            text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', '', text)
            # Normalize line breaks
            text = text.replace('\n', ' ').replace('\r', ' ')
            processed_text = text.strip()
            
            logger.info(f"Preprocessed text: {len(processed_text)} characters")
            return processed_text
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            return text  # Return original text if preprocessing fails

class AISummarizer:
    """Handles document summarization using basic text analysis"""
    
    def __init__(self):
        # Simplified - no heavy model loading
        pass
    
    def generate_summary(self, text: str, max_length: int = 400) -> Dict[str, str]:
        """Generate plain language summary of legal document"""
        try:
            if not text or len(text.strip()) < 50:
                return {
                    'plain_language_summary': 'Document contains insufficient text for meaningful summary.',
                    'legal_summary': 'Insufficient content for legal analysis.',
                    'key_points': ['Document too short for analysis'],
                    'word_count': 0
                }
            
            # Use basic summarization
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
                'legal_summary': 'Summary generation failed due to technical error.',
                'key_points': ['Error occurred during analysis'],
                'word_count': 0
            }
    
    def _basic_summarization(self, text: str, max_length: int) -> str:
        """Basic summarization when AI model is not available"""
        try:
            sentences = text.split('.')
            # Take first few meaningful sentences
            summary_sentences = []
            for sentence in sentences:
                if len(sentence.strip()) > 20:  # Only meaningful sentences
                    summary_sentences.append(sentence.strip())
                    if len(summary_sentences) >= 3:  # Limit to 3 sentences
                        break
            
            if not summary_sentences:
                summary_sentences = sentences[:2]  # Fallback to first 2 sentences
            
            summary = '. '.join(summary_sentences) + '.'
            
            if len(summary) > max_length:
                summary = summary[:max_length] + '...'
            
            return summary
        except Exception as e:
            logger.error(f"Error in basic summarization: {str(e)}")
            return "Document summary could not be generated."
    
    def _generate_legal_summary(self, text: str) -> str:
        """Generate more technical legal summary"""
        try:
            # Simple legal summary based on content analysis
            legal_terms = ['contract', 'agreement', 'terms', 'conditions', 'obligations', 
                          'liability', 'indemnification', 'termination', 'renewal']
            
            found_terms = [term for term in legal_terms if term.lower() in text.lower()]
            
            if found_terms:
                return f"This document contains legal provisions related to: {', '.join(found_terms)}."
            else:
                return "This document contains general legal content requiring review."
        except Exception as e:
            logger.error(f"Error generating legal summary: {str(e)}")
            return "Legal summary could not be generated."
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from the document"""
        try:
            # Simple keyword-based extraction
            legal_keywords = [
                'contract', 'agreement', 'terms', 'conditions', 'obligations',
                'liability', 'indemnification', 'termination', 'renewal',
                'confidentiality', 'intellectual property', 'governing law'
            ]
            
            key_points = []
            sentences = text.split('.')
            
            for sentence in sentences[:10]:  # Check first 10 sentences
                sentence = sentence.strip()
                if len(sentence) < 20:  # Skip very short sentences
                    continue
                    
                for keyword in legal_keywords:
                    if keyword.lower() in sentence.lower():
                        key_points.append(sentence)
                        break
                        
                if len(key_points) >= 5:  # Limit to 5 key points
                    break
            
            if not key_points:
                # Fallback: take first few meaningful sentences
                key_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
            
            return key_points[:5]
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return ["Key points could not be extracted due to technical error."]

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
    """Handles Q&A functionality using basic text analysis"""
    
    def __init__(self):
        # Simplified - no external API dependencies
        pass
    
    def generate_answer(self, question: str, document_context: str, clauses: List[Dict] = None) -> Dict:
        """Generate answer to user question about the document"""
        try:
            # Use basic text analysis to generate answers
            answer = self._generate_basic_answer(question, document_context, clauses)
            
            # Calculate confidence (simplified)
            confidence_score = self._calculate_confidence(answer, question, document_context)
            
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
    
    def _generate_basic_answer(self, question: str, document_context: str, clauses: List[Dict] = None) -> str:
        """Generate basic answer using text analysis"""
        question_lower = question.lower()
        
        # Simple keyword-based answering
        if 'summary' in question_lower or 'overview' in question_lower:
            return f"Based on the document content, this appears to be a legal document containing approximately {len(document_context.split())} words. The document covers various legal topics and should be reviewed carefully. This is not legal advice."
        
        elif 'risk' in question_lower or 'dangerous' in question_lower:
            if clauses:
                high_risk_count = sum(1 for clause in clauses if clause.get('risk_level') == 'high')
                if high_risk_count > 0:
                    return f"The document contains {high_risk_count} high-risk clauses that require careful attention. These clauses may have significant legal implications. This is not legal advice."
                else:
                    return "The document appears to have moderate to low risk levels based on the clauses analyzed. However, all legal documents should be reviewed by qualified professionals. This is not legal advice."
            else:
                return "Risk analysis is not available for this document. Please ensure you have the document properly processed. This is not legal advice."
        
        elif 'clause' in question_lower or 'section' in question_lower:
            if clauses:
                clause_types = list(set(clause.get('clause_type', 'unknown') for clause in clauses))
                return f"The document contains {len(clauses)} clauses of various types including: {', '.join(clause_types[:5])}. Each clause should be reviewed for its legal implications. This is not legal advice."
            else:
                return "No specific clauses have been identified in this document yet. Please ensure the document has been fully processed. This is not legal advice."
        
        else:
            return f"I can help you understand this legal document. The document contains {len(document_context.split())} words and covers various legal topics. For specific questions about clauses, risks, or summaries, please ask more specifically. This is not legal advice."
    
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
