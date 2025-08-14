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

class ConnectivityStatus(models.Model):
    """Model for tracking connectivity status and offline mode"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_online = models.BooleanField(default=True)
    last_online_check = models.DateTimeField(auto_now=True)
    offline_since = models.DateTimeField(null=True, blank=True)
    connection_quality = models.CharField(max_length=20, default='good', choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('offline', 'Offline'),
    ])
    api_endpoints_status = models.JSONField(default=dict)  # Status of various API endpoints
    
    class Meta:
        verbose_name_plural = "Connectivity Statuses"
    
    def __str__(self):
        return f"Connectivity: {'Online' if self.is_online else 'Offline'}"

class LocalCache(models.Model):
    """Model for local data caching in offline mode"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cache_key = models.CharField(max_length=255, unique=True)
    cache_data = models.JSONField()
    cache_type = models.CharField(max_length=50, choices=[
        ('document_summary', 'Document Summary'),
        ('clause_analysis', 'Clause Analysis'),
        ('risk_assessment', 'Risk Assessment'),
        ('glossary_term', 'Glossary Term'),
        ('ai_model', 'AI Model'),
        ('user_preferences', 'User Preferences'),
    ])
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    access_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Local Caches"
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['cache_type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.cache_type}: {self.cache_key}"
    
    def is_expired(self):
        """Check if cache entry has expired"""
        if self.expires_at is None:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

class OfflineFeature(models.Model):
    """Model for managing offline feature availability"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feature_name = models.CharField(max_length=100, unique=True)
    is_available_offline = models.BooleanField(default=True)
    requires_internet = models.BooleanField(default=False)
    fallback_mode = models.CharField(max_length=50, blank=True, help_text="Alternative mode when offline")
    local_model_required = models.BooleanField(default=False)
    cache_strategy = models.CharField(max_length=50, default='persistent', choices=[
        ('persistent', 'Persistent Cache'),
        ('temporary', 'Temporary Cache'),
        ('no_cache', 'No Caching'),
    ])
    priority = models.IntegerField(default=5, help_text="Priority for offline mode (1-10)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'feature_name']
    
    def __str__(self):
        return f"{self.feature_name} (Offline: {self.is_available_offline})"

class TransparencyPreference(models.Model):
    """Model for user transparency and explanation detail preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transparency_preferences')
    explanation_detail_level = models.CharField(max_length=20, default='medium', choices=[
        ('very_simple', 'Very Simple'),
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('detailed', 'Detailed'),
        ('legal_detailed', 'Legal Detailed'),
    ])
    show_confidence_scores = models.BooleanField(default=True)
    show_source_citations = models.BooleanField(default=True)
    show_technical_details = models.BooleanField(default=False)
    auto_adjust_complexity = models.BooleanField(default=True)
    preferred_explanation_style = models.CharField(max_length=50, default='conversational', choices=[
        ('conversational', 'Conversational'),
        ('formal', 'Formal'),
        ('technical', 'Technical'),
        ('educational', 'Educational'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'explanation_detail_level']
    
    def __str__(self):
        return f"{self.user.username} - {self.explanation_detail_level}"

class PerformanceMetrics(models.Model):
    """Model for tracking performance metrics and analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics', null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    feature_name = models.CharField(max_length=100)
    operation_type = models.CharField(max_length=50, choices=[
        ('document_upload', 'Document Upload'),
        ('text_extraction', 'Text Extraction'),
        ('ai_summarization', 'AI Summarization'),
        ('clause_detection', 'Clause Detection'),
        ('risk_analysis', 'Risk Analysis'),
        ('chat_query', 'Chat Query'),
        ('glossary_lookup', 'Glossary Lookup'),
        ('offline_operation', 'Offline Operation'),
    ])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_ms = models.FloatField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    resource_usage = models.JSONField(default=dict)  # CPU, memory, network usage
    cache_hit = models.BooleanField(default=False)
    offline_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['feature_name']),
            models.Index(fields=['operation_type']),
            models.Index(fields=['start_time']),
            models.Index(fields=['success']),
        ]
    
    def __str__(self):
        return f"{self.feature_name} - {self.operation_type} ({self.duration_ms}ms)"
    
    def calculate_duration(self):
        """Calculate duration in milliseconds"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_ms = delta.total_seconds() * 1000
            self.save()
        return self.duration_ms

# Phase 4 Models - Security & Compliance

class SecurityAudit(models.Model):
    """Model for tracking security audits and assessments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_type = models.CharField(max_length=50, choices=[
        ('security_scan', 'Security Scan'),
        ('penetration_test', 'Penetration Test'),
        ('vulnerability_assessment', 'Vulnerability Assessment'),
        ('compliance_check', 'Compliance Check'),
        ('code_review', 'Code Review'),
        ('infrastructure_audit', 'Infrastructure Audit'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('remediated', 'Remediated'),
    ])
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ])
    findings = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    remediation_actions = models.TextField(blank=True)
    auditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    next_audit_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['audit_type']),
            models.Index(fields=['status']),
            models.Index(fields=['severity']),
        ]
    
    def __str__(self):
        return f"{self.audit_type} - {self.status} ({self.severity})"

class ComplianceRecord(models.Model):
    """Model for tracking compliance with regulations (GDPR, PDPA, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regulation = models.CharField(max_length=50, choices=[
        ('GDPR', 'General Data Protection Regulation'),
        ('PDPA', 'Personal Data Protection Act'),
        ('CCPA', 'California Consumer Privacy Act'),
        ('LGPD', 'Lei Geral de Proteção de Dados'),
        ('PIPEDA', 'Personal Information Protection and Electronic Documents Act'),
    ])
    compliance_status = models.CharField(max_length=20, choices=[
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partially_compliant', 'Partially Compliant'),
        ('under_review', 'Under Review'),
    ])
    requirements = models.JSONField(default=dict)
    compliance_evidence = models.TextField(blank=True)
    gaps = models.TextField(blank=True)
    action_plan = models.TextField(blank=True)
    last_assessment = models.DateTimeField(auto_now_add=True)
    next_assessment = models.DateTimeField(null=True, blank=True)
    compliance_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-last_assessment']
        unique_together = ['regulation']
    
    def __str__(self):
        return f"{self.regulation} - {self.compliance_status}"

class DataRetentionPolicy(models.Model):
    """Model for managing data retention policies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_type = models.CharField(max_length=100, choices=[
        ('user_data', 'User Data'),
        ('document_data', 'Document Data'),
        ('analytics_data', 'Analytics Data'),
        ('audit_logs', 'Audit Logs'),
        ('system_logs', 'System Logs'),
        ('backup_data', 'Backup Data'),
    ])
    retention_period_days = models.IntegerField(help_text="Number of days to retain data")
    retention_reason = models.TextField(help_text="Legal or business reason for retention")
    disposal_method = models.CharField(max_length=50, choices=[
        ('secure_deletion', 'Secure Deletion'),
        ('anonymization', 'Anonymization'),
        ('archival', 'Archival'),
        ('transfer', 'Transfer to Third Party'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data_type']
        unique_together = ['data_type']
    
    def __str__(self):
        return f"{self.data_type} - {self.retention_period_days} days"

class UserConsent(models.Model):
    """Model for tracking user consent for data processing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=50, choices=[
        ('data_processing', 'Data Processing'),
        ('marketing', 'Marketing Communications'),
        ('analytics', 'Analytics and Tracking'),
        ('third_party', 'Third Party Sharing'),
        ('cookies', 'Cookie Usage'),
        ('location', 'Location Data'),
    ])
    granted = models.BooleanField(default=False)
    consent_text = models.TextField(help_text="Text presented to user for consent")
    consent_version = models.CharField(max_length=20, default='1.0')
    granted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-granted_at']
        unique_together = ['user', 'consent_type', 'consent_version']
    
    def __str__(self):
        status = "Granted" if self.granted else "Revoked"
        return f"{self.user.username} - {self.consent_type} ({status})"

class PrivacyPolicy(models.Model):
    """Model for managing privacy policies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    language = models.CharField(max_length=10, choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    effective_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"Privacy Policy v{self.version} ({self.language}) - {self.effective_date.date()}"

# Phase 4 Models - Testing & Quality Assurance

class TestResult(models.Model):
    """Model for tracking test results and coverage"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=50, choices=[
        ('unit', 'Unit Test'),
        ('integration', 'Integration Test'),
        ('end_to_end', 'End-to-End Test'),
        ('performance', 'Performance Test'),
        ('security', 'Security Test'),
        ('user_acceptance', 'User Acceptance Test'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('error', 'Error'),
    ])
    execution_time = models.FloatField(help_text="Execution time in seconds")
    coverage_percentage = models.FloatField(null=True, blank=True)
    test_output = models.TextField(blank=True)
    error_details = models.TextField(blank=True)
    test_environment = models.CharField(max_length=100, blank=True)
    run_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    run_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-run_at']
        indexes = [
            models.Index(fields=['test_type']),
            models.Index(fields=['status']),
            models.Index(fields=['run_at']),
        ]
    
    def __str__(self):
        return f"{self.test_name} - {self.status} ({self.test_type})"

class QualityMetric(models.Model):
    """Model for tracking quality metrics and KPIs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_name = models.CharField(max_length=100)
    metric_type = models.CharField(max_length=50, choices=[
        ('code_quality', 'Code Quality'),
        ('test_coverage', 'Test Coverage'),
        ('performance', 'Performance'),
        ('security', 'Security'),
        ('usability', 'Usability'),
        ('accessibility', 'Accessibility'),
    ])
    metric_value = models.FloatField()
    target_value = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    measurement_date = models.DateTimeField(auto_now_add=True)
    trend = models.CharField(max_length=20, choices=[
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
        ('unknown', 'Unknown'),
    ])
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-measurement_date']
        indexes = [
            models.Index(fields=['metric_name']),
            models.Index(fields=['metric_type']),
            models.Index(fields=['measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.unit}"

class PerformanceTest(models.Model):
    """Model for tracking performance test results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_name = models.CharField(max_length=200)
    test_scenario = models.CharField(max_length=100)
    load_level = models.CharField(max_length=50, choices=[
        ('low', 'Low Load'),
        ('medium', 'Medium Load'),
        ('high', 'High Load'),
        ('peak', 'Peak Load'),
        ('stress', 'Stress Test'),
    ])
    concurrent_users = models.IntegerField()
    response_time_avg = models.FloatField(help_text="Average response time in milliseconds")
    response_time_p95 = models.FloatField(help_text="95th percentile response time")
    response_time_p99 = models.FloatField(help_text="99th percentile response time")
    throughput = models.FloatField(help_text="Requests per second")
    error_rate = models.FloatField(help_text="Error rate percentage")
    cpu_usage = models.FloatField(help_text="CPU usage percentage")
    memory_usage = models.FloatField(help_text="Memory usage percentage")
    test_duration = models.IntegerField(help_text="Test duration in seconds")
    run_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-run_at']
        indexes = [
            models.Index(fields=['test_scenario']),
            models.Index(fields=['load_level']),
            models.Index(fields=['run_at']),
        ]
    
    def __str__(self):
        return f"{self.test_name} - {self.load_level} ({self.concurrent_users} users)"

class SecurityTest(models.Model):
    """Model for tracking security test results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(max_length=50, choices=[
        ('vulnerability_scan', 'Vulnerability Scan'),
        ('penetration_test', 'Penetration Test'),
        ('code_analysis', 'Code Analysis'),
        ('dependency_check', 'Dependency Check'),
        ('configuration_audit', 'Configuration Audit'),
        ('access_control', 'Access Control Test'),
    ])
    vulnerability_count = models.IntegerField(default=0)
    critical_vulnerabilities = models.IntegerField(default=0)
    high_vulnerabilities = models.IntegerField(default=0)
    medium_vulnerabilities = models.IntegerField(default=0)
    low_vulnerabilities = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    remediation_required = models.BooleanField(default=False)
    test_results = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    run_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-run_at']
        indexes = [
            models.Index(fields=['test_category']),
            models.Index(fields=['run_at']),
        ]
    
    def __str__(self):
        return f"{self.test_name} - {self.test_category} ({self.vulnerability_count} vulnerabilities)"

# Phase 4 Models - Documentation & Training

class Documentation(models.Model):
    """Model for managing project documentation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    doc_type = models.CharField(max_length=50, choices=[
        ('user_guide', 'User Guide'),
        ('api_documentation', 'API Documentation'),
        ('deployment_guide', 'Deployment Guide'),
        ('troubleshooting', 'Troubleshooting Guide'),
        ('faq', 'FAQ'),
        ('changelog', 'Changelog'),
        ('architecture', 'Architecture Documentation'),
    ])
    language = models.CharField(max_length=10, choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    version = models.CharField(max_length=20, default='1.0')
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['doc_type']),
            models.Index(fields=['language']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.doc_type} v{self.version}"

class TrainingMaterial(models.Model):
    """Model for managing user training materials"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    material_type = models.CharField(max_length=50, choices=[
        ('video', 'Video Tutorial'),
        ('interactive', 'Interactive Tutorial'),
        ('step_by_step', 'Step-by-Step Guide'),
        ('cheat_sheet', 'Cheat Sheet'),
        ('best_practices', 'Best Practices'),
        ('case_study', 'Case Study'),
    ])
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ])
    estimated_duration = models.IntegerField(help_text="Estimated duration in minutes")
    language = models.CharField(max_length=10, choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['difficulty_level', 'title']
        indexes = [
            models.Index(fields=['material_type']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['language']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.difficulty_level} ({self.material_type})"

class UserGuide(models.Model):
    """Model for managing user guides and tutorials"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    guide_type = models.CharField(max_length=50, choices=[
        ('getting_started', 'Getting Started'),
        ('feature_guide', 'Feature Guide'),
        ('workflow', 'Workflow Guide'),
        ('troubleshooting', 'Troubleshooting'),
        ('tips_tricks', 'Tips & Tricks'),
        ('advanced_usage', 'Advanced Usage'),
    ])
    target_audience = models.CharField(max_length=50, choices=[
        ('end_user', 'End User'),
        ('administrator', 'Administrator'),
        ('developer', 'Developer'),
        ('business_user', 'Business User'),
    ])
    language = models.CharField(max_length=10, choices=[
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('si', 'Sinhala'),
    ])
    version = models.CharField(max_length=20, default='1.0')
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['guide_type', 'title']
        indexes = [
            models.Index(fields=['guide_type']),
            models.Index(fields=['target_audience']),
            models.Index(fields=['language']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.guide_type} ({self.target_audience})"

class SupportTicket(models.Model):
    """Model for managing support tickets and issues"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    ticket_type = models.CharField(max_length=50, choices=[
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('technical_support', 'Technical Support'),
        ('user_guide', 'User Guide Request'),
        ('billing', 'Billing Issue'),
        ('general', 'General Inquiry'),
    ])
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_for_user', 'Waiting for User'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ])
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['ticket_type']),
        ]
    
    def __str__(self):
        return f"#{self.id} - {self.subject} ({self.status})"

# Phase 4 Models - Launch Preparation

class ProductionEnvironment(models.Model):
    """Model for managing production environment configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    environment_name = models.CharField(max_length=100, unique=True)
    environment_type = models.CharField(max_length=50, choices=[
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
        ('testing', 'Testing'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('decommissioned', 'Decommissioned'),
        ('error', 'Error'),
    ])
    infrastructure_details = models.JSONField(default=dict)
    configuration = models.JSONField(default=dict)
    monitoring_enabled = models.BooleanField(default=True)
    alerting_enabled = models.BooleanField(default=True)
    backup_enabled = models.BooleanField(default=True)
    last_deployment = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['environment_name']
    
    def __str__(self):
        return f"{self.environment_name} - {self.environment_type} ({self.status})"

class MonitoringAlert(models.Model):
    """Model for managing monitoring alerts and notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_name = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=50, choices=[
        ('performance', 'Performance Alert'),
        ('security', 'Security Alert'),
        ('availability', 'Availability Alert'),
        ('error_rate', 'Error Rate Alert'),
        ('resource_usage', 'Resource Usage Alert'),
        ('custom', 'Custom Alert'),
    ])
    severity = models.CharField(max_length=20, choices=[
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ])
    message = models.TextField()
    metric_value = models.FloatField(null=True, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('suppressed', 'Suppressed'),
    ])
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.alert_name} - {self.severity} ({self.status})"

class BackupRecord(models.Model):
    """Model for tracking backup operations and status"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup_name = models.CharField(max_length=200)
    backup_type = models.CharField(max_length=50, choices=[
        ('database', 'Database Backup'),
        ('files', 'File Backup'),
        ('configuration', 'Configuration Backup'),
        ('full_system', 'Full System Backup'),
        ('incremental', 'Incremental Backup'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('verification_pending', 'Verification Pending'),
        ('verified', 'Verified'),
        ('corrupted', 'Corrupted'),
    ])
    file_size_mb = models.FloatField(null=True, blank=True)
    backup_location = models.CharField(max_length=500)
    checksum = models.CharField(max_length=128, blank=True)
    compression_ratio = models.FloatField(null=True, blank=True)
    retention_days = models.IntegerField(default=30)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['backup_type']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.backup_name} - {self.backup_type} ({self.status})"

class UserOnboarding(models.Model):
    """Model for managing user onboarding processes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='onboarding_records')
    onboarding_stage = models.CharField(max_length=50, choices=[
        ('welcome', 'Welcome'),
        ('profile_setup', 'Profile Setup'),
        ('feature_tour', 'Feature Tour'),
        ('first_document', 'First Document'),
        ('training_completed', 'Training Completed'),
        ('onboarding_completed', 'Onboarding Completed'),
    ])
    stage_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)
    help_requests = models.IntegerField(default=0)
    satisfaction_score = models.IntegerField(null=True, blank=True, choices=[
        (1, 'Very Dissatisfied'),
        (2, 'Dissatisfied'),
        (3, 'Neutral'),
        (4, 'Satisfied'),
        (5, 'Very Satisfied'),
    ])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user', 'onboarding_stage']
        unique_together = ['user', 'onboarding_stage']
    
    def __str__(self):
        return f"{self.user.username} - {self.onboarding_stage} ({'Completed' if self.stage_completed else 'Pending'})"
