from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import pprint # For pretty printing sys.path
import json
from pathlib import Path
import threading
from datetime import datetime
import pandas as pd
import requests
from urllib.parse import urljoin
import numpy as np
from astropy.io import fits
from PIL import Image
import subprocess
# 使用绝对路径导入panstarrs_downloader.py中的函数
# 这样避免了需要将MAST_PanSTARRS当作Python包导入的问题
import os

# 构建panstarrs_downloader.py的绝对路径
panstarrs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'MAST_PanSTARRS')
panstarrs_downloader_path = os.path.join(panstarrs_path, 'panstarrs_downloader.py')

print(f"Attempting to load functions directly from: {panstarrs_downloader_path}")
print(f"File exists: {os.path.exists(panstarrs_downloader_path)}")

# 使用importlib.util直接从文件路径导入模块
import importlib.util
spec = importlib.util.spec_from_file_location("panstarrs_downloader", panstarrs_downloader_path)
panstarrs_downloader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panstarrs_downloader)

# 从模块中导入需要的函数
get_fitscutout_links = panstarrs_downloader.get_fitscutout_links
download_fits_files = panstarrs_downloader.download_fits_files
extract_fits_header = panstarrs_downloader.extract_fits_header
visualize_fits = panstarrs_downloader.visualize_fits
combine_rgb = panstarrs_downloader.combine_rgb
ds9_generate_images = panstarrs_downloader.ds9_generate_images
ds9_combine_rgb = panstarrs_downloader.ds9_combine_rgb
from bs4 import BeautifulSoup
import uuid
from threading import Thread

# --- Begin Path Modification for Debugging ---
print("Initial sys.path (within app.py):")
pprint.pprint(sys.path)

# Determine the '数据处理' directory
# Current file: .../数据处理/astro_data_portal/backend/app.py
# Target: .../数据处理
data_processing_base_dir = Path(__file__).resolve().parent.parent.parent
print(f"Calculated 'data_processing_base_dir': {data_processing_base_dir}")

# Add 'data_processing_base_dir' to sys.path to find packages like MAST_PanSTARRS
if str(data_processing_base_dir) not in sys.path:
    sys.path.insert(0, str(data_processing_base_dir))
    print(f"Inserted {data_processing_base_dir} into sys.path.")
else:
    print(f"{data_processing_base_dir} was already in sys.path.")

print("sys.path after modification:")
pprint.pprint(sys.path)

# Verify existence of the MAST_PanSTARRS package and its __init__.py
mast_package_path = data_processing_base_dir / 'MAST_PanSTARRS'
mast_init_file_path = mast_package_path / '__init__.py'

print(f"Checking for MAST_PanSTARRS directory: {mast_package_path}")
print(f"Exists? {mast_package_path.exists()}")
print(f"Is directory? {mast_package_path.is_dir()}")

print(f"Checking for __init__.py in MAST_PanSTARRS: {mast_init_file_path}")
print(f"Exists? {mast_init_file_path.exists()}")
print(f"Is file? {mast_init_file_path.is_file()}")
# --- End Path Modification for Debugging ---

# 确保所有需要的路径都添加到sys.path中
base_dir = Path(__file__).parent.parent.parent

# 添加MAST_PanSTARRS目录
sys.path.append(str(base_dir / 'MAST_PanSTARRS'))
print(f"Added {base_dir / 'MAST_PanSTARRS'} to sys.path")

# 添加DESI_download目录
sys.path.append(str(base_dir / 'DESI_download'))
print(f"Added {base_dir / 'DESI_download'} to sys.path")

# 重要：添加desi_data_processor目录
sys.path.append(str(base_dir / 'DESI_download' / 'desi_data_processor'))
print(f"Added {base_dir / 'DESI_download' / 'desi_data_processor'} to sys.path")

# 输出修改后的sys.path
print("\nsys.path after all modifications:")
pprint.pprint(sys.path)

# 现在尝试导入需要的模块
try:
    from desi_data_processor.desi_archive_handler import DesiArchiveHandler
    from desi_data_processor.imaging_utils import create_rgb_from_fits, combine_rgb_jpegs
    print("\nSuccessfully imported DESI modules!")
except ImportError as e:
    print(f"\nError importing DESI modules: {e}")
    # 如果还是无法导入，尝试直接导入文件
    print("Trying direct file import...")
    try:
        import sys
        import importlib.util
        
        # 直接导入desi_archive_handler.py
        handler_path = str(base_dir / 'DESI_download' / 'desi_data_processor' / 'desi_archive_handler.py')
        spec = importlib.util.spec_from_file_location("desi_archive_handler", handler_path)
        desi_archive_handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(desi_archive_handler)
        DesiArchiveHandler = desi_archive_handler.DesiArchiveHandler
        
        # 直接导入imaging_utils.py
        utils_path = str(base_dir / 'DESI_download' / 'desi_data_processor' / 'imaging_utils.py')
        spec = importlib.util.spec_from_file_location("imaging_utils", utils_path)
        imaging_utils = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(imaging_utils)
        create_rgb_from_fits = imaging_utils.create_rgb_from_fits
        combine_rgb_jpegs = imaging_utils.combine_rgb_jpegs
        
        print("Direct file import successful!")
    except Exception as e:
        print(f"Error with direct file import: {e}")
        # 如果直接导入也失败，创建空的代理类
        print("Creating placeholder classes for DESI modules")
        class DesiArchiveHandler:
            def __init__(self, *args, **kwargs):
                print("WARNING: Using placeholder DesiArchiveHandler class!")
                
        def create_rgb_from_fits(*args, **kwargs):
            print("WARNING: Using placeholder create_rgb_from_fits function!")
            return None
            
        def combine_rgb_jpegs(*args, **kwargs):
            print("WARNING: Using placeholder combine_rgb_jpegs function!")
            return None

# Import J-PLUS download scripts
# 添加J-PLUS目录到sys.path
jplus_dir = base_dir / 'J-PLUS'
sys.path.append(str(jplus_dir))
print(f"Added {jplus_dir} to sys.path")

# 尝试导入J-PLUS模块
try:
    from download_jplus_fits import download_jplus_fits
    from download_jplus_weight import download_jplus_weight
    from download_jplus_cutout import download_jplus_cutout
    from download_jplus_psf import download_jplus_psf
    from download_jplus_psf_by_position import download_jplus_psf_by_position
    from download_jplus_graphic_image import download_jplus_graphic_image
    print("Successfully imported J-PLUS modules!")
except ImportError as e:
    print(f"Error importing J-PLUS modules: {e}")
    # 如果无法导入，创建占位符函数
    print("Creating placeholder functions for J-PLUS modules")
    def download_jplus_fits(*args, **kwargs):
        print("WARNING: Using placeholder download_jplus_fits function!")
        return None
        
    def download_jplus_weight(*args, **kwargs):
        print("WARNING: Using placeholder download_jplus_weight function!")
        return None
        
    def download_jplus_cutout(*args, **kwargs):
        print("WARNING: Using placeholder download_jplus_cutout function!")
        return None
        
    def download_jplus_psf(*args, **kwargs):
        print("WARNING: Using placeholder download_jplus_psf function!")
        return None
        
    def download_jplus_psf_by_position(*args, **kwargs):
        print("WARNING: Using placeholder download_jplus_psf_by_position function!")
        return None
        
    def download_jplus_graphic_image(*args, **kwargs):
        print("WARNING: Using placeholder download_jplus_graphic_image function!")
        return None
        
# 尝试导入download_jplus_graphic_cutout模块
try:
    from download_jplus_graphic_cutout import download_jplus_graphic_cutout
    print("Successfully imported download_jplus_graphic_cutout!")
except ImportError as e:
    print(f"Error importing download_jplus_graphic_cutout: {e}")
    # 创建占位符函数
    def download_jplus_graphic_cutout(*args, **kwargs):
        print("WARNING: Using placeholder download_jplus_graphic_cutout function!")
        return None

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store task status
tasks = {}

# J-PLUS API endpoints
JPLUS_BASE_URL = 'https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/'
JPLUS_ENDPOINTS = {
    'fits': 'get_fits',
    'weight': 'get_weight',
    'cutout': 'get_fits_cutout',
    'psf': 'get_psf_file',
    'psf_position': 'get_psf_by_position',
    'graphic': 'get_graphic_image',
    'graphic_cutout': 'get_graphic_cutout'
}

# Pan-STARRS configuration
PS1_BASE_URL = 'https://ps1images.stsci.edu/cgi-bin/ps1cutouts'
PS1_BANDS = ['g', 'r', 'i', 'z', 'y']

def run_desi_download(task_id, data):
    try:
        # Initialize the handler
        handler = DesiArchiveHandler(data_release='dr10', catalog_data_release='dr1')
        
        # Create save directory if it doesn't exist
        save_dir = os.path.join(UPLOAD_FOLDER, data['saveDir'])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Validate size limits
        if data['format'] == 'fits' and data['size'] > 512:
            raise ValueError("FITS format maximum size is 512 pixels")
        elif data['format'] == 'jpeg' and data['size'] > 3000:
            raise ValueError("JPEG format maximum size is 3000 pixels")

        # Get targets from data
        targets = data.get('targets', [])
        if not targets:
            raise ValueError("No targets provided")

        total_targets = len(targets)
        total_steps = total_targets * len(data['bands'])  # 每个目标的所有波段
        current_step = 0
        
        # Process each target
        for index, target in enumerate(targets):
            try:
                # Download the cutouts for each band
                for band in data['bands']:
                    current_step += 1
                    progress = int((current_step / total_steps) * 100)
                    
                    # Update task status
                    tasks[task_id].update({
                        'progress': progress,
                        'status': f'Downloading {band} band for target {index + 1}/{total_targets}...'
                    })
                    
                    # Set file extension based on format
                    file_ext = '.fits' if data['format'] == 'fits' else '.jpg'
                    filename = f"{target['targetId']}_{band}{file_ext}"
                    
                    # Download the cutout
                    result = handler.download_cutout(
                        ra=target['ra'],
                        dec=target['dec'],
                        size=data['size'],
                        pixscale=data.get('pixscale', 0.262),  # Default to 0.262 arcsec/pixel
                        bands=[band],
                        img_format=data['format'],
                        save_dir=save_dir,
                        filename=filename
                    )
                    
                    if not result:
                        raise Exception(f"Failed to download {band} band for target {target['targetId']}")

                # If FITS format and RGB creation is requested
                if data['format'] == 'fits' and data.get('createRGB', False):
                    tasks[task_id].update({
                        'status': f'Creating RGB image for target {index + 1}/{total_targets}...'
                    })
                    fits_files = {
                        'g': os.path.join(save_dir, f"{target['targetId']}_g.fits"),
                        'r': os.path.join(save_dir, f"{target['targetId']}_r.fits"),
                        'z': os.path.join(save_dir, f"{target['targetId']}_z.fits")
                    }
                    
                    # Check if all required FITS files exist
                    if all(os.path.exists(f) for f in fits_files.values()):
                        create_rgb_from_fits(
                            fits_g_path=fits_files['g'],
                            fits_r_path=fits_files['r'],
                            fits_z_path=fits_files['z'],
                            output_png_path=os.path.join(save_dir, f"{target['targetId']}_rgb.png"),
                            lupton_minimum=data.get('luptonMinimum', 0.01),
                            lupton_stretch=data.get('luptonStretch', 0.1),
                            lupton_Q=data.get('luptonQ', 1.0),
                            perform_bg_subtraction=data.get('performBgSubtraction', False)
                        )
                    else:
                        raise Exception(f"Missing required FITS files for RGB creation for target {target['targetId']}")

                # If JPEG format and RGB creation is requested
                elif data['format'] == 'jpeg' and data.get('createRGB', False):
                    tasks[task_id].update({
                        'status': f'Creating RGB image for target {index + 1}/{total_targets}...'
                    })
                    jpeg_files = {
                        'g': os.path.join(save_dir, f"{target['targetId']}_g.jpg"),
                        'r': os.path.join(save_dir, f"{target['targetId']}_r.jpg"),
                        'z': os.path.join(save_dir, f"{target['targetId']}_z.jpg")
                    }
                    
                    # Check if all required JPEG files exist
                    if all(os.path.exists(f) for f in jpeg_files.values()):
                        combine_rgb_jpegs(
                            jpeg_files['z'],  # Red channel
                            jpeg_files['r'],  # Green channel
                            jpeg_files['g'],  # Blue channel
                            os.path.join(save_dir, f"{target['targetId']}_rgb.png")
                        )
                    else:
                        raise Exception(f"Missing required JPEG files for RGB creation for target {target['targetId']}")

            except Exception as e:
                print(f"Error processing target {target['targetId']}: {str(e)}")
                continue

        tasks[task_id].update({
            'status': 'completed',
            'progress': 100
        })
    except Exception as e:
        tasks[task_id].update({
            'status': 'failed',
            'error': str(e)
        })

def run_jplus_download(task_id, data):
    try:
        # Initialize task status
        tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'start_time': datetime.now().isoformat(),
            'error': None
        }

        # Get targets and parameters from data
        targets = data.get('targets', [])
        data_type = data.get('dataType')
        save_dir = os.path.join(UPLOAD_FOLDER, data.get('saveDir', 'jplus_downloads'))
        width = data.get('width', 0.1)
        height = data.get('height', 0.1)

        if not targets:
            raise ValueError("No targets provided")

        if not data_type:
            raise ValueError("Data type is required")

        # Create save directory
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        total_targets = len(targets)
        current_step = 0

        # Process each target
        for index, target in enumerate(targets):
            try:
                current_step += 1
                progress = int((current_step / total_targets) * 100)
                
                # Update task status
                tasks[task_id].update({
                    'progress': progress,
                    'status': f'Processing target {index + 1}/{total_targets}...'
                })

                # Create session for requests
                session = requests.Session()
                try:
                    # Download based on data type
                    if data_type == 'fits':
                        download_jplus_fits(session, target['tileId'], target['filterId'], save_dir)
                    elif data_type == 'weight':
                        download_jplus_weight(session, target['tileId'], target['filterId'], save_dir)
                    elif data_type == 'cutout':
                        if not target.get('ra') or not target.get('dec'):
                            raise ValueError('RA and DEC are required for cutout')
                        download_jplus_cutout(
                            session,
                            target['tileId'],
                            target['ra'],
                            target['dec'],
                            target['filterId'],
                            save_dir,
                            width,
                            height
                        )
                    elif data_type == 'psf':
                        download_jplus_psf(session, target['tileId'], save_dir)
                    elif data_type == 'psf_position':
                        if not target.get('ra') or not target.get('dec'):
                            raise ValueError('RA and DEC are required for PSF position')
                        download_jplus_psf_by_position(
                            session,
                            target['tileId'],
                            target['ra'],
                            target['dec'],
                            target['filterId'],
                            save_dir
                        )
                    elif data_type == 'graphic':
                        download_jplus_graphic_image(session, target['tileId'], save_dir)
                    elif data_type == 'graphic_cutout':
                        if not target.get('ra') or not target.get('dec'):
                            raise ValueError('RA and DEC are required for graphic cutout')
                        download_jplus_graphic_cutout(
                            session,
                            target['ra'],
                            target['dec'],
                            target['filterId'],
                            save_dir,
                            'RGB',
                            width,
                            height,
                            128,
                            128
                        )
                    else:
                        raise ValueError(f'Unknown data type: {data_type}')

                finally:
                    session.close()

            except Exception as e:
                print(f'Error processing target {target}: {str(e)}')
                continue

        tasks[task_id].update({
            'status': 'completed',
            'progress': 100
        })

    except Exception as e:
        tasks[task_id].update({
            'status': 'failed',
            'error': str(e)
        })

def get_ps1_fits_url(ra, dec, band, size):
    """获取 Pan-STARRS FITS 图像的下载 URL。"""
    url = (
        "https://ps1images.stsci.edu/cgi-bin/ps1cutouts"
        f"?pos={ra},{dec}"
        f"&filter={band}"
        f"&filetypes=stack&auxiliary=data"
        f"&size={size}&output_size=0"
        f"&autoscale=99.5&verbose=0"
    )
    return url

def download_ps1_fits(url, save_path):
    """Download a FITS file from Pan-STARRS."""
    try:
        print(f"[INFO] Downloading FITS file from: {url}")
        response = requests.get(url, timeout=(10, 60))
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"[INFO] Successfully saved FITS file to: {save_path}")
            return True
        else:
            print(f"[ERROR] Failed to download FITS file. Status code: {response.status_code}")
            print(f"[ERROR] Response content: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error downloading FITS file: {str(e)}")
        return False

def combine_rgb(fits_r, fits_g, fits_b, output_path, ds9_path=None):
    """使用 Matplotlib 或 DS9 合成 RGB 图像。"""
    try:
        # 读取 FITS 数据
        r_data = fits.getdata(fits_r)
        g_data = fits.getdata(fits_g)
        b_data = fits.getdata(fits_b)

        # 数据归一化
        def autoscale(data, low=1, high=99):
            vmin = np.nanpercentile(data, low)
            vmax = np.nanpercentile(data, high)
            if vmax - vmin < 1e-6:
                return np.zeros_like(data)
            return np.clip((data - vmin) / (vmax - vmin), 0, 1)

        r_norm = autoscale(r_data)
        g_norm = autoscale(g_data)
        b_norm = autoscale(b_data)

        # 合成 RGB
        rgb = np.dstack([r_norm, g_norm, b_norm])
        rgb = (rgb * 255).astype(np.uint8)

        # 保存图像
        Image.fromarray(rgb).save(output_path)
        print(f"[✓] RGB image saved: {output_path}")

        # 如果提供了 DS9 路径，也使用 DS9 生成图像
        if ds9_path:
            ds9_output = output_path.replace('.png', '_ds9.png')
            subprocess.run([
                ds9_path,
                '-rgb',
                '-red', fits_r,
                '-green', fits_g,
                '-blue', fits_b,
                '-scale', 'log',
                '-zoom', 'to', 'fit',
                '-saveimage', ds9_output,
                '-exit'
            ], check=True)
            print(f"[✓] DS9 RGB image saved: {ds9_output}")

    except Exception as e:
        print(f"[X] Failed to generate RGB image: {e}")
        raise

def run_panstarrs_download(task_id, data):
    try:
        # Initialize task status
        tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'start_time': datetime.now().isoformat(),
            'error': None
        }

        targets = data.get('targets', [])
        bands = data.get('bands', [])
        size = data.get('size', 128)
        visualization = data.get('visualization', 'matplotlib')
        save_dir = os.path.join(UPLOAD_FOLDER, data.get('saveDir', 'panstarrs_downloads'))
        ds9_path = data.get('ds9Path')

        if not targets:
            raise ValueError("No targets provided")

        if not bands:
            raise ValueError("No bands provided")

        # Create save directories
        save_dir = os.path.abspath(save_dir)
        fits_dir = os.path.join(save_dir, 'fits_files')
        image_dir = os.path.join(save_dir, 'images')
        ds9_dir = os.path.join(save_dir, 'ds9_images')
        header_dir = os.path.join(save_dir, 'fits_headers')

        for d in [fits_dir, image_dir, ds9_dir, header_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

        total_targets = len(targets)
        current_step = 0

        # Process each target
        for index, target in enumerate(targets):
            try:
                current_step += 1
                progress = int((current_step / total_targets) * 100)
                
                # Update task status
                tasks[task_id].update({
                    'progress': progress,
                    'status': f'Processing target {index + 1}/{total_targets}...'
                })

                # Get FITS download links for selected bands
                links = {}
                for band in bands:
                    url = (
                        "https://ps1images.stsci.edu/cgi-bin/ps1cutouts"
                        f"?pos={target['ra']},{target['dec']}"
                        f"&filter={band}"
                        f"&filetypes=stack&auxiliary=data"
                        f"&size={size}&output_size=0"
                        f"&autoscale=99.5&verbose=0"
                    )
                    resp = requests.get(url)
                    soup = BeautifulSoup(resp.text, "html.parser")
                    
                    for a in soup.find_all("a", string="FITS-cutout"):
                        href = a.get("href")
                        if "red=" in href and "format=fits" in href:
                            band_name = href.split(".stk.")[-1].split(".")[0]
                            if band_name == band:
                                full_url = requests.compat.urljoin("https://ps1images.stsci.edu", href)
                                links[band] = full_url
                                break

                if not links:
                    raise Exception(f"No FITS links found for target {target['id']}")

                # Download FITS files
                fits_files = download_fits_files(links, fits_dir, target['id'])
                if not fits_files:
                    raise Exception(f"Failed to download FITS files for target {target['id']}")

                # Extract headers and create visualizations
                for band, path in fits_files.items():
                    extract_fits_header(path, header_dir, target['id'])
                    if visualization == 'matplotlib':
                        visualize_fits(path, image_dir, target['id'])

                # Create RGB image if we have enough bands
                if all(b in fits_files for b in ['y', 'i', 'g']):
                    rgb_path = os.path.join(image_dir, f"{target['id']}_RGB.png")
                    combine_rgb(
                        fits_r=fits_files['y'],
                        fits_g=fits_files['i'],
                        fits_b=fits_files['g'],
                        output_path=rgb_path
                    )

                    # Use DS9 if requested
                    if visualization == 'ds9' and ds9_path:
                        # Generate individual band images with DS9
                        for band, path in fits_files.items():
                            ds9_output = os.path.join(ds9_dir, f"{target['id']}_{band}_ds9.png")
                            try:
                                subprocess.run([
                                    ds9_path,
                                    path,
                                    '-scale', 'log',
                                    '-zoom', 'to', 'fit',
                                    '-saveimage', ds9_output,
                                    '-exit'
                                ], check=True)
                            except Exception as e:
                                print(f"DS9 failed for {band} band: {e}")

                        # Generate RGB image with DS9
                        ds9_rgb_path = os.path.join(ds9_dir, f"{target['id']}_RGB_ds9.png")
                        try:
                            subprocess.run([
                                ds9_path,
                                '-rgb',
                                '-red', fits_files['y'],
                                '-green', fits_files['i'],
                                '-blue', fits_files['g'],
                                '-scale', 'log',
                                '-zoom', 'to', 'fit',
                                '-saveimage', ds9_rgb_path,
                                '-exit'
                            ], check=True)
                        except Exception as e:
                            print(f"DS9 failed to generate RGB image: {e}")

            except Exception as e:
                print(f"Error processing target {target['id']}: {str(e)}")
                continue

        tasks[task_id].update({
            'status': 'completed',
            'progress': 100
        })

    except Exception as e:
        tasks[task_id].update({
            'status': 'failed',
            'error': str(e)
        })

@app.route('/api/desi/download', methods=['POST'])
def desi_download():
    try:
        data = request.json
        task_id = str(uuid.uuid4())  # 使用 UUID 生成唯一任务 ID
        
        # Initialize task status
        tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'start_time': datetime.now().isoformat(),
            'error': None
        }
        
        # Start download in background thread
        thread = threading.Thread(target=run_desi_download, args=(task_id, data))
        thread.daemon = True  # 设置为守护线程
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'DESI download started',
            'task_id': task_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/jplus/download', methods=['POST'])
def jplus_download():
    try:
        data = request.get_json()
        task_id = str(uuid.uuid4())
        
        # Start download in background thread
        thread = threading.Thread(target=run_jplus_download, args=(task_id, data))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'J-PLUS download started',
            'task_id': task_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/panstarrs/download', methods=['POST'])
def panstarrs_download():
    try:
        data = request.json
        task_id = str(uuid.uuid4())
        
        # Start download in background thread
        thread = threading.Thread(target=run_panstarrs_download, args=(task_id, data))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Pan-STARRS download started',
            'task_id': task_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    if task_id in tasks:
        return jsonify(tasks[task_id])
    else:
        return jsonify({
            'status': 'not_found',
            'message': f'Task with ID {task_id} not found'
        }), 404

@app.route('/api/files', methods=['GET'])
def list_files():
    """列出上传目录中的所有文件和子目录"""
    try:
        # 获取查询参数中的子目录
        subdir = request.args.get('subdir', '')
        # 构建完整路径
        dir_path = os.path.join(UPLOAD_FOLDER, subdir)
        
        # 检查目录是否存在
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return jsonify({
                'status': 'error',
                'message': f'目录 {dir_path} 不存在'
            }), 404
        
        # 获取目录内容
        items = []
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            is_dir = os.path.isdir(item_path)
            # 计算文件大小（如果是文件）
            size = os.path.getsize(item_path) if not is_dir else 0
            # 获取修改时间
            mtime = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
            
            items.append({
                'name': item,
                'path': os.path.join(subdir, item) if subdir else item,
                'is_dir': is_dir,
                'size': size,
                'size_formatted': f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB",
                'modified': mtime
            })
        
        # 按名称排序
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        return jsonify({
            'status': 'success',
            'items': items,
            'current_dir': subdir
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/download/<path:file_path>', methods=['GET'])
def download_file(file_path):
    """提供文件下载"""
    try:
        # 构建完整的文件路径
        full_path = os.path.join(UPLOAD_FOLDER, file_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return jsonify({
                'status': 'error',
                'message': f'文件 {file_path} 不存在'
            }), 404
        
        # 获取文件的目录和文件名
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        
        # 返回文件供下载
        return send_file(full_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Run on port 5003 and accessible on the network
    app.run(debug=True, host='0.0.0.0', port=5003)
