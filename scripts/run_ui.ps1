# Start the Streamlit UI from the project root (opens http://localhost:8501).
# Use Continue — Streamlit logs "Uvicorn server started" on stderr; Stop would abort the script.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
$venvStreamlit = Join-Path $Root ".venv\Scripts\streamlit.exe"

if (-not (Test-Path $venvStreamlit)) {
    Write-Host "Virtual env not found. Run: python -m venv .venv; pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $Root "data\processed\restaurants.parquet"))) {
    Write-Host "No cached data. Running ingestion first..." -ForegroundColor Yellow
    $env:PYTHONPATH = "src"
    & $venvPython -m app.ingest
}

# Stop a stale Streamlit on 8501 so code changes always load
$portProc = @(Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    Where-Object { $_ -is [int] -and $_ -gt 0 })
if ($portProc.Count -gt 0) {
    Write-Host "Stopping previous Streamlit on port 8501..." -ForegroundColor Yellow
    $portProc | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}

Write-Host "Starting Streamlit at http://localhost:8501 ..." -ForegroundColor Green
Write-Host "If the browser does not open, paste that URL into Chrome/Edge manually." -ForegroundColor Cyan
$env:PYTHONPATH = "src"
$mainPy = Join-Path $Root "src\app\main.py"
& $venvStreamlit run $mainPy --server.port 8501 --browser.gatherUsageStats false
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Host "Streamlit exited with code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
