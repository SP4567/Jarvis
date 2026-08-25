@echo off
title J.A.R.V.I.S. Autonomous AI Engine
echo ========================================================
echo       J.A.R.V.I.S. AUTONOMOUS VOICE & HUD ENGINE
echo ========================================================
echo.

:: Check python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Check node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip install -q -r server/requirements.txt
cd client && call npm install --silent && cd ..

echo [2/3] Starting J.A.R.V.I.S. Core Server (Port 8000)...
start "JARVIS-Backend" cmd /k "set PYTHONPATH=. && python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload"

echo [3/3] Starting Sci-Fi HUD Interface (Port 3000)...
start "JARVIS-Frontend" cmd /k "cd client && npm run dev"

timeout /t 3 >nul
echo.
echo ========================================================
echo  J.A.R.V.I.S. IS ONLINE!
echo  HUD Interface: http://localhost:3000
echo  API / WS Core: http://localhost:8000
echo ========================================================
start http://localhost:3000
pause
