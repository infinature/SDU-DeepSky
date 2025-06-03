import os
import requests
import pandas as pd

# Import queryClient from astro-datalab
# Ensure astro-datalab is installed (e.g., pip install astro-datalab)
try:
    from dl import queryClient as qc
except ImportError:
    qc = None
    print("Warning: astro-datalab library not found. Catalog query functionality will be unavailable.")
    print("Please install it: pip install astro-datalab")

# Assuming utils.py is in the same package
from .utils.download_utils import download_file # Adjusted import path

class DesiArchiveHandler:
    """
    Handles querying the DESI Legacy Survey catalog and downloading data products.
    """
    def __init__(self, data_release='dr10', catalog_data_release='dr1'):
        """
        Initializes the handler with base URLs and default settings.

        Args:
            data_release (str): The data release for image cutouts (e.g., 'dr10', 'dr9').
                                Refers to Legacy Survey data releases.
            catalog_data_release (str): The data release for catalog queries (e.g., 'dr1', 'edr').
                                        Used to determine the schema (e.g., 'desi_dr1').
        """
        self.legacy_survey_base_url = "https://www.legacysurvey.org/viewer"
        self.data_release = data_release
        # Schema for catalog queries, e.g., 'desi_dr1' for DR1 at NOIRLab
        self.catalog_schema = f"desi_{catalog_data_release.lower()}" 

    def download_cutout(self, ra, dec, size, pixscale=0.262, bands=None, img_format='fits', save_dir='.', filename=None):
        """
        Download a cutout from the DESI Legacy Survey.
        
        Parameters:
        -----------
        ra : float
            Right ascension in degrees
        dec : float
            Declination in degrees
        size : int
            Size of the cutout in pixels
        pixscale : float, optional
            Pixel scale in arcseconds per pixel (default: 0.262)
        bands : list, optional
            List of bands to download (default: ['g', 'r', 'z'])
        img_format : str, optional
            Image format ('fits' or 'jpeg', default: 'fits')
        save_dir : str, optional
            Directory to save the files (default: '.')
        filename : str, optional
            Base filename for the output (default: None, will use coordinates)
            
        Returns:
        --------
        bool
            True if download was successful, False otherwise
        """
        if bands is None:
            bands = ['g', 'r', 'z']
            
        if filename is None:
            filename = f"{ra}_{dec}"
            
        # Ensure filename has correct extension
        if not filename.endswith('.fits') and not filename.endswith('.jpg'):
            file_ext = '.fits' if img_format == 'fits' else '.jpg'
            filename = f"{filename}{file_ext}"
            
        # Check if file already exists
        if os.path.exists(os.path.join(save_dir, filename)):
            print(f"文件已存在: {os.path.join(save_dir, filename)}。跳过下载。")
            return True
            
        # Construct the URL based on format
        if img_format == 'fits':
            url = (
                "https://www.legacysurvey.org/viewer/fits-cutout"
                f"?ra={ra}&dec={dec}&layer=ls-dr10"
                f"&pixscale={pixscale}&bands={bands}&size={size}"
            )
        else:  # jpeg
            url = (
                "https://www.legacysurvey.org/viewer/jpeg-cutout"
                f"?ra={ra}&dec={dec}&layer=ls-dr10"
                f"&pixscale={pixscale}&size={size}"
            )
            
        print(f"Downloading {img_format} cutout from: {url}")
        
        try:
            # Download the file
            print(f"开始下载: {url} -> {os.path.join(save_dir, filename)}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(os.path.join(save_dir, filename), 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            print(f"下载成功: {os.path.join(save_dir, filename)}")
            print(f"Successfully downloaded to {os.path.join(save_dir, filename)}")
            return True
            
        except Exception as e:
            print(f"Error downloading cutout: {str(e)}")
            return False

    def query_catalog(self, adql_query):
        """
        Launches an ADQL query against the DESI catalog via NOIRLab's Data Lab services.
        The user is responsible for ensuring the ADQL query uses the correct schema 
        (e.g., 'desi_dr1.tablename', 'desi_edr.tablename'), which can be inferred from
        the 'catalog_data_release' parameter passed to __init__ (self.catalog_schema).

        Args:
            adql_query (str): The ADQL query string. 
                              Example: f"SELECT TOP 10 targetid, ra, dec FROM {self.catalog_schema}.zpix WHERE ra > 150"

        Returns:
            pandas.DataFrame: A DataFrame containing the query results, or None if query failed or astro-datalab is not available.
        """
        if qc is None:
            print("Error: astro-datalab library is not available. Cannot execute query.")
            return None
        
        print(f"Executing ADQL query using Data Lab queryClient:")
        print(adql_query)

        try:
            results_table = qc.query(sql=adql_query, fmt='table')
            if results_table is not None:
                # Convert Astropy Table to Pandas DataFrame
                return results_table.to_pandas()
            else:
                # qc.query might return None if the query itself is problematic before execution
                # or if it's an empty result but still valid. 
                # An empty Astropy table converted to pandas is an empty DataFrame.
                print("Query executed but returned no data or an unexpected None result.")
                return pd.DataFrame() 
        except Exception as e:
            print(f"ADQL query failed: {e}")
            return None

if __name__ == '__main__':
    handler = DesiArchiveHandler(data_release='dr10', catalog_data_release='dr1')

    # Test cutout download
    ra_test, dec_test = 150.0776, 2.2169 # Example coordinates
    print(f"\n--- Testing Cutout Download (RA={ra_test}, DEC={dec_test}) ---")
    cutout_path_fits = handler.download_cutout(ra_test, dec_test, size=64, bands='grz', img_format='fits', save_dir='./desi_cutouts')
    # cutout_path_jpeg = handler.download_cutout(ra_test, dec_test, size=128, img_format='jpeg', save_dir='./desi_cutouts')
    
    if cutout_path_fits:
        print(f"FITS cutout saved to: {cutout_path_fits}")
    # if cutout_path_jpeg:
    #     print(f"JPEG cutout saved to: {cutout_path_jpeg}")

    # Test catalog query
    print(f"\n--- Testing Catalog Query (Schema: {handler.catalog_schema}) ---")
    if qc is not None: # Only attempt query if astro-datalab is available
        # Example query using the handler's catalog_schema property
        # This query selects a few columns from the 'zpix' table for a small region of the sky.
        # Note: Users should construct their queries carefully. The schema (e.g., desi_dr1) must be part of the table name.
        example_query = f"SELECT TOP 5 targetid, ra, dec, z, spectype " \
                        f"FROM {handler.catalog_schema}.zpix " \
                        f"WHERE ra > 150.0 AND ra < 150.1 AND dec > 2.2 AND dec < 2.3 AND zcat_primary = true"
        
        results_df = handler.query_catalog(example_query)
        
        if results_df is not None:
            if not results_df.empty:
                print("\nCatalog query results:")
                print(results_df)
            else:
                print("\nCatalog query returned no results (empty table).")
        else:
            print("\nCatalog query failed or astro-datalab is not available.")
    else:
        print("\nSkipping catalog query test as astro-datalab library is not available.")
    
    print("\nExample usage complete.")
