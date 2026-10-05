@echo off
rem Этап 2: несуществующий стартовый скрипт (сообщение об ошибке)
cd /d "%~dp0.."
call run.bat --script examples\scripts\no_such_file.emu
