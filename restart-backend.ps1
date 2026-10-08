# ============================================================
# restart-backend.ps1
# Kills the running Flask process, restarts it, and opens Vite
# in a separate PowerShell window.
# ============================================================

$projectRoot = "C:\Users\EDSG-JOOPSA\Documents\Apps\eco-flask-quick-login-db-control\eco"

Write-Host "Stopping existing Flask process..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force
        Write-Host "  Killed PID $($_.OwningProcess)"
    }
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Milliseconds 500

Write-Host "Stopping existing Vite process..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force
        Write-Host "  Killed PID $($_.OwningProcess)"
    }

Start-Sleep -Milliseconds 500

# --- Launch Flask in a new PowerShell window ---
Write-Host "Starting Flask backend on http://127.0.0.1:5000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot'; " +
    "Write-Host '=== FLASK BACKEND ===' -ForegroundColor Cyan; " +
    "py -3.12 backend\app.py"
)

# --- Wait for Flask to bind to port 5000 ---
Write-Host "Waiting for Flask to be ready..."
$flaskReady = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    $listening = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
    if ($listening) {
        $flaskReady = $true
        break
    }
}

if ($flaskReady) {
    Write-Host "  Flask is up." -ForegroundColor Green
} else {
    Write-Host "  WARNING: Flask did not bind to port 5000 within 15 seconds." -ForegroundColor Red
}

# --- Launch Vite in a new PowerShell window ---
Write-Host "Starting Vite frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot'; " +
    "Write-Host '=== VITE FRONTEND ===' -ForegroundColor Cyan; " +
    "npm run dev"
)

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " Both services launched in separate windows." -ForegroundColor Green
Write-Host "  Backend:  http://127.0.0.1:5000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Close those two windows to stop the servers."