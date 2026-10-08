$base = "http://localhost:5000"
$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# login as super admin
Invoke-RestMethod "$base/api/auth/login" -Method Post `
  -Body '{"username":"superadmin","password":"EDEFA-SUPER-2026"}' `
  -ContentType "application/json" -WebSession $s | Out-Null

Write-Host "`n=== BRANDING ===" -ForegroundColor Cyan
Invoke-RestMethod "$base/api/cms/branding" -WebSession $s | ConvertTo-Json -Depth 5

Write-Host "`n=== USERS ===" -ForegroundColor Cyan
$users = Invoke-RestMethod "$base/api/cms/users" -WebSession $s
Write-Host "Total users:" $users.Count

Write-Host "`n=== DB STATS ===" -ForegroundColor Cyan
Invoke-RestMethod "$base/api/cms/database/stats" -WebSession $s | ConvertTo-Json

Write-Host "`n=== BACKUPS ===" -ForegroundColor Cyan
$bk = Invoke-RestMethod "$base/api/cms/database/backups" -WebSession $s
Write-Host "Backups:" $bk.Count

Write-Host "`n=== PUBLIC SIGNUP ===" -ForegroundColor Cyan
$newUser = '{"name":"Test User","username":"testuser01","email":"test01@example.com","password":"testpass123"}'
Invoke-RestMethod "$base/api/public/signup" -Method Post -Body $newUser `
  -ContentType "application/json" | ConvertTo-Json