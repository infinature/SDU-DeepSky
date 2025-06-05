# AstroYOLO前端启动脚本
$ROOT_DIR = "e:\SDU-DeepSky"
$PORT = 8083

Write-Host "开始启动AstroYOLO前端..." -ForegroundColor Green
Set-Location -Path "$ROOT_DIR\astroyolo"

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
    Write-Host "正在启动AstroYOLO前端 (端口:$PORT)..." -ForegroundColor Green
    npm run dev -- --port $PORT
}
