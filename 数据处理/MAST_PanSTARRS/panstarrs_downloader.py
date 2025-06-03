import os
import pandas as pd
import requests
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from PIL import Image
import subprocess

# 用户配置
USE_DS9 = True  # 是否使用 DS9 进行图像处理
DS9_PATH = 'D:\Program Files\SAOImageDS9\ds9.exe'  # DS9 可执行文件路径
BANDS = ['g', 'r', 'i', 'z', 'y']  # 需要下载的波段
FITS_DIR = 'fits_files'
IMAGE_DIR = 'images'
DS9_IMAGE_DIR = 'ds9_images'
HEADER_DIR = 'fits_headers'

def get_fitscutout_links(ra, dec, size=240):
    url = (
        "https://ps1images.stsci.edu/cgi-bin/ps1cutouts"
        f"?pos={ra},{dec}" + ''.join(f"&filter={band}" for band in BANDS) +
        f"&filetypes=stack&auxiliary=data&size={size}&output_size=0&autoscale=99.5&verbose=0"
    )
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    fits_links = {}
    for a in soup.find_all("a", string="FITS-cutout"):
        href = a.get("href")
        if "red=" in href and "format=fits" in href:
            band = href.split(".stk.")[-1].split(".")[0]
            full_url = requests.compat.urljoin("https://ps1images.stsci.edu", href)
            fits_links[band] = full_url
    return fits_links

def download_fits_files(links, save_dir, prefix):
    os.makedirs(save_dir, exist_ok=True)
    local_paths = {}
    for band, url in links.items():
        filename = os.path.join(save_dir, f"{prefix}_{band}.fits")
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(r.content)
            local_paths[band] = filename
        except Exception as e:
            print(f"[X] Failed to download {band} ({prefix}): {e}")
    return local_paths

def extract_fits_header(fits_path, output_dir, prefix):
    os.makedirs(output_dir, exist_ok=True)
    try:
        with fits.open(fits_path) as hdul:
            header = hdul[0].header
            header_path = os.path.join(output_dir, f"{prefix}_{os.path.basename(fits_path).replace('.fits', '_header.txt')}")
            with open(header_path, 'w') as f:
                f.write(repr(header))
            print(f"[✓] Saved header: {header_path}")
    except Exception as e:
        print(f"[X] Failed to extract header from {fits_path}: {e}")

def visualize_fits(fits_path, output_dir, prefix):
    os.makedirs(output_dir, exist_ok=True)
    try:
        data = fits.getdata(fits_path)
        plt.figure(figsize=(5, 5))
        plt.imshow(data, cmap='gray', origin='lower', vmin=np.percentile(data, 1), vmax=np.percentile(data, 99))
        plt.title(os.path.basename(fits_path))
        plt.colorbar()
        out_path = os.path.join(output_dir, f"{prefix}_{os.path.basename(fits_path).replace('.fits', '.png')}")
        plt.savefig(out_path, bbox_inches='tight')
        plt.close()
        print(f"[✓] Saved image: {out_path}")
    except Exception as e:
        print(f"[X] Failed to visualize {fits_path}: {e}")

def autoscale(data, low=1, high=99):
    vmin = np.nanpercentile(data, low)
    vmax = np.nanpercentile(data, high)
    if vmax - vmin < 1e-6:
        return np.zeros_like(data)
    return np.clip((data - vmin) / (vmax - vmin), 0, 1)

def combine_rgb(fits_r, fits_g, fits_b, output_path):
    try:
        r = fits.getdata(fits_r).astype(np.float32)
        g = fits.getdata(fits_g).astype(np.float32)
        b = fits.getdata(fits_b).astype(np.float32)

        r_norm = autoscale(r)
        g_norm = autoscale(g)
        b_norm = autoscale(b)

        rgb = np.dstack([r_norm, g_norm, b_norm])
        rgb = (rgb * 255).astype(np.uint8)

        Image.fromarray(rgb).save(output_path)
        print(f"[✓] RGB image saved: {output_path}")
    except Exception as e:
        print(f"[X] Failed to generate RGB image: {e}")

def ds9_generate_images(fits_paths, output_dir, prefix):
    os.makedirs(output_dir, exist_ok=True)
    for band, path in fits_paths.items():
        output_image = os.path.join(output_dir, f"{prefix}_{band}_ds9.png")
        try:
            subprocess.run([
                DS9_PATH, path,
                '-scale', 'log',
                '-zoom', 'to', 'fit',
                '-saveimage', output_image,
                '-exit'
            ], check=True)
            print(f"[✓] DS9 image saved: {output_image}")
        except Exception as e:
            print(f"[X] DS9 failed for {band} band: {e}")

def ds9_combine_rgb(fits_r, fits_g, fits_b, output_path):
    try:
        subprocess.run([
            DS9_PATH,
            '-rgb',
            '-red', fits_r,
            '-green', fits_g,
            '-blue', fits_b,
            '-scale', 'log',
            '-zoom', 'to', 'fit',
            '-saveimage', output_path,
            '-exit'
        ], check=True)
        print(f"[✓] DS9 RGB image saved: {output_path}")
    except Exception as e:
        print(f"[X] DS9 failed to generate RGB image: {e}")

def process_catalog(catalog_csv):
    df = pd.read_csv(catalog_csv)
    for _, row in df.iterrows():
        object_id = str(row.get("id", f"{row.ra}_{row.dec}")).replace(" ", "_")
        ra = row["ra"]
        dec = row["dec"]
        print(f"\n[→] Processing {object_id} (RA={ra}, Dec={dec})")

        links = get_fitscutout_links(ra, dec)
        fits_paths = download_fits_files(links, save_dir=FITS_DIR, prefix=object_id)

        for band, path in fits_paths.items():
            extract_fits_header(path, output_dir=HEADER_DIR, prefix=object_id)
            visualize_fits(path, output_dir=IMAGE_DIR, prefix=object_id)

        if USE_DS9:
            ds9_generate_images(fits_paths, output_dir=DS9_IMAGE_DIR, prefix=object_id)

        if all(b in fits_paths for b in ['y', 'i', 'g']):
            rgb_path = os.path.join(IMAGE_DIR, f"{object_id}_RGB.png")
            combine_rgb(fits_r=fits_paths['y'], fits_g=fits_paths['i'], fits_b=fits_paths['g'], output_path=rgb_path)
            if USE_DS9:
                ds9_rgb_path = os.path.join(DS9_IMAGE_DIR, f"{object_id}_RGB_ds9.png")
                ds9_combine_rgb(fits_r=fits_paths['y'], fits_g=fits_paths['i'], fits_b=fits_paths['g'], output_path=ds9_rgb_path)

if __name__ == "__main__":
    process_catalog("targets.csv")