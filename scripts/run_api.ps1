# FastAPI only — http://127.0.0.1:8000
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "src"
$env:API_RELOAD = "1"
& (Join-Path $Root ".venv\Scripts\python.exe") -m app.api.main
