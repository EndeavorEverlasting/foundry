# Wipe local dev state (stops containers and deletes volumes).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    docker compose -f infra/compose/docker-compose.yml down -v
    Write-Host "Foundry local state wiped." -ForegroundColor Yellow
}
finally { Pop-Location }
