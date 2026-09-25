# PowerShell launcher for codex-lb (Hardened Community Edition)
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  codex-lb (Hardened Community Edition)" -ForegroundColor Cyan
Write-Host "  Web Dashboard: http://localhost:2455" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Warning "[ERROR] 'uv' was not found in PATH."
    Write-Host "Install uv by running:" -ForegroundColor Yellow
    Write-Host "powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
    exit 1
}

uv run codex-lb @args
