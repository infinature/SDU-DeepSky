"""
DESI数据从AWS S3下载工具

该模块提供从AWS S3下载DESI数据的功能。
由于DESI数据也在AWS Open Data计划中提供，这提供了一种替代的下载方式。
"""

import os
import logging
import time
from pathlib import Path
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('desi_aws_downloader')

# AWS S3 DESI数据桶
DESI_S3_BUCKET = 'desidata'
# AWS S3 区域
DESI_S3_REGION = 'us-west-2'


class DESIS3Downloader:
    """
    从AWS S3下载DESI数据的工具
    
    使用boto3库从AWS S3下载DESI数据文件。
    """
    def __init__(self, data_release='dr1', output_dir=None):
        """
        初始化AWS S3下载器
        
        参数:
            data_release (str): 数据发布版本，如'dr1'、'edr'等
            output_dir (str): 输出目录，默认为当前目录下的'desi_data'
        """
        self.data_release = data_release
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'desi_data')
        self.s3_client = None
        self.s3_resource = None
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 尝试导入boto3
        try:
            import boto3
            self.s3_client = boto3.client('s3', region_name=DESI_S3_REGION)
            self.s3_resource = boto3.resource('s3', region_name=DESI_S3_REGION)
            logger.info("已成功初始化AWS S3客户端")
        except ImportError:
            logger.warning("无法导入boto3库，请安装：pip install boto3")
        except Exception as e:
            logger.error(f"初始化AWS S3客户端时出错: {e}")
    
    def is_available(self):
        """
        检查AWS S3下载功能是否可用
        
        返回:
            bool: 如果可用则返回True，否则返回False
        """
        return self.s3_client is not None and self.s3_resource is not None
    
    def download_file(self, s3_path, local_path, overwrite=False):
        """
        从S3下载单个文件
        
        参数:
            s3_path (str): S3对象路径，相对于数据发布目录
            local_path (str): 本地保存路径
            overwrite (bool): 是否覆盖已存在的文件
            
        返回:
            bool: 成功返回True，否则返回False
        """
        if not self.is_available():
            logger.error("AWS S3客户端不可用")
            return False
            
        if os.path.exists(local_path) and not overwrite:
            logger.info(f"文件已存在，跳过: {local_path}")
            return True
            
        # 确保输出目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 构建S3对象路径
        full_s3_path = f"{self.data_release}/{s3_path}"
        
        try:
            logger.info(f"开始从S3下载: {full_s3_path} -> {local_path}")
            
            # 获取文件大小用于进度条
            try:
                s3_object = self.s3_resource.Object(DESI_S3_BUCKET, full_s3_path)
                file_size = s3_object.content_length
            except:
                file_size = 0
                
            # 使用回调函数显示下载进度
            progress = tqdm(total=file_size, unit='B', unit_scale=True, desc=os.path.basename(local_path))
            
            def progress_callback(bytes_transferred):
                progress.update(bytes_transferred)
            
            # 下载文件
            self.s3_client.download_file(
                DESI_S3_BUCKET,
                full_s3_path,
                local_path,
                Callback=progress_callback
            )
            
            progress.close()
            logger.info(f"S3下载成功: {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"从S3下载失败 {full_s3_path}: {e}")
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    logger.info(f"已删除不完整的文件: {local_path}")
                except:
                    pass
            return False
    
    def list_objects(self, prefix):
        """
        列出S3桶中的对象
        
        参数:
            prefix (str): 对象前缀，用于筛选
            
        返回:
            list: 对象列表
        """
        if not self.is_available():
            logger.error("AWS S3客户端不可用")
            return []
        
        try:
            full_prefix = f"{self.data_release}/{prefix}"
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=DESI_S3_BUCKET, Prefix=full_prefix)
            
            objects = []
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # 去除数据发布版本前缀，便于后续处理
                        key = obj['Key']
                        if key.startswith(f"{self.data_release}/"):
                            key = key[len(f"{self.data_release}/"):]
                        objects.append({
                            'key': key,
                            'size': obj['Size'],
                            'last_modified': obj['LastModified']
                        })
            
            return objects
        except Exception as e:
            logger.error(f"列出S3对象时出错 {prefix}: {e}")
            return []


if __name__ == '__main__':
    print("DESI AWS S3下载工具")
    print("该模块提供从AWS S3下载DESI数据的功能。")
    print("使用示例:")
    print("```python")
    print("from desi_data_processor.utils.aws_downloader import DESIS3Downloader")
    print("")
    print("# 创建S3下载器")
    print("s3_downloader = DESIS3Downloader(data_release='dr1')")
    print("")
    print("# 检查是否可用")
    print("if s3_downloader.is_available():")
    print("    # 列出特定前缀的对象")
    print("    objects = s3_downloader.list_objects('spectro/redux/iron/zcatalog/')")
    print("    print(f'找到 {len(objects)} 个对象')")
    print("    ")
    print("    # 下载文件")
    print("    s3_downloader.download_file('spectro/redux/iron/zcatalog/v1/zall-pix-iron.fits', './zcat.fits')")
    print("else:")
    print("    print('AWS S3客户端不可用，请安装boto3: pip install boto3')")
    print("```")
