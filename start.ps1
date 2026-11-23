# MailMind AI Launcher Script
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    if (Test-Path "C:\Program Files\nodejs") { $env:PATH = "C:\Program Files\nodejs;$env:PATH" }
    elseif (Test-Path "C:\nvm4w\nodejs") { $env:PATH = "C:\nvm4w\nodejs;$env:PATH" }
    elseif (Test-Path "$env:LOCALAPPDATA\Programs\nodejs") { $env:PATH = "$env:LOCALAPPDATA\Programs\nodejs;$env:PATH" }
}

Write-Host "Starting MailMind AI Backend (FastAPI on http://127.0.0.1:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 2

Write-Host "Starting MailMind AI Frontend (Vite on http://localhost:5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host "`nBoth servers have been launched!" -ForegroundColor Green
Write-Host "Open your browser to: http://localhost:5173" -ForegroundColor Yellow
