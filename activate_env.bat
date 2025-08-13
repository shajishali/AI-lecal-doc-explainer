@echo off
echo Activating AI_Legal_Explainer Virtual Environment...
echo.
call AI_Legal_Explainer_env\Scripts\activate.bat
echo.
echo Virtual environment activated!
echo You can now run Django commands like:
echo   python manage.py runserver
echo   python manage.py migrate
echo   python manage.py createsuperuser
echo.
echo To deactivate, simply type: deactivate
echo.
cmd /k
