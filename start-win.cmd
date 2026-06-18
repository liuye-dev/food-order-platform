@echo off
setlocal

cd /d "%~dp0"
set "PROJECT_DIR=%~dp0"

echo [1/4] Installing Python dependencies...
uv sync
if errorlevel 1 goto error

echo [2/4] Preparing SQLite database...
uv run python backend\manage.py migrate
if errorlevel 1 goto error

echo [3/4] Loading demo data...
uv run python backend\manage.py loaddata demo_data
if errorlevel 1 goto error

echo [4/4] Starting backend and frontend...
start "food-order-backend" cmd /k "cd /d ""%PROJECT_DIR%"" && uv run python backend\manage.py runserver"
start "food-order-frontend" cmd /k "cd /d ""%PROJECT_DIR%frontend"" && npm install && npm run dev"

echo.
echo Demo is starting.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000/api/health/
echo.
pause
exit /b 0

:error
echo.
echo Start failed. Please check whether Python uv and Node.js are installed.
pause
exit /b 1
