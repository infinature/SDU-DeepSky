"""
处理DESI光谱数据的通用模块
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

class SpectraProcessor:
    """
    处理和分析DESI光谱数据的类。
    这个类可以处理从 HEALPixProcessor 或其他来源获得的光谱数据。
    """
    def __init__(self, flux, ivar, wavelength, mask=None, target_id=None, metadata=None):
        """
        初始化光谱处理器。

        参数:
            flux (dict): 包含各波段 ('B', 'R', 'Z') 通量数组的字典。
            ivar (dict): 包含各波段 ('B', 'R', 'Z') 逆方差数组的字典。
            wavelength (dict): 包含各波段 ('B', 'R', 'Z') 波长数组的字典。
            mask (dict, optional): 包含各波段 ('B', 'R', 'Z') 掩码数组的字典。
            target_id (any, optional): 光谱对应的目标ID。
            metadata (dict, optional): 光谱相关的元数据。
        """
        self.flux = flux
        self.ivar = ivar
        self.wavelength = wavelength
        self.mask = mask if mask is not None else {}
        self.target_id = target_id
        self.metadata = metadata if metadata is not None else {}
        self.bands = sorted(self.flux.keys()) # 通常是 ['B', 'R', 'Z']

        self._validate_input()

    def _validate_input(self):
        """验证输入数据的结构和一致性。"""
        for band in self.bands:
            if band not in self.ivar or band not in self.wavelength:
                raise ValueError(f"波段 '{band}' 的通量、逆方差和波长数据必须都存在。")
            if not (len(self.flux[band]) == len(self.ivar[band]) == len(self.wavelength[band])):
                raise ValueError(f"波段 '{band}' 的通量、逆方差和波长数组长度必须一致。")
            if band in self.mask and (len(self.mask[band]) != len(self.flux[band])):
                raise ValueError(f"波段 '{band}' 的掩码数组长度必须与通量一致。")
        print(f"SpectraProcessor 初始化成功，目标ID: {self.target_id}, 波段: {self.bands}")

    def get_combined_spectrum(self, apply_mask=True):
        """
        将所有波段的光谱数据合并（按波长排序）。

        参数:
            apply_mask (bool): 是否应用掩码（将掩码位置的通量和逆方差设为NaN）。

        返回:
            tuple: (combined_wavelength, combined_flux, combined_ivar)
        """
        all_wl, all_flux, all_ivar = [], [], []

        for band in self.bands:
            wl = self.wavelength[band]
            fx = self.flux[band].copy()
            iv = self.ivar[band].copy()

            if apply_mask and band in self.mask and self.mask[band] is not None:
                # DESI的掩码通常标记坏点，0表示好，非0表示有问题
                # 这里假设掩码中非0值表示需要掩盖的点
                bad_pixels = self.mask[band] != 0
                fx[bad_pixels] = np.nan
                iv[bad_pixels] = 0 # 或者 np.nan，取决于后续处理
            
            all_wl.append(wl)
            all_flux.append(fx)
            all_ivar.append(iv)
        
        combined_wl = np.concatenate(all_wl)
        combined_flux = np.concatenate(all_flux)
        combined_ivar = np.concatenate(all_ivar)

        # 按波长排序
        sort_indices = np.argsort(combined_wl)
        return combined_wl[sort_indices], combined_flux[sort_indices], combined_ivar[sort_indices]

    def plot_spectrum(self, band=None, title=None, show_ivar=False, apply_mask=True, ax=None):
        """
        绘制光谱图。

        参数:
            band (str, optional): 要绘制的特定波段 ('B', 'R', 'Z')。如果为None，则绘制合并光谱。
            title (str, optional): 图表标题。
            show_ivar (bool): 是否在图上显示逆方差（作为误差棒的近似）。
            apply_mask (bool): 是否在绘图时应用掩码。
            ax (matplotlib.axes.Axes, optional): 用于绘图的现有Axes对象。
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        
        if band is not None:
            if band not in self.bands:
                print(f"波段 '{band}' 不可用。可用波段: {self.bands}")
                return
            
            wl = self.wavelength[band]
            fx = self.flux[band].copy()
            iv = self.ivar[band].copy()

            if apply_mask and band in self.mask and self.mask[band] is not None:
                bad_pixels = self.mask[band] != 0
                fx[bad_pixels] = np.nan
                if show_ivar: iv[bad_pixels] = 0 # 避免计算无效误差

            ax.plot(wl, fx, label=f'Flux ({band})')
            if show_ivar:
                # 误差 = 1 / sqrt(ivar)，但要处理 ivar <= 0 的情况
                err = np.zeros_like(iv)
                good_ivar = iv > 0
                err[good_ivar] = 1.0 / np.sqrt(iv[good_ivar])
                ax.fill_between(wl, fx - err, fx + err, alpha=0.3, label=f'Error ({band})')
            plot_title = f'Spectrum (Band {band})' 
        else:
            wl, fx, iv = self.get_combined_spectrum(apply_mask=apply_mask)
            ax.plot(wl, fx, label='Combined Flux')
            if show_ivar:
                err = np.zeros_like(iv)
                good_ivar = iv > 0
                err[good_ivar] = 1.0 / np.sqrt(iv[good_ivar])
                ax.fill_between(wl, fx - err, fx + err, alpha=0.3, label='Error')
            plot_title = 'Combined Spectrum'

        if self.target_id is not None:
            plot_title += f' - Target ID: {self.target_id}'
        
        ax.set_xlabel('Wavelength (Angstrom)')
        ax.set_ylabel('Flux')
        ax.set_title(title if title is not None else plot_title)
        ax.legend()
        ax.grid(True, alpha=0.5)
        
        if ax is None: # 如果是新创建的fig
            plt.show()

    def calculate_snr(self, band, wavelength_range=None):
        """
        计算指定波段和波长范围内的信噪比 (SNR)。
        SNR 定义为: sum(flux * ivar) / sqrt(sum(ivar))  (近似)
        或者更简单的: median(flux) / median(error) = median(flux) * median(sqrt(ivar))

        参数:
            band (str): 要计算SNR的波段。
            wavelength_range (tuple, optional): (min_wl, max_wl) 波长范围。如果为None，则使用整个波段。

        返回:
            float or None: 计算得到的SNR，如果数据不足或无效则返回None。
        """
        if band not in self.bands:
            print(f"波段 '{band}' 不可用。")
            return None

        wl = self.wavelength[band]
        fx = self.flux[band]
        iv = self.ivar[band]

        mask_indices = np.ones_like(wl, dtype=bool)
        if wavelength_range is not None:
            mask_indices &= (wl >= wavelength_range[0]) & (wl <= wavelength_range[1])
        
        if self.mask is not None and band in self.mask and self.mask[band] is not None:
            # 只使用未被掩码的像素
            mask_indices &= (self.mask[band] == 0)

        wl_roi = wl[mask_indices]
        fx_roi = fx[mask_indices]
        iv_roi = iv[mask_indices]

        if len(fx_roi) == 0 or len(iv_roi) == 0:
            print(f"在波段 {band} 的指定范围内没有有效数据点用于SNR计算。")
            return None
        
        # 使用 median(flux * sqrt(ivar)) 作为SNR的简单估计
        # 确保ivar是正的
        good_ivar = iv_roi > 1e-6 # 避免sqrt(0)或极小ivar导致的问题
        if np.sum(good_ivar) == 0:
            print(f"在波段 {band} 的指定范围内没有有效的ivar数据点。")
            return 0.0 # 或者 None
        
        snr_per_pixel = fx_roi[good_ivar] * np.sqrt(iv_roi[good_ivar])
        # 通常取中位数或平均值
        # median_snr = np.nanmedian(snr_per_pixel)
        # 另一种定义： signal = sum(flux*ivar) / sum(ivar), noise_variance = 1/sum(ivar)
        # signal_weighted_sum = np.nansum(fx_roi * iv_roi)
        # ivar_sum = np.nansum(iv_roi)
        # if ivar_sum <= 1e-6:
        #     return 0.0
        # mean_flux_weighted = signal_weighted_sum / ivar_sum
        # snr = mean_flux_weighted * np.sqrt(ivar_sum)
        
        # DESI通常报告每个相机的SNR中位数，这里我们用一个简化的版本
        # 参考 desispec.coaddition.coadd_cameras
        # flux_sum = np.nansum(fx_roi)
        # ivar_eff = np.nansum(iv_roi)
        # if ivar_eff <= 0:
        #     return 0.0
        # snr = flux_sum * np.sqrt(ivar_eff) / np.sqrt(len(fx_roi)) # 这不完全标准

        # 使用更标准的定义： sum(S_i * w_i) / sqrt(sum(w_i)) where w_i = ivar_i
        # This is effectively sqrt(chi^2) if null hypothesis is S=0.
        # Or, more simply, median(flux / sigma) = median(flux * sqrt(ivar))
        median_snr_per_pixel = np.nanmedian(fx_roi[good_ivar] * np.sqrt(iv_roi[good_ivar]))
        return median_snr_per_pixel


if __name__ == '__main__':
    # 这是一个使用示例，通常你会从 HEALPixProcessor 获取光谱数据
    print("SpectraProcessor 类已定义。")
    print("你需要从 HEALPixProcessor 或其他来源获取光谱数据来实例化此类。")

    # 模拟数据示例
    bands_data = {
        'B': {
            'wavelength': np.linspace(3600, 5800, 2200),
            'flux': np.random.normal(10, 2, 2200) + 50 * np.exp(-0.5 * ((np.linspace(3600, 5800, 2200) - 4500) / 100)**2),
            'ivar': np.ones(2200) * 0.25, # (error = 2)
            'mask': np.zeros(2200, dtype=int)
        },
        'R': {
            'wavelength': np.linspace(5700, 7700, 2000),
            'flux': np.random.normal(12, 2.5, 2000) + 70 * np.exp(-0.5 * ((np.linspace(5700, 7700, 2000) - 6500) / 120)**2),
            'ivar': np.ones(2000) * 0.16, # (error = 2.5)
            'mask': np.zeros(2000, dtype=int)
        },
        'Z': {
            'wavelength': np.linspace(7600, 9800, 2200),
            'flux': np.random.normal(9, 1.8, 2200) + 60 * np.exp(-0.5 * ((np.linspace(7600, 9800, 2200) - 8500) / 150)**2),
            'ivar': np.ones(2200) * 0.3, 
            'mask': np.zeros(2200, dtype=int)
        }
    }
    # 添加一些掩码点
    bands_data['B']['mask'][100:150] = 1 
    bands_data['R']['flux'][500:550] += 50 # 模拟宇宙线
    bands_data['R']['mask'][500:550] = 1 # 假设被正确标记

    flux_dict = {b: d['flux'] for b, d in bands_data.items()}
    ivar_dict = {b: d['ivar'] for b, d in bands_data.items()}
    wave_dict = {b: d['wavelength'] for b, d in bands_data.items()}
    mask_dict = {b: d['mask'] for b, d in bands_data.items()}

    try:
        spec_proc = SpectraProcessor(
            flux=flux_dict, 
            ivar=ivar_dict, 
            wavelength=wave_dict, 
            mask=mask_dict, 
            target_id=12345
        )

        print("\n绘制单个波段 (R) 的光谱:")
        spec_proc.plot_spectrum(band='R', show_ivar=True)
        plt.show() # 在脚本模式下需要 plt.show()

        print("\n绘制合并的光谱:")
        spec_proc.plot_spectrum(show_ivar=True, apply_mask=True)
        plt.show()

        print("\n计算各波段SNR:")
        for b in spec_proc.bands:
            snr = spec_proc.calculate_snr(band=b)
            print(f"  SNR ({b}): {snr:.2f}")
        
        snr_r_region = spec_proc.calculate_snr(band='R', wavelength_range=(6000, 7000))
        print(f"  SNR (R, 6000-7000A): {snr_r_region:.2f}")

    except ValueError as e:
        print(f"创建SpectraProcessor实例时出错: {e}")
    except Exception as e:
        print(f"运行示例时发生意外错误: {e}")

