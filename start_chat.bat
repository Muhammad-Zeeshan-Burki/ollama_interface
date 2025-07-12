@echo off
title OLLAMA Chat Interface Launcher
color 0A
echo.
echo ========================================
echo  OLLAMA Chat Interface Launcher
echo ========================================
echo.
echo Starting OLLAMA service...
echo.

REM Check if OLLAMA is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: OLLAMA is not installed or not in PATH
    echo Please install OLLAMA from https://ollama.ai
    pause
    exit /b 1
)

REM Start OLLAMA service in background
echo Starting OLLAMA service...
start /B ollama serve

REM Wait for OLLAMA to be ready
echo Waiting for OLLAMA service to start...
timeout /t 5 /nobreak >nul

REM Check if OLLAMA is running by testing the API
:check_ollama
echo Checking OLLAMA connection...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method GET -TimeoutSec 5 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo Waiting for OLLAMA to be ready...
    timeout /t 2 /nobreak >nul
    goto check_ollama
)

echo ✓ OLLAMA service is ready!
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking Python packages...
python -c "import streamlit, ollama" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install streamlit ollama
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo ✓ Python packages are ready!
echo.

REM Start Streamlit app
echo Starting Streamlit Chat Interface...
echo.
echo ========================================
echo  Chat Interface will open in browser
echo ========================================
echo.
echo Access URLs:
echo - Local: http://localhost:8501
echo - Network: http://192.168.18.5:8501
echo.
echo Press Ctrl+C to stop both services
echo ========================================
echo.

REM Start Streamlit with auto-browser opening and skip email prompt
(echo. & echo.) | python -m streamlit run app.py --server.headless=false --browser.gatherUsageStats=false --server.port=8501

REM If we get here, Streamlit was stopped
echo.
echo Streamlit stopped. Cleaning up...
echo.

REM Kill OLLAMA service
taskkill /F /IM ollama.exe >nul 2>&1

echo ✓ Services stopped.
echo.
echo Thank you for using OLLAMA Chat Interface!
pause
