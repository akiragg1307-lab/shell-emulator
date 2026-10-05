@echo off
rem Stage 3 test script (see the .sh version for details)
cd /d "%~dp0.."
if exist out\ok-copy rmdir /s /q out\ok-copy
call run.bat --vfs examples\vfs\several --script examples\scripts\stage3_errors.emu
