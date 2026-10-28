@echo off
title Intelligent Supply Chain Optimization System
echo ====================================================================
echo   INTELLIGENT SUPPLY CHAIN OPTIMIZATION SYSTEM
echo   College Data Structures and Algorithms Project
echo   Starting Python Flask Server...
echo   URL: http://127.0.0.1:5000
echo ====================================================================

REM Launch browser in 2 seconds
start "" http://127.0.0.1:5000

REM Run Flask app using local virtualenv or system python
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe app.py
) else (
    python app.py
)
pause
