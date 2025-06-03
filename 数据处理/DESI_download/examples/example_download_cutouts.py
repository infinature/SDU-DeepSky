import os
from desi_data_processor import DesiArchiveHandler

def main():
    # Initialize the handler
    # data_release for images (e.g., 'dr10', 'dr9')
    # catalog_data_release for catalog queries (e.g., 'dr1', 'edr')
    handler = DesiArchiveHandler(data_release='dr10', catalog_data_release='dr1')

    # Define coordinates and parameters for download
    ra_example = 150.0776
    dec_example = 2.2169
    size_pixels = 64 # Size of the cutout in pixels

    # Define output directory for cutouts
    # This path assumes the example is run from the 'examples' directory
    output_dir_base = '../test_downloads/' # Base directory for all test downloads
    fits_save_dir = os.path.join(output_dir_base, 'image_cutouts_fits_examples')
    jpeg_save_dir = os.path.join(output_dir_base, 'image_cutouts_jpeg_examples')
    
    os.makedirs(fits_save_dir, exist_ok=True)
    os.makedirs(jpeg_save_dir, exist_ok=True)

    print(f"--- Example: Downloading FITS cutouts for RA={ra_example}, Dec={dec_example} ---")
    
    # Download a 3-band (grz) FITS cutout
    fits_path_grz = handler.download_cutout(
        ra=ra_example, 
        dec=dec_example, 
        size=size_pixels, 
        bands='grz', 
        img_format='fits', 
        save_dir=fits_save_dir,
        filename=f"cutout_{ra_example}_{dec_example}_grz_{size_pixels}pix.fits"
    )
    if fits_path_grz:
        print(f"Multi-band FITS cutout saved to: {os.path.abspath(fits_path_grz)}")
    else:
        print("Multi-band FITS cutout download failed.")

    # Download single-band FITS cutouts (g, r, z separately)
    # These are needed for create_rgb_from_fits example
    # Using slightly different filenames to distinguish from the multi-band FITS
    coord_part_for_rgb = f"ra_{ra_example:.4f}_dec_{dec_example:.4f}_size_{size_pixels}" # Match example_create_rgb naming

    print("\n--- Downloading individual g, r, z FITS bands (for RGB creation example) ---")
    fits_g_path = handler.download_cutout(
        ra=ra_example, dec=dec_example, size=size_pixels, bands='g', img_format='fits', 
        save_dir=fits_save_dir, filename=f"{coord_part_for_rgb}_g.fits"
    )
    fits_r_path = handler.download_cutout(
        ra=ra_example, dec=dec_example, size=size_pixels, bands='r', img_format='fits', 
        save_dir=fits_save_dir, filename=f"{coord_part_for_rgb}_r.fits"
    )
    fits_z_path = handler.download_cutout(
        ra=ra_example, dec=dec_example, size=size_pixels, bands='z', img_format='fits', 
        save_dir=fits_save_dir, filename=f"{coord_part_for_rgb}_z.fits"
    )

    if all([fits_g_path, fits_r_path, fits_z_path]):
        print(f"Individual FITS bands saved to directory: {os.path.abspath(fits_save_dir)}")
        print(f"  g: {os.path.basename(fits_g_path)}")
        print(f"  r: {os.path.basename(fits_r_path)}")
        print(f"  z: {os.path.basename(fits_z_path)}")
    else:
        print("One or more individual FITS band downloads failed.")

    print(f"\n--- Example: Downloading JPEG cutout for RA={ra_example}, Dec={dec_example} ---")
    jpeg_path = handler.download_cutout(
        ra=ra_example, 
        dec=dec_example, 
        size=128, # JPEGs can be larger
        img_format='jpeg', 
        save_dir=jpeg_save_dir,
        # Default layer 'ls-dr10' will be used from handler
        filename=f"cutout_{ra_example}_{dec_example}_128pix.jpg"
    )
    if jpeg_path:
        print(f"JPEG cutout saved to: {os.path.abspath(jpeg_path)}")
    else:
        print("JPEG cutout download failed.")

    # Example for combine_jpegs: download r, g, z band JPEGs
    # Using filenames consistent with example_combine_jpegs.py
    print("\n--- Downloading individual r, g, z JPEG bands (for JPEG combination example) ---")
    layer_name = f"ls-{handler.data_release.lower().replace('ls-', '')}"
    jpeg_r_filename = f"cutout_ra{ra_example}_dec{dec_example}_{layer_name}_r.jpg"
    jpeg_g_filename = f"cutout_ra{ra_example}_dec{dec_example}_{layer_name}_g.jpg"
    jpeg_z_filename = f"cutout_ra{ra_example}_dec{dec_example}_{layer_name}_z.jpg" # z-band for blue channel

    jpeg_r_path = handler.download_cutout(ra=ra_example, dec=dec_example, size=128, layer=layer_name, bands='r', img_format='jpeg', save_dir=jpeg_save_dir, filename=jpeg_r_filename)
    jpeg_g_path = handler.download_cutout(ra=ra_example, dec=dec_example, size=128, layer=layer_name, bands='g', img_format='jpeg', save_dir=jpeg_save_dir, filename=jpeg_g_filename)
    jpeg_z_path = handler.download_cutout(ra=ra_example, dec=dec_example, size=128, layer=layer_name, bands='z', img_format='jpeg', save_dir=jpeg_save_dir, filename=jpeg_z_filename)

    if all([jpeg_r_path, jpeg_g_path, jpeg_z_path]):
        print(f"Individual JPEG bands saved to directory: {os.path.abspath(jpeg_save_dir)}")
        print(f"  r: {os.path.basename(jpeg_r_path)}")
        print(f"  g: {os.path.basename(jpeg_g_path)}")
        print(f"  z (for blue): {os.path.basename(jpeg_z_path)}")
    else:
        print("One or more individual JPEG band downloads failed.")

    print("\nExample cutout download script finished.")

if __name__ == '__main__':
    main()
