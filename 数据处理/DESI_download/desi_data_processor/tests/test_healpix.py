"""
测试 HEALPixProcessor 类
"""

import unittest
import os
import tempfile
import shutil
import numpy as np
from astropy.io import fits
from astropy.table import Table, Column

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from desi_data_processor.healpix import HEALPixProcessor

class TestHEALPixProcessor(unittest.TestCase):

    def setUp(self):
        """为测试创建临时的HEALPix数据目录结构和文件。"""
        self.temp_root_dir = tempfile.mkdtemp() # e.g., /tmp/somerandomname
        
        self.mountain = 'test_mountain'
        self.survey = 'main'
        self.program = 'dark'
        self.nside = 64
        self.example_healpix_id = 12345
        self.hpix_group = int(np.floor(self.example_healpix_id / 100)) # 123

        # base_path for HEALPixProcessor will be .../temp_root_dir/test_mountain/healpix/
        self.base_path_for_processor = os.path.join(self.temp_root_dir, self.mountain, 'healpix')

        # 实际文件将存储在 .../base_path_for_processor/main/dark/123/12345/
        self.healpix_data_dir = os.path.join(
            self.base_path_for_processor, 
            self.survey, 
            self.program, 
            str(self.hpix_group), 
            str(self.example_healpix_id)
        )
        os.makedirs(self.healpix_data_dir, exist_ok=True)

        # 创建一个假的 coadd FITS 文件
        self.coadd_filename = f"coadd-{self.survey}-{self.program}-{self.example_healpix_id}.fits"
        self.coadd_filepath = os.path.join(self.healpix_data_dir, self.coadd_filename)
        self._create_dummy_coadd_fits(self.coadd_filepath)
        
        # 创建一个其他文件以测试列表功能
        self.other_filename = f"spectra-{self.survey}-{self.program}-{self.example_healpix_id}.fits"
        other_filepath = os.path.join(self.healpix_data_dir, self.other_filename)
        self._create_dummy_coadd_fits(other_filepath) # 用同样的结构创建，内容不重要

        self.processor = HEALPixProcessor(
            base_path=self.base_path_for_processor, 
            survey=self.survey, 
            program=self.program, 
            nside=self.nside
        )

    def _create_dummy_coadd_fits(self, filepath, num_targets=3):
        """创建一个包含基本HDUs的虚拟coadd FITS文件。"""
        hdul = fits.HDUList()
        hdul.append(fits.PrimaryHDU()) # Primary HDU

        # FIBERMAP HDU
        target_ids = np.array([101, 102, 103])[:num_targets]
        fibermap_data = Table([
            Column(target_ids, name='TARGETID'),
            Column(np.random.rand(num_targets), name='FLUX_G'), # Dummy column
        ])
        hdul.append(fits.BinTableHDU(fibermap_data, name='FIBERMAP'))

        # 光谱数据 HDUs (B, R, Z bands)
        num_pixels = 100
        wavelength_b = np.linspace(3600, 5800, num_pixels)
        wavelength_r = np.linspace(5700, 7700, num_pixels)
        wavelength_z = np.linspace(7600, 9800, num_pixels)

        for band, wave_array in zip(['B', 'R', 'Z'], [wavelength_b, wavelength_r, wavelength_z]):
            flux = np.random.rand(num_targets, num_pixels).astype(np.float32)
            ivar = np.ones_like(flux).astype(np.float32)
            mask = np.zeros_like(flux, dtype=np.int32)
            # wavelength is 1D
            hdul.append(fits.ImageHDU(flux, name=f'FLUX_{band}'))
            hdul.append(fits.ImageHDU(ivar, name=f'IVAR_{band}'))
            hdul.append(fits.ImageHDU(mask, name=f'MASK_{band}'))
            hdul.append(fits.ImageHDU(wave_array.astype(np.float32), name=f'WAVELENGTH_{band}'))
        
        try:
            hdul.writeto(filepath, overwrite=True)
        except Exception as e:
            self.fail(f"Failed to create dummy FITS file {filepath}: {e}")
        finally:
            hdul.close()

    def tearDown(self):
        """清理临时目录。"""
        shutil.rmtree(self.temp_root_dir)
        # print(f"Test HEALPix data directory cleaned up from: {self.temp_root_dir}")

    def test_get_healpix_data_path(self):
        """测试获取HEALPix数据路径的逻辑。"""
        expected_path = self.healpix_data_dir
        calculated_path = self.processor.get_healpix_data_path(self.example_healpix_id)
        self.assertEqual(calculated_path, expected_path)

    def test_list_files_in_healpix_dir(self):
        """测试列出HEALPix目录中的文件。"""
        # 测试 coadd 文件
        coadd_files = self.processor.list_files_in_healpix_dir(self.example_healpix_id, file_prefix='coadd')
        self.assertEqual(len(coadd_files), 1)
        self.assertIn(self.coadd_filepath, coadd_files[0]) # Check full path

        # 测试 spectra 文件 (我们创建了一个名为 spectra-...fits 的文件)
        spectra_files = self.processor.list_files_in_healpix_dir(self.example_healpix_id, file_prefix='spectra')
        self.assertEqual(len(spectra_files), 1)
        self.assertIn(self.other_filename, spectra_files[0])

        # 测试不存在的前缀
        non_existent_files = self.processor.list_files_in_healpix_dir(self.example_healpix_id, file_prefix='nonexistent')
        self.assertEqual(len(non_existent_files), 0)

    def test_list_files_in_nonexistent_healpix_dir(self):
        """测试当HEALPix目录不存在时列出文件。"""
        non_existent_hpix_id = 99999
        files = self.processor.list_files_in_healpix_dir(non_existent_hpix_id)
        self.assertEqual(len(files), 0)

    def test_load_coadd_spectra_success(self):
        """测试成功加载coadd光谱数据。"""
        spectra_data = self.processor.load_coadd_spectra(self.example_healpix_id)
        self.assertIsNotNone(spectra_data)
        self.assertIsInstance(spectra_data, dict)
        
        # 基于 _create_dummy_coadd_fits 中的设置
        expected_num_targets = 3 
        self.assertEqual(len(spectra_data), expected_num_targets)
        
        # 检查其中一个目标的数据结构
        first_target_id = list(spectra_data.keys())[0]
        self.assertIn(first_target_id, [101, 102, 103])
        self.assertIn('B', spectra_data[first_target_id])
        self.assertIn('flux', spectra_data[first_target_id]['B'])
        self.assertEqual(spectra_data[first_target_id]['B']['flux'].shape, (100,))
        self.assertEqual(spectra_data[first_target_id]['B']['wavelength'].shape, (100,))

    def test_load_coadd_spectra_specific_targets(self):
        """测试加载特定目标的光谱。"""
        target_ids_to_load = [101, 103] # 这些ID在 _create_dummy_coadd_fits 中定义
        spectra_data = self.processor.load_coadd_spectra(self.example_healpix_id, target_ids=target_ids_to_load)
        self.assertIsNotNone(spectra_data)
        self.assertEqual(len(spectra_data), 2)
        self.assertIn(101, spectra_data)
        self.assertIn(103, spectra_data)
        self.assertNotIn(102, spectra_data)

    def test_load_coadd_spectra_file_not_found(self):
        """测试当coadd文件不存在时加载光谱。"""
        # 移除创建的coadd文件
        os.remove(self.coadd_filepath)
        spectra_data = self.processor.load_coadd_spectra(self.example_healpix_id)
        self.assertIsNone(spectra_data)

    def test_get_healpix_pixel_coords(self):
        """测试获取HEALPix像素坐标。"""
        # 这个测试依赖于healpy的正确性，主要是检查调用是否正常
        ra, dec = self.processor.get_healpix_pixel_coords(self.example_healpix_id)
        self.assertIsInstance(ra, np.ndarray)
        self.assertIsInstance(dec, np.ndarray)
        self.assertEqual(ra.shape, (1,))
        self.assertEqual(dec.shape, (1,))

        # 测试多个ID
        ids = [self.example_healpix_id, self.example_healpix_id + 1]
        ra_multi, dec_multi = self.processor.get_healpix_pixel_coords(ids)
        self.assertEqual(ra_multi.shape, (2,))
        self.assertEqual(dec_multi.shape, (2,))

if __name__ == '__main__':
    unittest.main()
