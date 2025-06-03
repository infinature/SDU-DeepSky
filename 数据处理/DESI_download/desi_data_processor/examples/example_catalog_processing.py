"""
示例：使用 DESIRedshiftCatalog 处理红移目录
"""

import os
import sys

# 将项目根目录添加到Python路径，以便导入desi_data_processor模块
# 这在直接从examples目录运行脚本时特别有用
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # examples -> desi_data_processor -> project_root
sys.path.insert(0, project_root)

from desi_data_processor.catalog import DESIRedshiftCatalog
from desi_data_processor.utils.download_utils import download_file

def main():
    print("DESI 红移目录处理示例")
    print("=========================")

    # --- 配置 --- #
    # DESI DR1 zall-pix-iron.fits 文件信息
    # 这是DR1中推荐的HEALPix基础的组合红移目录
    catalog_url = 'https://data.desi.lbl.gov/public/dr1/spectro/redux/iron/zcatalog/v1/zall-pix-iron.fits'
    
    # 本地数据存储目录 (示例将文件下载到项目根目录下的 'data/catalogs' 子目录中)
    # 你可以根据需要修改此路径
    data_storage_dir = os.path.join(project_root, 'data', 'catalogs')
    local_catalog_filename = 'zall-pix-iron.fits'
    local_catalog_path = os.path.join(data_storage_dir, local_catalog_filename)

    print(f"本地目录路径: {data_storage_dir}")
    print(f"本地FITS文件路径: {local_catalog_path}")

    # --- 1. 下载数据 (如果本地不存在) --- #
    print("\n--- 步骤 1: 检查并下载红移目录文件 --- ")
    if not os.path.exists(local_catalog_path):
        print(f"本地文件 '{local_catalog_path}' 未找到。")
        print(f"尝试从 '{catalog_url}' 下载...")
        # 确保目录存在
        if not os.path.exists(data_storage_dir):
            os.makedirs(data_storage_dir)
            print(f"已创建目录: {data_storage_dir}")
        
        success = download_file(catalog_url, local_catalog_path, overwrite=False)
        if success:
            print(f"文件已成功下载到: {local_catalog_path}")
        else:
            print(f"文件下载失败。请检查URL或网络连接，或手动下载文件到指定路径。")
            print("脚本将退出，因为无法获取必要的目录文件。")
            return
    else:
        print(f"本地文件 '{local_catalog_path}' 已存在。跳过下载。")

    # --- 2. 加载红移目录 --- #
    print("\n--- 步骤 2: 加载红移目录 --- ")
    desi_catalog = DESIRedshiftCatalog(local_catalog_path)

    if desi_catalog.data is None:
        print("无法加载目录数据，脚本将退出。")
        return

    # --- 3. 显示目录基本信息 --- #
    print("\n--- 步骤 3: 显示目录基本信息 --- ")
    print(f"目录对象: {desi_catalog}")
    print(f"包含 {len(desi_catalog.data)} 个目标。")
    print("前5行数据:")
    # 使用 astropy.table 的 show_in_notebook() 或 pformat() 以获得更好的格式
    # desi_catalog.data[:5].info('stats') # 显示统计信息
    print(desi_catalog.data[:5])
    
    print("\n目录列名:")
    # 每行打印几个列名，使其更易读
    col_names = desi_catalog.get_column_names()
    for i in range(0, len(col_names), 5):
        print(", ".join(col_names[i:i+5]))

    # --- 4. 获取主要目标 (ZCAT_PRIMARY) --- #
    print("\n--- 步骤 4: 获取主要目标 --- ")
    # 默认使用 'ZCAT_PRIMARY' 列，这是DR1推荐的
    primary_targets = desi_catalog.get_primary_targets()
    if primary_targets is not None:
        print(f"共找到 {len(primary_targets)} 个主要目标。")
        if len(primary_targets) > 0:
            print("前5个主要目标:")
            print(primary_targets[:5]['TARGETID', 'Z', 'ZERR', 'SPECTYPE', 'DELTACHI2'])
    else:
        print("未能获取主要目标。")

    # --- 5. 计算红移统计 --- #
    print("\n--- 步骤 5: 计算红移统计 (基于所有目标) --- ")
    # 默认使用 'Z' 列作为红移列
    redshift_stats = desi_catalog.calculate_redshift_stats()
    if redshift_stats:
        print("红移 (Z) 统计数据:")
        for key, value in redshift_stats.items():
            print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
    
    # 如果有主要目标，也可以计算主要目标的红移统计
    if primary_targets is not None and len(primary_targets) > 0:
        print("\n计算主要目标的红移统计:")
        # 临时创建一个只包含主要目标的Catalog对象 (或者直接操作Table)
        # 这里我们直接操作 primary_targets Table
        primary_redshifts = primary_targets['Z']
        primary_stats = {
            'mean': np.nanmean(primary_redshifts),
            'median': np.nanmedian(primary_redshifts),
            'std': np.nanstd(primary_redshifts),
            'min': np.nanmin(primary_redshifts),
            'max': np.nanmax(primary_redshifts),
            'count': np.sum(~np.isnan(primary_redshifts))
        }
        print("主要目标红移 (Z) 统计数据:")
        for key, value in primary_stats.items():
            print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")

    # --- 6. 按红移范围筛选 --- #
    print("\n--- 步骤 6: 按红移范围筛选目标 (0.8 < Z < 1.2) --- ")
    min_z, max_z = 0.8, 1.2
    filtered_targets = desi_catalog.filter_by_redshift_range(min_z, max_z)
    if filtered_targets is not None:
        print(f"在红移范围 [{min_z}, {max_z}] 内找到 {len(filtered_targets)} 个目标。")
        if len(filtered_targets) > 0:
            print("前5个筛选出的目标:")
            print(filtered_targets[:5]['TARGETID', 'Z', 'ZERR', 'SPECTYPE'])

    # --- 7. 探索特定列 --- #
    print("\n--- 步骤 7: 探索 SPECTYPE 列 --- ")
    if 'SPECTYPE' in desi_catalog.data.colnames:
        spectypes = desi_catalog.data['SPECTYPE']
        unique_spectypes, counts = np.unique(spectypes, return_counts=True)
        print("目标光谱类型分布:")
        for stype, count in zip(unique_spectypes, counts):
            print(f"  {stype}: {count}")
    else:
        print("目录中未找到 'SPECTYPE' 列。")

    print("\n示例处理完成。")

if __name__ == '__main__':
    # 为了使numpy的统计函数正常工作，导入它
    import numpy as np 
    main()
