@echo off
rem Этап 2: все параметры сразу (скрипт завершается командой exit)
cd /d "%~dp0.."
call run.bat --vfs examples\vfs\demo --prompt "demo$ " --script examples\scripts\stage2_ok.emu
