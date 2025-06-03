"""
测试 DESIRedshiftCatalog 类
"""

import unittest
import os
import tempfile
from astropy.table import Table, Column
import numpy as np

# 将项目根目录添加到Python路径，以便导入desi_data_processor模块
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # tests -> desi_data_processor -> project_root
sys.path.insert(0, project_root)

from desi_data_processor.catalog import DESIRedshiftCatalog

class TestDESIRedshiftCatalog(unittest.TestCase):

    def setUp(self):
        """为每个测试创建一个临时的FITS文件。"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_fits_file = os.path.join(self.temp_dir.name, 'test_catalog.fits')

        # 创建一个简单的Astropy Table作为测试数据
        self.n_rows = 10
        self.target_ids = np.arange(self.n_rows)
        self.redshifts = np.linspace(0.1, 1.0, self.n_rows)
        self.z_errors = np.random.uniform(0.001, 0.01, self.n_rows)
        self.spectypes = np.random.choice(['GALAXY', 'QSO', 'STAR'], self.n_rows)
        # ZCAT_PRIMARY: 假设一半是True，一半是False
        self.primary_flags = np.array([True, False] * (self.n_rows // 2) + ([True] if self.n_rows % 2 != 0 else []))

        self.sample_table = Table([
            Column(self.target_ids, name='TARGETID'),
            Column(self.redshifts, name='Z'),
            Column(self.z_errors, name='ZERR'),
            Column(self.spectypes, name='SPECTYPE'),
            Column(self.primary_flags, name='ZCAT_PRIMARY', dtype=bool) # 确保是布尔类型
        ])
        
        # 添加一些其他列以模拟真实目录
        self.sample_table['RA'] = np.random.uniform(0, 360, self.n_rows)
        self.sample_table['DEC'] = np.random.uniform(-90, 90, self.n_rows)
        self.sample_table['DELTACHI2'] = np.random.uniform(10, 100, self.n_rows)

        try:
            self.sample_table.write(self.test_fits_file, format='fits', overwrite=True)
            # print(f"Test FITS file created at: {self.test_fits_file}")
        except Exception as e:
            self.fail(f"Failed to create test FITS file: {e}")

    def tearDown(self):
        """清理临时文件和目录。"""
        self.temp_dir.cleanup()
        # print(f"Test FITS file cleaned up from: {self.test_fits_file}")

    def test_catalog_loading_success(self):
        """测试成功加载目录。"""
        catalog = DESIRedshiftCatalog(self.test_fits_file)
        self.assertIsNotNone(catalog.data, "目录数据不应为None")
        self.assertEqual(len(catalog.data), self.n_rows, "加载的行数不匹配")
        self.assertIn('TARGETID', catalog.data.colnames, "'TARGETID'列应存在")
        self.assertIn('ZCAT_PRIMARY', catalog.data.colnames, "'ZCAT_PRIMARY'列应存在")

    def test_catalog_loading_file_not_found(self):
        """测试当文件不存在时加载目录。"""
        non_existent_file = os.path.join(self.temp_dir.name, 'does_not_exist.fits')
        catalog = DESIRedshiftCatalog(non_existent_file)
        self.assertIsNone(catalog.data, "当文件不存在时，目录数据应为None")

    def test_get_primary_targets(self):
        """测试获取主要目标。"""
        catalog = DESIRedshiftCatalog(self.test_fits_file)
        primary_targets = catalog.get_primary_targets()
        self.assertIsNotNone(primary_targets, "主要目标不应为None")
        expected_primary_count = np.sum(self.primary_flags)
        self.assertEqual(len(primary_targets), expected_primary_count, "主要目标数量不匹配")
        # 检查所有返回的目标确实是ZCAT_PRIMARY=True
        if len(primary_targets) > 0:
            self.assertTrue(np.all(primary_targets['ZCAT_PRIMARY']), "并非所有获取的目标都是主要目标")

    def test_get_primary_targets_no_primary_column(self):
        """测试当主要目标列不存在时的行为。"""
        # 创建一个没有ZCAT_PRIMARY列的FITS文件
        table_no_primary = self.sample_table.copy()
        table_no_primary.remove_column('ZCAT_PRIMARY')
        # 添加一个名为 'BEST_FIT' 的列，看它是否会被备用逻辑选中
        table_no_primary['BEST_FIT_EVER'] = np.ones(self.n_rows, dtype=bool)
        no_primary_fits_file = os.path.join(self.temp_dir.name, 'no_primary_col.fits')
        table_no_primary.write(no_primary_fits_file, format='fits', overwrite=True)

        catalog = DESIRedshiftCatalog(no_primary_fits_file)
        # 默认 primary_column='ZCAT_PRIMARY' 会失败，但备用逻辑应该找到 'BEST_FIT_EVER'
        primary_targets = catalog.get_primary_targets() 
        self.assertIsNotNone(primary_targets, "当尝试备用列时，主要目标不应为None")
        self.assertEqual(len(primary_targets), self.n_rows, "使用备用列时，主要目标数量不匹配")

    def test_calculate_redshift_stats(self):
        """测试计算红移统计。"""
        catalog = DESIRedshiftCatalog(self.test_fits_file)
        stats = catalog.calculate_redshift_stats()
        self.assertIsNotNone(stats, "红移统计不应为None")
        self.assertIn('mean', stats)
        self.assertIn('median', stats)
        self.assertAlmostEqual(stats['mean'], np.mean(self.redshifts), places=5)
        self.assertAlmostEqual(stats['median'], np.median(self.redshifts), places=5)
        self.assertEqual(stats['count'], self.n_rows)

    def test_calculate_redshift_stats_custom_column(self):
        """测试使用自定义红移列计算统计。"""
        # 添加一个名为 'MY_Z' 的新红移列
        self.sample_table['MY_Z'] = self.redshifts * 1.1
        custom_z_fits_file = os.path.join(self.temp_dir.name, 'custom_z_col.fits')
        self.sample_table.write(custom_z_fits_file, format='fits', overwrite=True)
        
        catalog = DESIRedshiftCatalog(custom_z_fits_file)
        stats = catalog.calculate_redshift_stats(redshift_column='MY_Z')
        self.assertIsNotNone(stats)
        self.assertAlmostEqual(stats['mean'], np.mean(self.redshifts * 1.1), places=5)

    def test_filter_by_redshift_range(self):
        """测试按红移范围筛选。"""
        catalog = DESIRedshiftCatalog(self.test_fits_file)
        min_z, max_z = 0.3, 0.7
        filtered = catalog.filter_by_redshift_range(min_z, max_z)
        self.assertIsNotNone(filtered)
        
        expected_mask = (self.redshifts >= min_z) & (self.redshifts <= max_z)
        expected_count = np.sum(expected_mask)
        self.assertEqual(len(filtered), expected_count, "筛选后的目标数量不匹配")
        if expected_count > 0:
            self.assertTrue(np.all((filtered['Z'] >= min_z) & (filtered['Z'] <= max_z)))

    def test_get_column_names(self):
        """测试获取列名。"""
        catalog = DESIRedshiftCatalog(self.test_fits_file)
        colnames = catalog.get_column_names()
        self.assertIsInstance(colnames, list)
        self.assertEqual(len(colnames), len(self.sample_table.colnames))
        for col in self.sample_table.colnames:
            self.assertIn(col, colnames)

if __name__ == '__main__':
    unittest.main()
