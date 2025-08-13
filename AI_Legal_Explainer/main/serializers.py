from rest_framework import serializers
from .models import (
    Document, Clause, RiskAnalysis, DocumentSummary, 
    ChatSession, ChatMessage, LegalTerm, DocumentProcessingLog
)

class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    clauses_count = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'file', 'file_size',
            'uploaded_at', 'processed_at', 'is_processed',
            'clauses_count', 'risk_level'
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_at', 'processed_at', 'is_processed']
    
    def get_clauses_count(self, obj):
        return obj.clauses.count()
    
    def get_risk_level(self, obj):
        if hasattr(obj, 'risk_analysis'):
            return obj.risk_analysis.overall_risk_level
        return 'unknown'

class ClauseSerializer(serializers.ModelSerializer):
    """Serializer for Clause model"""
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    clause_type_display = serializers.CharField(source='get_clause_type_display', read_only=True)
    
    class Meta:
        model = Clause
        fields = [
            'id', 'document', 'clause_type', 'clause_type_display',
            'original_text', 'start_position', 'end_position',
            'risk_level', 'risk_level_display', 'risk_score',
            'plain_language_summary', 'risk_explanation', 'detected_at'
        ]
        read_only_fields = ['id', 'detected_at']

class RiskAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for RiskAnalysis model"""
    risk_level_display = serializers.CharField(source='get_overall_risk_level_display', read_only=True)
    
    class Meta:
        model = RiskAnalysis
        fields = [
            'id', 'document', 'overall_risk_score', 'overall_risk_level',
            'risk_level_display', 'high_risk_clauses_count',
            'medium_risk_clauses_count', 'low_risk_clauses_count',
            'analysis_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DocumentSummarySerializer(serializers.ModelSerializer):
    """Serializer for DocumentSummary model"""
    class Meta:
        model = DocumentSummary
        fields = [
            'id', 'document', 'plain_language_summary', 'legal_summary',
            'key_points', 'word_count', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession model"""
    messages_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'document', 'session_id', 'created_at',
            'last_activity', 'messages_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']
    
    def get_messages_count(self, obj):
        return obj.messages.count()

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model"""
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'chat_session', 'message_type', 'message_type_display',
            'content', 'confidence_score', 'sources', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class LegalTermSerializer(serializers.ModelSerializer):
    """Serializer for LegalTerm model"""
    class Meta:
        model = LegalTerm
        fields = [
            'id', 'term', 'definition', 'plain_language_explanation',
            'examples', 'category', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DocumentProcessingLogSerializer(serializers.ModelSerializer):
    """Serializer for DocumentProcessingLog model"""
    step_display = serializers.CharField(source='get_step_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DocumentProcessingLog
        fields = [
            'id', 'document', 'step', 'step_display', 'status',
            'status_display', 'started_at', 'completed_at',
            'error_message', 'processing_time'
        ]
        read_only_fields = ['id', 'started_at']

class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload"""
    class Meta:
        model = Document
        fields = ['title', 'document_type', 'file']

class DocumentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Document with related data"""
    clauses = ClauseSerializer(many=True, read_only=True)
    risk_analysis = RiskAnalysisSerializer(read_only=True)
    summary = DocumentSummarySerializer(read_only=True)
    processing_logs = DocumentProcessingLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'file', 'original_text',
            'processed_text', 'file_size', 'uploaded_at', 'processed_at',
            'is_processed', 'clauses', 'risk_analysis', 'summary', 'processing_logs'
        ]

class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat requests"""
    question = serializers.CharField(max_length=1000)
    session_id = serializers.CharField(max_length=100, required=False)

class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    answer = serializers.CharField()
    confidence_score = serializers.FloatField()
    sources = serializers.ListField(child=serializers.CharField())
    session_id = serializers.CharField()
