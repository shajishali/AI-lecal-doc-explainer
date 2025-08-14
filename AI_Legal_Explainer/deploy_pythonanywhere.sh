#!/bin/bash

# 🚀 PythonAnywhere Deployment Script
# This script automates the deployment process on PythonAnywhere

echo "🚀 Starting PythonAnywhere Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "Please run this script from the directory containing manage.py"
    exit 1
fi

print_status "Current directory: $(pwd)"

# Create virtual environment
print_status "Creating virtual environment..."
python3.9 -m venv venv
if [ $? -eq 0 ]; then
    print_status "Virtual environment created successfully"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    print_status "Virtual environment activated"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Install requirements
print_status "Installing Python requirements..."
pip install -r requirements_pythonanywhere.txt
if [ $? -eq 0 ]; then
    print_status "Requirements installed successfully"
else
    print_error "Failed to install requirements"
    exit 1
fi

# Create .env file template
print_status "Creating .env file template..."
cat > .env << EOF
# PythonAnywhere Environment Variables
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DB_NAME=yourusername\$ai_legal_explainer
DB_USER=yourusername
DB_PASSWORD=your_database_password_here
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_PORT=3306
PYTHONANYWHERE_SITE_NAME=yourusername.pythonanywhere.com
EOF

print_status ".env file created. Please update with your actual PythonAnywhere credentials."

# Run migrations
print_status "Running database migrations..."
python manage.py migrate
if [ $? -eq 0 ]; then
    print_status "Migrations completed successfully"
else
    print_warning "Migrations failed. This is normal if database is not configured yet."
fi

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    print_status "Static files collected successfully"
else
    print_warning "Static files collection failed. This is normal if STATIC_ROOT is not configured."
fi

# Create superuser prompt
print_status "Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

print_status "🎉 Deployment script completed!"
print_status ""
print_status "Next steps:"
print_status "1. Update .env file with your PythonAnywhere credentials"
print_status "2. Configure your web app in PythonAnywhere dashboard"
print_status "3. Update WSGI configuration file"
print_status "4. Reload your web app"
print_status ""
print_status "For detailed instructions, see: PYTHONANYWHERE_DEPLOYMENT.md"
