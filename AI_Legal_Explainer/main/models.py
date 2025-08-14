from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid
import os

def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents', filename)

class Document(models.Model):
    """Model for uploaded legal documents"""
    DOCUMENT_TYPES = [
        ('contract', 'Contract'),
        ('agreement', 'Agreement'),
        ('terms', 'Terms of Service'),
        ('policy', 'Privacy Policy'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'txt'])]
    )
    original_text = models.TextField(blank=True)
    processed_text = models.TextField(blank=True)
    file_size = models.BigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"
    
    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

class Clause(models.Model):
    """Model for identified legal clauses"""
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ]
    
    CLAUSE_TYPES = [
        ('penalty', 'Penalty/Fine'),
        ('auto_renewal', 'Auto-Renewal'),
        ('termination', 'Termination'),
        ('indemnification', 'Indemnification'),
        ('liability', 'Liability'),
        ('confidentiality', 'Confidentiality'),
        ('intellectual_property', 'Intellectual Property'),
        ('governing_law', 'Governing Law'),
        ('dispute_resolution', 'Dispute Resolution'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='clauses')
    clause_type = models.CharField(max_length=30, choices=CLAUSE_TYPES, default='other')
    original_text = models.TextField()
    start_position = models.IntegerField()
    end_position = models.IntegerField()
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='low')
    risk_score = models.FloatField(default=0.0)
    plain_language_summary = models.TextField(blank=True)
    risk_explanation = models.TextField(blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_position']
    
    def __str__(self):
        return f"{self.clause_type} - {self.risk_level} risk"

class RiskAnalysis(models.Model):
    """Model for overall risk analysis of documents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='risk_analysis')
    overall_risk_score = models.FloatField(default=0.0)
    overall_risk_level = models.CharField(max_length=10, choices=Clause.RISK_LEVELS, default='low')
    high_risk_clauses_count = models.IntegerField(default=0)
    medium_risk_clauses_count = models.IntegerField(default=0)
    low_risk_clauses_count = models.IntegerField(default=0)
    analysis_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Risk Analysis for {self.document.title}"

class DocumentSummary(models.Model):
    """Model for AI-generated document summaries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='summary')
    plain_language_summary = models.TextField()
    legal_summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list)
    word_count = models.IntegerField(default=0)
    
    # Multilingual support
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    multilingual_summaries = models.JSONField(default=dict)  # Store summaries in all languages
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Summary for {self.document.title} ({self.language})"

class ChatSession(models.Model):
    """Model for Q&A chat sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chat Session {self.session_id} for {self.document.title}"

class ChatMessage(models.Model):
    """Model for individual chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User Question'),
        ('assistant', 'AI Answer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    confidence_score = models.FloatField(null=True, blank=True)
    sources = models.JSONField(default=list)  # List of clause references
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type} message in {self.chat_session.session_id}"

class LegalTerm(models.Model):
    """Model for legal glossary terms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=200, unique=True)
    definition = models.TextField()
    plain_language_explanation = models.TextField()
    examples = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    
    # Multilingual support
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    multilingual_definitions = models.JSONField(default=dict)  # Store definitions in all languages
    multilingual_explanations = models.JSONField(default=dict)  # Store explanations in all languages
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['term']
    
    def __str__(self):
        return f"{self.term} ({self.language})"

class DocumentProcessingLog(models.Model):
    """Model for tracking document processing steps"""
    PROCESSING_STEPS = [
        ('upload', 'Document Upload'),
        ('extraction', 'Text Extraction'),
        ('summarization', 'AI Summarization'),
        ('clause_detection', 'Clause Detection'),
        ('risk_analysis', 'Risk Analysis'),
        ('glossary_processing', 'Glossary Processing'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='processing_logs')
    step = models.CharField(max_length=20, choices=PROCESSING_STEPS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # in seconds
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.step} - {self.status} for {self.document.title}"


class UserLanguagePreference(models.Model):
    """Model for storing user language preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_preferences')
    preferred_language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    fallback_language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    auto_translate = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'preferred_language']
    
    def __str__(self):
        return f"{self.user.username} - {self.preferred_language}"
