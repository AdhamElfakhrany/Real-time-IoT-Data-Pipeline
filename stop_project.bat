@echo off
echo ================================================================================
echo  Stopping IoT Project
echo ================================================================================

echo Stopping all project processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM streamlit.exe >nul 2>&1

echo Stopping Docker containers (if running)...
docker-compose -f infra/docker-compose.yml down

echo.
echo ================================================================================
echo  All services (Generator, ETL, Dashboard) have been stopped.
echo ================================================================================
pause
