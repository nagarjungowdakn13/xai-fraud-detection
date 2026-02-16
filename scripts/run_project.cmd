@echo off
REM Launch Fraud Detection Enterprise stack (Windows cmd)
REM - Prediction API
REM - API Gateway
REM - Frontend (Vite)

setlocal ENABLEDELAYEDEXPANSION

REM Configure frontend to call the gateway
set VITE_GATEWAY_URL=http://localhost:5000

REM Move to repo root (this script lives in scripts/)
pushd "%~dp0.."

REM Capture repo root in a variable so we can safely handle
REM Windows paths that contain spaces and special characters like '&'.
set "PROJECT_ROOT=%CD%"

REM Start Prediction API in a new terminal
if exist "prediction-api\run.py" (
  start "Prediction API" cmd /k pushd "%PROJECT_ROOT%" ^&^& python "prediction-api\run.py"
) else (
  echo [WARN] prediction-api\run.py not found.
)

REM Start API Gateway in a new terminal
if exist "api-gateway\app\main.py" (
  start "API Gateway" cmd /k pushd "%PROJECT_ROOT%" ^&^& python "api-gateway\app\main.py"
) else (
  echo [WARN] api-gateway\app\main.py not found.
)

REM Start Frontend in a new terminal via npm (Vite dev server)
if exist "frontend\package.json" (
  start "Frontend" cmd /k pushd "%PROJECT_ROOT%\frontend" ^&^& npm run dev
) else (
  echo [WARN] frontend\package.json not found.
)

REM Print helpful URLs
echo.
echo ==============================================
echo Services starting... open these in your browser:
echo - Frontend Dashboard:   http://localhost:5173
echo - API Gateway:          http://localhost:5000
echo - Graph Endpoint:       http://localhost:5000/graph/network
echo - Heatmap Endpoint:     http://localhost:5000/analytics/heatmap
echo ==============================================

echo.
echo Press any key to close this launcher window; services keep running in their terminals.
pause >nul

popd
endlocal
