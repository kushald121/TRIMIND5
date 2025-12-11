@echo off
echo Starting LLM Council...

echo Starting backend on http://localhost:8002...
start "Backend" /D "c:\Users\Kushal\Desktop\Tri2" cmd /k "venv\Scripts\activate.bat && python -m backend.main"

timeout /t 5 /nobreak >nul

echo Starting frontend on http://localhost:5174...
cd TriMind
start "Frontend" cmd /k "npm run dev"

echo.
echo ^>^>^> LLM Council is running! ^<^<^<
echo    Backend:  http://localhost:8002
echo    Frontend: http://localhost:5174
echo.
echo Press Ctrl+C in each window to stop the servers