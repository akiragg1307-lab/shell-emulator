@echo off
rem Stage 5 test script: chown errors (close each window)
cd /d "%~dp0.."
for %%n in (path args group) do call run.bat --vfs examples\vfs\deep --script examples\scripts\stage5_error_%%n.emu
