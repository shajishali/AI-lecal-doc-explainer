#!/usr/bin/env python
"""
Simple test script to check if Django is working
"""
import os
import sys

# Add the Django project to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'AI_Legal_Explainer'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Legal_Explainer.settings')

try:
    import django
    django.setup()
    print("✅ Django imported successfully!")
    
    # Test basic Django functionality
    from django.conf import settings
    print(f"✅ Django settings loaded: {settings.DEBUG}")
    
    # Test database connection
    from django.db import connection
    connection.ensure_connection()
    print("✅ Database connection successful!")
    
    # Test models
    from main.models import Document
    print(f"✅ Models imported successfully! Document count: {Document.objects.count()}")
    
    print("\n🎉 Django is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
