# ============================================
# DEPLOY MODAL — Seminuevos Cozumel
# Requiere Python 3.12 instalado
# Corre en PowerShell: .\scripts\deploy-modal.ps1
# ============================================

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  MEGA SISTEMA IA — Deploy Modal" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# 1. Verificar Python 3.12
Write-Host "`n[1/5] Verificando Python 3.12..." -ForegroundColor Yellow
$python = $null
foreach ($cmd in @("python3.12", "py -3.12")) {
    try {
        $ver = & $cmd.Split()[0] $cmd.Split()[1..99] --version 2>&1
        if ($ver -like "*3.12*") { $python = $cmd; break }
    } catch {}
}

if (-not $python) {
    Write-Host "❌ Python 3.12 no encontrado." -ForegroundColor Red
    Write-Host "   Descarga: https://www.python.org/downloads/release/python-31210/" -ForegroundColor Yellow
    Write-Host "   Instala y vuelve a correr este script." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Python 3.12 encontrado: $python" -ForegroundColor Green

# 2. Crear venv si no existe
Write-Host "`n[2/5] Configurando entorno virtual..." -ForegroundColor Yellow
$venv = "$ROOT\.venv-modal"
if (-not (Test-Path $venv)) {
    & $python.Split()[0] $python.Split()[1..99] -m venv $venv
}
$pip = "$venv\Scripts\pip.exe"
$modal = "$venv\Scripts\modal.exe"
& $pip install modal --quiet
Write-Host "✅ Modal instalado" -ForegroundColor Green

# 3. Configurar token de Modal
Write-Host "`n[3/5] Configurando token Modal..." -ForegroundColor Yellow
$tokenId = "ak-gyKmmBBzJ3cH5RZ0B0f0Pq"
$tokenSecret = "as-M9jnUOrjaR6hhT6Mj0YLpS"
& $modal token set --token-id $tokenId --token-secret $tokenSecret
Write-Host "✅ Token configurado" -ForegroundColor Green

# 4. Crear secret con todas las credenciales
Write-Host "`n[4/5] Creando secret en Modal..." -ForegroundColor Yellow

# Leer .env
$envPath = "$ROOT\.env"
$envVars = @{}
Get-Content $envPath | Where-Object { $_ -match "^[A-Z]" -and $_ -notmatch "^#" } | ForEach-Object {
    $parts = $_ -split "=", 2
    if ($parts.Count -eq 2) { $envVars[$parts[0].Trim()] = $parts[1].Trim() }
}

$secretArgs = @("secret", "create", "mega-sistema-credentials", "--force")
foreach ($key in $envVars.Keys) {
    $secretArgs += "$key=$($envVars[$key])"
}

& $modal @secretArgs
Write-Host "✅ Secret creado con $($envVars.Count) variables" -ForegroundColor Green

# 5. Deploy
Write-Host "`n[5/5] Desplegando en Modal..." -ForegroundColor Yellow
Set-Location $ROOT
& $modal deploy app/main.py

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "  ✅ DEPLOY COMPLETADO" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "`nRevisa tu dashboard de Modal para obtener la URL:" -ForegroundColor Yellow
Write-Host "https://modal.com/apps" -ForegroundColor White
Write-Host "`nUna vez que tengas la URL, actualiza las herramientas de Retell:" -ForegroundColor Yellow
Write-Host "python scripts/update-retell-tools.py <TU_URL_MODAL>" -ForegroundColor White
