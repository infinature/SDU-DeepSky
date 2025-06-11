# 天文数据下载平台

一个用于下载和管理多个天文数据源（DESI、J-PLUS、Pan-STARRS）的桌面应用程序。

## 功能特点

### 1. DESI 数据下载
- 支持单个目标或批量下载
- 支持 FITS 和 JPEG 格式
- 支持多波段（g, r, z）下载
- 支持 RGB 图像生成
- 可自定义图像大小和像素比例
- 支持背景减除

### 2. J-PLUS 数据下载
- 支持多种数据类型：
  - FITS 科学图像
  - 权重图
  - FITS 切图
  - PSF 文件
  - 位置 PSF
  - RGB 预览图
  - 预览图切图
- 支持自定义切图大小
- 支持批量下载

### 3. Pan-STARRS 数据下载
- 支持多波段（g, r, i, z, y）下载
- 支持 Matplotlib 和 DS9 可视化
- 支持自定义图像大小
- 支持批量下载
- 支持手动输入目标坐标

## 系统要求

- Windows 10 或更高版本
- Python 3.8 或更高版本
- Node.js 16 或更高版本
- 足够的磁盘空间用于存储下载的数据

## 安装说明

1. 克隆项目：
```bash
git clone [项目地址]
cd astro_data_portal
```

2. 安装后端依赖：
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirement.txt
```

3. 安装前端依赖：
```bash
cd frontend
npm install
```

4. 创建数据存储目录（可选）：
```bash
# 在项目根目录下创建数据存储目录
mkdir DESI_download
mkdir J-PLUS
mkdir MAST_PanSTARRS
```

5. 启动应用：
```bash
# 启动后端
python app.py

# 启动前端（新终端）
cd frontend
npm run dev
```

## 使用说明

### DESI 数据下载
1. 选择数据格式（FITS/JPEG）
2. 选择波段（FITS 格式支持多波段）
3. 设置图像大小和像素比例
4. 选择是否生成 RGB 图像
5. 上传 CSV 文件或手动输入坐标
6. 选择保存目录
7. 点击下载

### J-PLUS 数据下载
1. 上传包含 TILE_ID 和 FILTER_ID 的 CSV 文件
2. 选择数据类型
3. 设置切图大小（如适用）
4. 选择保存目录
5. 点击下载

### Pan-STARRS 数据下载
1. 上传包含 ID、RA、DEC 的 CSV 文件或手动输入坐标
2. 选择波段
3. 设置图像大小
4. 选择可视化方式
5. 选择保存目录
6. 点击下载

## CSV 文件格式

### DESI
```
RA,DEC,TARGET_ID
180.0,30.0,obj1
181.0,31.0,obj2
```

### J-PLUS
```
TILE_ID,FILTER_ID,RA,DEC
12345,g,180.0,30.0
12345,r,180.0,30.0
```

### Pan-STARRS
```
id,ra,dec
obj1,180.0,30.0
obj2,181.0,31.0
```

## 项目结构

```
astro_data_portal/          # 项目根目录
├── app.py                  # 后端主程序（必需）
├── requirement.txt         # Python 依赖（必需）
├── frontend/              # 前端代码（必需）
│   ├── src/
│   │   ├── pages/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   └── App.vue       # 主应用组件
│   └── package.json      # 前端依赖
└── README.md              # 项目说明文档（必需）
test3.csv,test2.csv,test.csv分别是三个数据集下载的测试星表csv文件

# 以下目录用于是项目代码的一部分（即三个数据集下载原函数）
DESI_download/             # DESI 数据存储目录（可选）
J-PLUS/                   # J-PLUS 数据存储目录（可选）
MAST_PanSTARRS/          # Pan-STARRS 数据存储目录（可选）
```

## 注意事项

1. 数据格式限制：
   - DESI FITS 格式最大图像尺寸：512 像素
   - DESI JPEG 格式最大图像尺寸：3000 像素
   - Pan-STARRS 图像尺寸范围：100-1000 像素

2. 文件大小限制：
   - CSV 文件大小限制：10MB
   - 建议批量下载时控制目标数量

3. 网络要求：
   - 需要稳定的网络连接
   - 下载大量数据时建议使用有线网络

4. 存储空间：
   - 建议定期清理下载目录
   - 确保有足够的磁盘空间

## 常见问题

1. 下载失败：
   - 检查网络连接
   - 验证坐标是否有效
   - 确认文件格式是否正确

2. 进度条不更新：
   - 检查后端服务是否运行
   - 刷新页面重试

3. 文件无法保存：
   - 检查保存目录权限
   - 确保磁盘空间充足

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。

## 许可证

[添加许可证信息] 
