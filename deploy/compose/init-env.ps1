Param()

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Copy-IfExists {
    param(
        [string]$Source,
        [string]$Destination
    )
    if (Test-Path $Source) {
        Copy-Item -Force $Source $Destination
        return $true
    }
    return $false
}

if (Test-Path .env) {
    Write-Output ".env already exists. Skipping."
    exit 0
}

if (Copy-IfExists ".env.example" ".env") { exit 0 }
if (Copy-IfExists "env.example" ".env") { exit 0 }

$content = @"
REGISTRY=local
TAG=dev
APP_VERSION=0.1.0
GIT_SHA=dev
API_HOST=api.localhost
TRAEFIK_HOST=traefik.localhost
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=app
"@

Set-Content -NoNewline -Path ".env" -Value $content
Write-Output ".env created with defaults."


