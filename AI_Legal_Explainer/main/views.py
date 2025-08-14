from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
import json
import uuid
import os
from datetime import datetime
import logging

from .models import (
    Document, Clause, RiskAnalysis, DocumentSummary, 
    ChatSession, ChatMessage, LegalTerm, DocumentProcessingLog
)
from .serializers import (
    DocumentSerializer, ClauseSerializer, RiskAnalysisSerializer,
    DocumentSummarySerializer, ChatSessionSerializer, ChatMessageSerializer,
    LegalTermSerializer, DocumentProcessingLogSerializer,
    DocumentUploadSerializer, DocumentDetailSerializer,
    ChatRequestSerializer, ChatResponseSerializer
)
from .ai_services import (
    DocumentProcessor, AISummarizer, ClauseDetector, 
    RiskAnalyzer, ChatService, GlossaryService
)

logger = logging.getLogger(__name__)

# Traditional Django views
def welcome(request):
    """Welcome page for AI_Legal_Explainer"""
    return render(request, 'main/welcome.html')

def home(request):
    """Home page for the application"""
    return render(request, 'main/home.html')

def test(request):
    """Simple test view to verify the app is working"""
    return HttpResponse("<h1>AI Legal Explainer is working! 🎉</h1><p>Django is running successfully.</p>")

def signup(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Basic validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'All fields are required.')
            return render(request, 'main/signup.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/signup.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'main/signup.html')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'main/signup.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'main/signup.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Log the user in
            user = authenticate(username=username, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {username}! Your account has been created successfully.')
                return redirect('main:home')
            else:
                messages.error(request, 'Account created but login failed. Please try logging in.')
                return redirect('main:login')
                
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'main/signup.html')
    
    return render(request, 'main/signup.html')

# REST API Viewsets
class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document model"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        elif self.action == 'create':
            return DocumentUploadSerializer
        return DocumentSerializer
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process uploaded document with AI analysis"""
        document = self.get_object()
        
        try:
            # Start processing log
            processing_log = DocumentProcessingLog.objects.create(
                document=document,
                step='upload',
                status='processing'
            )
            
            # Extract text from document
            processor = DocumentProcessor()
            original_text = processor.extract_text(document)
            processed_text = processor.preprocess_text(original_text)
            
            # Update document with extracted text
            document.original_text = original_text
            document.processed_text = processed_text
            document.is_processed = True
            document.processed_at = datetime.now()
            document.save()
            
            # Update processing log
            processing_log.status = 'completed'
            processing_log.completed_at = datetime.now()
            processing_log.save()
            
            # Generate summary
            summary_log = DocumentProcessingLog.objects.create(
                document=document,
                step='summarization',
                status='processing'
            )
            
            summarizer = AISummarizer()
            summary_data = summarizer.generate_summary(processed_text)
            
            # Create or update document summary
            summary, created = DocumentSummary.objects.get_or_create(
                document=document,
                defaults=summary_data
            )
            if not created:
                for key, value in summary_data.items():
                    setattr(summary, key, value)
                summary.save()
            
            summary_log.status = 'completed'
            summary_log.completed_at = datetime.now()
            summary_log.save()
            
            # Detect clauses
            clause_log = DocumentProcessingLog.objects.create(
                document=document,
                step='clause_detection',
                status='processing'
            )
            
            clause_detector = ClauseDetector()
            detected_clauses = clause_detector.detect_clauses(processed_text)
            
            # Create clause objects
            for clause_data in detected_clauses:
                Clause.objects.create(
                    document=document,
                    **clause_data
                )
            
            clause_log.status = 'completed'
            clause_log.completed_at = datetime.now()
            clause_log.save()
            
            # Analyze risk
            risk_log = DocumentProcessingLog.objects.create(
                document=document,
                step='risk_analysis',
                status='processing'
            )
            
            risk_analyzer = RiskAnalyzer()
            risk_data = risk_analyzer.analyze_document_risk(detected_clauses)
            
            # Create or update risk analysis
            risk_analysis, created = RiskAnalysis.objects.get_or_create(
                document=document,
                defaults=risk_data
            )
            if not created:
                for key, value in risk_data.items():
                    setattr(risk_analysis, key, value)
                risk_analysis.save()
            
            risk_log.status = 'completed'
            risk_log.completed_at = datetime.now()
            risk_log.save()
            
            # Glossary processing
            glossary_log = DocumentProcessingLog.objects.create(
                document=document,
                step='glossary_processing',
                status='processing'
            )
            
            # Highlight legal terms in processed text
            glossary_service = GlossaryService()
            highlighted_text = glossary_service.highlight_terms_in_text(processed_text)
            
            # Update document with highlighted text
            document.processed_text = highlighted_text
            document.save()
            
            glossary_log.status = 'completed'
            glossary_log.completed_at = datetime.now()
            glossary_log.save()
            
            return Response({
                'message': 'Document processed successfully',
                'document_id': document.id,
                'clauses_detected': len(detected_clauses),
                'risk_level': risk_data['overall_risk_level']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            
            # Update processing log with error
            if 'processing_log' in locals():
                processing_log.status = 'failed'
                processing_log.error_message = str(e)
                processing_log.completed_at = datetime.now()
                processing_log.save()
            
            return Response({
                'error': 'Document processing failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def clauses(self, request, pk=None):
        """Get all clauses for a document"""
        document = self.get_object()
        clauses = document.clauses.all()
        serializer = ClauseSerializer(clauses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def risk_analysis(self, request, pk=None):
        """Get risk analysis for a document"""
        document = self.get_object()
        try:
            risk_analysis = document.risk_analysis
            serializer = RiskAnalysisSerializer(risk_analysis)
            return Response(serializer.data)
        except RiskAnalysis.DoesNotExist:
            return Response({
                'message': 'Risk analysis not available for this document'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get document summary"""
        document = self.get_object()
        try:
            summary = document.summary
            serializer = DocumentSummarySerializer(summary)
            return Response(serializer.data)
        except DocumentSummary.DoesNotExist:
            return Response({
                'message': 'Summary not available for this document'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        """Custom delete method to handle file cleanup and related data"""
        document = self.get_object()
        
        try:
            # Get the file path before deleting the document
            file_path = document.file.path if document.file else None
            
            # Delete the document (this will cascade delete related objects)
            document.delete()
            
            # Clean up the physical file if it exists
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Physical file deleted: {file_path}")
                except OSError as e:
                    logger.warning(f"Could not delete physical file {file_path}: {e}")
            
            return Response({
                'message': 'Document and all related data deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting document {document.id}: {str(e)}")
            return Response({
                'error': 'Failed to delete document',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClauseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Clause model"""
    queryset = Clause.objects.all()
    serializer_class = ClauseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Clause.objects.all()
        document_id = self.request.query_params.get('document', None)
        risk_level = self.request.query_params.get('risk_level', None)
        
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        return queryset

class RiskAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for RiskAnalysis model"""
    queryset = RiskAnalysis.objects.all()
    serializer_class = RiskAnalysisSerializer
    permission_classes = [AllowAny]

class DocumentSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DocumentSummary model"""
    queryset = DocumentSummary.objects.all()
    serializer_class = DocumentSummarySerializer
    permission_classes = [AllowAny]

class ChatViewSet(viewsets.ViewSet):
    """ViewSet for Chat functionality"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def ask_question(self, request):
        """Ask a question about a document"""
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data['question']
            session_id = serializer.validated_data.get('session_id')
            document_id = request.data.get('document_id')
            
            try:
                document = Document.objects.get(id=document_id)
                
                # Get or create chat session
                if session_id:
                    chat_session, created = ChatSession.objects.get_or_create(
                        session_id=session_id,
                        document=document
                    )
                else:
                    session_id = str(uuid.uuid4())
                    chat_session = ChatSession.objects.create(
                        session_id=session_id,
                        document=document
                    )
                
                # Create user message
                ChatMessage.objects.create(
                    chat_session=chat_session,
                    message_type='user',
                    content=question
                )
                
                # Generate AI answer
                chat_service = ChatService()
                document_context = document.processed_text or document.original_text
                clauses = list(document.clauses.all().values())
                
                answer_data = chat_service.generate_answer(
                    question, document_context, clauses
                )
                
                # Create AI message
                ChatMessage.objects.create(
                    chat_session=chat_session,
                    message_type='assistant',
                    content=answer_data['answer'],
                    confidence_score=answer_data['confidence_score'],
                    sources=answer_data['sources']
                )
                
                return Response({
                    'answer': answer_data['answer'],
                    'confidence_score': answer_data['confidence_score'],
                    'sources': answer_data['sources'],
                    'session_id': session_id
                })
                
            except Document.DoesNotExist:
                return Response({
                    'error': 'Document not found'
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error in chat: {str(e)}")
                return Response({
                    'error': 'Failed to process question',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def session_history(self, request):
        """Get chat history for a session"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({
                'error': 'Session ID required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
            messages = chat_session.messages.all()
            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response({
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)

class LegalTermViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for LegalTerm model"""
    queryset = LegalTerm.objects.all()
    serializer_class = LegalTermSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search for legal terms"""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        
        glossary_service = GlossaryService()
        matching_terms = glossary_service.search_terms(query)
        return Response(matching_terms)
    
    @action(detail=False, methods=['get'])
    def highlight_text(self, request):
        """Highlight legal terms in text"""
        text = request.query_params.get('text', '')
        if not text:
            return Response({'text': ''})
        
        glossary_service = GlossaryService()
        highlighted_text = glossary_service.highlight_terms_in_text(text)
        return Response({'text': highlighted_text})

class DocumentProcessingLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DocumentProcessingLog model"""
    queryset = DocumentProcessingLog.objects.all()
    serializer_class = DocumentProcessingLogSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = DocumentProcessingLog.objects.all()
        document_id = self.request.query_params.get('document', None)
        
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        
        return queryset

# Additional utility views
def upload_document(request):
    """Handle document upload via traditional form"""
    if request.method == 'POST':
        try:
            # Log the request data for debugging
            logger.info(f'Upload request received - Method: {request.method}')
            logger.info(f'Upload request received - Content-Type: {request.content_type}')
            logger.info(f'Upload request received - POST data: {dict(request.POST)}')
            logger.info(f'Upload request received - FILES data: {dict(request.FILES)}')
            logger.info(f'Upload request received - FILES keys: {list(request.FILES.keys())}')
            logger.info(f'Request headers: {dict(request.headers)}')
            logger.info(f'Request META: {dict(request.META)}')
            
            # Check if request.FILES is empty
            if not request.FILES:
                logger.error('Upload failed: request.FILES is empty')
                logger.error(f'Request content type: {request.content_type}')
                logger.error(f'Request headers: {dict(request.headers)}')
                logger.error(f'Request META: {dict(request.META)}')

                
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'No file provided. Please select a file to upload.')
                return redirect('main:home')
            
            # Get form data with proper validation
            title = request.POST.get('title', '').strip()
            document_type = request.POST.get('document_type', '').strip()
            file = request.FILES.get('file')
            
            logger.info(f'Extracted data - Title: "{title}", Type: "{document_type}", File: {file}')
            
            # Validate required fields
            if not title:
                logger.warning('Upload failed: Missing title')
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'Document title is required.')
                return redirect('main:home')
            
            if not document_type:
                logger.warning('Upload failed: Missing document type')
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'Document type is required.')
                return redirect('main:home')
            
            if not file:
                logger.warning('Upload failed: No file provided')
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'No file provided.')
                return redirect('main:home')
            
            # Validate file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                logger.warning(f'Upload failed: File size {file.size} exceeds 10MB limit')
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'File size exceeds 10MB limit.')
                return redirect('main:home')
            
            # Validate file extension
            allowed_extensions = ['pdf', 'docx', 'txt']
            file_extension = file.name.split('.')[-1].lower()
            logger.info(f'File extension: {file_extension}')
            
            if file_extension not in allowed_extensions:
                logger.warning(f'Upload failed: Invalid file extension {file_extension}')
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, f'File type not supported. Allowed: {", ".join(allowed_extensions)}')
                return redirect('main:home')
            
            # Validate document type choices
            valid_document_types = ['contract', 'agreement', 'terms', 'policy', 'other']
            if document_type not in valid_document_types:
                logger.warning(f'Upload failed: Invalid document type {document_type}')
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, f'Invalid document type. Allowed: {", ".join(valid_document_types)}')
                return redirect('main:home')
            
            # Create document with proper error handling
            try:
                # Validate the data before creating the model
                from django.core.exceptions import ValidationError
                
                # Create a temporary document instance to validate
                temp_document = Document(
                    title=title,
                    document_type=document_type,
                    file=file
                )
                
                # Validate the model
                temp_document.full_clean()
                
                # If validation passes, save the document
                document = temp_document
                document.save()
                
                logger.info(f'Document uploaded successfully: {document.id} - {title}')
                
                # 🔥 NEW: Trigger AI processing after successful upload
                try:
                    logger.info(f'Starting AI processing for document {document.id}')
                    
                    # Start processing log
                    processing_log = DocumentProcessingLog.objects.create(
                        document=document,
                        step='upload',
                        status='processing'
                    )
                    logger.info(f'Created processing log: {processing_log.id}')
                    
                    # Extract text from document
                    logger.info(f'Extracting text from document {document.id}')
                    processor = DocumentProcessor()
                    original_text = processor.extract_text(document)
                    logger.info(f'Extracted {len(original_text)} characters from document')
                    
                    processed_text = processor.preprocess_text(original_text)
                    logger.info(f'Preprocessed text: {len(processed_text)} characters')
                    
                    # Update document with extracted text
                    document.original_text = original_text
                    document.processed_text = processed_text
                    document.is_processed = True
                    document.processed_at = datetime.now()
                    document.save()
                    logger.info(f'Updated document {document.id} with extracted text')
                    
                    # Update processing log
                    processing_log.status = 'completed'
                    processing_log.completed_at = datetime.now()
                    processing_log.save()
                    logger.info(f'Completed text extraction step')
                    
                    # Generate summary
                    logger.info(f'Starting summary generation for document {document.id}')
                    summary_log = DocumentProcessingLog.objects.create(
                        document=document,
                        step='summarization',
                        status='processing'
                    )
                    
                    summarizer = AISummarizer()
                    summary_data = summarizer.generate_summary(processed_text)
                    logger.info(f'Generated summary with {summary_data.get("word_count", 0)} words')
                    
                    # Create or update document summary
                    summary, created = DocumentSummary.objects.get_or_create(
                        document=document,
                        defaults=summary_data
                    )
                    if not created:
                        for key, value in summary_data.items():
                            setattr(summary, key, value)
                        summary.save()
                    
                    summary_log.status = 'completed'
                    summary_log.completed_at = datetime.now()
                    summary_log.save()
                    logger.info(f'Completed summary generation step')
                    
                    # Detect clauses
                    logger.info(f'Starting clause detection for document {document.id}')
                    clause_log = DocumentProcessingLog.objects.create(
                        document=document,
                        step='clause_detection',
                        status='processing'
                    )
                    
                    clause_detector = ClauseDetector()
                    detected_clauses = clause_detector.detect_clauses(processed_text)
                    logger.info(f'Detected {len(detected_clauses)} clauses')
                    
                    # Create clause objects
                    for clause_data in detected_clauses:
                        Clause.objects.create(
                            document=document,
                            **clause_data
                        )
                    
                    clause_log.status = 'completed'
                    clause_log.completed_at = datetime.now()
                    clause_log.save()
                    logger.info(f'Completed clause detection step')
                    
                    # Analyze risk
                    logger.info(f'Starting risk analysis for document {document.id}')
                    risk_log = DocumentProcessingLog.objects.create(
                        document=document,
                        step='risk_analysis',
                        status='processing'
                    )
                    
                    risk_analyzer = RiskAnalyzer()
                    risk_data = risk_analyzer.analyze_document_risk(detected_clauses)
                    logger.info(f'Risk analysis completed: {risk_data.get("overall_risk_level", "unknown")} risk')
                    
                    # Create or update risk analysis
                    risk_analysis, created = RiskAnalysis.objects.get_or_create(
                        document=document,
                        defaults=risk_data
                    )
                    if not created:
                        for key, value in risk_data.items():
                            setattr(risk_analysis, key, value)
                        risk_analysis.save()
                    
                    risk_log.status = 'completed'
                    risk_log.completed_at = datetime.now()
                    risk_log.save()
                    logger.info(f'Completed risk analysis step')
                    
                    # Glossary processing
                    logger.info(f'Starting glossary processing for document {document.id}')
                    glossary_log = DocumentProcessingLog.objects.create(
                        document=document,
                        step='glossary_processing',
                        status='processing'
                    )
                    
                    # Highlight legal terms in processed text
                    glossary_service = GlossaryService()
                    highlighted_text = glossary_service.highlight_terms_in_text(processed_text)
                    
                    # Update document with highlighted text
                    document.processed_text = highlighted_text
                    document.save()
                    
                    glossary_log.status = 'completed'
                    glossary_log.completed_at = datetime.now()
                    glossary_log.save()
                    logger.info(f'Completed glossary processing step')
                    
                    logger.info(f'AI processing completed successfully for document {document.id}')
                    
                    # Redirect to document detail page with success message
                    from django.shortcuts import redirect
                    from django.contrib import messages
                    
                    messages.success(request, f'Document "{title}" uploaded and analyzed successfully!')
                    return redirect('main:document_detail', document_id=document.id)
                    
                except Exception as processing_error:
                    logger.error(f'AI processing failed for document {document.id}: {str(processing_error)}')
                    logger.error(f'Processing error details: {type(processing_error).__name__}: {str(processing_error)}')
                    
                    # Document was uploaded but processing failed
                    messages.warning(request, f'Document uploaded but AI analysis failed: {str(processing_error)}. You can retry processing later.')
                    return redirect('main:document_detail', document_id=document.id)
                
            except ValidationError as validation_error:
                logger.error(f'Validation error: {validation_error}')
                error_messages = []
                for field, errors in validation_error.message_dict.items():
                    error_messages.extend(errors)
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, f'Validation failed: {", ".join(error_messages)}')
                return redirect('main:home')
                
            except Exception as model_error:
                logger.error(f'Model creation error: {str(model_error)}')
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, f'Failed to create document: {str(model_error)}')
                return redirect('main:home')
            
        except Exception as e:
            logger.error(f'Upload error: {str(e)}')
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, f'Upload failed: {str(e)}')
            return redirect('main:home')
    
    from django.shortcuts import redirect
    return redirect('main:home')

def test_upload(request):
    """Test endpoint to debug upload issues"""
    if request.method == 'POST':
        response_data = {
            'method': 'POST',
            'content_type': request.content_type,
            'post_data': dict(request.POST),
            'files_data': {name: {'size': f.size, 'name': f.name} for name, f in request.FILES.items()},
            'headers': dict(request.headers)
        }
        return JsonResponse(response_data)
    
    return JsonResponse({'method': 'GET', 'message': 'Use POST to test upload'})

def debug_upload(request):
    """Simple debug endpoint for upload testing"""
    if request.method == 'POST':
        # Just return the raw request data for debugging
        debug_info = {
            'method': request.method,
            'content_type': request.content_type,
            'content_length': request.headers.get('content-length'),
            'post_keys': list(request.POST.keys()),
            'files_keys': list(request.FILES.keys()),
            'post_data': dict(request.POST),
            'files_data': {name: {'size': f.size, 'name': f.name, 'content_type': f.content_type} for name, f in request.FILES.items()},
            'headers': {k: v for k, v in request.headers.items() if k.lower() not in ['cookie', 'authorization']}
        }
        return JsonResponse(debug_info, status=200)
    
    return JsonResponse({'method': 'GET', 'message': 'Send POST request with file to debug'})

def document_detail(request, document_id):
    """Display document detail page"""
    document = get_object_or_404(Document, id=document_id)
    context = {
        'document': document,
        'clauses': document.clauses.all(),
        'risk_analysis': getattr(document, 'risk_analysis', None),
        'summary': getattr(document, 'summary', None)
    }
    return render(request, 'main/document_detail.html', context)

def glossary_view(request):
    """Display legal glossary"""
    terms = LegalTerm.objects.all()
    context = {'terms': terms}
    return render(request, 'main/glossary.html', context)

def document_processing_status(request, document_id):
    """Show document processing status"""
    document = get_object_or_404(Document, id=document_id)
    processing_logs = document.processing_logs.all().order_by('started_at')
    
    context = {
        'document': document,
        'processing_logs': processing_logs,
        'is_fully_processed': document.is_processed and document.summary and document.risk_analysis
    }
    return render(request, 'main/processing_status.html', context)

def simple_upload_test(request):
    """Simple test view for debugging upload issues"""
    if request.method == 'POST':
        try:
            # Basic logging
            logger.info(f'Simple upload test - Method: {request.method}')
            logger.info(f'Simple upload test - Content-Type: {request.content_type}')
            logger.info(f'Simple upload test - POST keys: {list(request.POST.keys())}')
            logger.info(f'Simple upload test - FILES keys: {list(request.FILES.keys())}')
            
            # Check for file
            if 'file' in request.FILES:
                file = request.FILES['file']
                logger.info(f'File received: {file.name}, size: {file.size}')
                
                # Try to read a small portion of the file
                try:
                    # Read first 100 characters for text files
                    if file.name.endswith('.txt'):
                        content = file.read(100).decode('utf-8', errors='ignore')
                        logger.info(f'File content preview: {content[:50]}...')
                    else:
                        logger.info(f'Binary file received: {file.name}')
                except Exception as read_error:
                    logger.error(f'Error reading file: {str(read_error)}')
                
                return JsonResponse({
                    'success': True,
                    'message': 'File received successfully',
                    'filename': file.name,
                    'size': file.size,
                    'content_type': file.content_type
                })
            else:
                logger.error('No file in request.FILES')
                return JsonResponse({
                    'success': False,
                    'error': 'No file received',
                    'post_keys': list(request.POST.keys()),
                    'files_keys': list(request.FILES.keys())
                }, status=400)
                
        except Exception as e:
            logger.error(f'Simple upload test error: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'method': 'GET', 'message': 'Send POST request with file to test'})

def test_upload_page(request):
    """Serve the test upload page"""
    from django.http import HttpResponse
    from pathlib import Path
    
    test_file_path = Path(__file__).parent.parent / 'test_upload.html'
    
    if test_file_path.exists():
        with open(test_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    else:
        return HttpResponse('Test upload page not found. Please check the file path.', status=404)
