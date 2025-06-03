# J-PLUS 天文数据下载脚本

## 项目简介

本项目包含一系列 Python 脚本，用于从 J-PLUS (Javalambre Physics of the Accelerating Universe Astrophysical Survey) 档案库下载不同类型的天文数据产品。这些脚本通过读取一个名为 `object.csv` 的配置文件来获取下载所需的参数。
该项目参照网站https://archive.cefca.es/catalogues/jplus-dr3/download_services.html

## 依赖项

*   Python 3.12.5
*   `requests` 库 (用于发起HTTP请求)

您可以使用 pip 安装 `requests` 库：
```bash
pip install requests
```

## 文件结构

```
.
├── object.csv                # 配置文件，包含下载目标的信息
├── download_jplus_fits.py            # 下载 FITS 图像
├── download_jplus_weight.py          # 下载 FITS 图像的权重图 (Weight maps)
├── download_jplus_cutout.py          # 下载 FITS 图像的切图 (Cutouts)
├── download_jplus_psf.py             # 下载点延展函数 (PSF) 文件
├── download_jplus_psf_by_position.py # 下载指定位置的 PSF 模型文件
├── download_jplus_graphic_image.py   # 下载预览图 (Graphic Images)
├── download_jplus_graphic_cutout.py  # 下载预览图的切图 (Graphic Cutouts)
└── README.md                       # 本说明文件
```

下载的数据会保存在各个脚本对应的子目录中，例如 `jplus_fits_data/`, `jplus_graphic_cutouts_data/` 等。

## 通用配置 (`object.csv`)

所有脚本都依赖于工作目录下的 `object.csv` 文件。该文件是一个标准的 CSV (逗号分隔值) 文件，其第一行必须是表头，定义了后续数据行中各列的含义。
关于如何获得`object.csv`，请去J-Plus官网下的https://archive.cefca.es/catalogues/jplus-dr3/tap_async.html 进行ADQL查询，查询到你需要的内容之后可以导出一个.csv文件，请复制该.csv文件中的内容到项目目录下的`objects.csv`文件中，就可以进行自动化下载了。在此之前，你需要注册一个J-Plus账号。关于ADQL的使用，详见查询界面右上角的`ADQL help and examples`

**必需列 (根据脚本不同而有所不同)：**

*   `TILE_ID`: 天区/图像的唯一标识符。几乎所有脚本都需要。
*   `FILTER_ID`: 滤光片的标识符。许多脚本需要。
*   `RA`: 赤经 (Right Ascension)，通常以度为单位。用于需要精确位置的下载 (如切图、按位置的PSF)。
*   `DEC`: 赤纬 (Declination)，通常以度为单位。用于需要精确位置的下载。

**`object.csv` 示例：**

```csv
"TILE_ID","FILTER_ID","RA","DEC","name","REF_TILE_ID",...
"85282","6","144.7648","27.6581","object_name_1","ref_id_1",...
"88565","7","155.2496","36.0123","object_name_2","ref_id_2",...
...
```

**注意：** 表头名称必须与脚本中期望的完全一致 (例如 `TILE_ID` 而不是 `Tile_ID` 或 `tile_id`)。脚本会自动处理表头字段名包含在双引号内的情况。

## 脚本说明

以下是每个脚本的功能和具体参数说明(固定或默认参数可根据自己需求在相应函数内做修改)：

1.  **`download_jplus_fits.py`**
    *   **功能**: 下载完整的 FITS 科学图像。
    *   **URL**: `https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_fits`
    *   **CSV必需列**: `TILE_ID`, `FILTER_ID`
    *   **输出目录**: `jplus_fits_data/`

2.  **`download_jplus_weight.py`**
    *   **功能**: 下载 FITS 图像对应的权重图 (Weight/Variance maps)。
    *   **URL**: `https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_weight`
    *   **CSV必需列**: `TILE_ID`, `FILTER_ID`
    *   **输出目录**: `jplus_weight_data/`

3.  **`download_jplus_cutout.py`**
    *   **功能**: 下载 FITS 图像的切图。
    *   **URL**: `https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_fits_cutout`
    *   **CSV必需列**: `TILE_ID`, `RA`, `DEC`, `FILTER_ID`
    *   **固定/默认参数**: `width=0.1` (度), `height=0.1` (度), `include_weight=0` (不包含权重图)
    *   **输出目录**: `jplus_cutout_data/`

4.  **`download_jplus_psf.py`**
    *   **功能**: 下载与整个 `TILE_ID` 关联的点延展函数 (PSF) 文件。
    *   **URL**: `https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_psf_file`
    *   **CSV必需列**: `TILE_ID`
    *   **输出目录**: `jplus_psf_data/`
    *   **文件名**: 默认为 `.psf` 扩展名。

5.  **`download_jplus_psf_by_position.py`**
    *   **功能**: 下载在图像中指定 `RA`, `DEC` 位置计算的 PSF 模型文件。
    *   **URL**: `https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_psf_by_position`
    *   **CSV必需列**: `TILE_ID`, `RA`, `DEC`, `FILTER_ID`
    *   **输出目录**: `jplus_psf_by_position_data/`
    *   **文件名**: 默认为 `.psf` 扩展名。

6.  **`download_jplus_graphic_image.py`**
    *   **功能**: 下载与 `TILE_ID` 关联的 RGB 预览图。
    *   **URL**: `https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_graphic_image`
    *   **CSV必需列**: `TILE_ID`
    *   **固定参数**: `band=RGB`
    *   **输出目录**: `jplus_graphic_images/`
    *   **文件名**: 扩展名根据服务器响应的 `Content-Type` 确定 (如 `.jpg`, `.png`)。

7.  **`download_jplus_graphic_cutout.py`**
    *   **功能**: 下载指定位置和大小的 RGB 预览图切图。
    *   **URL**: `https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_graphic_cutout`
    *   **CSV必需列**: `RA`, `DEC`, `FILTER_ID`
    *   **固定/默认参数**: `band=RGB`, `sizex=128` (像素), `sizey=128` (像素), `width=0.1` (角宽度, 度), `height=0.1` (角高度, 度)
    *   **输出目录**: `jplus_graphic_cutouts_data/`
    *   **文件名**: 扩展名根据服务器响应的 `Content-Type` 确定，优先 `.png`。

## 如何运行脚本

1.  确保您的 `object.csv` 文件已正确配置并与脚本放在同一目录下。
2.  打开终端或命令行界面。
3.  导航到脚本所在的目录。
4.  使用 Python 运行您选择的脚本，例如：
    ```
    python download_jplus_graphic_cutout.py
脚本会打印下载进度和最终的摘要信息。

## 注意事项和故障排除

*   **网络连接**: 确保您有稳定的网络连接。
*   **超时**: 脚本内置了请求超时设置 (连接10秒，读取60秒)。如果下载大文件或网络较慢，可能需要调整这些值。
*   **404 错误**: 如果遇到大量 404 (Not Found) 错误，请：
    *   检查 `object.csv` 中的参数值是否正确有效。
    *   手动在浏览器中尝试脚本输出的请求 URL，看是否能访问。这有助于判断是脚本问题还是服务器端问题。
    *   确认目标服务器上的服务是否可用，以及URL结构和参数名是否与脚本中的一致。
*   **CSV 解析**: 
    *   脚本期望 `object.csv` 使用 UTF-8 (带 BOM 或不带 BOM 均可) 编码。
    *   确保 CSV 文件中的字段数与表头一致。
    *   字段值不应包含未被正确引用的逗号。
*   **文件扩展名**: 对于某些下载 (如 PSF 文件、Graphic Images)，脚本会根据服务器响应或预设来决定文件扩展名。如果实际文件类型与扩展名不符，您可能需要手动更改或调整脚本中的逻辑。
*   **磁盘空间**: 确保您有足够的磁盘空间来保存下载的数据。

---
希望这些脚本对您有所帮助！ 