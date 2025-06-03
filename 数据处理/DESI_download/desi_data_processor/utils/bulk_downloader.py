"""
DESI数据批量下载工具

该模块提供了通过CSV文件批量下载DESI数据的功能。
支持多种下载方式：
1. 直接HTTP下载 (requests/wget)
2. 命令行工具下载 (wget/curl)
3. AWS S3访问
"""

import os
import csv
import json
import pandas as pd
import logging
import requests
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse, urljoin

# 导入本地下载工具
from .download_utils import download_file

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('desi_bulk_downloader')

# DESI数据基础URL
DESI_BASE_URL = 'https://data.desi.lbl.gov/public'

class DESIBulkDownloader:
    """
    DESI数据批量下载器
    
    从CSV文件中读取下载信息，并批量下载DESI数据。
    """
    def __init__(self, data_release='dr1', output_dir=None, max_workers=5):
        """
        初始化下载器
        
        参数:
            data_release (str): 数据发布版本，如'dr1'、'edr'等
            output_dir (str): 输出目录，默认为当前目录下的'desi_data'
            max_workers (int): 最大并行下载线程数
        """
        self.data_release = data_release
        self.base_url = f'{DESI_BASE_URL}/{data_release}'
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'desi_data')
        self.max_workers = max_workers
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 检查wget是否可用
        self.wget_available = self._check_wget_available()
        
    def _check_wget_available(self):
        """
        检查wget是否可用
        
        返回:
            bool: 如果wget可用则返回True，否则返回False
        """
        try:
            subprocess.run(['wget', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (FileNotFoundError, subprocess.SubprocessError):
            logger.warning("wget不可用，将使用requests进行下载")
            return False
    
    def process_csv(self, csv_path):
        """
        处理CSV文件，获取下载列表
        
        CSV文件格式应包含以下列:
        - data_type: 数据类型，如'zcat', 'spectra', 'healpix'等
        - path: DESI数据路径，相对于基础URL
        - (可选) output_path: 本地保存路径，相对于output_dir
        - (可选) download_method: 下载方式，'http', 'wget', 'aws'之一
        
        参数:
            csv_path (str): CSV文件路径
            
        返回:
            list: 下载任务列表
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"找不到CSV文件: {csv_path}")
            
        try:
            df = pd.read_csv(csv_path)
            required_columns = ['data_type', 'path']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"CSV文件缺少必要的列: {col}")
            
            # 转换为下载任务列表
            download_tasks = []
            for _, row in df.iterrows():
                data_type = row['data_type']
                path = row['path']
                
                # 构造下载URL
                url = urljoin(self.base_url, path)
                
                # 确定输出路径
                output_path = row.get('output_path', path)
                full_output_path = os.path.join(self.output_dir, output_path)
                
                # 下载方法
                download_method = row.get('download_method', 'http')
                if download_method == 'wget' and not self.wget_available:
                    download_method = 'http'
                
                download_tasks.append({
                    'data_type': data_type,
                    'url': url,
                    'output_path': output_path,
                    'download_method': download_method
                })
            
            return download_tasks
        
        except Exception as e:
            logger.error(f"处理CSV文件时出错: {e}")
            raise
    
    def download_all(self, tasks, overwrite=False):
        """
        下载所有任务
        
        参数:
            tasks (list): 下载任务列表
            overwrite (bool): 是否覆盖已存在的文件
            
        返回:
            dict: 下载结果统计
        """
        results = {
            'total': len(tasks),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'failed_tasks': []
        }
        
        logger.info(f"开始下载 {len(tasks)} 个文件")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for task in tasks:
                futures.append(executor.submit(
                    self.download_single_task, task, overwrite
                ))
            
            # 使用tqdm显示进度
            for future in tqdm(futures, desc="下载进度", unit="文件"):
                success = future.result()
                if success is True:
                    results['success'] += 1
                elif success is False:
                    results['failed'] += 1
                else:  # 跳过
                    results['skipped'] += 1
        
        logger.info(f"下载完成: 成功 {results['success']}, "  
                   f"失败 {results['failed']}, 跳过 {results['skipped']}")
        return results
    
    def download_single_task(self, task, overwrite=False):
        """
        下载单个任务
        
        参数:
            task (dict): 下载任务
            overwrite (bool): 是否覆盖已存在的文件
            
        返回:
            bool/None: 成功返回True，失败返回False，跳过返回None
        """
        url = task['url']
        relative_output_path = task['output_path']
        full_output_path = os.path.join(self.output_dir, relative_output_path)
        download_method = task['download_method']
        
        # 如果文件已存在且不覆盖，则跳过
        if os.path.exists(full_output_path) and not overwrite:
            logger.info(f"文件已存在，跳过: {full_output_path}")
            return None
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        
        try:
            if download_method == 'wget' and self.wget_available:
                return self._download_with_wget(url, full_output_path)
            else:
                return download_file(url, full_output_path, overwrite=True)
        except Exception as e:
            logger.error(f"下载失败 {url} -> {full_output_path}: {e}")
            return False
    
    def _download_with_wget(self, url, output_path):
        """
        使用wget下载文件
        
        参数:
            url (str): 下载URL
            output_path (str): 输出路径
            
        返回:
            bool: 成功返回True，否则返回False
        """
        try:
            logger.info(f"使用wget下载: {url} -> {output_path}")
            cmd = ['wget', '-O', output_path, url, '--no-check-certificate']
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"wget下载失败 {url}: {e}")
            return False

    def create_csv_template(self, output_path="desi_download_template.csv"):
        """
        创建CSV模板文件
        
        参数:
            output_path (str): 模板文件输出路径
        """
        data = [
            {"data_type": "zcat", "path": "spectro/redux/iron/zcatalog/v1/zall-pix-iron.fits", "output_path": "zcat/zall-pix-iron.fits", "download_method": "http"},
            {"data_type": "spectra", "path": "spectro/redux/iron/healpix/spectra-64/149/14981.fits", "output_path": "spectra/14981.fits", "download_method": "http"},
            {"data_type": "tile", "path": "spectro/redux/iron/tiles/cumulative/80607/coadd-80607-thru20220326.fits", "output_path": "tiles/80607-coadd.fits", "download_method": "wget"}
        ]
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        logger.info(f"CSV模板已创建: {output_path}")
        print(f"CSV模板已创建: {output_path}，您可以编辑此文件并添加更多下载项")


if __name__ == '__main__':
    print("DESI批量下载工具")
    print("该模块提供了从CSV文件批量下载DESI数据的功能。")
    print("使用示例:")
    print("```python")
    print("from desi_data_processor.utils.bulk_downloader import DESIBulkDownloader")
    print("")
    print("# 创建下载器")
    print("downloader = DESIBulkDownloader(data_release='dr1', output_dir='./desi_data')")
    print("")
    print("# 创建CSV模板文件")
    print("downloader.create_csv_template('download_list.csv')")
    print("")
    print("# 编辑CSV文件后，处理下载任务")
    print("tasks = downloader.process_csv('download_list.csv')")
    print("results = downloader.download_all(tasks)")
    print("```")
