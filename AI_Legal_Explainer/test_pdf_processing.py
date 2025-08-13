#!/usr/bin/env python3
"""
Simple test script to verify PDF processing works
Run this from the AI_Legal_Explainer directory
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Legal_Explainer.settings')
django.setup()

from main.ai_services import DocumentProcessor
from main.models import Document

def test_pdf_processing():
    """Test PDF text extraction"""
    print("Testing PDF processing...")
    
    # Check if we have any documents in the database
    try:
        documents = Document.objects.all()
        print(f"Found {documents.count()} documents in database")
        
        if documents.exists():
            # Test with the first document
            doc = documents.first()
            print(f"Testing with document: {doc.title} ({doc.file.name})")
            
            processor = DocumentProcessor()
            text = processor.extract_text(doc)
            
            print(f"Extracted text length: {len(text)} characters")
            print(f"First 200 characters: {text[:200]}...")
            
            if len(text) > 100:
                print("✅ PDF processing successful!")
            else:
                print("⚠️ PDF processing may have issues")
                
        else:
            print("No documents found in database")
            
    except Exception as e:
        print(f"Error testing PDF processing: {e}")
        print("This might be due to database connection issues")

def test_file_handling():
    """Test basic file handling"""
    print("\nTesting file handling...")
    
    try:
        # Check if media directory exists
        media_dir = os.path.join(os.path.dirname(__file__), 'media')
        if os.path.exists(media_dir):
            print(f"✅ Media directory exists: {media_dir}")
            
            # List files in media directory
            files = [f for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))]
            print(f"Files in media directory: {files}")
        else:
            print(f"⚠️ Media directory not found: {media_dir}")
            
    except Exception as e:
        print(f"Error checking file handling: {e}")

if __name__ == "__main__":
    print("AI Legal Explainer - PDF Processing Test")
    print("=" * 50)
    
    test_file_handling()
    test_pdf_processing()
    
    print("\nTest completed!")
