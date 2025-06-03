"""
DESI数据处理工具库

这个库提供了一系列工具，用于处理DESI（Dark Energy Spectroscopic Instrument）的数据。
"""

from .catalog import DESIRedshiftCatalog
from .healpix import HEALPixProcessor
from .spectra import SpectraProcessor
from .desi_archive_handler import DesiArchiveHandler
from .imaging_utils import (
    create_rgb_from_fits,
    combine_rgb_jpegs,
    # get_default_lupton_params # This was commented out, keeping it as is
)
from .utils.download_utils import download_file
from .utils.bulk_downloader import DESIBulkDownloader

# Version of the desi_data_processor package
__version__ = "0.2.1" # Incremented version due to restored/combined exports

__all__ = [
    'DesiArchiveHandler',
    'DESIRedshiftCatalog',
    'HEALPixProcessor',
    'SpectraProcessor',
    'create_rgb_from_fits',
    'combine_rgb_jpegs',
    'download_file',
    'DESIBulkDownloader',
]
