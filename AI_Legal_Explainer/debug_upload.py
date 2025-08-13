#!/usr/bin/env python3
"""
Debug script to test PDF upload step by step
This will help identify where the upload process is failing
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Legal_Explainer.settings')

try:
    django.setup()
    print("✅ Django environment setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def test_upload_simulation():
    """Simulate the upload process step by step"""
    print("\n🧪 Testing Upload Process Simulation...")
    
    try:
        from main.models import Document, DocumentProcessingLog
        from main.ai_services import DocumentProcessor, AISummarizer, ClauseDetector, RiskAnalyzer, GlossaryService
        from datetime import datetime
        
        print("✅ All imports successful")
        
        # Test 1: Check if we can create a document
        print("\n1️⃣ Testing Document Creation...")
        try:
            # Create a test document (without file for now)
            test_doc = Document.objects.create(
                title="Test Document",
                document_type="contract",
                is_processed=False
            )
            print(f"✅ Document created with ID: {test_doc.id}")
            
            # Clean up
            test_doc.delete()
            print("✅ Test document cleaned up")
            
        except Exception as e:
            print(f"❌ Document creation failed: {e}")
            return False
        
        # Test 2: Test AI services individually
        print("\n2️⃣ Testing AI Services...")
        try:
            processor = DocumentProcessor()
            summarizer = AISummarizer()
            clause_detector = ClauseDetector()
            risk_analyzer = RiskAnalyzer()
            glossary_service = GlossaryService()
            print("✅ All AI services initialized")
            
        except Exception as e:
            print(f"❌ AI services initialization failed: {e}")
            return False
        
        # Test 3: Test text processing with sample text
        print("\n3️⃣ Testing Text Processing...")
        try:
            sample_text = """
            This is a sample legal contract between Party A and Party B.
            The contract contains terms and conditions for services.
            Party A agrees to provide services and Party B agrees to pay.
            This contract is governed by the laws of the jurisdiction.
            """
            
            processed_text = processor.preprocess_text(sample_text)
            print(f"✅ Text preprocessing works: {len(processed_text)} characters")
            
            summary = summarizer.generate_summary(processed_text)
            print(f"✅ Summary generation works: {summary['word_count']} words")
            
            clauses = clause_detector.detect_clauses(processed_text)
            print(f"✅ Clause detection works: {len(clauses)} clauses found")
            
            risk_data = risk_analyzer.analyze_document_risk(clauses)
            print(f"✅ Risk analysis works: {risk_data['overall_risk_level']} risk")
            
            highlighted_text = glossary_service.highlight_terms_in_text(processed_text)
            print(f"✅ Glossary processing works: {len(highlighted_text)} characters")
            
        except Exception as e:
            print(f"❌ Text processing failed: {e}")
            return False
        
        # Test 4: Test database operations
        print("\n4️⃣ Testing Database Operations...")
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Test creating processing logs
                test_doc = Document.objects.create(
                    title="Test Document for Logs",
                    document_type="contract",
                    is_processed=False
                )
                
                log = DocumentProcessingLog.objects.create(
                    document=test_doc,
                    step='test',
                    status='processing'
                )
                
                print(f"✅ Processing log created: {log.id}")
                
                # Clean up
                test_doc.delete()
                
            print("✅ Database operations successful")
            
        except Exception as e:
            print(f"❌ Database operations failed: {e}")
            return False
        
        print("\n🎉 All upload simulation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Upload simulation test failed: {e}")
        return False

def test_file_handling():
    """Test file handling capabilities"""
    print("\n📁 Testing File Handling...")
    
    try:
        media_dir = Path(__file__).parent / 'media'
        if not media_dir.exists():
            media_dir.mkdir(exist_ok=True)
            print(f"✅ Created media directory: {media_dir}")
        else:
            print(f"✅ Media directory exists: {media_dir}")
        
        # Test file creation and deletion
        test_file = media_dir / 'test_upload.txt'
        test_file.write_text('Test content for upload simulation')
        
        if test_file.exists():
            print(f"✅ Test file created: {test_file}")
            file_size = test_file.stat().st_size
            print(f"✅ File size: {file_size} bytes")
            
            # Clean up
            test_file.unlink()
            print("✅ Test file cleaned up")
            
        return True
        
    except Exception as e:
        print(f"❌ File handling test failed: {e}")
        return False

def test_upload_view():
    """Test the upload view directly"""
    print("\n🌐 Testing Upload View...")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        from main.views import upload_document
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/upload/', {
            'title': 'Test Document',
            'document_type': 'contract'
        })
        request.user = AnonymousUser()
        
        # Test if the view can be called
        try:
            response = upload_document(request)
            print(f"✅ Upload view response: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Upload view error (expected without file): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload view test failed: {e}")
        return False

def main():
    """Run all debug tests"""
    print("🔍 AI Legal Explainer - Upload Debug Test")
    print("=" * 50)
    
    tests = [
        ("Upload Process Simulation", test_upload_simulation),
        ("File Handling", test_file_handling),
        ("Upload View", test_upload_view),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Debug Test Results:")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All debug tests passed! The issue might be in the web interface.")
        print("Try uploading a PDF through the browser now.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
