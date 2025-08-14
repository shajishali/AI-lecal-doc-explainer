"""
Enhanced AI Services for AI Legal Explainer
Implements missing functionality: better AI models, risk visualizations, what-if simulations
"""

import os
import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import numpy as np

from django.conf import settings
from .models import Document, Clause, RiskAnalysis, DocumentSummary, LegalTerm

logger = logging.getLogger(__name__)

class EnhancedAISummarizer:
    """Enhanced AI summarization using Google Generative AI"""
    
    def __init__(self):
        self.model = None
        self._initialize_ai_model()
    
    def _initialize_ai_model(self):
        """Initialize Google Generative AI model"""
        try:
            import google.generativeai as genai
            
            # Set up API key (should be in environment variables)
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Google Generative AI model initialized successfully")
            else:
                logger.warning("GOOGLE_API_KEY not found, using fallback summarization")
                
        except ImportError:
            logger.warning("Google Generative AI not available, using fallback")
        except Exception as e:
            logger.error(f"Error initializing AI model: {e}")
    
    def generate_summary(self, text: str, max_length: int = 400) -> Dict[str, str]:
        """Generate enhanced AI summary"""
        if self.model:
            return self._generate_ai_summary(text, max_length)
        else:
            return self._generate_fallback_summary(text, max_length)
    
    def _generate_ai_summary(self, text: str, max_length: int) -> Dict[str, str]:
        """Generate summary using Google Generative AI"""
        try:
            prompt = f"""
            Analyze this legal document and provide:
            1. A plain language summary (max {max_length} words)
            2. A technical legal summary
            3. Key legal points and risks
            
            Document text: {text[:3000]}...
            
            Format the response as JSON with keys: plain_language_summary, legal_summary, key_points
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                result = json.loads(response.text)
                return {
                    'plain_language_summary': result.get('plain_language_summary', ''),
                    'legal_summary': result.get('legal_summary', ''),
                    'key_points': result.get('key_points', []),
                    'word_count': len(result.get('plain_language_summary', '').split()),
                    'ai_generated': True
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._parse_ai_response(response.text, max_length)
                
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return self._generate_fallback_summary(text, max_length)
    
    def _parse_ai_response(self, response_text: str, max_length: int) -> Dict[str, str]:
        """Parse AI response when JSON parsing fails"""
        lines = response_text.split('\n')
        plain_summary = ""
        legal_summary = ""
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('1.') or 'plain language' in line.lower():
                plain_summary = line.replace('1.', '').replace('Plain language summary:', '').strip()
            elif line.startswith('2.') or 'technical' in line.lower():
                legal_summary = line.replace('2.', '').replace('Technical legal summary:', '').strip()
            elif line.startswith('3.') or 'key points' in line.lower():
                key_points = [point.strip() for point in line.replace('3.', '').replace('Key points:', '').split(',')]
        
        return {
            'plain_language_summary': plain_summary[:max_length] if plain_summary else 'AI summary generation failed',
            'legal_summary': legal_summary if legal_summary else 'Technical summary not available',
            'key_points': key_points if key_points else ['Summary generation failed'],
            'word_count': len(plain_summary.split()),
            'ai_generated': True
        }
    
    def _generate_fallback_summary(self, text: str, max_length: int) -> Dict[str, str]:
        """Fallback summarization when AI is not available"""
        sentences = text.split('.')
        summary_sentences = []
        
        for sentence in sentences[:5]:
            if len(sentence.strip()) > 20:
                summary_sentences.append(sentence.strip())
                if len(' '.join(summary_sentences)) > max_length:
                    break
        
        plain_summary = '. '.join(summary_sentences) + '.'
        
        return {
            'plain_language_summary': plain_summary,
            'legal_summary': 'AI-powered legal summary not available',
            'key_points': ['AI service unavailable', 'Basic summary provided'],
            'word_count': len(plain_summary.split()),
            'ai_generated': False
        }

class RiskVisualizer:
    """Creates interactive risk visualizations and charts"""
    
    def __init__(self):
        self.colors = {
            'high': '#ff4444',
            'medium': '#ffaa00',
            'low': '#44ff44'
        }
    
    def create_risk_dashboard(self, document: Document) -> Dict[str, str]:
        """Create comprehensive risk visualization dashboard"""
        try:
            # Get document data
            clauses = document.clauses.all()
            risk_analysis = getattr(document, 'risk_analysis', None)
            
            if not clauses:
                return {'error': 'No clauses available for visualization'}
            
            # Create multiple visualizations
            risk_distribution_chart = self._create_risk_distribution_chart(clauses)
            risk_timeline_chart = self._create_risk_timeline_chart(clauses)
            clause_type_analysis = self._create_clause_type_analysis(clauses)
            overall_risk_gauge = self._create_risk_gauge(risk_analysis)
            
            return {
                'risk_distribution': risk_distribution_chart,
                'risk_timeline': risk_timeline_chart,
                'clause_analysis': clause_type_analysis,
                'risk_gauge': overall_risk_gauge
            }
            
        except Exception as e:
            logger.error(f"Error creating risk dashboard: {e}")
            return {'error': f'Visualization failed: {str(e)}'}
    
    def _create_risk_distribution_chart(self, clauses: List[Clause]) -> str:
        """Create pie chart showing risk distribution"""
        try:
            risk_counts = {'high': 0, 'medium': 0, 'low': 0}
            for clause in clauses:
                risk_counts[clause.risk_level] += 1
            
            # Create simple HTML chart since Plotly might not be available
            chart_html = f"""
            <div class="risk-chart">
                <h4>Risk Distribution by Clause</h4>
                <div class="chart-container">
                    <div class="chart-item high-risk">
                        <span class="risk-label">High Risk: {risk_counts['high']}</span>
                        <div class="risk-bar" style="width: {risk_counts['high'] * 50}px; background-color: {self.colors['high']};"></div>
                    </div>
                    <div class="chart-item medium-risk">
                        <span class="risk-label">Medium Risk: {risk_counts['medium']}</span>
                        <div class="risk-bar" style="width: {risk_counts['medium'] * 50}px; background-color: {self.colors['medium']};"></div>
                    </div>
                    <div class="chart-item low-risk">
                        <span class="risk-label">Low Risk: {risk_counts['low']}</span>
                        <div class="risk-bar" style="width: {risk_counts['low'] * 50}px; background-color: {self.colors['low']};"></div>
                    </div>
                </div>
            </div>
            """
            return chart_html
            
        except Exception as e:
            logger.error(f"Error creating risk distribution chart: {e}")
            return f"<p>Chart generation failed: {str(e)}</p>"
    
    def _create_risk_timeline_chart(self, clauses: List[Clause]) -> str:
        """Create timeline chart showing clause positions"""
        try:
            # Prepare data for timeline
            timeline_data = []
            for clause in clauses:
                timeline_data.append({
                    'clause_type': clause.clause_type.replace('_', ' ').title(),
                    'position': clause.start_position,
                    'risk_level': clause.risk_level,
                    'text': clause.original_text[:50] + '...'
                })
            
            # Sort by position
            timeline_data.sort(key=lambda x: x['position'])
            
            # Create simple HTML timeline
            timeline_html = """
            <div class="timeline-chart">
                <h4>Clause Timeline by Document Position</h4>
                <div class="timeline-container">
            """
            
            for item in timeline_data:
                color = self.colors.get(item['risk_level'], '#888888')
                timeline_html += f"""
                    <div class="timeline-item" style="border-left-color: {color};">
                        <div class="timeline-marker" style="background-color: {color};"></div>
                        <div class="timeline-content">
                            <strong>{item['clause_type']}</strong>
                            <span class="risk-level">{item['risk_level'].title()} Risk</span>
                            <div class="clause-preview">{item['text']}</div>
                        </div>
                    </div>
                """
            
            timeline_html += """
                </div>
            </div>
            """
            
            return timeline_html
            
        except Exception as e:
            logger.error(f"Error creating risk timeline chart: {e}")
            return f"<p>Timeline chart generation failed: {str(e)}</p>"
    
    def _create_clause_type_analysis(self, clauses: List[Clause]) -> str:
        """Create bar chart showing clause types and their risk levels"""
        try:
            # Group clauses by type and risk level
            clause_data = {}
            for clause in clauses:
                clause_type = clause.clause_type.replace('_', ' ').title()
                if clause_type not in clause_data:
                    clause_data[clause_type] = {'high': 0, 'medium': 0, 'low': 0}
                clause_data[clause_type][clause.risk_level] += 1
            
            # Create simple HTML stacked bar chart
            chart_html = """
            <div class="clause-analysis-chart">
                <h4>Clause Types by Risk Level</h4>
                <div class="chart-container">
            """
            
            for clause_type, risks in clause_data.items():
                chart_html += f"""
                    <div class="clause-type-group">
                        <div class="clause-type-label">{clause_type}</div>
                        <div class="risk-bars">
                            <div class="risk-bar high" style="width: {risks['high'] * 30}px; background-color: {self.colors['high']};">
                                {risks['high']}
                            </div>
                            <div class="risk-bar medium" style="width: {risks['medium'] * 30}px; background-color: {self.colors['medium']};">
                                {risks['medium']}
                            </div>
                            <div class="risk-bar low" style="width: {risks['low'] * 30}px; background-color: {self.colors['low']};">
                                {risks['low']}
                            </div>
                        </div>
                    </div>
                """
            
            chart_html += """
                </div>
                <div class="legend">
                    <span class="legend-item"><span class="legend-color high"></span> High Risk</span>
                    <span class="legend-item"><span class="legend-color medium"></span> Medium Risk</span>
                    <span class="legend-item"><span class="legend-color low"></span> Low Risk</span>
                </div>
            </div>
            """
            
            return chart_html
            
        except Exception as e:
            logger.error(f"Error creating clause type analysis: {e}")
            return f"<p>Clause analysis chart generation failed: {str(e)}</p>"
    
    def _create_risk_gauge(self, risk_analysis: RiskAnalysis) -> str:
        """Create gauge chart showing overall risk level"""
        try:
            if not risk_analysis:
                return "<p>Risk analysis not available</p>"
            
            # Create simple HTML gauge
            risk_percentage = risk_analysis.overall_risk_score * 100
            color = self._get_risk_color(risk_analysis.overall_risk_level)
            
            gauge_html = f"""
            <div class="risk-gauge">
                <h4>Overall Risk Score</h4>
                <div class="gauge-container">
                    <div class="gauge-circle" style="border-color: {color};">
                        <div class="gauge-value">{risk_percentage:.1f}%</div>
                        <div class="gauge-label">{risk_analysis.overall_risk_level.title()} Risk</div>
                    </div>
                </div>
                <div class="gauge-details">
                    <div class="detail-item">High Risk Clauses: {risk_analysis.high_risk_clauses_count}</div>
                    <div class="detail-item">Medium Risk Clauses: {risk_analysis.medium_risk_clauses_count}</div>
                    <div class="detail-item">Low Risk Clauses: {risk_analysis.low_risk_clauses_count}</div>
                </div>
            </div>
            """
            
            return gauge_html
            
        except Exception as e:
            logger.error(f"Error creating risk gauge: {e}")
            return f"<p>Risk gauge generation failed: {str(e)}</p>"
    
    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level"""
        return self.colors.get(risk_level, '#888888')

class WhatIfSimulator:
    """Simulates what-if scenarios for legal clauses"""
    
    def __init__(self):
        self.scenario_templates = self._load_scenario_templates()
    
    def _load_scenario_templates(self) -> Dict[str, Dict]:
        """Load predefined what-if scenario templates"""
        return {
            'penalty_modification': {
                'name': 'Penalty Amount Modification',
                'description': 'What if the penalty amount is reduced or increased?',
                'parameters': ['penalty_amount', 'payment_terms', 'grace_period'],
                'impact_areas': ['financial_risk', 'compliance_risk', 'operational_risk']
            },
            'termination_timing': {
                'name': 'Termination Notice Period',
                'description': 'What if the termination notice period is changed?',
                'parameters': ['notice_period', 'termination_reasons', 'compensation'],
                'impact_areas': ['operational_risk', 'financial_risk', 'legal_risk']
            },
            'liability_limits': {
                'name': 'Liability Limit Changes',
                'description': 'What if liability limits are modified?',
                'parameters': ['liability_cap', 'exclusions', 'insurance_requirements'],
                'impact_areas': ['financial_risk', 'legal_risk', 'reputation_risk']
            },
            'auto_renewal_terms': {
                'name': 'Auto-Renewal Modification',
                'description': 'What if auto-renewal terms are changed?',
                'parameters': ['renewal_period', 'cancellation_terms', 'price_changes'],
                'impact_areas': ['operational_risk', 'financial_risk', 'strategic_risk']
            }
        }
    
    def simulate_scenario(self, clause: Clause, scenario_type: str, modifications: Dict) -> Dict:
        """Simulate a what-if scenario for a specific clause"""
        try:
            if scenario_type not in self.scenario_templates:
                return {'error': f'Unknown scenario type: {scenario_type}'}
            
            template = self.scenario_templates[scenario_type]
            
            # Analyze original clause
            original_analysis = self._analyze_clause_risk(clause)
            
            # Apply modifications
            modified_analysis = self._apply_modifications(original_analysis, modifications)
            
            # Calculate impact
            impact_analysis = self._calculate_impact(original_analysis, modified_analysis)
            
            return {
                'scenario_name': template['name'],
                'scenario_description': template['description'],
                'original_clause': {
                    'text': clause.original_text,
                    'risk_level': clause.risk_level,
                    'risk_score': clause.risk_score
                },
                'modifications_applied': modifications,
                'original_analysis': original_analysis,
                'modified_analysis': modified_analysis,
                'impact_analysis': impact_analysis,
                'recommendations': self._generate_recommendations(impact_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error simulating scenario: {e}")
            return {'error': f'Simulation failed: {str(e)}'}
    
    def _analyze_clause_risk(self, clause: Clause) -> Dict:
        """Analyze the risk profile of a clause"""
        risk_factors = {
            'financial_impact': self._assess_financial_impact(clause),
            'legal_complexity': self._assess_legal_complexity(clause),
            'enforcement_risk': self._assess_enforcement_risk(clause),
            'compliance_requirements': self._assess_compliance_risk(clause)
        }
        
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        return {
            'risk_factors': risk_factors,
            'overall_risk': overall_risk,
            'risk_level': clause.risk_level,
            'risk_score': clause.risk_score
        }
    
    def _assess_financial_impact(self, clause: Clause) -> float:
        """Assess financial impact of a clause"""
        text_lower = clause.original_text.lower()
        
        if any(word in text_lower for word in ['penalty', 'fine', 'damages', '$', 'dollar']):
            return 0.8
        elif any(word in text_lower for word in ['cost', 'expense', 'payment', 'fee']):
            return 0.6
        else:
            return 0.3
    
    def _assess_legal_complexity(self, clause: Clause) -> float:
        """Assess legal complexity of a clause"""
        text_lower = clause.original_text.lower()
        
        complex_terms = ['indemnification', 'jurisdiction', 'governing law', 'arbitration']
        if any(term in text_lower for term in complex_terms):
            return 0.8
        elif len(clause.original_text.split()) > 50:
            return 0.6
        else:
            return 0.4
    
    def _assess_enforcement_risk(self, clause: Clause) -> float:
        """Assess enforcement risk of a clause"""
        text_lower = clause.original_text.lower()
        
        if any(word in text_lower for word in ['immediate', 'instant', 'without notice']):
            return 0.9
        elif any(word in text_lower for word in ['reasonable', 'appropriate', 'standard']):
            return 0.5
        else:
            return 0.7
    
    def _assess_compliance_risk(self, clause: Clause) -> float:
        """Assess compliance risk of a clause"""
        text_lower = clause.original_text.lower()
        
        if any(word in text_lower for word in ['compliance', 'regulatory', 'statutory', 'law']):
            return 0.8
        elif any(word in text_lower for word in ['standard', 'industry', 'best practice']):
            return 0.6
        else:
            return 0.4
    
    def _apply_modifications(self, original_analysis: Dict, modifications: Dict) -> Dict:
        """Apply modifications to clause analysis"""
        modified_analysis = original_analysis.copy()
        
        # Apply modification effects
        for param, value in modifications.items():
            if param == 'penalty_amount':
                if value < 1000:  # Reduced penalty
                    modified_analysis['risk_factors']['financial_impact'] *= 0.7
                else:  # Increased penalty
                    modified_analysis['risk_factors']['financial_impact'] *= 1.3
            
            elif param == 'notice_period':
                if value > 30:  # Longer notice period
                    modified_analysis['risk_factors']['enforcement_risk'] *= 0.8
                else:  # Shorter notice period
                    modified_analysis['risk_factors']['enforcement_risk'] *= 1.2
            
            elif param == 'liability_cap':
                if value > 100000:  # Higher liability cap
                    modified_analysis['risk_factors']['financial_impact'] *= 1.4
                else:  # Lower liability cap
                    modified_analysis['risk_factors']['financial_impact'] *= 0.6
        
        # Recalculate overall risk
        modified_analysis['overall_risk'] = sum(modified_analysis['risk_factors'].values()) / len(modified_analysis['risk_factors'])
        
        return modified_analysis
    
    def _calculate_impact(self, original: Dict, modified: Dict) -> Dict:
        """Calculate the impact of modifications"""
        risk_change = modified['overall_risk'] - original['overall_risk']
        risk_change_percentage = (risk_change / original['overall_risk']) * 100 if original['overall_risk'] > 0 else 0
        
        impact_level = 'low'
        if abs(risk_change_percentage) > 30:
            impact_level = 'high'
        elif abs(risk_change_percentage) > 15:
            impact_level = 'medium'
        
        return {
            'risk_change': risk_change,
            'risk_change_percentage': risk_change_percentage,
            'impact_level': impact_level,
            'risk_direction': 'increase' if risk_change > 0 else 'decrease',
            'significant_change': abs(risk_change_percentage) > 15
        }
    
    def _generate_recommendations(self, impact_analysis: Dict) -> List[str]:
        """Generate recommendations based on impact analysis"""
        recommendations = []
        
        if impact_analysis['significant_change']:
            if impact_analysis['risk_direction'] == 'increase':
                recommendations.append("Consider negotiating more favorable terms to reduce risk exposure")
                recommendations.append("Review insurance coverage to ensure adequate protection")
                recommendations.append("Consult with legal counsel before proceeding with modifications")
            else:
                recommendations.append("Modification appears to reduce risk - consider implementing")
                recommendations.append("Monitor for any unintended consequences of changes")
        else:
            recommendations.append("Modification has minimal impact on overall risk profile")
            recommendations.append("Proceed with standard review procedures")
        
        return recommendations

class ClauseLibraryService:
    """Service for managing and comparing legal clauses"""
    
    def __init__(self):
        self.clause_templates = self._load_clause_templates()
        self.best_practices = self._load_best_practices()
    
    def _load_clause_templates(self) -> Dict[str, Dict]:
        """Load standard clause templates"""
        return {
            'indemnification_standard': {
                'name': 'Standard Indemnification Clause',
                'text': 'Party A shall indemnify and hold harmless Party B from and against any and all claims, damages, losses, and expenses...',
                'risk_level': 'medium',
                'best_practice': True,
                'jurisdiction': 'general',
                'industry': 'general'
            },
            'liability_limitation_standard': {
                'name': 'Standard Liability Limitation',
                'text': 'In no event shall either party be liable for any indirect, incidental, special, consequential, or punitive damages...',
                'risk_level': 'low',
                'best_practice': True,
                'jurisdiction': 'general',
                'industry': 'general'
            },
            'termination_standard': {
                'name': 'Standard Termination Clause',
                'text': 'Either party may terminate this agreement upon thirty (30) days written notice to the other party...',
                'risk_level': 'low',
                'best_practice': True,
                'jurisdiction': 'general',
                'industry': 'general'
            }
        }
    
    def _load_best_practices(self) -> Dict[str, List[str]]:
        """Load best practices for different clause types"""
        return {
            'indemnification': [
                'Include specific scope of indemnification',
                'Define exceptions and limitations',
                'Specify notice requirements',
                'Include defense obligations'
            ],
            'liability': [
                'Clearly define damage types',
                'Include reasonable limitations',
                'Specify exclusions',
                'Consider insurance requirements'
            ],
            'termination': [
                'Provide reasonable notice periods',
                'Define termination reasons',
                'Specify post-termination obligations',
                'Include survival clauses'
            ]
        }
    
    def compare_clauses(self, clause1: Clause, clause2: Clause) -> Dict:
        """Compare two clauses and identify differences"""
        try:
            comparison = {
                'clause1': {
                    'id': str(clause1.id),
                    'type': clause1.clause_type,
                    'text': clause1.original_text,
                    'risk_level': clause1.risk_level,
                    'risk_score': clause1.risk_score
                },
                'clause2': {
                    'id': str(clause2.id),
                    'type': clause2.clause_type,
                    'text': clause2.original_text,
                    'risk_level': clause2.risk_level,
                    'risk_score': clause2.risk_score
                },
                'analysis': {}
            }
            
            # Analyze differences
            comparison['analysis'] = {
                'risk_comparison': self._compare_risk_profiles(clause1, clause2),
                'text_similarity': self._calculate_text_similarity(clause1.original_text, clause2.original_text),
                'best_practice_compliance': self._assess_best_practice_compliance(clause1, clause2),
                'recommendations': self._generate_comparison_recommendations(clause1, clause2)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing clauses: {e}")
            return {'error': f'Comparison failed: {str(e)}'}
    
    def _compare_risk_profiles(self, clause1: Clause, clause2: Clause) -> Dict:
        """Compare risk profiles of two clauses"""
        risk1 = clause1.risk_score
        risk2 = clause2.risk_score
        
        risk_difference = risk2 - risk1
        risk_difference_percentage = (risk_difference / risk1) * 100 if risk1 > 0 else 0
        
        return {
            'clause1_risk': risk1,
            'clause2_risk': risk2,
            'risk_difference': risk_difference,
            'risk_difference_percentage': risk_difference_percentage,
            'higher_risk_clause': 'clause2' if risk2 > risk1 else 'clause1' if risk1 > risk2 else 'equal'
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        except ImportError:
            # Fallback similarity calculation
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
    
    def _assess_best_practice_compliance(self, clause1: Clause, clause2: Clause) -> Dict:
        """Assess compliance with best practices"""
        clause_type = clause1.clause_type
        
        if clause_type not in self.best_practices:
            return {'error': f'No best practices available for {clause_type}'}
        
        best_practices = self.best_practices[clause_type]
        
        compliance1 = self._check_practice_compliance(clause1.original_text, best_practices)
        compliance2 = self._check_practice_compliance(clause2.original_text, best_practices)
        
        return {
            'clause1_compliance': compliance1,
            'clause2_compliance': compliance2,
            'best_practices': best_practices,
            'overall_assessment': self._assess_overall_compliance(compliance1, compliance2)
        }
    
    def _check_practice_compliance(self, text: str, practices: List[str]) -> Dict[str, bool]:
        """Check if a clause complies with best practices"""
        compliance = {}
        text_lower = text.lower()
        
        for practice in practices:
            # Simple keyword-based compliance checking
            practice_lower = practice.lower()
            if any(word in text_lower for word in practice_lower.split()):
                compliance[practice] = True
            else:
                compliance[practice] = False
        
        return compliance
    
    def _assess_overall_compliance(self, compliance1: Dict, compliance2: Dict) -> str:
        """Assess overall compliance of two clauses"""
        score1 = sum(compliance1.values()) / len(compliance1) if compliance1 else 0
        score2 = sum(compliance2.values()) / len(compliance2) if compliance2 else 0
        
        if score1 > score2:
            return 'clause1_better'
        elif score2 > score1:
            return 'clause2_better'
        else:
            return 'equal'
    
    def _generate_comparison_recommendations(self, clause1: Clause, clause2: Clause) -> List[str]:
        """Generate recommendations based on clause comparison"""
        recommendations = []
        
        if clause1.risk_score < clause2.risk_score:
            recommendations.append(f"Clause 1 has lower risk ({clause1.risk_score:.2f} vs {clause2.risk_score:.2f})")
            recommendations.append("Consider using Clause 1 as a template for future agreements")
        elif clause2.risk_score < clause1.risk_score:
            recommendations.append(f"Clause 2 has lower risk ({clause2.risk_score:.2f} vs {clause1.risk_score:.2f})")
            recommendations.append("Consider using Clause 2 as a template for future agreements")
        
        if clause1.risk_level != clause2.risk_level:
            recommendations.append(f"Risk levels differ: {clause1.risk_level} vs {clause2.risk_level}")
            recommendations.append("Review both clauses to understand risk differences")
        
        return recommendations
    
    def find_similar_clauses(self, target_clause: Clause, all_clauses: List[Clause], threshold: float = 0.7) -> List[Dict]:
        """Find clauses similar to a target clause"""
        similar_clauses = []
        
        for clause in all_clauses:
            if clause.id == target_clause.id:
                continue
            
            similarity = self._calculate_text_similarity(target_clause.original_text, clause.original_text)
            
            if similarity >= threshold:
                similar_clauses.append({
                    'clause': clause,
                    'similarity_score': similarity,
                    'risk_comparison': self._compare_risk_profiles(target_clause, clause)
                })
        
        # Sort by similarity score
        similar_clauses.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar_clauses[:5]  # Return top 5 similar clauses
    
    def get_clause_recommendations(self, clause: Clause) -> Dict:
        """Get recommendations for improving a clause"""
        try:
            clause_type = clause.clause_type
            
            if clause_type not in self.best_practices:
                return {'error': f'No recommendations available for {clause_type}'}
            
            best_practices = self.best_practices[clause_type]
            current_compliance = self._check_practice_compliance(clause.original_text, best_practices)
            
            missing_practices = [practice for practice, compliant in current_compliance.items() if not compliant]
            
            recommendations = {
                'clause_type': clause_type,
                'current_risk_level': clause.risk_level,
                'current_risk_score': clause.risk_score,
                'best_practices': best_practices,
                'compliance_status': current_compliance,
                'missing_practices': missing_practices,
                'improvement_suggestions': self._generate_improvement_suggestions(clause, missing_practices)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting clause recommendations: {e}")
            return {'error': f'Recommendations generation failed: {str(e)}'}
    
    def _generate_improvement_suggestions(self, clause: Clause, missing_practices: List[str]) -> List[str]:
        """Generate specific suggestions for improving a clause"""
        suggestions = []
        
        for practice in missing_practices:
            if 'scope' in practice.lower():
                suggestions.append("Consider adding specific scope limitations to the clause")
            elif 'notice' in practice.lower():
                suggestions.append("Include clear notice requirements and procedures")
            elif 'limitations' in practice.lower():
                suggestions.append("Add reasonable limitations to prevent excessive exposure")
            elif 'exceptions' in practice.lower():
                suggestions.append("Define specific exceptions to the clause's application")
            elif 'defense' in practice.lower():
                suggestions.append("Include defense obligations and procedures")
        
        return suggestions
