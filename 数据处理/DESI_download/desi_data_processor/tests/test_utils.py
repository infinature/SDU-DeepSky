"""
测试 desi_data_processor.utils 中的工具函数
"""

import unittest
import numpy as np
import os
import tempfile
import shutil
from astropy.io import fits
from astropy.table import Table, Column

# 将项目根目录添加到Python路径
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from desi_data_processor.utils import data_stats
from desi_data_processor.utils import fits_utils
from desi_data_processor.utils import download_utils

class TestDataStats(unittest.TestCase):

    def test_robust_mean_std(self):
        """测试 robust_mean_std 函数。"""
        data_clean = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        mean_clean, std_clean = data_stats.robust_mean_std(data_clean)
        self.assertAlmostEqual(mean_clean, np.mean(data_clean))
        self.assertAlmostEqual(std_clean, np.std(data_clean))

        # 数据包含异常值
        data_outliers = np.array([1, 2, 3, 4, 5, 100, 6, 7, 8, 9, 10, -50])
        mean_outliers, std_outliers = data_stats.robust_mean_std(data_outliers, sigma_clip=3.0)
        
        # 期望稳健均值接近没有异常值的数据的均值
        # 期望稳健标准差小于包含异常值的数据的标准标准差
        true_values_no_outliers = np.array([1,2,3,4,5,6,7,8,9,10])
        self.assertLess(abs(mean_outliers - np.mean(true_values_no_outliers)), 2.0) # 允许一些偏差
        self.assertLess(std_outliers, np.std(data_outliers))
        self.assertGreater(std_outliers, 0)

        # 测试空数组
        mean_empty, std_empty = data_stats.robust_mean_std(np.array([]))
        self.assertTrue(np.isnan(mean_empty))
        self.assertTrue(np.isnan(std_empty))

        # 测试所有元素相同的数组
        data_same = np.array([5, 5, 5, 5, 5])
        mean_same, std_same = data_stats.robust_mean_std(data_same)
        self.assertEqual(mean_same, 5)
        self.assertEqual(std_same, 0)

    def test_weighted_mean_std(self):
        """测试 weighted_mean_std 函数。"""
        data = np.array([1, 2, 3, 4, 5])
        weights_equal = np.array([1, 1, 1, 1, 1])
        w_mean_eq, w_std_eq = data_stats.weighted_mean_std(data, weights_equal)
        self.assertAlmostEqual(w_mean_eq, np.mean(data))
        # 加权标准差的定义可能略有不同，但对于等权重，它应该接近
        # np.sqrt(np.sum(weights_equal * (data - w_mean_eq)**2) / np.sum(weights_equal))
        # 或者，对于无偏估计器，分母可能是 (N-1)/N * sum(weights) 或 sum(weights) - sum(weights^2)/sum(weights)
        # 这里我们只检查它是否合理
        self.assertAlmostEqual(w_std_eq, np.std(data), places=5) 

        weights_unequal = np.array([1, 0, 0, 0, 5]) # 重点在最后一个元素
        w_mean_uneq, w_std_uneq = data_stats.weighted_mean_std(data, weights_unequal)
        expected_mean_uneq = (1*1 + 5*5) / (1+5) # (1+25)/6 = 26/6 = 4.333...
        self.assertAlmostEqual(w_mean_uneq, expected_mean_uneq)
        # 此时标准差应该较小，因为权重集中
        self.assertLess(w_std_uneq, np.std(data))

        # 测试零权重
        weights_zero = np.array([0, 0, 0, 0, 0])
        w_mean_zero, w_std_zero = data_stats.weighted_mean_std(data, weights_zero)
        self.assertTrue(np.isnan(w_mean_zero))
        self.assertTrue(np.isnan(w_std_zero))
        
        # 测试空数组
        w_mean_empty, w_std_empty = data_stats.weighted_mean_std(np.array([]), np.array([]))
        self.assertTrue(np.isnan(w_mean_empty))
        self.assertTrue(np.isnan(w_std_empty))

        # 测试数据和权重长度不匹配
        with self.assertRaises(ValueError):
            data_stats.weighted_mean_std(data, np.array([1,1]))

class TestFitsUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_fits_file = os.path.join(self.temp_dir.name, "test.fits")
        self._create_dummy_fits(self.test_fits_file)

    def _create_dummy_fits(self, filepath):
        hdul = fits.HDUList()
        # Primary HDU with a header keyword
        primary_hdu = fits.PrimaryHDU()
        primary_hdu.header['TESTKEY'] = ('TestValue', 'This is a test keyword')
        hdul.append(primary_hdu)

        # BinTable HDU
        data = Table([
            Column(np.array([1,2,3]), name='ID'), 
            Column(np.array(['a','b','c']), name='CODE')
        ])
        table_hdu = fits.BinTableHDU(data, name='MYTABLE')
        table_hdu.header['EXTKEY'] = ('ExtValue', 'Extension keyword')
        hdul.append(table_hdu)
        
        # Image HDU
        image_hdu = fits.ImageHDU(np.arange(100).reshape(10,10), name='MYIMAGE')
        hdul.append(image_hdu)
        
        hdul.writeto(filepath, overwrite=True)
        hdul.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_read_fits_header(self):
        """测试 read_fits_header 函数。"""
        header_p = fits_utils.read_fits_header(self.test_fits_file, hdu_index=0)
        self.assertIsNotNone(header_p)
        self.assertEqual(header_p['TESTKEY'], 'TestValue')

        header_1 = fits_utils.read_fits_header(self.test_fits_file, hdu_index=1)
        self.assertIsNotNone(header_1)
        self.assertEqual(header_1['EXTKEY'], 'ExtValue')
        self.assertEqual(header_1['XTENSION'], 'BINTABLE')
        self.assertEqual(header_1['EXTNAME'], 'MYTABLE')

        header_by_name = fits_utils.read_fits_header(self.test_fits_file, hdu_name='MYTABLE')
        self.assertIsNotNone(header_by_name)
        self.assertEqual(header_by_name['EXTNAME'], 'MYTABLE')

        # 测试无效索引/名称
        self.assertIsNone(fits_utils.read_fits_header(self.test_fits_file, hdu_index=10))
        self.assertIsNone(fits_utils.read_fits_header(self.test_fits_file, hdu_name='NONEXISTENT'))
        self.assertIsNone(fits_utils.read_fits_header("nonexistent.fits"))

    def test_extract_table_from_fits(self):
        """测试 extract_table_from_fits 函数。"""
        table = fits_utils.extract_table_from_fits(self.test_fits_file, hdu_index=1)
        self.assertIsNotNone(table)
        self.assertIsInstance(table, Table)
        self.assertEqual(len(table), 3)
        self.assertIn('ID', table.colnames)

        table_by_name = fits_utils.extract_table_from_fits(self.test_fits_file, hdu_name='MYTABLE')
        self.assertIsNotNone(table_by_name)
        self.assertEqual(len(table_by_name), 3)

        # 测试非表格HDU
        self.assertIsNone(fits_utils.extract_table_from_fits(self.test_fits_file, hdu_index=0)) # Primary
        self.assertIsNone(fits_utils.extract_table_from_fits(self.test_fits_file, hdu_index=2)) # Image
        self.assertIsNone(fits_utils.extract_table_from_fits("nonexistent.fits"))

    def test_list_hdus(self):
        """测试 list_hdus 函数。"""
        hdu_info_list = fits_utils.list_hdus(self.test_fits_file)
        self.assertIsNotNone(hdu_info_list)
        self.assertEqual(len(hdu_info_list), 3)
        
        # 检查第一个HDU (Primary)
        self.assertEqual(hdu_info_list[0][0], 0) # index
        self.assertEqual(hdu_info_list[0][1], '') # name for Primary is usually empty or 'PRIMARY'
        self.assertIn(hdu_info_list[0][2].lower(), ['primaryhdu', 'imagehdu']) # Type can vary slightly
        self.assertEqual(hdu_info_list[0][3], 'IMAGE') # XTENSION for Primary is IMAGE

        # 检查第二个HDU (BinTable)
        self.assertEqual(hdu_info_list[1][0], 1) # index
        self.assertEqual(hdu_info_list[1][1], 'MYTABLE') # name
        self.assertEqual(hdu_info_list[1][2].lower(), 'bintablehdu') # type
        self.assertEqual(hdu_info_list[1][3], 'BINTABLE') # XTENSION

        # 检查第三个HDU (Image)
        self.assertEqual(hdu_info_list[2][0], 2) # index
        self.assertEqual(hdu_info_list[2][1], 'MYIMAGE') # name
        self.assertEqual(hdu_info_list[2][2].lower(), 'imagehdu') # type
        self.assertEqual(hdu_info_list[2][3], 'IMAGE') # XTENSION

        self.assertIsNone(fits_utils.list_hdus("nonexistent.fits"))

class TestDownloadUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.download_path = os.path.join(self.temp_dir.name, "downloaded_file.txt")
        # 一个小的、可靠的公共文件URL用于测试
        # 使用GitHub raw content URL指向一个简单的文本文件
        # 注意：这个URL可能会改变或变得不可用，这会使测试失败。理想情况下，应该使用本地服务器或mock。
        self.test_url = "https://raw.githubusercontent.com/desihub/desiutil/master/LICENSE.rst"
        self.test_file_content_start = "desiutil License Agreement"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_download_file_success(self):
        """测试成功下载文件。"""
        success = download_utils.download_file(self.test_url, self.download_path)
        self.assertTrue(success, f"下载失败，URL: {self.test_url}")
        self.assertTrue(os.path.exists(self.download_path))
        with open(self.download_path, 'r') as f:
            content = f.read()
        self.assertTrue(content.startswith(self.test_file_content_start), "下载的文件内容不符合预期")

    def test_download_file_overwrite_false(self):
        """测试当文件已存在且overwrite=False时不下载。"""
        # 先创建一个假文件
        with open(self.download_path, 'w') as f:
            f.write("dummy content")
        original_mtime = os.path.getmtime(self.download_path)

        success = download_utils.download_file(self.test_url, self.download_path, overwrite=False)
        self.assertTrue(success, "即使文件存在且overwrite=False，download_file也应返回True")
        self.assertEqual(os.path.getmtime(self.download_path), original_mtime, "文件不应被覆盖")
        with open(self.download_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "dummy content")

    def test_download_file_overwrite_true(self):
        """测试当文件已存在且overwrite=True时下载。"""
        with open(self.download_path, 'w') as f:
            f.write("old dummy content")
        
        success = download_utils.download_file(self.test_url, self.download_path, overwrite=True)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.download_path))
        with open(self.download_path, 'r') as f:
            content = f.read()
        self.assertTrue(content.startswith(self.test_file_content_start), "覆盖后的文件内容不符合预期")

    def test_download_file_invalid_url(self):
        """测试使用无效URL下载。"""
        invalid_url = "http://thisurldoesnotexistatallipromise.com/file.txt"
        success = download_utils.download_file(invalid_url, self.download_path)
        self.assertFalse(success)
        self.assertFalse(os.path.exists(self.download_path))

    def test_download_file_non_existent_path(self):
        """测试下载到不存在的目录路径 (应自动创建)。"""
        non_existent_subdir = os.path.join(self.temp_dir.name, "new_subdir", "downloaded.txt")
        success = download_utils.download_file(self.test_url, non_existent_subdir)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(non_existent_subdir))

if __name__ == '__main__':
    unittest.main()
