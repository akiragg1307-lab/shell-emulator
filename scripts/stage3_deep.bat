@echo off
rem Stage 3 test script (see the .sh version for details)
cd /d "%~dp0.."
if exist out\vfs-copy rmdir /s /q out\vfs-copy
call run.bat --vfs examples\vfs\deep --script examples\scripts\stage3_all.emu
