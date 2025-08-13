from django.contrib import admin
from .models import (
    Document, Clause, RiskAnalysis, DocumentSummary, 
    ChatSession, ChatMessage, LegalTerm, DocumentProcessingLog
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

# Customize admin site
admin.site.site_header = "AI Legal Explainer Administration"
admin.site.site_title = "AI Legal Explainer Admin"
admin.site.index_title = "Welcome to AI Legal Explainer Administration"
