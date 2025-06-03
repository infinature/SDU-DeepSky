"""
FITS文件处理相关的辅助函数。
"""

from astropy.io import fits
import os

def get_fits_header(file_path, hdu_index=0):
    """
    获取FITS文件的指定HDU的头信息。

    参数:
        file_path (str): FITS文件的路径。
        hdu_index (int or str): HDU的索引或名称。

    返回:
        astropy.io.fits.Header or None: HDU的头信息，如果文件不存在或HDU无效则返回None。
    """
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    try:
        with fits.open(file_path) as hdul:
            header = hdul[hdu_index].header
        return header
    except Exception as e:
        print(f"读取FITS头信息失败 {file_path} (HDU: {hdu_index}): {e}")
        return None

def list_hdus(file_path):
    """
    列出FITS文件中的所有HDU信息。

    参数:
        file_path (str): FITS文件的路径。

    返回:
        list of tuples or None: 每个HDU的 (索引, 名称, 类型) 列表，如果文件不存在则返回None。
    """
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    try:
        with fits.open(file_path) as hdul:
            info = []
            for i, hdu in enumerate(hdul):
                hdu_name = hdu.name if hdu.name else f'HDU_{i}'
                hdu_type = type(hdu).__name__ # e.g., PrimaryHDU, ImageHDU, BinTableHDU
                info.append((i, hdu_name, hdu_type, hdu.header.get('XTENSION', 'PRIMARY')))
            # hdul.info() # astropy的内置方法，可以直接打印到控制台
        return info
    except Exception as e:
        print(f"列出HDU失败 {file_path}: {e}")
        return None

def get_table_from_fits(file_path, hdu_name_or_index):
    """
    从FITS文件中读取一个表 (BinTableHDU)。

    参数:
        file_path (str): FITS文件的路径。
        hdu_name_or_index (str or int): HDU的名称或索引。

    返回:
        astropy.table.Table or None: 读取到的表数据，如果出错则返回None。
    """
    from astropy.table import Table
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    try:
        table_data = Table.read(file_path, hdu=hdu_name_or_index)
        return table_data
    except Exception as e:
        print(f"从FITS读取表失败 {file_path} (HDU: {hdu_name_or_index}): {e}")
        return None

if __name__ == '__main__':
    print("fits_utils.py 包含FITS文件处理的辅助函数。")
    # 示例: (需要一个实际的FITS文件来测试)
    # dummy_fits_file = 'path/to/your/test.fits'
    # if os.path.exists(dummy_fits_file):
    #     print(f"\n头信息 (HDU 0) for {dummy_fits_file}:")
    #     header = get_fits_header(dummy_fits_file)
    #     if header:
    #         print(header)
        
    #     print(f"\nHDU列表 for {dummy_fits_file}:")
    #     hdus = list_hdus(dummy_fits_file)
    #     if hdus:
    #         for hdu_info in hdus:
    #             print(f"  Index: {hdu_info[0]}, Name: {hdu_info[1]}, Type: {hdu_info[2]}, XTENSION: {hdu_info[3]}")

    #     # 假设 'FIBERMAP' 是一个BinTableHDU
    #     # fibermap_table = get_table_from_fits(dummy_fits_file, 'FIBERMAP')
    #     # if fibermap_table:
    #     #     print(f"\nFIBERMAP table (first 5 rows) from {dummy_fits_file}:")
    #     #     print(fibermap_table[:5])
    # else:
    #     print(f"测试FITS文件 '{dummy_fits_file}' 未找到。请提供一个有效路径以运行示例。")
    print("取消注释并提供FITS文件路径以运行fits_utils.py中的示例。")
