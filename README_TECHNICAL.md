# 山东大学深空预测平台 - 技术文档

## 1. 项目概述

山东大学深空预测平台是一个集成了多个AI驱动的天文数据分析与处理工具的综合性项目。旨在为天文学研究者提供便捷的数据获取、目标检测、光谱分类和恒星参数化等功能。项目采用微服务化的前端和后端组件，通过统一的导航门户进行访问。

本文档主要面向开发者，提供项目的技术架构、模块详情、部署指南和贡献方式。

## 2. 系统架构

项目整体采用多模块、多仓库（逻辑上，物理上在同一根目录下）的方式组织，主要包括：

*   **导航门户 (Navigation Portal)**: 静态HTML/CSS/JS页面，作为所有子系统的统一入口。
*   **AI 应用模块**: 包括 AstroYOLO, MSPC-Net, MSTAR 分类，各自拥有独立的前端界面，后端逻辑可能内嵌或独立（具体视各模块实现）。
*   **天文数据综合处理平台**: 包含独立的Vue.js前端和Python Flask后端，提供数据下载、处理和文件管理服务。

所有服务均可通过本地脚本启动和管理。

## 3. 技术栈

*   **前端**: HTML, CSS, JavaScript, Vue.js (用于数据处理平台及可能的AI模块前端)
*   **后端 (数据处理平台)**: Python 3.9/3.10, Flask
*   **AI 模型**: TensorFlow/Keras, PyTorch (具体视各AI模块)
*   **开发与构建工具**: Node.js, npm, Conda
*   **脚本**: Windows PowerShell (.ps1)

## 4. 项目结构

```
. (e:\2025-undergrad-astro-frontend-mengjunyu)
├── navigation-portal/        # 导航门户 (静态站点)
│   ├── images/
│   ├── index.html
│   └── style.css
├── astroyolo/                # AstroYOLO 项目 (前端 + 可能的后端/模型)
├── mspc-net/                 # MSPC-Net 项目 (前端 + 可能的后端/模型)
├── mstar-classification-frontend/ # MSTAR 分类前端 (Vue/React等)
├── 数据处理/                   # 天文数据综合处理平台
│   ├── backend/              # 后端 (Flask API)
│   │   ├── app.py            # Flask 应用主文件
│   │   ├── requirements.txt  # Python 依赖
│   │   └── uploads/          # 用户上传/下载文件存储目录
│   └── frontend/             # 前端 (Vue.js)
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   ├── pages/        # 主要页面组件 (DESIPage, JPlusPage, etc.)
│       │   ├── router/       # Vue Router 配置
│       │   └── main.js       # Vue 应用入口
│       ├── package.json      # Node.js 依赖
│       └── vue.config.js   # Vue CLI 配置
├── start-all-projects.ps1    # 统一启动脚本
├── start-astroyolo-frontend.ps1 # AstroYOLO 启动脚本
├── start-mspcnet-frontend.ps1  # MSPC-Net 启动脚本
├── start-mstar-frontend.ps1   # MSTAR 启动脚本
├── README.md                 # 项目整体介绍 (偏用户/故事性)
└── README_TECHNICAL.md       # 本技术文档
```

## 5. 环境搭建与运行

### 5.1. 先决条件

*   Git
*   Conda (Anaconda or Miniconda)
*   Node.js (LTS version recommended) and npm

### 5.2. 安装步骤

1.  **克隆仓库**:
    ```bash
    git clone <your-repository-url>
    cd 2025-undergrad-astro-frontend-mengjunyu
    ```

2.  **后端环境 (数据处理平台)**:
    *   创建并激活 Conda 环境 (命名为 `astronn`):
        ```bash
        conda create -n astronn python=3.10
        conda activate astronn
        ```
    *   安装依赖:
        ```bash
        cd "数据处理/backend"
        pip install -r requirements.txt
        cd ../..
        ```

3.  **前端环境 (所有前端项目)**:
    *   **数据处理前端**:
        ```bash
        cd "数据处理/frontend"
        npm install
        cd ../..
        ```
    *   **MSTAR 分类前端**:
        ```bash
        cd mstar-classification-frontend
        npm install
        cd ..
        ```
    *   (类似地为 `astroyolo` 和 `mspc-net` 的前端部分执行 `npm install`)

### 5.3. 运行项目

*   **统一启动 (推荐)**:
    在项目根目录执行 PowerShell 脚本:
    ```powershell
    .\start-all-projects.ps1
    ```
    该脚本会尝试按预设端口启动所有服务。请查看脚本输出以确认各服务状态和访问URL。

*   **单独启动模块**:
    可以进入各模块目录，参照其独立的启动脚本 (如 `start-mstar-frontend.ps1`) 或标准命令运行：
    *   Flask 后端: `conda activate astronn && python app.py` (在 `数据处理/backend` 目录)
    *   Vue.js 前端: `npm run dev` 或 `npm run serve` (在各前端项目目录)

### 5.4. 默认端口

*   导航门户: `http://localhost:8000`
*   数据处理前端: `http://localhost:9000`
*   数据处理后端 API: `http://localhost:5003`
*   AstroYOLO 前端: `http://localhost:8083`
*   MSPC-Net 前端: `http://localhost:8081`
*   MSTAR 分类前端: `http://localhost:8082`

## 6. 核心模块详解

### 6.1. 导航门户 (`navigation-portal`)

*   **技术**: 纯静态 HTML, CSS, JavaScript。
*   **功能**: 提供到各个子系统和数据处理模块的链接。

### 6.2. AstroYOLO (`astroyolo`)

*   **核心技术**: Hybrid CNN-Transformer 目标检测模型。
*   **目标**: 自动检测蓝离水平支星 (BHBs)。
*   **接口**: 前端应用，端口 `8083`。

### 6.3. MSPC-Net (`mspc-net`)

*   **核心技术**: 基于多尺度部分卷积的光谱分类模型。
*   **目标**: 自动天文光谱分类。
*   **接口**: 前端应用，端口 `8081`。

### 6.4. MSTAR 分类 (`mstar-classification-frontend`)

*   **核心技术**: 深度多模态网络 (Transformer融合光谱与光度图像)。
*   **目标**: M型恒星亚型分类。
*   **接口**: 前端应用，端口 `8082`。

### 6.5. 天文数据综合处理平台 (`数据处理/`)

#### 6.5.1. 后端 (`数据处理/backend/`)

*   **框架**: Flask (Python)
*   **运行端口**: `5003`
*   **主要 API 端点**:
    *   `POST /api/desi/download`: 接收DESI下载任务参数，启动异步下载。
        *   请求体 (JSON): `{ "targets": [...], "saveDir": "...", ... }`
        *   响应 (JSON): `{ "task_id": "..." }`
    *   `POST /api/jplus/download`: J-PLUS下载任务。
    *   `POST /api/panstarrs/download`: Pan-STARRS下载任务。
    *   `GET /api/status/<task_id>`: 查询异步任务状态。
        *   响应 (JSON): `{ "status": "PENDING|PROCESSING|COMPLETED|FAILED", "progress": %, "message": "..." }`
    *   `GET /api/files`: 列出 `uploads/` 目录下的文件和子目录。
        *   可选查询参数: `path` (相对于 `uploads/` 的子路径)
        *   响应 (JSON): `[{ "name": "...", "type": "file|directory", "size": bytes, "last_modified": "..." }, ...]`
    *   `GET /api/download/<path:file_path>`: 下载指定路径的文件 (路径相对于 `uploads/`)。
*   **文件存储**: 下载的文件默认保存在 `数据处理/backend/uploads/` 目录下，按用户指定的子目录组织。
*   **环境**: 需在 `astronn` Conda 环境 (Python 3.9/3.10) 下运行。

#### 6.5.2. 前端 (`数据处理/frontend/`)

*   **框架**: Vue.js (Vue 3 with Quasar Framework)
*   **运行端口**: `9000`
*   **主要功能页面**:
    *   `DESIPage.vue`, `JPlusPage.vue`, `PanSTARRSPage.vue`: 各巡天项目的数据下载配置与任务提交界面。
    *   `FilesPage.vue`: 文件管理器，用于浏览和下载后端 `uploads/` 目录中的文件。
*   **状态管理**: Pinia (或 Vuex, 具体视项目配置)
*   **路由**: Vue Router, 配置文件在 `src/router/routes.js`。
*   **API交互**: 使用 `fetch` 或 `axios` 调用运行在 `http://localhost:5003` 的后端API。

## 7. 启动脚本说明

*   **`start-all-projects.ps1`**: 核心启动脚本，负责：
    1.  激活 `astronn` Conda 环境并启动数据处理后端。
    2.  依次启动数据处理前端、AstroYOLO前端、MSPC-Net前端、MSTAR前端和导航门户。
    3.  每个前端启动前会检查指定端口是否被占用，若被占用则尝试使用默认端口启动。
*   **各子项目启动脚本 (e.g., `start-mstar-frontend.ps1`)**: 通常包含：
    1.  设置工作目录到对应前端项目。
    2.  检查 `node_modules` 是否存在，不存在则运行 `npm install`。
    3.  检查预设端口是否被占用，并据此决定是否使用 `--port` 参数启动 `npm run dev`。

## 8. 贡献指南

欢迎对本项目进行贡献！

1.  **Fork 仓库** 并从 `main` 或 `develop` 分支创建您的特性分支。
2.  **代码风格**: 
    *   Vue/JS: 遵循项目已配置的 ESLint 规则。
    *   Python: 遵循 PEP 8。
3.  **提交 PR**: 确保您的代码通过了所有检查，并清晰描述您的更改。
4.  **Issue跟踪**: 使用 GitHub Issues 报告BUG或提出功能建议。

## 9. 故障排查

*   **端口冲突**: 检查启动脚本输出，确认是否有端口被占用的警告。可以手动修改脚本中的 `$PORT`变量，或关闭占用端口的程序。
*   **依赖问题**: 确保所有 `requirements.txt` (Python) 和 `package.json` (Node.js) 中的依赖都已正确安装在对应的环境中。
*   **Conda环境问题**: 确保在运行Python后端或脚本时已激活正确的Conda环境 (如 `astronn`)。

## 10. 致谢

本平台作为山东大学数据结构课程设计项目，主要贡献者及分工：

*   **孟俊宇**: AstroYOLO; DESI (数据处理平台)
*   **何准**: MSTAR; Jplus (数据处理平台)
*   **徐王炜梵**: MSPC-Net; PanSTARRS (数据处理平台)

感谢所有为本项目提供支持和贡献的老师与同学。

---
*本文档旨在提供技术概览，具体实现细节请参考各模块源代码。*
