# Authentication Setup Guide

## Overview
The AI Legal Explainer now includes user authentication to protect advanced features like dashboards and analytics.

## Setup Instructions

### 1. Create a Default User
Run the following command to create a default admin user:

```bash
cd AI_Legal_Explainer
python manage.py create_user
```

This will create a user with:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Superuser (full access)

### 2. Start the Development Server
```bash
python manage.py runserver
```

### 3. Access the Application
- Navigate to `http://127.0.0.1:8000/`
- Click "Login" in the navigation bar
- Use the credentials: `admin` / `admin123`

## Features

### Public Access (No Login Required)
- Welcome page
- Home page
- Document upload
- Legal glossary
- Language switching

### Protected Features (Login Required)
- Offline Dashboard
- Transparency Controls
- Performance Dashboard
- Analytics Dashboard

## Navigation Changes

- **Before Login**: Advanced Features shows "(Login Required)" and redirects to login
- **After Login**: Advanced Features dropdown is fully functional
- **User Menu**: Shows username and logout option when logged in

## Security Notes

- The default password (`admin123`) should be changed in production
- All dashboard views are protected with `@login_required` decorator
- Login redirects to `/home/` after successful authentication
- Logout redirects to `/welcome/`

## Customization

### Change Default Credentials
Edit `main/management/commands/create_user.py` to modify the default user creation.

### Modify Authentication Settings
Update `AI_Legal_Explainer/settings.py`:
```python
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/welcome/'
```

### Add More Protected Views
Use the `@login_required` decorator on any view function:
```python
from django.contrib.auth.decorators import login_required

@login_required
def my_protected_view(request):
    # Your view logic here
    pass
```

## Troubleshooting

### Common Issues

1. **"Page not found (404)" for /accounts/login/**
   - Ensure the authentication URLs are added to `main/urls.py`
   - Check that `login.html` template exists

2. **Login form not working**
   - Verify CSRF token is included in the form
   - Check that the user exists in the database

3. **Still getting redirected to login after authentication**
   - Clear browser cookies/session
   - Check Django session configuration

### Reset Database
If you need to start fresh:
```bash
python manage.py flush  # Clears all data
python manage.py create_user  # Recreates default user
```

## Production Considerations

- Change default passwords
- Use environment variables for sensitive settings
- Enable HTTPS
- Configure proper session security
- Set up user registration if needed
- Implement password reset functionality
