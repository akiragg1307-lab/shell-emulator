@echo off
rem Stage 5 test script: all modes of chown (in-memory only)
cd /d "%~dp0.."
if exist out\stage5-copy rmdir /s /q out\stage5-copy
call run.bat --vfs examples\vfs\deep --script examples\scripts\stage5_all.emu
