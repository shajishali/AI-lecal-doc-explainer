from django.contrib import admin
from .models import (
    Document, Clause, RiskAnalysis, DocumentSummary, 
    ChatSession, ChatMessage, LegalTerm, DocumentProcessingLog,
    # Phase 4 Models
    SecurityAudit, ComplianceRecord, DataRetentionPolicy, UserConsent, PrivacyPolicy,
    TestResult, QualityMetric, PerformanceTest, SecurityTest,
    Documentation, TrainingMaterial, UserGuide, SupportTicket,
    ProductionEnvironment, MonitoringAlert, BackupRecord, UserOnboarding
)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'file_size', 'uploaded_at', 'is_processed', 'processed_at']
    list_filter = ['document_type', 'is_processed', 'uploaded_at']
    search_fields = ['title', 'original_text']
    readonly_fields = ['id', 'file_size', 'uploaded_at', 'processed_at']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'document_type', 'file')
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'processed_at')
        }),
        ('Content', {
            'fields': ('original_text', 'processed_text'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'file_size', 'uploaded_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ['clause_type', 'risk_level', 'risk_score', 'document', 'detected_at']
    list_filter = ['clause_type', 'risk_level', 'detected_at']
    search_fields = ['original_text', 'document__title']
    readonly_fields = ['id', 'detected_at']
    date_hierarchy = 'detected_at'
    
    fieldsets = (
        ('Clause Information', {
            'fields': ('clause_type', 'document', 'risk_level', 'risk_score')
        }),
        ('Content', {
            'fields': ('original_text', 'start_position', 'end_position')
        }),
        ('Analysis', {
            'fields': ('plain_language_summary', 'risk_explanation')
        }),
        ('Metadata', {
            'fields': ('id', 'detected_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(RiskAnalysis)
class RiskAnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'overall_risk_level', 'overall_risk_score', 'high_risk_clauses_count', 'created_at']
    list_filter = ['overall_risk_level', 'created_at']
    search_fields = ['document__title', 'analysis_summary']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Document', {
            'fields': ('document',)
        }),
        ('Risk Assessment', {
            'fields': ('overall_risk_level', 'overall_risk_score')
        }),
        ('Clause Counts', {
            'fields': ('high_risk_clauses_count', 'medium_risk_clauses_count', 'low_risk_clauses_count')
        }),
        ('Analysis', {
            'fields': ('analysis_summary',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(DocumentSummary)
class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ['document', 'word_count', 'generated_at']
    list_filter = ['generated_at']
    search_fields = ['document__title', 'plain_language_summary']
    readonly_fields = ['id', 'generated_at']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Document', {
            'fields': ('document',)
        }),
        ('Summary Content', {
            'fields': ('plain_language_summary', 'legal_summary', 'key_points')
        }),
        ('Metadata', {
            'fields': ('word_count', 'id', 'generated_at')
        })
    )

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'document', 'created_at', 'last_activity', 'messages_count']
    list_filter = ['created_at', 'last_activity']
    search_fields = ['session_id', 'document__title']
    readonly_fields = ['id', 'created_at', 'last_activity']
    date_hierarchy = 'created_at'
    
    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = 'Messages'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['chat_session', 'message_type', 'content_preview', 'confidence_score', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['content', 'chat_session__session_id']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(LegalTerm)
class LegalTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'category', 'created_at', 'updated_at']
    list_filter = ['category', 'created_at']
    search_fields = ['term', 'definition', 'plain_language_explanation']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Term Information', {
            'fields': ('term', 'category')
        }),
        ('Definitions', {
            'fields': ('definition', 'plain_language_explanation', 'examples')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(DocumentProcessingLog)
class DocumentProcessingLogAdmin(admin.ModelAdmin):
    list_display = ['document', 'step', 'status', 'started_at', 'completed_at', 'processing_time']
    list_filter = ['step', 'status', 'started_at']
    search_fields = ['document__title', 'error_message']
    readonly_fields = ['id', 'started_at', 'completed_at']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Processing Information', {
            'fields': ('document', 'step', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'processing_time')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )

# Phase 4 Admin Models

@admin.register(SecurityAudit)
class SecurityAuditAdmin(admin.ModelAdmin):
    list_display = ['audit_type', 'status', 'severity', 'auditor', 'started_at', 'completed_at']
    list_filter = ['audit_type', 'status', 'severity', 'started_at']
    search_fields = ['audit_type', 'findings', 'recommendations']
    readonly_fields = ['id', 'started_at']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Audit Information', {
            'fields': ('audit_type', 'status', 'severity', 'auditor')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'next_audit_date')
        }),
        ('Results', {
            'fields': ('findings', 'recommendations', 'remediation_actions'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )

@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ['regulation', 'compliance_status', 'last_assessment', 'next_assessment', 'compliance_officer']
    list_filter = ['regulation', 'compliance_status', 'last_assessment']
    search_fields = ['regulation', 'compliance_evidence', 'gaps']
    readonly_fields = ['id', 'last_assessment']
    date_hierarchy = 'last_assessment'
    
    fieldsets = (
        ('Compliance Information', {
            'fields': ('regulation', 'compliance_status', 'compliance_officer')
        }),
        ('Assessment', {
            'fields': ('last_assessment', 'next_assessment')
        }),
        ('Details', {
            'fields': ('requirements', 'compliance_evidence', 'gaps', 'action_plan'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )

@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ['data_type', 'retention_period_days', 'disposal_method', 'is_active', 'created_at']
    list_filter = ['data_type', 'disposal_method', 'is_active', 'created_at']
    search_fields = ['data_type', 'retention_reason']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('data_type', 'retention_period_days', 'disposal_method')
        }),
        ('Details', {
            'fields': ('retention_reason', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ['user', 'consent_type', 'granted', 'consent_version', 'granted_at', 'revoked_at']
    list_filter = ['consent_type', 'granted', 'consent_version', 'granted_at']
    search_fields = ['user__username', 'user__email', 'consent_type']
    readonly_fields = ['id', 'granted_at', 'revoked_at']
    date_hierarchy = 'granted_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'consent_type', 'consent_version')
        }),
        ('Consent Status', {
            'fields': ('granted', 'granted_at', 'revoked_at')
        }),
        ('Details', {
            'fields': ('consent_text', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['version', 'title', 'language', 'effective_date', 'is_active', 'created_by']
    list_filter = ['version', 'language', 'is_active', 'effective_date']
    search_fields = ['title', 'content', 'version']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('version', 'title', 'language', 'effective_date', 'is_active')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'test_type', 'status', 'execution_time', 'coverage_percentage', 'run_by', 'run_at']
    list_filter = ['test_type', 'status', 'run_at']
    search_fields = ['test_name', 'test_output', 'error_details']
    readonly_fields = ['id', 'run_at']
    date_hierarchy = 'run_at'
    
    fieldsets = (
        ('Test Information', {
            'fields': ('test_name', 'test_type', 'status', 'run_by')
        }),
        ('Results', {
            'fields': ('execution_time', 'coverage_percentage', 'test_output')
        }),
        ('Error Details', {
            'fields': ('error_details', 'test_environment'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'run_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(QualityMetric)
class QualityMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'metric_type', 'metric_value', 'target_value', 'unit', 'trend', 'measurement_date']
    list_filter = ['metric_type', 'trend', 'measurement_date']
    search_fields = ['metric_name', 'notes']
    readonly_fields = ['id', 'measurement_date']
    date_hierarchy = 'measurement_date'
    
    fieldsets = (
        ('Metric Information', {
            'fields': ('metric_name', 'metric_type', 'metric_value', 'target_value', 'unit')
        }),
        ('Analysis', {
            'fields': ('trend', 'notes')
        }),
        ('Metadata', {
            'fields': ('id', 'measurement_date'),
            'classes': ('collapse',)
        })
    )

@admin.register(PerformanceTest)
class PerformanceTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'test_scenario', 'load_level', 'concurrent_users', 'response_time_avg', 'run_at']
    list_filter = ['test_scenario', 'load_level', 'run_at']
    search_fields = ['test_name', 'test_scenario']
    readonly_fields = ['id', 'run_at']
    date_hierarchy = 'run_at'
    
    fieldsets = (
        ('Test Information', {
            'fields': ('test_name', 'test_scenario', 'load_level', 'concurrent_users')
        }),
        ('Performance Results', {
            'fields': ('response_time_avg', 'response_time_p95', 'response_time_p99', 'throughput')
        }),
        ('System Metrics', {
            'fields': ('error_rate', 'cpu_usage', 'memory_usage', 'test_duration'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'run_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SecurityTest)
class SecurityTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'test_category', 'vulnerability_count', 'critical_vulnerabilities', 'run_at']
    list_filter = ['test_category', 'run_at']
    search_fields = ['test_name', 'recommendations']
    readonly_fields = ['id', 'run_at']
    date_hierarchy = 'run_at'
    
    fieldsets = (
        ('Test Information', {
            'fields': ('test_name', 'test_category')
        }),
        ('Vulnerability Counts', {
            'fields': ('vulnerability_count', 'critical_vulnerabilities', 'high_vulnerabilities', 'medium_vulnerabilities', 'low_vulnerabilities')
        }),
        ('Results', {
            'fields': ('false_positives', 'remediation_required', 'test_results', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'run_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ['title', 'doc_type', 'language', 'version', 'is_published', 'created_by', 'created_at']
    list_filter = ['doc_type', 'language', 'is_published', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Documentation Information', {
            'fields': ('title', 'doc_type', 'language', 'version', 'is_published')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(TrainingMaterial)
class TrainingMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'material_type', 'difficulty_level', 'estimated_duration', 'language', 'is_active', 'created_by']
    list_filter = ['material_type', 'difficulty_level', 'language', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Training Information', {
            'fields': ('title', 'material_type', 'difficulty_level', 'estimated_duration', 'language', 'is_active')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(UserGuide)
class UserGuideAdmin(admin.ModelAdmin):
    list_display = ['title', 'guide_type', 'target_audience', 'language', 'version', 'is_published', 'created_by']
    list_filter = ['guide_type', 'target_audience', 'language', 'is_published', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Guide Information', {
            'fields': ('title', 'guide_type', 'target_audience', 'language', 'version', 'is_published')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'ticket_type', 'priority', 'status', 'assigned_to', 'created_at']
    list_filter = ['ticket_type', 'priority', 'status', 'created_at']
    search_fields = ['subject', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('user', 'subject', 'ticket_type', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Content', {
            'fields': ('description', 'resolution'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )

@admin.register(ProductionEnvironment)
class ProductionEnvironmentAdmin(admin.ModelAdmin):
    list_display = ['environment_name', 'environment_type', 'status', 'monitoring_enabled', 'backup_enabled', 'last_deployment']
    list_filter = ['environment_type', 'status', 'monitoring_enabled', 'backup_enabled']
    search_fields = ['environment_name', 'infrastructure_details']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Environment Information', {
            'fields': ('environment_name', 'environment_type', 'status')
        }),
        ('Configuration', {
            'fields': ('infrastructure_details', 'configuration'),
            'classes': ('collapse',)
        }),
        ('Features', {
            'fields': ('monitoring_enabled', 'alerting_enabled', 'backup_enabled')
        }),
        ('Deployment', {
            'fields': ('last_deployment',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(MonitoringAlert)
class MonitoringAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_name', 'alert_type', 'severity', 'status', 'created_at', 'acknowledged_by']
    list_filter = ['alert_type', 'severity', 'status', 'created_at']
    search_fields = ['alert_name', 'message']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_name', 'alert_type', 'severity', 'status')
        }),
        ('Details', {
            'fields': ('message', 'metric_value', 'threshold_value')
        }),
        ('Resolution', {
            'fields': ('acknowledged_by', 'acknowledged_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ['backup_name', 'backup_type', 'status', 'file_size_mb', 'retention_days', 'started_at', 'completed_at']
    list_filter = ['backup_type', 'status', 'started_at']
    search_fields = ['backup_name', 'backup_location', 'notes']
    readonly_fields = ['id', 'started_at']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Backup Information', {
            'fields': ('backup_name', 'backup_type', 'status')
        }),
        ('Details', {
            'fields': ('file_size_mb', 'backup_location', 'checksum', 'compression_ratio')
        }),
        ('Retention', {
            'fields': ('retention_days', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'verified_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )

@admin.register(UserOnboarding)
class UserOnboardingAdmin(admin.ModelAdmin):
    list_display = ['user', 'onboarding_stage', 'stage_completed', 'completion_date', 'time_spent_minutes', 'satisfaction_score']
    list_filter = ['onboarding_stage', 'stage_completed', 'satisfaction_score', 'created_at']
    search_fields = ['user__username', 'user__email', 'onboarding_stage']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'onboarding_stage', 'stage_completed')
        }),
        ('Progress', {
            'fields': ('completion_date', 'time_spent_minutes', 'help_requests')
        }),
        ('Feedback', {
            'fields': ('satisfaction_score', 'feedback'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# Customize admin site
admin.site.site_header = "AI Legal Explainer Administration"
admin.site.site_title = "AI Legal Explainer Admin"
admin.site.index_title = "Welcome to AI Legal Explainer Administration"
