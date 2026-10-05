@echo off
rem Stage 2 test script for the emulator (see the .sh version for details)
cd /d "%~dp0.."
call run.bat --script examples\scripts\no_such_file.emu
