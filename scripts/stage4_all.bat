@echo off
rem Stage 4 test script: all modes of ls, cd, tree, tac
cd /d "%~dp0.."
call run.bat --vfs examples\vfs\deep --script examples\scripts\stage4_all.emu
