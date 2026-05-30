# TastePilot — FastAPI backend + React frontend (Vite)
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual env not found. Run: python -m venv .venv; pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $Root "data\processed\restaurants.parquet"))) {
    Write-Host "No cached data. Running ingestion..." -ForegroundColor Yellow
    $env:PYTHONPATH = "src"
    & $venvPython -m app.ingest
}

$env:PYTHONPATH = "src"

Write-Host "Starting API at http://127.0.0.1:8000 ..." -ForegroundColor Green
$apiJob = Start-Job -ScriptBlock {
    param($Root)
    Set-Location $Root
    $env:PYTHONPATH = "src"
    $env:API_RELOAD = "1"
    & (Join-Path $Root ".venv\Scripts\python.exe") -m app.api.main
} -ArgumentList $Root

Start-Sleep -Seconds 2

$frontendDir = Join-Path $Root "frontend"
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js/npm not found. Install from https://nodejs.org/ then run: cd frontend; npm install; npm run dev" -ForegroundColor Red
    Write-Host "API is still running in the background job." -ForegroundColor Yellow
    Wait-Job $apiJob
    exit 1
}
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies (npm install)..." -ForegroundColor Yellow
    Set-Location $frontendDir
    npm install
    Set-Location $Root
}

Write-Host "Starting React at http://localhost:5173 ..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop both servers." -ForegroundColor Cyan
Set-Location $frontendDir
try {
    npm run dev
} finally {
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -Force -ErrorAction SilentlyContinue
}
