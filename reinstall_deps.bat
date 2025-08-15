@echo off
echo 🔄 Reinstalling dependencies for AI Legal Explainer...

REM Deactivate virtual environment if active
if defined VIRTUAL_ENV (
    echo 📦 Deactivating virtual environment...
    deactivate
)

REM Remove existing virtual environment
if exist "AI_Legal_Explainer_env" (
    echo 🗑️  Removing existing virtual environment...
    rmdir /s /q "AI_Legal_Explainer_env"
)

REM Create new virtual environment
echo 🔧 Creating new virtual environment...
python -m venv AI_Legal_Explainer_env

REM Activate virtual environment
echo 📦 Activating virtual environment...
call AI_Legal_Explainer_env\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies from updated requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt

echo ✅ Dependencies installed successfully!
echo 🚀 You can now run: python manage.py runserver

pause


