# Foundry bootstrap (PowerShell)
# Idempotent: safe to run repeatedly.

$ErrorActionPreference = "Stop"

Write-Host "==> Foundry bootstrap (Windows / PowerShell)" -ForegroundColor Cyan

# --- Tool checks -------------------------------------------------------------
function Require-Tool {
    param([string]$Name, [string]$Hint)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Error "Missing tool: $Name. $Hint"
        exit 1
    }
    Write-Host "  [ok] $Name"
}

Require-Tool "node"   "Install Node 20+ (https://nodejs.org/)"
Require-Tool "pnpm"   "Install pnpm: 'corepack enable && corepack prepare pnpm@9 --activate'"
Require-Tool "uv"     "Install uv: 'powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"'"
Require-Tool "docker" "Install Docker Desktop"
Require-Tool "git"    "Install Git"

# --- Env file ---------------------------------------------------------------
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    if (-not (Test-Path ".env")) {
        Write-Host "==> Creating .env from .env.example"
        Copy-Item ".env.example" ".env"
    }

    Write-Host "==> Installing JS dependencies (pnpm install)"
    pnpm install

    Write-Host "==> Installing Python dependencies (uv sync)"
    uv sync

    Write-Host "==> Starting Postgres + Redis"
    docker compose -f infra/compose/docker-compose.yml up -d postgres redis

    Write-Host "==> Waiting for Postgres to be healthy..."
    $retries = 30
    while ($retries -gt 0) {
        $status = docker compose -f infra/compose/docker-compose.yml ps postgres --format json | ConvertFrom-Json
        if ($status.Health -eq "healthy") { break }
        Start-Sleep -Seconds 2
        $retries--
    }

    Write-Host "==> Running DB migrations"
    uv run --package foundry-api alembic -c infra/migrations/alembic.ini upgrade head

    Write-Host ""
    Write-Host "Done. Next steps:" -ForegroundColor Green
    Write-Host "  pnpm compose:up     # bring up api + worker + web"
    Write-Host "  pnpm dev            # run web locally against containerized api"
}
finally {
    Pop-Location
}
