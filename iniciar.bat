@echo off
cd /d "%~dp0"
python -m uvicorn painel:app --reload
pause
