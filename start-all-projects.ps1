# 天文项目启动脚本
# 此脚本将启动所有三个项目的前端和后端服务

# 设置项目根目录
$ROOT_DIR = "e:\2025-undergrad-astro-frontend-mengjunyu"

# 设置端口配置
$PORTS = @{
    "astroyolo_frontend" = 8083
    "astroyolo_backend" = 5000
    "mspcnet_frontend" = 8081
    "mspcnet_backend" = 5001
    "mstar_frontend" = 8082
    "mstar_backend" = 5002
    "data_processing_frontend" = 9000
    "data_processing_backend" = 5003
}
$PORT_NAVIGATION_PORTAL = 8000 # 导航门户端口

# 清屏
Clear-Host
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "         天文项目统一启动脚本                     " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 启动导航门户服务
Write-Host "正在启动导航门户服务 (端口 $PORT_NAVIGATION_PORTAL)..." -ForegroundColor Yellow
$navigationPortalScript = @"
cd '$ROOT_DIR\navigation-portal'
Write-Host '准备启动导航门户 HTTP 服务器...' -ForegroundColor Yellow
python -m http.server $PORT_NAVIGATION_PORTAL
Read-Host '按回车键退出导航门户服务器'
"@
Start-Process powershell -ArgumentList "-NoProfile", "-Command", $navigationPortalScript

# 检查并结束当前正在运行的进程
Write-Host "正在检查并清理现有进程..." -ForegroundColor Yellow
Stop-Process -Name "node" -ErrorAction SilentlyContinue
Stop-Process -Name "python" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 检查端口是否被占用
function Test-PortInUse {
    param(
        [int]$Port
    )
    
    $connections = netstat -ano | findstr ":$Port"
    return [bool]$connections
}

# 检查关键端口
foreach ($port in $PORTS.Values) {
    if (Test-PortInUse -Port $port) {
        Write-Host "警告: 端口 $port 已被占用，可能会影响项目启动" -ForegroundColor Yellow
    }
}

# 检查 Node.js 和 npm 是否已安装
$npmVersion = npm -v 2>$null
if (-not $npmVersion) {
    Write-Host "错误: 未检测到 npm！请先安装 Node.js 和 npm。" -ForegroundColor Red
    exit 1
}
Write-Host "检测到 npm 版本: $npmVersion" -ForegroundColor Green

# 检查 Python 是否已安装
$pythonVersion = python --version 2>&1
if (-not $pythonVersion) {
    Write-Host "错误: 未检测到 Python！请先安装 Python。" -ForegroundColor Red
    exit 1
}
Write-Host "检测到 Python 版本: $pythonVersion" -ForegroundColor Green

# 安装必要的Python包
function Install-PythonPackages {
    Write-Host "正在检查并安装必要的Python包..." -ForegroundColor Yellow
    $condaPath = "conda"
    
    # 尝试使用conda安装包
    try {
        Write-Host "使用conda安装必要的包..." -ForegroundColor Yellow
        & $condaPath install -n astroyolo -y uvicorn fastapi 2>&1 | Out-Null
        & $condaPath install -n astroyolo -y pytorch torchvision -c pytorch 2>&1 | Out-Null
        & $condaPath install -n astroyolo -y astropy pillow pandas 2>&1 | Out-Null
        Write-Host "Python包安装完成" -ForegroundColor Green
    } catch {
        Write-Host "conda安装包时出错: $_" -ForegroundColor Red
        Write-Host "请手动安装所需的包: uvicorn, fastapi, pytorch, astropy, pillow, pandas" -ForegroundColor Yellow
    }
}

# Install-PythonPackages  # 跳过安装步骤

# 更新导航页面端口
Write-Host "正在更新导航页面端口配置..." -ForegroundColor Cyan
$navPageContent = Get-Content "$ROOT_DIR\navigation-portal\index.html" -Raw
$navPageContent = $navPageContent -replace 'http://localhost:8080', "http://localhost:$($PORTS["astroyolo_frontend"])"
$navPageContent = $navPageContent -replace 'http://localhost:8081', "http://localhost:$($PORTS["mspcnet_frontend"])"
$navPageContent = $navPageContent -replace 'http://localhost:8082', "http://localhost:$($PORTS["mstar_frontend"])"
$navPageContent = $navPageContent -replace 'http://localhost:8083', "http://localhost:$($PORTS["astroyolo_frontend"])"
Set-Content -Path "$ROOT_DIR\navigation-portal\index.html" -Value $navPageContent

# 创建环境变量文件
# AstroYOLO环境变量
$astroyoloEnvContent = @"
# AstroYOLO前端环境变量
API_BASE_URL=http://localhost:$($PORTS["astroyolo_backend"])
VUE_PORT=$($PORTS["astroyolo_frontend"])
"@
Set-Content -Path "$ROOT_DIR\astroyolo\.env.local" -Value $astroyoloEnvContent

# MSPC-Net环境变量
$mspcnetEnvContent = @"
# MSPC-Net前端环境变量
API_BASE_URL=http://localhost:$($PORTS["mspcnet_backend"])
"@
Set-Content -Path "$ROOT_DIR\mspc-net\frontend_test\.env.local" -Value $mspcnetEnvContent

# MSTAR环境变量
$mstarEnvContent = @"
# MSTAR前端环境变量
FASTAPI_URL=http://localhost:$($PORTS["mstar_backend"])
"@
Set-Content -Path "$ROOT_DIR\mstar-classification-frontend\.env.local" -Value $mstarEnvContent

# 创建AstroYOLO后端启动命令
Write-Host "正在启动 AstroYOLO 后端服务 (端口$($PORTS["astroyolo_backend"]))..." -ForegroundColor Yellow
$astroyoloBackendScript = @"
cd '$ROOT_DIR\astroyolo'
Write-Host '准备启动 AstroYOLO 后端...' -ForegroundColor Yellow
# 设置环境变量避免OpenMP警告
Set-Item -Path 'env:KMP_DUPLICATE_LIB_OK' -Value 'TRUE'
Write-Host '正在启动 AstroYOLO 后端服务 (端口$($PORTS["astroyolo_backend"]))...' -ForegroundColor Green
# 简化的启动方式
conda activate astroyolo
python app.py
Read-Host '按回车键退出'
"@
Start-Process powershell -ArgumentList "-Command", $astroyoloBackendScript

# 等待一会儿，确保后端先启动
Start-Sleep -Seconds 3

# 启动MSPC-Net后端
Write-Host "正在启动 MSPC-Net 后端服务 (端口$($PORTS["mspcnet_backend"]))..." -ForegroundColor Yellow
$mspcnetBackendScript = @"
cd '$ROOT_DIR\mspc-net\backend'
Write-Host '准备启动 MSPC-Net 后端...' -ForegroundColor Yellow
# 设置环境变量避免OpenMP警告
Set-Item -Path 'env:KMP_DUPLICATE_LIB_OK' -Value 'TRUE'
Write-Host '正在启动 MSPC-Net 后端服务 (端口$($PORTS["mspcnet_backend"]))...' -ForegroundColor Green
# 简化的启动方式
conda activate astroyolo
python app_test.py
Read-Host '按回车键退出'
"@
Start-Process powershell -ArgumentList "-Command", $mspcnetBackendScript

# 启动MSTAR Classification后端
Write-Host "正在启动 MSTAR Classification 后端服务 (端口$($PORTS["mstar_backend"]))..." -ForegroundColor Yellow
$mstarBackendScript = @"
cd '$ROOT_DIR\mstar-classification-frontend'
Write-Host '准备启动 MSTAR Classification 后端...' -ForegroundColor Yellow
# 设置环境变量避免OpenMP警告
Set-Item -Path 'env:KMP_DUPLICATE_LIB_OK' -Value 'TRUE'
# 简化的启动方式
conda activate astroyolo
python app.py
Read-Host '按回车键退出'
"@
Start-Process powershell -ArgumentList "-Command", $mstarBackendScript

# 启动数据处理后端
Write-Host "正在启动数据处理后端服务 (端口$($PORTS["data_processing_backend"]))..." -ForegroundColor Yellow
$dataProcessingBackendScript = @"
cd '$ROOT_DIR\数据处理\astro_data_portal\backend'
Write-Host '准备启动数据处理后端...' -ForegroundColor Yellow
Set-Item -Path 'env:KMP_DUPLICATE_LIB_OK' -Value 'TRUE'
Set-Item -Path "env:PYTHONPATH" -Value "$ROOT_DIR\数据处理"
Write-Host "Temporarily setting PYTHONPATH for Data Processing Backend to: $($env:PYTHONPATH)" -ForegroundColor Magenta
Write-Host '正在启动数据处理后端服务 (端口$($PORTS["data_processing_backend"]))...' -ForegroundColor Green
conda activate astronn
python app.py
Read-Host '按回车键退出'
"@
Start-Process powershell -ArgumentList "-Command", $dataProcessingBackendScript

# 等待一会儿，确保后端先启动
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "正在启动所有前端服务..." -ForegroundColor Green

# 启动AstroYOLO前端
Write-Host "正在启动 AstroYOLO 前端服务 (端口$($PORTS["astroyolo_frontend"]))..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "& '$ROOT_DIR\start-astroyolo-frontend.ps1'; Read-Host '按回车键退出'"

# 启动MSPC-Net前端
Write-Host "正在启动 MSPC-Net 前端服务 (端口$($PORTS["mspcnet_frontend"]))..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "& '$ROOT_DIR\start-mspcnet-frontend.ps1'; Read-Host '按回车键退出'"

# 启动MSTAR前端
Write-Host "正在启动 MSTAR Classification Frontend 前端服务 (端口$($PORTS["mstar_frontend"]))..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "& '$ROOT_DIR\start-mstar-frontend.ps1'; Read-Host '按回车键退出'"

# 启动数据处理前端
Write-Host "正在启动数据处理前端服务 (端口$($PORTS["data_processing_frontend"]))..." -ForegroundColor Green
$dataProcessingFrontendScript = @"
cd '$ROOT_DIR\数据处理\astro_data_portal\frontend'
Write-Host '准备启动数据处理前端 (端口$($PORTS["data_processing_frontend"]))...请稍候，首次启动可能需要一些时间。' -ForegroundColor Yellow
npm install
npm run dev -- --port $($PORTS["data_processing_frontend"]) --host 0.0.0.0
Read-Host '按回车键退出'
"@
Start-Process powershell -ArgumentList "-Command", $dataProcessingFrontendScript

# 等待所有服务启动
Write-Host ""
Write-Host "正在等待所有服务启动..." -ForegroundColor Magenta
Start-Sleep -Seconds 15

# 打开导航页面
Write-Host "正在打开导航页面..." -ForegroundColor Cyan
Start-Process "$ROOT_DIR\navigation-portal\index.html"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "所有服务已启动！" -ForegroundColor Cyan
Write-Host "" 
Write-Host "* AstroYOLO 前端: http://localhost:$($PORTS["astroyolo_frontend"])" -ForegroundColor White
Write-Host "* AstroYOLO 后端: http://localhost:$($PORTS["astroyolo_backend"])" -ForegroundColor White
Write-Host "* MSPC-Net 前端: http://localhost:$($PORTS["mspcnet_frontend"])" -ForegroundColor White
Write-Host "* MSPC-Net 后端: http://localhost:$($PORTS["mspcnet_backend"])" -ForegroundColor White
Write-Host "* MSTAR Classification Frontend 前端: http://localhost:$($PORTS["mstar_frontend"])" -ForegroundColor White
Write-Host "* MSTAR Classification Frontend 后端: http://localhost:$($PORTS["mstar_backend"])" -ForegroundColor White
Write-Host "* 数据处理前端 (DESI): http://localhost:$($PORTS["data_processing_frontend"])/#/desi" -ForegroundColor White
Write-Host "* 数据处理前端 (J-PLUS): http://localhost:$($PORTS["data_processing_frontend"])/#/jplus" -ForegroundColor White
Write-Host "* 数据处理前端 (Pan-STARRS): http://localhost:$($PORTS["data_processing_frontend"])/#/panstarrs" -ForegroundColor White
Write-Host "* 数据处理前端 (文件管理): http://localhost:$($PORTS["data_processing_frontend"])/#/files" -ForegroundColor White
Write-Host "* 数据处理后端: http://localhost:$($PORTS["data_processing_backend"])" -ForegroundColor White
Write-Host ""
Write-Host "导航门户现已通过HTTP服务运行在: http://localhost:$PORT_NAVIGATION_PORTAL" -ForegroundColor Green
Write-Host "如果您需要手动打开导航页面，请在浏览器中访问: http://localhost:$PORT_NAVIGATION_PORTAL" -ForegroundColor Yellow
Write-Host ""
Write-Host "您可以关闭此窗口，但请保持其他窗口运行以维持服务正常运行。" -ForegroundColor Magenta
Write-Host ""
Write-Host "常见问题排查:" -ForegroundColor Yellow
Write-Host "1. 如果某个项目无法启动，请检查对应的命令窗口是否有错误信息" -ForegroundColor Yellow
Write-Host "2. AstroYOLO 项目可能需要较长时间加载模型，请耐心等待" -ForegroundColor Yellow
Write-Host "3. 如果浏览器缓存导致链接不正确，请尝试清除缓存或使用隐私模式" -ForegroundColor Yellow
Write-Host "4. 确保所有端口没有被其他应用占用" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按Ctrl+C退出此脚本" -ForegroundColor Yellow

# 保持脚本运行，直到用户手动关闭
while ($true) {
    Start-Sleep -Seconds 1
}