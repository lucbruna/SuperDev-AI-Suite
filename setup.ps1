# SuperDev AI Suite - Setup Script for Windows
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SuperDev AI Suite v5.0 - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/4] Verificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERRO: Docker nao esta rodando! Inicie o Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "  OK" -ForegroundColor Green

# Step 2: Copy .env if not exists
Write-Host "[2/4] Configurando variaveis de ambiente..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  .env criado a partir de .env.example" -ForegroundColor Green
} else {
    Write-Host "  .env ja existe" -ForegroundColor Green
}

# Step 3: Build and start services
Write-Host "[3/4] Construindo e iniciando servicos..." -ForegroundColor Yellow
docker compose build --parallel
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERRO: Falha no build!" -ForegroundColor Red
    exit 1
}
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERRO: Falha ao iniciar servicos!" -ForegroundColor Red
    exit 1
}
Write-Host "  OK" -ForegroundColor Green

# Step 4: Health check
Write-Host "[4/4] Aguardando servicos ficarem prontos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "  Backend: ONLINE (http://localhost:8000)" -ForegroundColor Green
} catch {
    Write-Host "  Backend: ainda iniciando..." -ForegroundColor Yellow
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000" -TimeoutSec 10
    Write-Host "  Frontend: ONLINE (http://localhost:3000)" -ForegroundColor Green
} catch {
    Write-Host "  Frontend: ainda iniciando..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SuperDev AI Suite pronto!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Grafana:  http://localhost:3001 (admin/admin)" -ForegroundColor White
Write-Host "  Traefik:  http://localhost:8081" -ForegroundColor White
Write-Host ""
Write-Host "  Login: admin@superdev.com / SuperDev@2025" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Comandos uteis:" -ForegroundColor Gray
Write-Host "    docker compose logs -f backend    # Logs do backend" -ForegroundColor Gray
Write-Host "    docker compose down               # Parar tudo" -ForegroundColor Gray
Write-Host "    docker compose up -d              # Subir novamente" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
