@echo off
title QuantPulse AI - Real-Time Stock Market Launcher
echo ====================================================================
echo   QuantPulse AI: Real-Time Stock Market Intelligence Platform
echo ====================================================================
echo.
echo [1/2] Initializing Real-Time FastAPI Market Gateway on port 8000...
start "QuantPulse Real-Time API" python backend/main.py
echo.
echo [2/2] Launching interactive interface in your browser...
timeout /t 2 /nobreak > nul
start index.html
echo.
echo ====================================================================
echo   Live system active!
echo   - Backend URL: http://127.0.0.1:8000
echo   - Swagger Docs: http://127.0.0.1:8000/docs
echo   - Ticker Search: Enter any stock symbol (RELIANCE, INFY, NVDA, TSLA)
echo ====================================================================
