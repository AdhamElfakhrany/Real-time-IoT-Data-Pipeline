@echo off
echo Starting ETL Loop (runs every 10 seconds)...
rem set DB_HOST=sqlite
:loop
echo [%TIME%] Running Batch ETL...
python -m batch.batch_etl
timeout /t 10 >nul
goto loop
