@echo off
cd /d %~dp0  :: Ensures the script runs in the current directory
SET FLASK_APP=app.py
SET FLASK_DEBUG=1

python -m flask run --host=127.0.0.1 --port=5000
timeout /t 2 >nul
start "" "http://127.0.0.1:5000"
