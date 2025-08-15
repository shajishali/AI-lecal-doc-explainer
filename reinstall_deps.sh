#!/bin/bash

echo "🔄 Reinstalling dependencies for AI Legal Explainer..."

# Deactivate virtual environment if active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "📦 Deactivating virtual environment..."
    deactivate
fi

# Remove existing virtual environment
if [ -d "AI_Legal_Explainer_env" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf AI_Legal_Explainer_env
fi

# Create new virtual environment
echo "🔧 Creating new virtual environment..."
python3 -m venv AI_Legal_Explainer_env

# Activate virtual environment
echo "📦 Activating virtual environment..."
source AI_Legal_Explainer_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies from updated requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"
echo "🚀 You can now run: python manage.py runserver"


