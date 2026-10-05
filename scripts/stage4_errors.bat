@echo off
rem Stage 4 test script: errors of ls, cd, tree, tac (close each window)
cd /d "%~dp0.."
for %%n in (ls cd tree tac) do call run.bat --vfs examples\vfs\deep --script examples\scripts\stage4_error_%%n.emu
