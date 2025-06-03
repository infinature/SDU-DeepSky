import numpy as np
from astropy.io import fits
from astropy.visualization import make_lupton_rgb
import matplotlib.pyplot as plt
from PIL import Image
import os

def create_rgb_from_fits(fits_g_path, fits_r_path, fits_z_path, output_png_path,
                           lupton_minimum=0.01, lupton_stretch=0.1, lupton_Q=1,
                           perform_bg_subtraction=False):
    """
    Creates an RGB PNG image from g, r, z FITS files using Lupton et al. (2004) algorithm.
    Default parameters are optimized based on user's findings.
    For DESI, the conventional color mapping is R=z, G=r, B=g.

    Args:
        fits_g_path (str): Path to the g-band FITS file.
        fits_r_path (str): Path to the r-band FITS file.
        fits_z_path (str): Path to the z-band FITS file.
        output_png_path (str): Path to save the output PNG image.
        lupton_minimum (float or list): The minimum intensity value for scaling. 
                                      If scalar, applied to all bands. If list, [min_z, min_r, min_g].
        lupton_stretch (float): The stretch factor for scaling.
        lupton_Q (float): The Q factor for the asinh stretch.
        perform_bg_subtraction (bool): If True, perform median background subtraction from each band.

    Returns:
        bool: True if image creation was successful, False otherwise.
    """
    try:
        print(f"Reading FITS files:")
        print(f"  g-band: {fits_g_path}")
        print(f"  r-band: {fits_r_path}")
        print(f"  z-band: {fits_z_path}")
        
        with fits.open(fits_g_path) as hdul_g, \
             fits.open(fits_r_path) as hdul_r, \
             fits.open(fits_z_path) as hdul_z:
            
            # 读取数据并确保是 2D 数组
            image_g = hdul_g[0].data.astype(np.float32)
            image_r = hdul_r[0].data.astype(np.float32)
            image_z = hdul_z[0].data.astype(np.float32)

            # 如果是 3D 数组，取第一个切片
            if len(image_g.shape) == 3:
                image_g = image_g[0]
            if len(image_r.shape) == 3:
                image_r = image_r[0]
            if len(image_z.shape) == 3:
                image_z = image_z[0]

        print(f"Image shapes after processing:")
        print(f"  g-band: {image_g.shape}")
        print(f"  r-band: {image_r.shape}")
        print(f"  z-band: {image_z.shape}")

        if perform_bg_subtraction:
            print("  Performing median background subtraction...")
            bg_g = np.median(image_g)
            bg_r = np.median(image_r)
            bg_z = np.median(image_z)
            
            image_g -= bg_g
            image_r -= bg_r
            image_z -= bg_z
            
            image_g[image_g < 0] = 0
            image_r[image_r < 0] = 0
            image_z[image_z < 0] = 0
            print(f"    Subtracted g-bg: {bg_g:.3f}, r-bg: {bg_r:.3f}, z-bg: {bg_z:.3f}")

        if not (image_g.shape == image_r.shape == image_z.shape):
            print("Warning: Input FITS images do not have the same dimensions. Attempting to resize to smallest common shape.")
            min_h = min(image_g.shape[0], image_r.shape[0], image_z.shape[0])
            min_w = min(image_g.shape[1], image_r.shape[1], image_z.shape[1])
            image_g = image_g[:min_h, :min_w]
            image_r = image_r[:min_h, :min_w]
            image_z = image_z[:min_h, :min_w]
            print(f"Resized images to common shape: ({min_h}, {min_w})")

        print(f"Final image shapes:")
        print(f"  g-band: {image_g.shape}")
        print(f"  r-band: {image_r.shape}")
        print(f"  z-band: {image_z.shape}")

        # Lupton RGB composition: R=z, G=r, B=g for DESI.
        # make_lupton_rgb expects images in order R, G, B.
        print(f"  Using make_lupton_rgb with minimum={lupton_minimum}, stretch={lupton_stretch}, Q={lupton_Q}")
        rgb_image = make_lupton_rgb(image_z, image_r, image_g,
                                    minimum=lupton_minimum,
                                    stretch=lupton_stretch,
                                    Q=lupton_Q)
        
        print(f"RGB image shape: {rgb_image.shape}")
        
        output_dir = os.path.dirname(output_png_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
            
        plt.imsave(output_png_path, rgb_image, origin='lower')
        print(f"RGB image saved to {output_png_path}")
        return True

    except Exception as e:
        print(f"Error creating RGB image from FITS {output_png_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def combine_rgb_jpegs(r_path, g_path, b_path, output_path):
    """
    Combines three single-band JPEG images (assumed to be grayscale)
    into a single RGB color image.

    Args:
        r_path (str): Path to the JPEG image for the Red channel.
        g_path (str): Path to the JPEG image for the Green channel.
        b_path (str): Path to the JPEG image for the Blue channel.
        output_path (str): Path to save the combined RGB PNG image.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # print(f"Loading Red channel: {r_path}")
        r_image = Image.open(r_path)
        # print(f"Loading Green channel: {g_path}")
        g_image = Image.open(g_path)
        # print(f"Loading Blue channel: {b_path}")
        b_image = Image.open(b_path)

        if r_image.mode != 'L':
            # print(f"Warning: Red channel image {r_path} is not in 'L' mode (mode: {r_image.mode}). Converting to 'L'.")
            r_image = r_image.convert('L')
        if g_image.mode != 'L':
            # print(f"Warning: Green channel image {g_path} is not in 'L' mode (mode: {g_image.mode}). Converting to 'L'.")
            g_image = g_image.convert('L')
        if b_image.mode != 'L':
            # print(f"Warning: Blue channel image {b_path} is not in 'L' mode (mode: {b_image.mode}). Converting to 'L'.")
            b_image = b_image.convert('L')

        if not (r_image.size == g_image.size == b_image.size):
            print("Error: Input JPEG images must have the same dimensions.")
            print(f"  R: {r_image.size}, G: {g_image.size}, B: {b_image.size}")
            return False

        # print(f"Merging images into RGB. Image size: {r_image.size}")
        rgb_image = Image.merge("RGB", (r_image, g_image, b_image))

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            # print(f"Created output directory: {output_dir}")

        # print(f"Saving combined RGB image to: {output_path}")
        rgb_image.save(output_path, "PNG")
        print(f"Combined JPEG image saved to {output_path}")
        return True

    except FileNotFoundError as e:
        print(f"Error: One or more input JPEG files not found. {e}")
        return False
    except Exception as e:
        print(f"An error occurred while combining JPEGs: {e}")
        return False
