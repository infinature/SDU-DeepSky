# 🌌 Pan-STARRS FITS 数据下载与可视化脚本

该脚本旨在从 Pan-STARRS（PS1） 图像服务中批量下载天文目标的多波段 FITS 图像，提取其头信息，并进行图像可视化（包含普通图像和 RGB 合成图像）。支持使用本地安装的 SAOImage DS9 进行图像处理和渲染。

---

## 📋 功能简介

**脚本核心功能包括：**
- 自动下载 PS1 的 g、r、i、z、y 波段 FITS 图像
- 提取并保存 FITS 文件头信息（Header）
- 用 Matplotlib 渲染单波段图像
- 合成 RGB 伪彩图像（支持本地生成或通过 DS9 生成）
- 集成 DS9 自动生成图像或合成 RGB 图
- 目录自动创建，输出分类清晰

---

## 🧑‍💻 使用说明

###  1. 安装依赖
请先安装以下 Python 包：
```bash
pip install astropy numpy pandas matplotlib requests beautifulsoup4 pillow
```

###  1. 用户配置
根据自身情况填写配置
```bash
USE_DS9 = True  # 是否使用 DS9 进行图像处理
DS9_PATH = 'D:\Program Files\SAOImageDS9\ds9.exe'  # DS9 可执行文件路径
BANDS = ['g', 'r', 'i', 'z', 'y']  # 需要下载的波段
FITS_DIR = 'fits_files' #自动生成，用于保存下载的fits文件
IMAGE_DIR = 'images' #自动生成，用于保存matplotlib生成的图片
DS9_IMAGE_DIR = 'ds9_images' #自动生成，用于保存ds9生成的图片
HEADER_DIR = 'fits_headers' #自动生成，用于保存提取的fits信息
```

###  3. 安装 SAOImage DS9（可选）
如需使用 DS9 自动渲染图像或生成 RGB 图像，请从官网下载安装 DS9 并确保其可执行路径在环境变量中（或手动配置脚本中的 DS9_PATH）。

官网：https://sites.google.com/cfa.harvard.edu/saoimageds9

###  4. 准备目标天体列表（CSV）
准备一个包含目标坐标的 CSV 文件（例如：targets.csv），格式如下：
```bash
id,ra,dec
M51,202.4696,47.1952
NGC5195,202.4842,47.2665
```
- id：对象名称或编号（可选）
- ra：赤经（单位：度）
- dec：赤纬（单位：度）

###  5. 运行脚本
修改脚本顶部的配置项：
```
USE_DS9 = True  # 是否使用 DS9 渲染图像
BANDS = ['g', 'r', 'i', 'z', 'y']  # 要下载的波段
```
然后执行脚本：
```
python panstarrs_downloader.py
```

---

## 📂 输出文件说明
脚本将自动创建以下文件夹：
- fits_files/：保存下载的 FITS 文件
- fits_headers/：每个 FITS 文件对应的头信息文本文件
- images/：使用 matplotlib 渲染的 PNG 图像（单波段 + RGB 合成图）
- ds9_images/：使用 SAOImage DS9 渲染的图像（单波段 + RGB 合成图）

---

## 🧠 函数功能详细说明

### `get_fitscutout_links(ra, dec, size=240)`

获取给定天体在 Pan-STARRS 中各波段的 FITS 图像下载链接。

- **参数**:
  - `ra` *(float)*：天体的赤经坐标（单位：度）
  - `dec` *(float)*：天体的赤纬坐标（单位：度）
  - `size` *(int, 默认=240)*：图像切片大小（以像素为单位）

- **返回**:
  - `dict`：包含波段名为键、对应 FITS 下载链接为值的字典，例如：`{'g': url1, 'r': url2}`

- **用途**:
  - 通过构造 URL 查询 Pan-STARRS 的 cutout 服务，获取该位置上各波段图像的下载链接。

---

### `download_fits_files(links, save_dir, prefix)`

下载 FITS 图像文件，并保存到本地目录。

- **参数**:
  - `links` *(dict)*：每个波段对应的 FITS 文件 URL（来自 `get_fitscutout_links`）
  - `save_dir` *(str)*：FITS 文件保存目录
  - `prefix` *(str)*：保存文件的命名前缀（通常为目标名称）

- **返回**:
  - `dict`：成功保存的 FITS 文件路径字典，键为波段，值为文件路径

- **用途**:
  - 支持网络自动请求并保存文件，包含失败处理逻辑。

---

### `extract_fits_header(fits_path, output_dir, prefix)`

从 FITS 文件中提取头部信息（Header）并以文本文件保存。

- **参数**:
  - `fits_path` *(str)*：FITS 文件的路径
  - `output_dir` *(str)*：保存头信息文本的目录
  - `prefix` *(str)*：文本文件名的前缀（通常为目标名称）

- **功能**:
  - 使用 `astropy.io.fits` 读取 Header，并将其以可读文本形式写入 `.txt` 文件。

---

### `visualize_fits(fits_path, output_dir, prefix)`

使用 Matplotlib 渲染 FITS 图像，并保存为 PNG 图像。

- **参数**:
  - `fits_path` *(str)*：FITS 文件路径
  - `output_dir` *(str)*：输出图像保存目录
  - `prefix` *(str)*：图像文件名前缀

- **功能**:
  - 使用 FITS 数据中的主扩展（Primary HDU）进行图像绘制；
  - 添加颜色条与图像标题；
  - 自动保存为 PNG 图像，适合快速浏览。

---

### `autoscale(data, low=1, high=99)`

对图像数据进行线性拉伸，用于 RGB 合成的像素归一化处理。

- **参数**:
  - `data` *(ndarray)*：输入图像数组
  - `low` *(int, 默认=1)*：下限百分位数
  - `high` *(int, 默认=99)*：上限百分位数

- **返回**:
  - `ndarray`：归一化后的图像数组（范围 [0, 1]）

- **用途**:
  - 消除极端像素值的影响，提升 RGB 图像显示效果。

---

### `combine_rgb(fits_r, fits_g, fits_b, output_path)`

从 R/G/B 三个 FITS 文件中读取数据并合成 RGB 彩色图像。

- **参数**:
  - `fits_r/g/b` *(str)*：三个波段（如 y、i、g）的 FITS 路径
  - `output_path` *(str)*：输出的 RGB 图像保存路径（PNG）

- **功能**:
  - 使用 `Pillow` 构造 RGB 图像；
  - 自动拉伸各通道图像；
  - 保存为 PNG，适合科学展示。

---

### `ds9_generate_images(fits_paths, output_dir, prefix)`

调用 SAOImage DS9 渲染单波段图像并保存。

- **参数**:
  - `fits_paths` *(dict)*：包含每个波段的本地 FITS 路径
  - `output_dir` *(str)*：输出 PNG 图像目录
  - `prefix` *(str)*：输出图像文件名前缀

- **功能**:
  - 使用命令行模式调用 DS9；
  - 自动设定比例拉伸、颜色图；
  - 将图像导出为 PNG。

---

### `ds9_combine_rgb(fits_r, fits_g, fits_b, output_path)`

使用 DS9 合成 RGB 图像并保存为 PNG。

- **参数**:
  - `fits_r/g/b` *(str)*：三个 FITS 文件路径
  - `output_path` *(str)*：输出 RGB 图像的保存路径

- **功能**:
  - 使用 DS9 的 RGB 合成功能；
  - 合成后以 PNG 格式导出；
  - 支持高质量图像生成，适合科研展示。

---

### `process_catalog(catalog_csv)`

读取天体坐标 CSV 文件并批量处理每一个目标。

- **参数**:
  - `catalog_csv` *(str)*：CSV 文件路径，包含 `id`, `ra`, `dec` 三列

- **处理流程**:
  1. 读取 CSV 文件，逐行处理；
  2. 获取 FITS 下载链接；
  3. 下载所有波段 FITS；
  4. 提取 Header 信息；
  5. 使用 matplotlib 渲染单波段图像；
  6. （可选）使用 DS9 渲染图像；
  7. 合成 RGB 图像（matplotlib 和/或 DS9）。

- **作用**:
  - 脚本的核心入口函数；
  - 便于批量化自动处理多个天体图像和数据。

---

## 🧪 示例运行效果
- 下载并保存 M51 各波段 FITS
- 提取每个 FITS 的头信息为 txt 文件
- 使用 Matplotlib 可视化图像
- 使用 DS9 渲染图像（单波段）
- 合成 RGB 图像（Matplotlib 和 DS9 双版本）

---

## 📌 注意事项
- 网络请求可能受限，请确保网络可访问 PS1 服务；
- SAOImage DS9 为可选但推荐安装；
- FITS 图像中部分波段可能缺失，脚本会跳过错误；
- RGB 合成采用 Y, I, G 作为默认的 R, G, B 渠道顺序，符合 PS1 的图像发布标准。