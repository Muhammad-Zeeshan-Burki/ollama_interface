@echo off
title Stop OLLAMA Chat Interface
color 0C
echo.
echo ========================================
echo  Stopping OLLAMA Chat Interface
echo ========================================
echo.

echo Stopping Streamlit...
taskkill /F /IM python.exe >nul 2>&1

echo Stopping OLLAMA service...
taskkill /F /IM ollama.exe >nul 2>&1

echo.
echo ✓ All services stopped successfully!
echo.
echo ========================================
echo  OLLAMA Chat Interface Stopped
echo ========================================
echo.
pause
