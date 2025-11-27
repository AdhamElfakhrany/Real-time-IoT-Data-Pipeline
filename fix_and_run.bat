@echo off
echo ================================================================================
echo  IoT Project - Master Launcher
echo ================================================================================
echo.
echo Please select a running mode:
echo.
echo  [1] Local Mode (Simulated)
echo      - Uses local Python and MySQL.
echo      - No Docker required.
echo      - Good for quick testing and development.
echo.
echo  [2] Docker Mode (Milestone 3 Requirement)
echo      - Runs full stack: Kafka, Zookeeper, Stream Processor.
echo      - Requires Docker Desktop to be running.
echo      - Necessary for "Streaming Pipeline" deliverables.
echo.
set /p mode="Enter choice (1 or 2): "

if "%mode%"=="2" goto docker_mode
if "%mode%"=="1" goto local_mode
echo Invalid choice. Exiting.
pause
exit /b 1

:docker_mode
echo.
echo [Docker Mode] Starting Infrastructure...
echo --------------------------------------------------------------------------------
echo Checking for Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH.
    echo Please install Docker Desktop and try again.
    pause
    exit /b 1
)

echo Stopping existing containers...
docker-compose -f infra/docker-compose.yml down

echo Starting Services (Kafka, Zookeeper, MySQL, Generator, Stream Processor)...
docker-compose -f infra/docker-compose.yml up -d --build

echo Waiting for services to stabilize...
timeout /t 10

echo ================================================================================
echo  Stack is running!
echo  - Dashboard: http://localhost:8501
echo  - Kafka: localhost:9092
echo  - MySQL: localhost:3307
echo.
echo  To view logs: docker-compose -f infra/docker-compose.yml logs -f
echo ================================================================================
pause
exit /b 0

:local_mode
echo.
echo [Local Mode] Starting Components...
echo --------------------------------------------------------------------------------

echo [1/5] Stopping any lingering processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM streamlit.exe >nul 2>&1

echo [2/5] Activating Virtual Environment (.venv_sql)...
call .venv_sql\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Could not activate .venv_sql.
    pause
    exit /b 1
)

echo [3/5] Installing Dependencies...
echo Downgrading Altair to <5.5 to avoid Python 3.14 TypedDict error...
python -m pip install --upgrade pip
python -m pip install --prefer-binary --only-binary=:all: "altair<5.5" streamlit matplotlib
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [3.5/5] Configuring Database (MySQL)...
rem set DB_HOST=sqlite
python -m batch.migrate
if %errorlevel% neq 0 (
    echo WARNING: Migration failed or tables already exist. Continuing...
)

echo [4/5] Starting Components...

echo   - Starting Sensor Generator (generating 500 events)...
start "Sensor Generator" .venv_sql\Scripts\python -m generator.sensor_generator --sink file --interval 2 --max-events 500

echo   - Starting Batch ETL Loop (runs every 10s)...
start "Batch ETL Loop" run_etl_loop.bat

echo [5/5] Launching Dashboard...
echo   - Opening http://localhost:8501
set DASHBOARD_REFRESH_SECONDS=5
streamlit run dashboard\app.py

pause
