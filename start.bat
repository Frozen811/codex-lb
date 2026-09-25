@echo off
title codex-lb (Hardened Community Edition)
echo ========================================================
echo   codex-lb (Hardened Community Edition)
echo   Dashboard: http://localhost:2455
echo ========================================================
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 'uv' was not found in PATH.
    echo Install uv: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)
uv run codex-lb %*
pause
