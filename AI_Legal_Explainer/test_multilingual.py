#!/usr/bin/env python
"""
Test script for multilingual functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Legal_Explainer.settings')
django.setup()

from main.multilingual_service import MultilingualService, LegalTermTranslator

def test_multilingual_service():
    """Test the multilingual service functionality"""
    print("🧪 Testing Multilingual Service...")
    
    try:
        # Initialize service
        service = MultilingualService()
        print("✅ Multilingual service initialized")
        
        # Test language detection
        test_texts = [
            ("This is a legal contract", "en"),
            ("இது ஒரு சட்ட ஒப்பந்தம்", "ta"),
            ("මෙය නීති ගිවිසුමක්", "si")
        ]
        
        for text, expected_lang in test_texts:
            detected = service.detect_language(text)
            print(f"   Text: '{text[:20]}...' -> Detected: {detected} (Expected: {expected_lang})")
        
        # Test translation
        english_text = "This is a legal document about contracts and liability."
        print(f"\n📝 Testing translation of: '{english_text}'")
        
        for target_lang in ['ta', 'si']:
            translated = service.translate_text(english_text, target_lang, 'en')
            print(f"   {target_lang.upper()}: {translated}")
        
        # Test supported languages
        languages = service.get_supported_languages()
        print(f"\n🌍 Supported languages: {[lang['code'] for lang in languages]}")
        
        print("\n✅ Multilingual service tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing multilingual service: {e}")
        return False
    
    return True

def test_legal_translator():
    """Test the legal term translator"""
    print("\n🧪 Testing Legal Term Translator...")
    
    try:
        translator = LegalTermTranslator()
        print("✅ Legal term translator initialized")
        
        # Test legal term translation
        test_terms = ['contract', 'liability', 'indemnification']
        
        for term in test_terms:
            print(f"\n📚 Term: {term}")
            for lang in ['en', 'ta', 'si']:
                translated = translator.translate_legal_term(term, lang)
                print(f"   {lang.upper()}: {translated}")
        
        # Test glossary
        for lang in ['en', 'ta', 'si']:
            glossary = translator.get_legal_glossary(lang)
            print(f"\n📖 {lang.upper()} Glossary: {len(glossary)} terms")
        
        print("\n✅ Legal term translator tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing legal term translator: {e}")
        return False
    
    return False

def main():
    """Main test function"""
    print("🚀 Starting Multilingual Functionality Tests\n")
    
    # Test multilingual service
    service_ok = test_multilingual_service()
    
    # Test legal translator
    translator_ok = test_legal_translator()
    
    print("\n" + "="*50)
    if service_ok and translator_ok:
        print("🎉 All tests passed! Multilingual functionality is working.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print("="*50)

if __name__ == "__main__":
    main()
