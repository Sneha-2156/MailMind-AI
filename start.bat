@echo off
title MailMind AI Launcher
echo ===================================================
echo             Starting MailMind AI Platform
echo ===================================================
echo.

where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Program Files\nodejs" set "PATH=C:\Program Files\nodejs;%PATH%"
    if exist "C:\nvm4w\nodejs" set "PATH=C:\nvm4w\nodejs;%PATH%"
    if exist "%LOCALAPPDATA%\Programs\nodejs" set "PATH=%LOCALAPPDATA%\Programs\nodejs;%PATH%"
)

echo Starting Backend server (FastAPI on http://127.0.0.1:8000)...
start "MailMind Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 2 /nobreak >nul

echo Starting Frontend server (Vite on http://localhost:5173)...
start "MailMind Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===================================================
echo Both servers are starting!
echo Open your browser to: http://localhost:5173
echo ===================================================
pause
