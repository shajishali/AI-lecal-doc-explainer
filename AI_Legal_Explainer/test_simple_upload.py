#!/usr/bin/env python3
"""
Simple upload test script
This tests the basic functionality without the full web interface
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

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        # Test imports
        from main.ai_services import DocumentProcessor, AISummarizer, ClauseDetector
        print("✅ AI services imported successfully")
        
        # Test service initialization
        processor = DocumentProcessor()
        summarizer = AISummarizer()
        clause_detector = ClauseDetector()
        print("✅ AI services initialized successfully")
        
        # Test text processing
        test_text = "This is a test legal document containing contract terms and conditions."
        processed_text = processor.preprocess_text(test_text)
        print(f"✅ Text preprocessing works: {len(processed_text)} characters")
        
        # Test summary generation
        summary = summarizer.generate_summary(test_text)
        print(f"✅ Summary generation works: {summary['word_count']} words")
        
        # Test clause detection
        clauses = clause_detector.detect_clauses(test_text)
        print(f"✅ Clause detection works: {len(clauses)} clauses found")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing Database Connection...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_media_directory():
    """Test media directory setup"""
    print("\n📁 Testing Media Directory...")
    
    try:
        media_dir = Path(__file__).parent / 'media'
        if not media_dir.exists():
            media_dir.mkdir(exist_ok=True)
            print(f"✅ Created media directory: {media_dir}")
        else:
            print(f"✅ Media directory exists: {media_dir}")
        
        # Test if it's writable
        test_file = media_dir / 'test.txt'
        test_file.write_text('test')
        test_file.unlink()  # Clean up
        print("✅ Media directory is writable")
        
        return True
        
    except Exception as e:
        print(f"❌ Media directory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Legal Explainer - System Test")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Database Connection", test_database_connection),
        ("Media Directory", test_media_directory),
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
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your system should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
