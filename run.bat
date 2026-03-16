@echo off
chcp 65001 > nul
set PYTHONUTF8=1
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" main.py >> logs\digest.log 2>&1
