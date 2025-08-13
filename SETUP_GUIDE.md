# AI_Legal_Explainer - Setup Guide

## Quick Start

### 1. Environment Setup (Already Done ✅)
- ✅ Python virtual environment created: `AI_Legal_Explainer_env`
- ✅ Django 5.2.5 installed
- ✅ MySQL client installed
- ✅ Project structure created

### 2. Database Setup (Required)
1. **Install MySQL Server** if not already installed
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use XAMPP: https://www.apachefriends.org/

2. **Create Database**
   ```sql
   CREATE DATABASE ai_legal_explainer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Create MySQL User**
   ```sql
   CREATE USER 'ai_legal_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON ai_legal_explainer.* TO 'ai_legal_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **Update Database Settings**
   - Edit `AI_Legal_Explainer/AI_Legal_Explainer/settings.py`
   - Update the DATABASES section with your MySQL credentials

### 3. Activate Environment

**Option 1: PowerShell (Recommended)**
```powershell
.\activate_env.ps1
```

**Option 2: Command Prompt**
```cmd
activate_env.bat
```

**Option 3: Manual**
```powershell
AI_Legal_Explainer_env\Scripts\Activate.ps1
```

### 4. Run Django Commands

```bash
# Navigate to Django project
cd AI_Legal_Explainer

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 5. Access Your Application

- **Django Admin**: http://127.0.0.1:8000/admin/
- **Main Site**: http://127.0.0.1:8000/

## Project Structure

```
AI_Legal_Explainer/
├── AI_Legal_Explainer/              # Django project
│   ├── AI_Legal_Explainer/          # Project settings
│   │   ├── __init__.py
│   │   ├── settings.py              # Database & app settings
│   │   ├── urls.py                  # Main URL configuration
│   │   ├── wsgi.py                  # WSGI configuration
│   │   └── asgi.py                  # ASGI configuration
│   └── manage.py                    # Django management script
├── AI_Legal_Explainer_env/          # Virtual environment
├── requirements.txt                  # Python dependencies
├── database_config.py               # Database configuration template
├── activate_env.ps1                 # PowerShell activation script
├── activate_env.bat                 # Command prompt activation script
├── README.md                        # Project overview
├── SETUP_GUIDE.md                   # This setup guide
└── .gitignore                       # Git ignore patterns
```

## Next Steps

1. **Create Django Apps**
   ```bash
   python manage.py startapp legal_docs
   python manage.py startapp ai_analysis
   ```

2. **Add Bootstrap**
   - Download Bootstrap 5
   - Add to static files
   - Configure templates

3. **Configure URLs and Views**
   - Set up app URLs
   - Create views and templates
   - Implement legal document handling

4. **Database Models**
   - Design document models
   - Create user models
   - Set up relationships

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Verify MySQL service is running
   - Check credentials in settings.py
   - Ensure database exists

2. **Virtual Environment Not Activating**
   - Use PowerShell for .ps1 scripts
   - Use Command Prompt for .bat scripts
   - Check execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

3. **Django Import Error**
   - Ensure virtual environment is activated
   - Verify Django is installed: `pip list | findstr Django`

### Getting Help

- Check Django documentation: https://docs.djangoproject.com/
- MySQL documentation: https://dev.mysql.com/doc/
- Bootstrap documentation: https://getbootstrap.com/docs/

## Development Commands

```bash
# Check Django version
python -m django --version

# List installed packages
pip list

# Update requirements.txt
pip freeze > requirements.txt

# Check for outdated packages
pip list --outdated

# Install additional packages
pip install package_name
```

## Environment Variables (Optional)

Create a `.env` file for sensitive information:
```
DEBUG=True
SECRET_KEY=your_secret_key_here
DB_NAME=ai_legal_explainer
DB_USER=ai_legal_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

Remember to add `.env` to your `.gitignore` file!
