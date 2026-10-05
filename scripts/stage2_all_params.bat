@echo off
rem Stage 2 test script for the emulator (see the .sh version for details)
cd /d "%~dp0.."
call run.bat --vfs examples\vfs\several --prompt "demo$ " --script examples\scripts\stage2_ok.emu
