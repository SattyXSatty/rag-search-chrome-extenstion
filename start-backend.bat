@echo off
echo Starting Web Memory RAG Backend
echo ==================================

cd backend

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\.installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo. > venv\.installed
    echo Dependencies installed!
)

echo.
echo Starting FAISS backend server...
echo URL: http://localhost:8000
echo Press Ctrl+C to stop
echo.

python server.py
