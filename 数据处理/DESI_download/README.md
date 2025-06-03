# DESI 数据处理器

`desi_data_processor` 是一个 Python 工具包，旨在简化从暗能量光谱仪器 (DESI) 巡天以及相关的天空巡天（如 DESI Legacy 成像巡天）访问、下载和处理数据的过程。

它提供了查询星表、下载图像切片（FITS 和 JPEG）、从 FITS 文件创建 RGB 图像以及将单波段 JPEG 合并为彩色图像的功能。

## 主要特性

- **数据访问与下载:**
  - `DesiArchiveHandler`: 与 DESI 和 Legacy Survey 数据存档交互的核心类。
    - 下载指定天体坐标和波段的 FITS 及 JPEG 图像切片。
    - 使用 ADQL 查询天文星表 (通过 `astro-datalab`)。
  - `DESIBulkDownloader`: 基于 CSV 清单批量下载文件的实用工具 (主要用于通用的 DESI 数据文件)。
  - `download_file`: 一个强大的函数，用于下载单个文件并显示进度。
- **图像处理:**
  - `create_rgb_from_fits`: 使用 Lupton (asinh) 缩放从 g, r, z 波段的 FITS 文件生成彩色 PNG 图像。
  - `combine_rgb_jpegs`: 通过合并三个单波段 (例如 r, g, b/z) JPEG 图像来创建彩色 RGB JPEG。
- **模块化设计:** 代码组织到子模块中，清晰易用。
- **示例代码:** `examples/` 目录下提供了一系列示例脚本，演示核心功能。

## 安装

1. 克隆仓库:

   ```bash
   git clone <repository_url>
   cd desi_data_processor # 或者你的项目根目录名
   ```

2. 安装所需依赖:

   ```bash
   pip install -r requirements.txt
   ```

   如果您打算使用星表查询功能，请确保已安装并配置 `astro-datalab`。您可能需要登录 NOIRLab Astro Data Lab 服务。

## 项目结构

```text
desi_data_processor/
├── desi_data_processor/      # 主包源代码
│   ├── __init__.py
│   ├── desi_archive_handler.py # 数据访问核心类
│   ├── imaging_utils.py      # FITS 转 RGB, 合并 JPEG
│   ├── catalog.py            # 星表相关类 (例如 DESIRedshiftCatalog)
│   ├── healpix.py            # HEALPix 处理
│   ├── spectra.py            # 光谱处理
│   └── utils/                  # 实用工具模块
│       ├── __init__.py
│       ├── download_utils.py   # download_file 函数
│       └── bulk_downloader.py  # DESIBulkDownloader 类
├── examples/                 # 示例脚本
│   ├── data/                   # 示例用 CSV 文件
│   ├── example_download_cutouts.py
│   ├── example_batch_download_from_csv.py # 用于下载切片
│   ├── example_create_rgb_from_fits.py
│   ├── example_combine_jpegs.py
│   └── example_query_catalog.py
├── README.md                 # 本文件
└── requirements.txt          # Python 依赖
```

## 核心组件

### `DesiArchiveHandler`

位于 `desi_data_processor.desi_archive_handler`。
该类是您进行以下操作的主要接口:

- 下载图像切片: `handler.download_cutout(ra, dec, size, bands, img_format, save_dir, filename)`
- 查询星表: `handler.query_catalog(adql_query)` (需要 `astro-datalab`)

### `imaging_utils`

位于 `desi_data_processor.imaging_utils`。

- `create_rgb_from_fits(fits_g_path, fits_r_path, fits_z_path, output_png_path, ...)`: 从三个 FITS 文件创建彩色图像。
- `combine_rgb_jpegs(r_path, g_path, b_path, output_path)`: 将三个 JPEG 合并为一个 RGB JPEG。

### `utils.download_utils` & `utils.bulk_downloader`

- `download_file(url, local_path, overwrite=False)`: 通用文件下载器。
- `DESIBulkDownloader`: 用于管理从 CSV 文件进行的批量下载的类 (通常用于非切片的 DESI 数据产品)。

## 使用示例

`examples/` 目录包含演示各种功能的脚本。要运行它们，请导航到 `examples/` 目录。

1. **下载图像切片**

   ```bash
   cd examples
   python example_download_cutouts.py
   ```

   此脚本将使用 `DesiArchiveHandler` 下载示例 FITS 和 JPEG 切片到 `test_downloads/` 子目录 (相对于项目主目录)。

2. **从 CSV 批量下载切片**

   ```bash
   cd examples
   python example_batch_download_from_csv.py
   ```

   此脚本从 `examples/data/cutout_batch_template.csv` 读取参数，并将指定的切片下载到 `batch_cutout_downloads/` 子目录。

3. **从 FITS 文件创建 RGB 图像**

   确保您有 g, r, z 波段的 FITS 文件 (例如，通过 `example_download_cutouts.py` 下载)。

   ```bash
   cd examples
   python example_create_rgb_from_fits.py
   ```

   此脚本使用示例 FITS 文件 (预计位于 `../test_downloads/image_cutouts_fits_examples/`) 并在 `../test_rgb_images/` 中创建 RGB PNG 图像。

4. **合并 JPEG 图像**

   确保您有 r, g, b (或 z 代表蓝色) 波段的 JPEG 文件。

   ```bash
   cd examples
   python example_combine_jpegs.py
   ```

   此脚本使用示例 JPEG (预计位于 `../test_downloads/image_cutouts_jpeg_examples/`) 并在 `../test_rgb_images/` 中创建合并的 RGB JPEG。

5. **查询星表**

   ```bash
   cd examples
   python example_query_catalog.py
   ```

   此脚本演示如何使用 `DesiArchiveHandler.query_catalog()` 执行 ADQL 查询。结果将打印到控制台。

## 数据来源

该工具包主要针对来自 DESI 巡天和 DESI Legacy 成像巡天的数据。

- DESI 公共数据发布: [https://data.desi.lbl.gov/public/](https://data.desi.lbl.gov/public/)
- DESI Legacy 成像巡天: [https://www.legacysurvey.org/](https://www.legacysurvey.org/)

## 许可证

本项目采用 MIT 许可证。详情请参阅 `LICENSE` 文件 (如果存在，否则默认为 MIT)。
