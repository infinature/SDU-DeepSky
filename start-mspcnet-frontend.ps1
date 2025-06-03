# MSPC-Net前端启动脚本
$ROOT_DIR = "e:\2025-undergrad-astro-frontend-mengjunyu"
$PORT = 8081

Write-Host "开始启动MSPC-Net前端..." -ForegroundColor Green
Set-Location -Path "$ROOT_DIR\mspc-net\frontend_test"

# 检查是否存在node_modules
if (-not (Test-Path node_modules)) {
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    npm install
}

# 检查端口是否被占用
$isPortUsed = netstat -ano | Select-String ":$PORT "
if ($isPortUsed) {
    Write-Host "警告: 端口 $PORT 已被占用，将使用默认端口..." -ForegroundColor Yellow
    npm run dev
} else {
    Write-Host "正在启动MSPC-Net前端 (端口:$PORT)..." -ForegroundColor Green
    npm run dev -- --port $PORT
}
