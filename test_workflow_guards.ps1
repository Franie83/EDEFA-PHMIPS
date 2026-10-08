$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod http://localhost:5000/api/auth/login -Method Post -Body '{"username":"superadmin","password":"EDEFA-SUPER-2026"}' -ContentType "application/json" -WebSession $s | Out-Null

function Test-Guard {
  param([string]$Label, [string]$Url, [string]$Body)
  Write-Host ""
  Write-Host $Label -ForegroundColor Cyan
  try {
    $resp = Invoke-WebRequest $Url -Method Post -Body $Body -ContentType "application/json" -WebSession $s -UseBasicParsing
    Write-Host "  Status:" $resp.StatusCode -ForegroundColor Green
    $preview = $resp.Content.Substring(0, [Math]::Min(200, $resp.Content.Length))
    Write-Host "  Body:" $preview
  } catch [System.Net.WebException] {
    $response = $_.Exception.Response
    if ($response) {
      $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
      $body = $reader.ReadToEnd()
      $code = [int]$response.StatusCode
      $color = "Yellow"
      if ($code -ne 400) { $color = "Red" }
      Write-Host "  Status:" $code -ForegroundColor $color
      Write-Host "  Body:" $body
    } else {
      Write-Host "  Error:" $_.Exception.Message -ForegroundColor Red
    }
  }
}

Write-Host ""
Write-Host "--- Creating fresh unverified hazard ---" -ForegroundColor Magenta
$newHazard = Invoke-RestMethod "http://localhost:5000/api/hazards" -Method Post -Body '{"title":"Workflow guard test hazard","category":"Gully erosion","lga":"Oredo","community":"Test","description":"clean test","severity":"MEDIUM"}' -ContentType "application/json" -WebSession $s
$hid = $newHazard.id
Write-Host "Created:" $hid "with status:" $newHazard.status -ForegroundColor Green

Test-Guard ("Test 1 - assess unverified hazard " + $hid + " (expect 400)") "http://localhost:5000/api/hazards/$hid/assess" '{"severity_score":7,"urgency_score":7,"exposure_score":7,"impact_score":7,"escalation_risk_score":7}'

Test-Guard ("Test 2 - plan intervention for unverified hazard " + $hid + " (expect 400)") "http://localhost:5000/api/hazards/$hid/intervention" '{"title":"Should be blocked"}'

Write-Host ""
Write-Host "--- Verifying $hid ---" -ForegroundColor Magenta
$verified = Invoke-RestMethod "http://localhost:5000/api/hazards/$hid/verify" -Method Post -Body '{"is_valid":true,"verification_notes":"Approved for testing"}' -ContentType "application/json" -WebSession $s
Write-Host "Verified. Status:" $verified.hazard.status -ForegroundColor Green

Test-Guard ("Test 4 - plan intervention after verify but before assess " + $hid + " (expect 400)") "http://localhost:5000/api/hazards/$hid/intervention" '{"title":"Should be blocked until assessed"}'

Write-Host ""
Write-Host "--- Assessing $hid ---" -ForegroundColor Magenta
$assessed = Invoke-RestMethod "http://localhost:5000/api/hazards/$hid/assess" -Method Post -Body '{"severity_score":7,"urgency_score":7,"exposure_score":7,"impact_score":7,"escalation_risk_score":7}' -ContentType "application/json" -WebSession $s
Write-Host "Assessed. Status:" $assessed.hazard.status -ForegroundColor Green

Test-Guard ("Test 6 - plan intervention after verified+assessed " + $hid + " (expect 201)") "http://localhost:5000/api/hazards/$hid/intervention" '{"title":"Legitimate intervention","estimated_cost_ngn":25000000}'

Test-Guard ("Test 7 - plan intervention twice " + $hid + " (expect 400 duplicate)") "http://localhost:5000/api/hazards/$hid/intervention" '{"title":"Duplicate attempt"}'

Write-Host ""
Write-Host "--- Summary ---" -ForegroundColor Magenta
Write-Host "Test 1 should be 400 (assess unverified)"
Write-Host "Test 2 should be 400 (intervention unverified)"
Write-Host "Test 4 should be 400 (intervention unassessed)"
Write-Host "Test 6 should be 201 (all guards passed)"
Write-Host "Test 7 should be 400 (duplicate intervention)"
