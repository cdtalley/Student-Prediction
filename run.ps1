# Student Prediction Analytics - Start API
# Run from project root: .\run.ps1
# Then in another terminal: cd web && npm run dev

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot

# Check if data and models exist
if (-not (Test-Path "$projectRoot\data\retention_data.csv")) {
    Write-Host "Data not found. Running train.py first..." -ForegroundColor Yellow
    $env:PYTHONPATH = $projectRoot
    python "$projectRoot\src\train.py"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "`nTraining complete. Starting API...`n" -ForegroundColor Green
}

$env:PYTHONPATH = $projectRoot
Write-Host "API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "In another terminal: cd web && npm run dev  (then open http://localhost:3000)`n" -ForegroundColor Gray
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
