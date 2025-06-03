"""
测试 SpectraProcessor 类
"""

import unittest
import numpy as np
import matplotlib.pyplot as plt

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from desi_data_processor.spectra import SpectraProcessor

class TestSpectraProcessor(unittest.TestCase):

    def setUp(self):
        """设置基本的光谱数据用于测试。"""
        self.num_pixels = 100
        self.target_id = 12345

        self.flux = {
            'B': np.random.rand(self.num_pixels) + 1, # 确保flux为正以计算SNR
            'R': np.random.rand(self.num_pixels) + 1,
            'Z': np.random.rand(self.num_pixels) + 1
        }
        self.ivar = {
            'B': np.random.rand(self.num_pixels) * 10 + 1, # 确保ivar为正
            'R': np.random.rand(self.num_pixels) * 10 + 1,
            'Z': np.random.rand(self.num_pixels) * 10 + 1
        }
        self.wavelength = {
            'B': np.linspace(3600, 5800, self.num_pixels),
            'R': np.linspace(5700, 7700, self.num_pixels),
            'Z': np.linspace(7600, 9800, self.num_pixels)
        }
        self.mask = {
            'B': np.zeros(self.num_pixels, dtype=int),
            'R': np.zeros(self.num_pixels, dtype=int),
            'Z': np.zeros(self.num_pixels, dtype=int)
        }
        # 在R波段引入一些掩码位
        self.mask['R'][10:15] = 1 # 假设1是一些需要屏蔽的位

        self.processor = SpectraProcessor(
            flux=self.flux,
            ivar=self.ivar,
            wavelength=self.wavelength,
            mask=self.mask,
            target_id=self.target_id
        )

    def test_initialization(self):
        """测试SpectraProcessor的初始化。"""
        self.assertEqual(self.processor.target_id, self.target_id)
        self.assertEqual(len(self.processor.bands), 3)
        self.assertListEqual(sorted(self.processor.bands), ['B', 'R', 'Z'])
        self.assertTrue(all(band in self.processor.flux for band in ['B', 'R', 'Z']))

    def test_initialization_mismatched_bands(self):
        """测试当波段不匹配时初始化是否失败。"""
        flux_bad = self.flux.copy()
        del flux_bad['Z'] # flux中缺少Z波段
        with self.assertRaises(ValueError):
            SpectraProcessor(flux_bad, self.ivar, self.wavelength, self.mask, self.target_id)

    def test_initialization_mismatched_shapes(self):
        """测试当形状不匹配时初始化是否失败。"""
        ivar_bad_shape = self.ivar.copy()
        ivar_bad_shape['R'] = np.random.rand(self.num_pixels - 10) # R波段ivar形状错误
        with self.assertRaises(ValueError):
            SpectraProcessor(self.flux, ivar_bad_shape, self.wavelength, self.mask, self.target_id)

    def test_get_spectrum(self):
        """测试获取特定波段的光谱。"""
        spec_b = self.processor.get_spectrum('B')
        self.assertIsNotNone(spec_b)
        self.assertTrue(np.array_equal(spec_b['flux'], self.flux['B']))
        self.assertTrue(np.array_equal(spec_b['ivar'], self.ivar['B']))
        self.assertTrue(np.array_equal(spec_b['wavelength'], self.wavelength['B']))
        self.assertTrue(np.array_equal(spec_b['mask'], self.mask['B']))

    def test_get_spectrum_invalid_band(self):
        """测试获取无效波段的光谱。"""
        with self.assertRaises(ValueError):
            self.processor.get_spectrum('X') # X波段不存在

    def test_calculate_snr_single_band(self):
        """测试计算单个波段的SNR。"""
        snr_b = self.processor.calculate_snr(band='B')
        self.assertIsNotNone(snr_b)
        self.assertIsInstance(snr_b, float)
        
        # 手动计算B波段的SNR进行比较 (忽略掩码，因为B波段没有掩码)
        # SNR = median(flux * sqrt(ivar)) for flux > 0 and ivar > 0
        valid_flux_b = self.flux['B'][ (self.flux['B'] > 0) & (self.ivar['B'] > 0) ]
        valid_ivar_b = self.ivar['B'][ (self.flux['B'] > 0) & (self.ivar['B'] > 0) ]
        if len(valid_flux_b) > 0:
            expected_snr_b = np.median(valid_flux_b * np.sqrt(valid_ivar_b))
            self.assertAlmostEqual(snr_b, expected_snr_b, places=5)
        else:
            self.assertIsNone(snr_b) # 如果没有有效像素

    def test_calculate_snr_with_mask(self):
        """测试计算带有掩码的波段的SNR。"""
        snr_r = self.processor.calculate_snr(band='R')
        self.assertIsNotNone(snr_r)
        
        # 手动计算R波段的SNR，考虑掩码
        mask_r = self.mask['R'] == 0 # 只使用未被掩码的像素
        valid_flux_r = self.flux['R'][mask_r & (self.flux['R'] > 0) & (self.ivar['R'] > 0)]
        valid_ivar_r = self.ivar['R'][mask_r & (self.flux['R'] > 0) & (self.ivar['R'] > 0)]
        if len(valid_flux_r) > 0:
            expected_snr_r = np.median(valid_flux_r * np.sqrt(valid_ivar_r))
            self.assertAlmostEqual(snr_r, expected_snr_r, places=5)
        else:
            self.assertIsNone(snr_r)

    def test_calculate_snr_all_bands(self):
        """测试计算所有波段的SNR。"""
        snr_all = self.processor.calculate_snr()
        self.assertIsNotNone(snr_all)
        self.assertIsInstance(snr_all, dict)
        self.assertIn('B', snr_all)
        self.assertIn('R', snr_all)
        self.assertIn('Z', snr_all)
        self.assertAlmostEqual(snr_all['B'], self.processor.calculate_snr(band='B'), places=5)

    def test_plot_spectrum_single_band(self):
        """测试绘制单个波段的光谱 (检查是否能无错运行)。"""
        fig, ax = plt.subplots()
        try:
            self.processor.plot_spectrum(band='B', ax=ax)
            # 可以在这里添加更多关于绘图内容的断言，但这通常更复杂
            # 例如，检查ax上是否有线条对象
            self.assertTrue(len(ax.lines) > 0, "绘图上应有线条")
        except Exception as e:
            self.fail(f"plot_spectrum (single band) raised an exception: {e}")
        finally:
            plt.close(fig)

    def test_plot_spectrum_all_bands(self):
        """测试绘制所有波段的光谱 (检查是否能无错运行)。"""
        fig, ax = plt.subplots()
        try:
            self.processor.plot_spectrum(ax=ax)
            self.assertTrue(len(ax.lines) >= len(self.processor.bands), "绘图上应有对应波段数量的线条")
        except Exception as e:
            self.fail(f"plot_spectrum (all bands) raised an exception: {e}")
        finally:
            plt.close(fig)
            
    def test_plot_spectrum_with_ivar(self):
        """测试绘制光谱时显示ivar (检查是否能无错运行)。"""
        fig, ax = plt.subplots()
        try:
            self.processor.plot_spectrum(band='R', ax=ax, show_ivar=True)
            # 当 show_ivar=True 时，通常会绘制两条线 (flux 和 1/sqrt(ivar))
            # 或者使用 fill_between，检查ax上的collections
            self.assertTrue(len(ax.lines) > 0 or len(ax.collections) > 0, "绘图上应有线条或填充区域")
        except Exception as e:
            self.fail(f"plot_spectrum (with ivar) raised an exception: {e}")
        finally:
            plt.close(fig)

if __name__ == '__main__':
    unittest.main()
