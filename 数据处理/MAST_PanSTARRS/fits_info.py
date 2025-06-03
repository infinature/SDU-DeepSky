from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs import FITSFixedWarning
import warnings

def inspect_fits_structure(fits_path):
    print(f"\n===== Inspecting: {fits_path} =====")
    with fits.open(fits_path) as hdul:
        print(f"Number of HDUs: {len(hdul)}")
        for i, hdu in enumerate(hdul):
            print(f"\n--- HDU {i} ---")
            print(f"Type: {type(hdu)}")
            print(f"Data shape: {hdu.data.shape if hdu.data is not None else 'None'}")
            print(f"Header summary:")
            print(repr(hdu.header).split('\n')[0:10])  # 只打印前10行 header

            # 尝试解析 WCS 信息
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', FITSFixedWarning)
                    wcs = WCS(hdu.header)
                    print(f"WCS axes: {wcs.wcs.naxis}")
                    print(f"WCS ctype: {wcs.wcs.ctype}")
            except Exception as e:
                print(f"[!] Could not parse WCS from HDU {i}: {e}")

    print("\n===== Inspection complete =====\n")

if __name__ == "__main__":
    inspect_fits_structure("fits_files/10.684708_41.26875_g.fits")