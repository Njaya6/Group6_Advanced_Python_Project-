@echo off
echo ========================================================
echo   Launching QuantPulse AI - Stock Market Sense Platform
echo ========================================================
echo.
echo 1. Starting FastAPI Python Backend Server (Port 8000)...
start "QuantPulse API Backend" python backend/main.py
echo.
echo 2. Opening Dashboard in your browser...
timeout /t 2 /nobreak > nul
start index.html
echo.
echo ========================================================
echo   System running! Close the terminal window to stop.
echo ========================================================
