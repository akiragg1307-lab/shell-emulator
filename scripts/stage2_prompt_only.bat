@echo off
rem Этап 2: только пользовательское приглашение к вводу
cd /d "%~dp0.."
call run.bat --prompt "user@emu> "
