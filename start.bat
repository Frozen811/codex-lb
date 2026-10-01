@echo off
setlocal
title codex-lb (Hardened Community Edition)
echo ========================================================
echo   codex-lb (Hardened Community Edition)
echo   Dashboard: http://localhost:2455
echo ========================================================
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
set "launcher_exit=%errorlevel%"
if "%~1"=="" pause
exit /b %launcher_exit%
