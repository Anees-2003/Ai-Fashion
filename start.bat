@echo off
echo ========================================
echo   AI Fashion Design Generator
echo   Starting Backend + Frontend Servers
echo ========================================
echo.

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "AI Fashion - Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React Frontend on http://localhost:5173 ...
start "AI Fashion - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Both servers are starting...
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo  API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this launcher window...
pause >nul
