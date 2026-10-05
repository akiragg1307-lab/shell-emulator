@echo off
rem Launch the emulator: run.bat [emulator options]
cd /d "%~dp0"
set PYTHONPATH=src
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m shell_emulator %*
) else (
    python -m shell_emulator %*
)
