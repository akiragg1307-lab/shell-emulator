@echo off
rem Этап 2: стартовый скрипт с ошибкой (остановка и сообщение)
cd /d "%~dp0.."
call run.bat --script examples\scripts\stage2_error.emu
