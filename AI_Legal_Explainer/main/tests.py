from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
import tempfile
import os
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Document, Clause, RiskAnalysis, DocumentSummary, DocumentProcessingLog

class DocumentDeleteTests(APITestCase):
    """Test cases for document deletion functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test document
        self.document = Document.objects.create(
            title='Test Document',
            document_type='contract',
            original_text='This is a test document content.',
            processed_text='This is a test document content.',
            file_size=1024,
            is_processed=True
        )
        
        # Create related data
        self.clause = Clause.objects.create(
            document=self.document,
            clause_type='penalty',
            original_text='Penalty clause text',
            start_position=0,
            end_position=20,
            risk_level='high',
            risk_score=0.8
        )
        
        self.risk_analysis = RiskAnalysis.objects.create(
            document=self.document,
            overall_risk_score=0.8,
            overall_risk_level='high',
            high_risk_clauses_count=1,
            medium_risk_clauses_count=0,
            low_risk_clauses_count=0,
            analysis_summary='High risk document'
        )
        
        self.summary = DocumentSummary.objects.create(
            document=self.document,
            plain_language_summary='This is a test document',
            legal_summary='Legal summary of test document',
            key_points=['Point 1', 'Point 2'],
            word_count=10
        )
        
        self.processing_log = DocumentProcessingLog.objects.create(
            document=self.document,
            step='upload',
            status='completed'
        )
    
    def test_document_delete_api(self):
        """Test that the document delete API endpoint works correctly"""
        url = reverse('main:document-detail', kwargs={'pk': self.document.id})
        
        # Test DELETE request
        response = self.client.delete(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('deleted successfully', response.data['message'])
        
        # Check that document is deleted
        self.assertFalse(Document.objects.filter(id=self.document.id).exists())
        
        # Check that related data is also deleted (cascade delete)
        self.assertFalse(Clause.objects.filter(document_id=self.document.id).exists())
        self.assertFalse(RiskAnalysis.objects.filter(document_id=self.document.id).exists())
        self.assertFalse(DocumentSummary.objects.filter(document_id=self.document.id).exists())
        self.assertFalse(DocumentProcessingLog.objects.filter(document_id=self.document.id).exists())
    
    def test_document_delete_nonexistent(self):
        """Test deleting a non-existent document"""
        fake_id = '12345678-1234-1234-1234-123456789012'
        url = reverse('main:document-detail', kwargs={'pk': fake_id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_document_delete_with_file(self):
        """Test document deletion when document has an actual file"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(b'Test file content')
            temp_file_path = temp_file.name
        
        try:
            # Create document with file
            document_with_file = Document.objects.create(
                title='Document with File',
                document_type='contract',
                file=SimpleUploadedFile(
                    'test.txt',
                    b'Test file content',
                    content_type='text/plain'
                ),
                original_text='Test content',
                is_processed=True
            )
            
            # Test deletion
            url = reverse('main:document-detail', kwargs={'pk': document_with_file.id})
            response = self.client.delete(url)
            
            # Check response
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Check that document is deleted
            self.assertFalse(Document.objects.filter(id=document_with_file.id).exists())
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

class DocumentDeleteViewTests(TestCase):
    """Test cases for document deletion views and templates"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create document with a file to avoid template errors
        self.document = Document.objects.create(
            title='Test Document for View',
            document_type='agreement',
            file=SimpleUploadedFile(
                'test.txt',
                b'Test file content',
                content_type='text/plain'
            ),
            original_text='Test content',
            is_processed=True
        )
    
    def test_document_detail_page_has_delete_button(self):
        """Test that document detail page displays delete button"""
        url = reverse('main:document_detail', kwargs={'document_id': self.document.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete')
        self.assertContains(response, 'confirmDeleteDocument')
    
    def test_home_page_has_delete_buttons(self):
        """Test that home page displays delete buttons for documents"""
        url = reverse('main:home')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # The home page should contain delete functionality
        self.assertContains(response, 'Delete')
