# 山东大学深空预测平台：探索宇宙的新篇章

## 📖 引言：星辰大海的召唤与智能的火花

宇宙，一片无垠的星辰大海，充满了未解之谜和无限可能。从古至今，人类对星空的向往从未停止。如今，随着大型巡天项目的不断涌现，我们正以前所未有的速度获取着海量的天文数据。这既是巨大的机遇，也带来了前所未有的挑战：如何从这数据洪流中高效地提取有价值的信息，洞察宇宙的奥秘？

**山东大学深空预测平台** 我们梦想打造一个集成化的智能环境，将前沿的深度学习模型与便捷的数据处理工具相结合，让每一位对宇宙充满好奇心的人，无论是资深天文学家还是初入科研领域的学子，都能轻松驾驭这些强大的工具，开启属于自己的探索之旅。


## ✨ 平台意义：为何选择我们？

在天文学研究日益依赖大数据和人工智能的今天，本平台致力于：

*   **🌟 降低科研门槛**：将复杂的AI模型封装为易用的工具，让研究者无需深厚的编程背景也能利用最先进的技术进行天体目标检测、光谱分析和恒星分类。
*   **🔗 构建集成生态**：提供从数据获取、处理、模型应用到结果可视化的“一站式”服务，打破不同工具间的壁垒，提升科研效率。
*   **🚀 驱动科学发现**：通过自动化和智能化的分析，帮助研究者从海量数据中快速识别特殊天体、发现新的天文现象，加速科学突破的进程。
*   **🎓 赋能教育创新**：作为山东大学数据结构课程设计的成果，本平台也旨在为天文学及相关专业的学生提供一个实践和学习AI应用的绝佳场所，激发他们对交叉学科研究的兴趣。
*   **🤝 促进开放共享**：我们希望这个平台能成为一个起点，鼓励更多人参与到天文AI工具的开发与共享中，共同推动天文学的发展。

## 🛠️ 核心组件：平台的四大支柱

本平台由以下几个核心部分组成，通过统一的导航门户进行访问：

1.  **🌌 导航中枢 (Navigation Portal)**
    *   **位置**: `navigation-portal/`
    *   **描述**: 平台的统一入口，提供美观直观的界面，引导用户访问各个子系统和功能模块。它是连接所有智慧工具的枢纽。

2.  **🔭 AstroYOLO：蓝离水平支星的智能捕手**
    *   **位置**: `astroyolo/`
    *   **技术**: 混合CNN-Transformer深度学习目标检测模型。
    *   **使命**: 蓝离水平支星（BHBs）是研究银河系结构和质量的理想示踪物。AstroYOLO致力于从海量图像数据中快速、准确地自动识别BHBs，克服人工筛选的局限，为银河系研究提供更完整的数据支持。

3.  **✨ MSPC-Net：多尺度光谱的智能解读**
    *   **位置**: `mspc-net/`
    *   **技术**: 基于多尺度部分卷积的光谱分类模型。
    *   **使命**: 天文光谱蕴含着天体的物理化学信息。MSPC-Net旨在对多样化的光谱数据进行高效、精准的自动分类，提升模型在复杂数据集上的泛化能力，助力光谱分析研究。

4.  **🌟 MSTAR 分类：M型星的多模态智能识别**
    *   **位置**: `mstar-classification-frontend/` (前端) 及对应后端。
    *   **技术**: 深度多模态网络，融合光谱与光度图像数据。
    *   **使命**: M型星是银河系中数量最多的恒星。本项目开创性地结合光谱和图像信息，通过先进的Transformer融合模块和对比学习策略，显著提升M型星亚型分类的准确性和模型的判别能力。

5.  **🌠 天文数据综合处理平台 (Astro Data Comprehensive Processing Platform)**
    *   **位置**: `数据处理/` (包含 `backend/` 和 `frontend/`)
    *   **使命**: 天文研究始于数据。该平台提供针对 DESI、J-PLUS、Pan-STARRS 等大型巡天项目的一站式数据服务。用户可以便捷地进行数据检索、批量下载、初步处理、可视化分析，并通过新增的文件管理页面轻松管理已处理的数据。这大大简化了数据准备的繁琐流程，让研究者能更专注于科学分析本身。

## 🚀 快速开始：点亮您的星图

**环境要求:**
*   Conda (用于管理Python环境)
*   Node.js 和 npm (用于运行前端项目)
*   Python (具体版本视各子项目要求，如 `astronn` 环境使用 Python 3.9/3.10)

**安装与运行:**

1.  **获取项目**: 克隆本仓库到您的本地计算机。
    ```bash
    git clone <your-repository-url>
    cd 2025-undergrad-astro-frontend-mengjunyu
    ```

2.  **环境配置**:
    *   **数据处理后端**: 需要名为 `astronn` 的 Conda 环境 (Python 3.9/3.10)。参考 `数据处理/backend/` 下的依赖文件（如 `requirements.txt`）安装所需库。
    *   **其他Python项目**: 可能需要各自独立的 Conda 环境 (如 `astroyolo` 环境)。请参照各项目目录下的说明或 `requirements.txt` 文件进行配置。
    *   **前端项目**: 进入各前端项目目录 (如 `mstar-classification-frontend/`, `数据处理/frontend/` 等)，执行 `npm install` 安装依赖。

3.  **启动平台**: 我们提供了便捷的启动脚本。
    *   **一键启动所有服务**: 在项目根目录运行 `start-all-projects.ps1` (Windows PowerShell)。该脚本会自动设置并启动所有后端和前端服务。
        ```powershell
        .\start-all-projects.ps1
        ```
    *   **单独启动**: 您也可以使用各子项目的独立启动脚本 (如 `start-astroyolo-frontend.ps1`, `start-mstar-frontend.ps1` 等) 来分别启动特定服务。

4.  **访问平台**:
    *   **主导航门户**: `http://localhost:8000`
    *   **AstroYOLO 前端**: `http://localhost:8083`
    *   **MSPC-Net 前端**: `http://localhost:8081`
    *   **MSTAR 分类前端**: `http://localhost:8082`
    *   **数据处理前端**: `http://localhost:9000`
        *   DESI 数据服务: `http://localhost:9000/#/desi`
        *   J-PLUS 数据接口: `http://localhost:9000/#/jplus`
        *   Pan-STARRS 图像获取: `http://localhost:9000/#/panstarrs`
        *   文件管理: `http://localhost:9000/#/files`
    *   **数据处理后端 API**: `http://localhost:5003`

## 📂 项目结构概览

```
. (e:\2025-undergrad-astro-frontend-mengjunyu)
├── navigation-portal/        # 主导航页面 (HTML, CSS, JS)
│   ├── images/               # 导航页面图片资源
│   ├── index.html
│   └── style.css
├── astroyolo/                # AstroYOLO 项目 (具体结构待补充)
├── mspc-net/                 # MSPC-Net 项目 (具体结构待补充)
├── mstar-classification-frontend/ # MSTAR 分类前端 (Vue/React等)
├── 数据处理/                   # 天文数据综合处理平台
│   ├── backend/              # 后端服务 (Python, Flask)
│   │   └── app.py
│   │   └── requirements.txt
│   │   └── uploads/          # 数据下载保存目录
│   └── frontend/             # 前端界面 (Vue.js)
│       ├── public/
│       ├── src/
│       │   ├── pages/        # DESIPage.vue, JPlusPage.vue, PanSTARRSPage.vue, FilesPage.vue
│       │   └── ...
│       └── package.json
├── start-all-projects.ps1    # 一键启动所有服务的脚本
├── start-astroyolo-frontend.ps1 # AstroYOLO 前端启动脚本
├── start-mspcnet-frontend.ps1  # MSPC-Net 前端启动脚本
├── start-mstar-frontend.ps1   # MSTAR 前端启动脚本
├── README.md                 # 本文档
└── ... (其他配置文件或脚本)
```

## 🤝 贡献与展望

我们深知，探索宇宙的征途永无止境，本平台目前还只是一个初步的探索。我们热忱欢迎任何形式的贡献，无论是代码优化、新功能建议，还是发现和修复BUG。

**未来，我们期望：**
*   集成更多先进的天文AI模型和算法。
*   支持更多天文数据集的接入与处理。
*   持续优化用户体验，让平台更加易用和强大。
*   构建一个活跃的社区，共同推动天文智能化的发展。

## 🙏 致谢

本平台作为山东大学数据结构课程设计项目，离不开以下主要贡献者的辛勤付出：

*   **孟俊宇** (AstroYOLO ;DESI)
*   **何准** (MSTAR ;Jplus)
*   **徐王炜梵** (MSPC-Net ;PanSTARRS)

感谢所有为这个项目贡献过智慧和努力的同学和老师！

---

**让我们一起，用代码和热情，书写探索宇宙的新篇章！**
