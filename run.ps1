Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      J.A.R.V.I.S. AUTONOMOUS VOICE & HUD ENGINE        " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

$env:PYTHONPATH = "."

# Start Backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='.'; python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload"

# Start Frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd client; npm run dev"

Start-Sleep -Seconds 3
Write-Host "`nJ.A.R.V.I.S. IS ONLINE!" -ForegroundColor Green
Write-Host "HUD Interface: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API / WS Core: http://localhost:8000" -ForegroundColor Cyan

Start-Process "http://localhost:3000"
