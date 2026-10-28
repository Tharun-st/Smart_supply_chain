Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  Starting Intelligent Supply Chain Management System..." -ForegroundColor Green
Write-Host "  URL: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan

Start-Process "http://127.0.0.1:5000"
node server.js
