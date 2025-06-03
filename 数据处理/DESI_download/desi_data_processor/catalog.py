"""
处理DESI红移目录的模块
"""

from astropy.table import Table
import numpy as np

class DESIRedshiftCatalog:
    """
    处理DESI红移目录的类。

    参数:
        catalog_path (str): FITS格式红移目录文件的路径。
    """
    def __init__(self, catalog_path):
        self.catalog_path = catalog_path
        self.data = None
        self._load_catalog()

    def _load_catalog(self):
        """加载红移目录数据。"""
        try:
            self.data = Table.read(self.catalog_path, format='fits')
            print(f"成功加载目录: {self.catalog_path}")
            print(f"包含 {len(self.data)} 个目标。")
        except Exception as e:
            print(f"加载目录失败: {self.catalog_path}\n错误: {e}")
            self.data = None

    def get_primary_targets(self, primary_column='ZCAT_PRIMARY'):
        """
        获取主要目标（推荐的红移）。

        参数:
            primary_column (str): 指示主要目标的列名，默认为 'ZCAT_PRIMARY'。

        返回:
            astropy.table.Table or None: 包含主要目标的子表，如果数据未加载或列不存在则返回None。
        """
        if self.data is None:
            print("目录数据未加载。")
            return None
        
        if primary_column not in self.data.colnames:
            print(f"列 '{primary_column}' 在目录中未找到。可用的列: {self.data.colnames}")
            # 尝试备用列名，例如基于文档中提到的 zall-pix-iron.fits
            # 这部分可以根据实际的FITS文件结构进行调整
            potential_primary_cols = [col for col in self.data.colnames if 'PRIMARY' in col.upper() or 'BEST' in col.upper()]
            if potential_primary_cols:
                print(f"尝试使用备用列: {potential_primary_cols[0]}")
                primary_column = potential_primary_cols[0]
            else:
                print("未找到合适的主要目标列。")
                return None

        try:
            # 根据DESI文档，ZCAT_PRIMARY 是一个布尔列
            primary_mask = self.data[primary_column].astype(bool)
            primary_targets = self.data[primary_mask]
            print(f"找到 {len(primary_targets)} 个主要目标。")
            return primary_targets
        except Exception as e:
            print(f"获取主要目标时出错: {e}")
            return None

    def calculate_redshift_stats(self, redshift_column='Z'):
        """
        计算红移的基本统计数据。

        参数:
            redshift_column (str): 红移值所在的列名，默认为 'Z'。

        返回:
            dict or None: 包含红移统计信息的字典 (mean, median, std, min, max)，如果数据未加载或列不存在则返回None。
        """
        if self.data is None:
            print("目录数据未加载。")
            return None

        if redshift_column not in self.data.colnames:
            print(f"列 '{redshift_column}' 在目录中未找到。可用的列: {self.data.colnames}")
            # 尝试查找可能的红移列
            potential_z_cols = [col for col in self.data.colnames if 'Z' == col.upper() or 'REDSHIFT' in col.upper()]
            if potential_z_cols:
                print(f"尝试使用备用红移列: {potential_z_cols[0]}")
                redshift_column = potential_z_cols[0]
            else:
                print("未找到合适的红移列。")
                return None
        
        try:
            redshifts = self.data[redshift_column]
            stats = {
                'mean': np.nanmean(redshifts),
                'median': np.nanmedian(redshifts),
                'std': np.nanstd(redshifts),
                'min': np.nanmin(redshifts),
                'max': np.nanmax(redshifts),
                'count': np.sum(~np.isnan(redshifts))
            }
            print(f"红移 ({redshift_column}) 统计: {stats}")
            return stats
        except Exception as e:
            print(f"计算红移统计时出错: {e}")
            return None

    def filter_by_redshift_range(self, min_z, max_z, redshift_column='Z'):
        """
        根据红移范围筛选目标。

        参数:
            min_z (float): 最小红移值。
            max_z (float): 最大红移值。
            redshift_column (str): 红移值所在的列名，默认为 'Z'。

        返回:
            astropy.table.Table or None: 包含筛选后目标的子表。
        """
        if self.data is None:
            print("目录数据未加载。")
            return None

        if redshift_column not in self.data.colnames:
            print(f"列 '{redshift_column}' 在目录中未找到。")
            return None
        
        try:
            mask = (self.data[redshift_column] >= min_z) & (self.data[redshift_column] <= max_z)
            filtered_targets = self.data[mask]
            print(f"在红移范围 [{min_z}, {max_z}] 内找到 {len(filtered_targets)} 个目标。")
            return filtered_targets
        except Exception as e:
            print(f"按红移范围筛选时出错: {e}")
            return None

    def get_column_names(self):
        """获取目录中的所有列名。"""
        if self.data is not None:
            return self.data.colnames
        return []

    def __repr__(self):
        if self.data is not None:
            return f"<DESIRedshiftCatalog: {self.catalog_path} ({len(self.data)} targets)>"
        return f"<DESIRedshiftCatalog: {self.catalog_path} (unloaded)>"

if __name__ == '__main__':
    # 这是一个使用示例，你需要提供一个实际的DESI FITS目录文件路径
    # 例如: zall-pix-iron.fits
    # catalog_file = 'path/to/your/zall-pix-iron.fits' 
    # print(f"请将 'catalog_file' 变量替换为实际的FITS文件路径以运行示例。")

    # 假设你已经下载了 zall-pix-iron.fits 并放在了项目的 'data' 目录下 (你需要手动创建此目录并下载文件)
    # import os
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.dirname(current_dir) # desi_data_processor的上一级目录
    # catalog_file = os.path.join(project_root, 'data', 'zall-pix-iron.fits')

    # if os.path.exists(catalog_file):
    #     desi_catalog = DESIRedshiftCatalog(catalog_file)
        
    #     if desi_catalog.data is not None:
    #         print("\n列名:")
    #         print(desi_catalog.get_column_names())
            
    #         print("\n获取主要目标:")
    #         primary = desi_catalog.get_primary_targets()
    #         if primary is not None and len(primary) > 0:
    #             print(f"获取到 {len(primary)} 个主要目标，前5个:")
    #             print(primary[:5])
            
    #         print("\n计算红移统计:")
    #         stats = desi_catalog.calculate_redshift_stats()
    #         if stats:
    #             print(stats)

    #         print("\n按红移范围筛选 (0.5 < z < 1.0):")
    #         filtered = desi_catalog.filter_by_redshift_range(0.5, 1.0)
    #         if filtered is not None and len(filtered) > 0:
    #             print(f"筛选到 {len(filtered)} 个目标，前5个:")
    #             print(filtered[:5])
    # else:
    #     print(f"示例FITS文件未找到: {catalog_file}")
    #     print("请下载DESI DR1的 'zall-pix-iron.fits' 文件，并将其路径更新到脚本中。")
    #     print("下载链接: https://data.desi.lbl.gov/public/dr1/spectro/redux/iron/zcatalog/v1/zall-pix-iron.fits")
    print("DESIRedshiftCatalog 类已定义。取消注释并提供FITS文件路径以运行示例。")
