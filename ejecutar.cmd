
@echo off

if not exist .\.env\Scripts\activate.bat (
    py -m venv .env
    .\.env\Scripts\activate.bat
    pip install -r requirements.txt
)

call .\.env\Scripts\activate.bat 

py .\jobs.py

pause >nul
