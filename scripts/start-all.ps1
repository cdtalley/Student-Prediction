# Start both FastAPI backend and Next.js frontend
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "Starting Student Prediction Analytics..." -ForegroundColor Cyan

# Start FastAPI in background
$env:PYTHONPATH = $projectRoot
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    $env:PYTHONPATH = $using:projectRoot
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
}

Start-Sleep -Seconds 2

# Start Next.js
Write-Host "API: http://localhost:8000" -ForegroundColor Green
Write-Host "Web: http://localhost:3000" -ForegroundColor Green
Set-Location "$projectRoot\web"
npm run dev
