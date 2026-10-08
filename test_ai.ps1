# test_ai.ps1
$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod http://localhost:5000/api/auth/login `
  -Method Post `
  -Body '{"username":"superadmin","password":"EDEFA-SUPER-2026"}' `
  -ContentType "application/json" `
  -WebSession $s | Out-Null

$body = '{"query":"how many critical projects exist"}'
$resp = Invoke-RestMethod http://localhost:5000/api/ai/query `
  -Method Post `
  -Body $body `
  -ContentType "application/json" `
  -WebSession $s

Write-Host "is_ai_powered:" $resp.is_ai_powered
Write-Host "answer:" $resp.answer