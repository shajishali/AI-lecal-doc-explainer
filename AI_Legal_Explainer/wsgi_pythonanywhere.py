"""
WSGI config for AI_Legal_Explainer project on PythonAnywhere.
"""

import os
import sys

# Add the project directory to the Python path
path = '/home/yourusername/AI_Legal_Explainer'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables for PythonAnywhere
os.environ.setdefault('PYTHONANYWHERE_SITE_NAME', 'yourusername.pythonanywhere.com')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Legal_Explainer.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
