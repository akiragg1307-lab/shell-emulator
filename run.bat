@echo off
rem Запуск эмулятора: run.bat [параметры эмулятора]
cd /d "%~dp0"
set PYTHONPATH=src
python -m shell_emulator %*
