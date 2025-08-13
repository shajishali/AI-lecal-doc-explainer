# AI_Legal_Explainer Environment Activation Script
# Run this script to activate the virtual environment

Write-Host "Activating AI_Legal_Explainer Virtual Environment..." -ForegroundColor Green
Write-Host ""

# Activate the virtual environment
& ".\AI_Legal_Explainer_env\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "You can now run Django commands like:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor Cyan
Write-Host "  python manage.py migrate" -ForegroundColor Cyan
Write-Host "  python manage.py createsuperuser" -ForegroundColor Cyan
Write-Host ""
Write-Host "To deactivate, simply type: deactivate" -ForegroundColor Yellow
Write-Host ""

# Keep the shell open
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
