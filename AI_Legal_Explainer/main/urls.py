from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import multilingual_views
from . import enhanced_views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet)
router.register(r'clauses', views.ClauseViewSet)
router.register(r'risk-analysis', views.RiskAnalysisViewSet)
router.register(r'summaries', views.DocumentSummaryViewSet)
router.register(r'chat', views.ChatViewSet, basename='chat')
router.register(r'legal-terms', views.LegalTermViewSet)
router.register(r'processing-logs', views.DocumentProcessingLogViewSet)
router.register(r'multilingual', multilingual_views.MultilingualViewSet, basename='multilingual')

# Enhanced functionality routers
router.register(r'risk-visualization', enhanced_views.RiskVisualizationViewSet, basename='risk_visualization')
router.register(r'what-if-simulation', enhanced_views.WhatIfSimulationViewSet, basename='what_if_simulation')
router.register(r'clause-library', enhanced_views.ClauseLibraryViewSet, basename='clause_library')

app_name = 'main'

urlpatterns = [
    # Traditional Django views
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('test/', views.test, name='test'),
    path('document/<uuid:document_id>/', views.document_detail, name='document_detail'),
    path('document/<uuid:document_id>/status/', views.document_processing_status, name='document_processing_status'),
    path('glossary/', views.glossary_view, name='glossary'),
    path('upload/', views.upload_document, name='upload_document'),
    path('test-upload/', views.test_upload, name='test_upload'),
    path('debug-upload/', views.debug_upload, name='debug_upload'),
    path('simple-upload-test/', views.simple_upload_test, name='simple_upload_test'),
    path('test-upload-page/', views.test_upload_page, name='test_upload_page'),
    
    # Enhanced functionality views
    path('document/<uuid:document_id>/risk-dashboard/', enhanced_views.risk_dashboard_view, name='risk_dashboard'),
    path('clause/<uuid:clause_id>/simulation/', enhanced_views.what_if_simulation_view, name='what_if_simulation'),
    path('clause/<uuid:clause1_id>/compare/<uuid:clause2_id>/', enhanced_views.clause_comparison_view, name='clause_comparison'),
    path('clause-library/', enhanced_views.clause_library_view, name='clause_library'),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Additional API endpoints
    path('api/documents/<uuid:document_id>/process/', views.DocumentViewSet.as_view({'post': 'process'}), name='document_process'),
    path('api/documents/<uuid:document_id>/clauses/', views.DocumentViewSet.as_view({'get': 'clauses'}), name='document_clauses'),
    path('api/documents/<uuid:document_id>/risk-analysis/', views.DocumentViewSet.as_view({'get': 'risk_analysis'}), name='document_risk_analysis'),
    path('api/documents/<uuid:document_id>/summary/', views.DocumentViewSet.as_view({'get': 'summary'}), name='document_summary'),
    
    # Chat endpoints
    path('api/chat/ask/', views.ChatViewSet.as_view({'post': 'ask_question'}), name='chat_ask'),
    path('api/chat/history/', views.ChatViewSet.as_view({'get': 'session_history'}), name='chat_history'),
    
    # Legal terms endpoints
    path('api/legal-terms/search/', views.LegalTermViewSet.as_view({'get': 'search'}), name='legal_terms_search'),
    path('api/legal-terms/highlight/', views.LegalTermViewSet.as_view({'get': 'highlight_text'}), name='legal_terms_highlight'),
    
    # Enhanced functionality AJAX endpoints
    path('api/simulate-scenario/', enhanced_views.ajax_simulate_scenario, name='ajax_simulate_scenario'),
    path('api/compare-clauses/', enhanced_views.ajax_compare_clauses, name='ajax_compare_clauses'),
    
    # Multilingual endpoints
    path('language-switcher/', multilingual_views.language_switcher, name='language_switcher'),
    path('glossary/<str:language>/', multilingual_views.multilingual_glossary, name='multilingual_glossary'),
    path('glossary/', multilingual_views.multilingual_glossary, name='multilingual_glossary_default'),
]
