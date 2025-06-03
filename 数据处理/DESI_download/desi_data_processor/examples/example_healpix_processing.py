"""
示例：使用 HEALPixProcessor 和 SpectraProcessor 处理HEALPix数据和光谱
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from desi_data_processor.healpix import HEALPixProcessor
from desi_data_processor.spectra import SpectraProcessor
from desi_data_processor.utils.download_utils import download_file
from desi_data_processor.utils.fits_utils import list_hdus # 导入以备不时之需

def main():
    print("DESI HEALPix 和光谱处理示例")
    print("===============================")

    # --- 配置 --- #
    # 使用文档中提到的示例HEALPix ID: 31542 (main survey, dark program)
    example_healpix_id = 31542
    survey = 'main'
    program = 'dark'
    mountain = 'iron' # 对于DR1, MOUNTAIN=iron
    nside = 64 # DESI标准NSIDE

    # 对应的coadd光谱文件URL
    # https://data.desi.lbl.gov/public/dr1/spectro/redux/iron/healpix/main/dark/315/31542/coadd-main-dark-31542.fits
    hpix_group = int(np.floor(example_healpix_id / 100))
    coadd_filename = f"coadd-{survey}-{program}-{example_healpix_id}.fits"
    coadd_url = f"https://data.desi.lbl.gov/public/dr1/spectro/redux/{mountain}/healpix/{survey}/{program}/{hpix_group}/{example_healpix_id}/{coadd_filename}"

    # 本地数据存储路径
    # base_path for HEALPixProcessor should point to .../mountain/healpix/
    # Files will be downloaded to .../mountain/healpix/survey/program/hpixgroup/hpixid/
    local_data_root = os.path.join(project_root, 'data', 'healpix_data')
    local_healpix_base_path = os.path.join(local_data_root, mountain, 'healpix')
    
    # 完整本地文件路径
    local_coadd_file_dir = os.path.join(local_healpix_base_path, survey, program, str(hpix_group), str(example_healpix_id))
    local_coadd_file_path = os.path.join(local_coadd_file_dir, coadd_filename)

    print(f"示例HEALPix ID: {example_healpix_id}")
    print(f"Coadd文件URL: {coadd_url}")
    print(f"本地Coadd文件目标路径: {local_coadd_file_path}")

    # --- 1. 下载数据 (如果本地不存在) --- #
    print("\n--- 步骤 1: 检查并下载示例Coadd光谱文件 --- ")
    if not os.path.exists(local_coadd_file_path):
        print(f"本地文件 '{local_coadd_file_path}' 未找到。")
        print(f"尝试从 '{coadd_url}' 下载...")
        if not os.path.exists(local_coadd_file_dir):
            os.makedirs(local_coadd_file_dir)
            print(f"已创建目录: {local_coadd_file_dir}")
        
        success = download_file(coadd_url, local_coadd_file_path, overwrite=False)
        if success:
            print(f"文件已成功下载到: {local_coadd_file_path}")
        else:
            print(f"文件下载失败。请检查URL或网络连接，或手动下载文件到指定路径。")
            print("脚本将退出，因为无法获取必要的示例文件。")
            return
    else:
        print(f"本地文件 '{local_coadd_file_path}' 已存在。跳过下载。")

    # --- 2. 初始化 HEALPixProcessor --- #
    print("\n--- 步骤 2: 初始化 HEALPixProcessor --- ")
    # base_path 指向 .../mountain/healpix/
    hp_processor = HEALPixProcessor(base_path=local_healpix_base_path, survey=survey, program=program, nside=nside)

    # --- 3. 获取并验证HEALPix数据路径 --- #
    print("\n--- 步骤 3: 获取并验证HEALPix数据路径 --- ")
    data_path = hp_processor.get_healpix_data_path(example_healpix_id)
    print(f"计算得到的HEALPix {example_healpix_id} 数据目录: {data_path}")
    if not os.path.isdir(data_path):
        print(f"错误: 目录 {data_path} 不存在或不是一个目录。请检查base_path和下载结构。")
        # return # 如果严格要求目录必须存在，则退出
    else:
        print(f"目录 {data_path} 验证成功。")

    # --- 4. 列出HEALPix目录中的文件 --- #
    print("\n--- 步骤 4: 列出HEALPix目录中的Coadd文件 --- ")
    # 这里的路径是相对于 base_path + survey + program 的，所以list_files_in_healpix_dir内部会构建完整路径
    coadd_files_found = hp_processor.list_files_in_healpix_dir(example_healpix_id, file_prefix='coadd')
    if coadd_files_found:
        print(f"在HEALPix {example_healpix_id} 目录中找到以下coadd文件:")
        for f_path in coadd_files_found:
            print(f"  - {f_path}")
        # 验证我们下载的文件是否在列表中
        if local_coadd_file_path in coadd_files_found:
            print(f"下载的示例文件 '{local_coadd_file_path}' 已在列表中确认。")
        else:
            print(f"警告: 下载的示例文件 '{local_coadd_file_path}' 未在列表 '{coadd_files_found}' 中找到。路径可能不匹配。")
    else:
        print(f"在HEALPix {example_healpix_id} 目录中未找到coadd文件。")

    # --- 5. 加载Coadd光谱数据 --- #
    print("\n--- 步骤 5: 加载Coadd光谱数据 --- ")
    # load_coadd_spectra 会查找 coadd-{SURVEY}-{PROGRAM}-{HEALPIX}.fits
    # 它使用 self.base_path, self.survey, self.program 来构建路径
    all_spectra_data = hp_processor.load_coadd_spectra(example_healpix_id)

    if all_spectra_data is None:
        print(f"未能从HEALPix {example_healpix_id} 加载光谱数据。")
        # 尝试列出HDU以帮助调试
        if os.path.exists(local_coadd_file_path):
            print(f"检查文件 {local_coadd_file_path} 的HDU结构:")
            hdus = list_hdus(local_coadd_file_path)
            if hdus:
                for hinfo in hdus:
                    print(f"  Index: {hinfo[0]}, Name: {hinfo[1]}, Type: {hinfo[2]}, XTENSION: {hinfo[3]}")
        return
    
    if not all_spectra_data: # 如果返回空字典
        print(f"在HEALPix {example_healpix_id} 的文件中未找到目标的光谱数据。")
        return

    print(f"成功加载了 {len(all_spectra_data)} 个目标的光谱数据。")
    target_ids_loaded = list(all_spectra_data.keys())
    print(f"加载的目标ID示例: {target_ids_loaded[:5]} ...")

    # --- 6. 使用 SpectraProcessor 处理和绘制单个光谱 --- #
    print("\n--- 步骤 6: 使用 SpectraProcessor 处理和绘制单个光谱 --- ")
    if target_ids_loaded:
        # 选择第一个加载的目标进行演示
        target_to_plot = target_ids_loaded[0]
        print(f"选择目标ID {target_to_plot} 进行光谱绘制。")
        
        spec_data_single_target = all_spectra_data[target_to_plot]
        
        # SpectraProcessor 需要 flux, ivar, wavelength, mask 字典，每个键是一个波段
        flux_dict = {band: data['flux'] for band, data in spec_data_single_target.items() if 'flux' in data}
        ivar_dict = {band: data['ivar'] for band, data in spec_data_single_target.items() if 'ivar' in data}
        wave_dict = {band: data['wavelength'] for band, data in spec_data_single_target.items() if 'wavelength' in data}
        mask_dict = {band: data['mask'] for band, data in spec_data_single_target.items() if 'mask' in data and data['mask'] is not None}
        
        try:
            spec_proc = SpectraProcessor(
                flux=flux_dict,
                ivar=ivar_dict,
                wavelength=wave_dict,
                mask=mask_dict,
                target_id=target_to_plot
            )

            print(f"为目标 {target_to_plot} 绘制合并光谱:")
            fig, ax = plt.subplots(figsize=(15, 7))
            spec_proc.plot_spectrum(ax=ax, title=f"Combined Spectrum - Target {target_to_plot} (HEALPix {example_healpix_id})", show_ivar=True)
            plt.tight_layout()
            plt.show()
            
            # 绘制单个波段的光谱 (例如 R 波段)
            if 'R' in spec_proc.bands:
                print(f"为目标 {target_to_plot} 绘制 R 波段光谱:")
                fig_r, ax_r = plt.subplots(figsize=(10, 5))
                spec_proc.plot_spectrum(band='R', ax=ax_r, title=f"R-Band Spectrum - Target {target_to_plot}", show_ivar=True)
                plt.tight_layout()
                plt.show()
            
            # 计算SNR示例
            print("\n计算光谱信噪比 (SNR):")
            for band_calc in spec_proc.bands:
                snr = spec_proc.calculate_snr(band=band_calc)
                print(f"  SNR ({band_calc}): {snr:.2f}" if snr is not None else f"  SNR ({band_calc}): N/A")

        except ValueError as e:
            print(f"创建或使用SpectraProcessor时出错: {e}")
        except Exception as e:
            print(f"处理光谱时发生意外错误: {e}")
            import traceback
            traceback.print_exc()

    else:
        print("未加载任何目标的光谱数据，无法进行处理和绘制。")

    # --- 7. 获取HEALPix像素坐标 --- #
    print("\n--- 步骤 7: 获取HEALPix像素坐标 --- ")
    ra, dec = hp_processor.get_healpix_pixel_coords(example_healpix_id)
    print(f"HEALPix {example_healpix_id} (NSIDE={nside}, nested) 的中心坐标:")
    print(f"  RA: {ra[0]:.4f} deg")
    print(f"  Dec: {dec[0]:.4f} deg")

    # 多个HEALPix ID的坐标
    example_ids_multi = [example_healpix_id, example_healpix_id + 1, example_healpix_id + 2]
    ra_multi, dec_multi = hp_processor.get_healpix_pixel_coords(example_ids_multi)
    print(f"\n坐标 for HEALPix IDs {example_ids_multi}:")
    for i, hpid in enumerate(example_ids_multi):
        print(f"  ID {hpid}: RA={ra_multi[i]:.4f}, Dec={dec_multi[i]:.4f}")

    print("\n示例处理完成。")

if __name__ == '__main__':
    main()
