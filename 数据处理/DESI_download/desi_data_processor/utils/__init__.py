"""
DESI数据处理工具库的辅助函数模块。
"""

from . import fits_utils
from . import data_stats
from . import download_utils
from .download_utils import download_file
from .fits_utils import (get_fits_header, get_table_from_fits, list_hdus)
from .bulk_downloader import DESIBulkDownloader

try:
    from .aws_downloader import DESIS3Downloader
    aws_downloader_available = True
except ImportError:
    aws_downloader_available = False

__all__ = [
    'download_file',
    'get_fits_header',
    'get_table_from_fits',
    'list_hdus',
    'DESIBulkDownloader'
]

if aws_downloader_available:
    __all__.append('DESIS3Downloader')
