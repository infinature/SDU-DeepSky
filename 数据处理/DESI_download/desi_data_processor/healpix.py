"""
处理DESI HEALPixel数据的模块
"""

import numpy as np
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy_healpix import HEALPix
from astropy.coordinates import Galactic, ICRS
import os

class HEALPixProcessor:
    """
    处理DESI HEALPixel数据的类。

    参数:
        base_path (str): DESI HEALPixel数据的基础路径 (例如 'spectro/redux/MOUNTAIN/healpix/')
        survey (str): 巡天名称 (例如 'main', 'sv1', 'sv3')
        program (str): 程序名称 (例如 'dark', 'bright')
        nside (int): HEALPixel图的NSIDE参数，DESI通常使用64。
    """
    def __init__(self, base_path, survey, program, nside=64):
        self.base_path = base_path
        self.survey = survey
        self.program = program
        self.nside = nside
        self.hp = HEALPix(nside=nside, order='nested', frame=ICRS())
        print(f"HEALPixProcessor 初始化: survey='{survey}', program='{program}', nside={nside}")

    def get_healpix_data_path(self, healpix_id):
        """
        获取给定HEALPixel ID的数据文件路径。
        根据DESI的目录结构: spectro/redux/MOUNTAIN/healpix/SURVEY/PROGRAM/HPIXGROUP/HEALPIX/
        HPIXGROUP = floor(HEALPIX/100)

        参数:
            healpix_id (int): HEALPixel的ID。

        返回:
            str: 对应HEALPixel ID的数据目录路径。
        """
        hpix_group = int(np.floor(healpix_id / 100))
        # 路径格式可能需要根据实际数据服务器或本地存储调整
        # 例如: https://data.desi.lbl.gov/public/dr1/spectro/redux/iron/healpix/main/dark/315/31542/
        # 这里假设base_path指向 '.../iron/healpix/' 这样的层级
        return os.path.join(self.base_path, self.survey, self.program, str(hpix_group), str(healpix_id))

    def list_files_in_healpix_dir(self, healpix_id, file_prefix='coadd'):
        """
        列出给定HEALPixel目录中特定前缀的文件（通常是coadd光谱文件）。

        参数:
            healpix_id (int): HEALPixel的ID。
            file_prefix (str): 文件名前缀，例如 'coadd', 'spectra', 'redrock'。

        返回:
            list: 文件路径列表。
        """
        dir_path = self.get_healpix_data_path(healpix_id)
        if not os.path.isdir(dir_path):
            print(f"目录不存在: {dir_path}")
            # 尝试模拟从URL获取的场景，如果实际应用需要下载，则需要实现下载逻辑
            # print(f"提示: 如果这是远程路径，你需要先下载数据或使用支持远程访问的库。")
            return []
        
        files_found = []
        try:
            for fname in os.listdir(dir_path):
                if fname.startswith(file_prefix) and fname.endswith('.fits'):
                    files_found.append(os.path.join(dir_path, fname))
            print(f"在 {dir_path} 中找到 {len(files_found)} 个以 '{file_prefix}' 开头的文件。")
        except Exception as e:
            print(f"列出文件时出错 {dir_path}: {e}")
        return files_found

    def load_coadd_spectra(self, healpix_id, target_ids=None):
        """
        加载指定HEALPixel的coadd光谱数据，可以选择性地为特定目标加载。
        文件名通常是 coadd-{SURVEY}-{PROGRAM}-{HEALPIX}.fits

        参数:
            healpix_id (int): HEALPixel的ID。
            target_ids (list, optional): 要加载光谱的目标ID列表。如果为None，则尝试加载所有目标。

        返回:
            dict or None: 包含光谱数据的字典 (例如 {'TARGETID': spectra_data})，如果文件未找到或出错则返回None。
        """
        dir_path = self.get_healpix_data_path(healpix_id)
        # 构建标准coadd文件名
        coadd_filename = f"coadd-{self.survey}-{self.program}-{healpix_id}.fits"
        file_path = os.path.join(dir_path, coadd_filename)

        if not os.path.exists(file_path):
            print(f"Coadd光谱文件未找到: {file_path}")
            # 尝试查找其他可能的coadd文件，因为有时文件名可能略有不同
            alternative_files = self.list_files_in_healpix_dir(healpix_id, file_prefix='coadd')
            if alternative_files:
                print(f"找到备选coadd文件: {alternative_files[0]}，尝试加载它。")
                file_path = alternative_files[0]
            else:
                return None
        
        spectra_data = {}
        try:
            with fits.open(file_path) as hdul:
                print(f"成功打开: {file_path}")
                # 通常光谱数据在 'FLUX', 'IVAR', 'WAVELENGTH', 'MASK' 等HDUs中
                # 目标ID通常在 'FIBERMAP' HDU中
                fibermap = hdul['FIBERMAP'].data
                targetid_col_name = None
                for col in ['TARGETID', 'TARGET_ID']:
                    if col in fibermap.dtype.names:
                        targetid_col_name = col
                        break
                if not targetid_col_name:
                    print("在FIBERMAP中未找到TARGETID列。")
                    return None

                all_target_ids_in_file = fibermap[targetid_col_name]

                # 确定要加载的光谱索引
                indices_to_load = []
                if target_ids is not None:
                    for i, tid in enumerate(all_target_ids_in_file):
                        if tid in target_ids:
                            indices_to_load.append(i)
                    if not indices_to_load:
                        print(f"在文件中未找到指定的目标ID: {target_ids}")
                        return {}
                else:
                    indices_to_load = list(range(len(all_target_ids_in_file)))
                
                print(f"将为 {len(indices_to_load)} 个目标加载光谱数据。")

                # 加载各波段数据 (b, r, z)
                for band in ['B', 'R', 'Z']:
                    flux_hdu_name = f'FLUX_{band}'
                    ivar_hdu_name = f'IVAR_{band}'
                    wave_hdu_name = f'WAVELENGTH_{band}' # 波长通常每个波段一个，或者一个共享的
                    mask_hdu_name = f'MASK_{band}'

                    if flux_hdu_name in hdul and ivar_hdu_name in hdul:
                        flux = hdul[flux_hdu_name].data[indices_to_load]
                        ivar = hdul[ivar_hdu_name].data[indices_to_load]
                        wavelength = hdul[wave_hdu_name].data # 波长通常是一维数组
                        mask = hdul[mask_hdu_name].data[indices_to_load] if mask_hdu_name in hdul else None
                        
                        for i, original_idx in enumerate(indices_to_load):
                            tid = all_target_ids_in_file[original_idx]
                            if tid not in spectra_data:
                                spectra_data[tid] = {}
                            spectra_data[tid][band] = {
                                'flux': flux[i],
                                'ivar': ivar[i],
                                'wavelength': wavelength,
                                'mask': mask[i] if mask is not None else None
                            }
            return spectra_data
        except Exception as e:
            print(f"加载coadd光谱时出错 {file_path}: {e}")
            return None

    def get_healpix_pixel_coords(self, healpix_ids):
        """
        获取给定HEALPixel ID列表的赤道坐标 (RA, Dec)。

        参数:
            healpix_ids (int or list): 一个或多个HEALPixel ID。

        返回:
            tuple: (ra, dec) 坐标数组 (度)。
        """
        if not isinstance(healpix_ids, (list, np.ndarray)):
            healpix_ids = [healpix_ids]
        
        # 使用 astropy_healpix 获取像素中心坐标
        coords = self.hp.healpix_to_skycoord(healpix_ids)
        ra = coords.ra.deg
        dec = coords.dec.deg
        return ra, dec

if __name__ == '__main__':
    # 这是一个使用示例，你需要提供一个实际的DESI HEALPixel数据基础路径
    # 并确保相应的 survey/program/healpix_id 结构存在且包含数据文件
    
    # 示例路径，你需要根据你的数据存储位置进行修改
    # base_data_dir = '/global/cfs/cdirs/desi/public/dr1/spectro/redux/iron/healpix/'
    # print(f"请将 'base_data_dir' 变量替换为实际的DESI HEALPixel数据基础路径以运行示例。")

    # if os.path.isdir(base_data_dir):
    #     # 示例：处理 main survey, dark program 的数据
    #     processor = HEALPixProcessor(base_path=base_data_dir, survey='main', program='dark', nside=64)

    #     # 示例HEALPixel ID (来自文档)
    #     example_hpix_id = 31542

    #     print(f"\n获取HEALPixel {example_hpix_id} 的数据路径:")
    #     hp_path = processor.get_healpix_data_path(example_hpix_id)
    #     print(hp_path)

    #     print(f"\n列出HEALPixel {example_hpix_id} 目录中的coadd文件:")
    #     coadd_files = processor.list_files_in_healpix_dir(example_hpix_id, file_prefix='coadd')
    #     print(coadd_files)

    #     if coadd_files:
    #         print(f"\n加载HEALPixel {example_hpix_id} 的coadd光谱数据 (前2个目标，如果存在):")
    #         # 为了测试，我们首先需要知道哪些TARGETID在该文件中
    #         # 实际应用中，你可能从一个目录中获得TARGETID列表
    #         # 这里我们尝试加载所有目标，然后取前几个
    #         all_spectra = processor.load_coadd_spectra(example_hpix_id)
    #         if all_spectra:
    #             print(f"成功加载 {len(all_spectra)} 个目标的光谱。")
    #             count = 0
    #             for tid, spec_data in all_spectra.items():
    #                 print(f"  目标ID: {tid}")
    #                 # print(f"    B波段通量形状: {spec_data.get('B', {}).get('flux', np.array([])).shape}")
    #                 count += 1
    #                 if count >= 2: break
    #         else:
    #             print(f"未能加载HEALPixel {example_hpix_id} 的光谱数据。")
    #     else:
    #         print(f"在 {hp_path} 中未找到coadd文件，无法加载光谱。")
        
    #     print(f"\n获取HEALPixel {example_hpix_id} 的坐标:")
    #     ra, dec = processor.get_healpix_pixel_coords(example_hpix_id)
    #     print(f"RA: {ra}, Dec: {dec}")

    # else:
    #     print(f"基础数据目录未找到: {base_data_dir}")
    #     print("请确保DESI数据已下载并正确配置了路径。")
    #     print("例如，从 https://data.desi.lbl.gov/public/dr1/spectro/redux/iron/healpix/ 下载数据")

    print("HEALPixProcessor 类已定义。取消注释并提供正确的数据路径以运行示例。")
