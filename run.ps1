# NEXUS PowerShell 1-Click Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting NEXUS Smart Energy Optimization Platform" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launching server on http://localhost:5000 ..." -ForegroundColor Yellow

# Open default browser
Start-Process "http://localhost:5000"

# Start Python server
python server.py
