@echo off
echo Starting GST Compliance Backend...
:: Navigate to the directory where this script is located
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements if needed (checks automatically)
echo Checking dependencies...
pip install -r requirements.txt

:: Set Environment Variables (Modify these or use a .env file locally)
:: In production Windows, better to set these in System Properties > Environment Variables
:: But for this script, we can load from .env if python-dotenv is used in code (which it is)

echo Starting Uvicorn Server on Port 80...
:: Note: Port 80 requires this script to be run as Administrator
python -m uvicorn app.main:app --host 0.0.0.0 --port 80

pause
