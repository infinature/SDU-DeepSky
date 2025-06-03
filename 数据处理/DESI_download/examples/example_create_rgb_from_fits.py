import os
from desi_data_processor.imaging_utils import create_rgb_from_fits

def main():
    # Define base directories for input FITS files and output PNGs
    # Users should adjust these paths according to their setup.
    # These paths assume the example is run from the 'examples' directory
    # or that the 'test_downloads' directory is accessible relative to CWD.
    base_fits_dir = '../test_downloads/image_cutouts_fits/' # Adjust if your FITS are elsewhere
    output_base_dir = '../test_downloads/rgb_from_fits_examples/' # Output directory
    os.makedirs(output_base_dir, exist_ok=True)

    # Example FITS file paths (these would typically be outputs from DesiArchiveHandler.download_cutout)
    # Replace with actual paths to your g, r, z band FITS files.
    # The original script used hardcoded names based on a specific download.
    # For a general example, we'll assume some naming convention or specific files.
    # For this example to run, ensure these FITS files exist.
    coord_part = "ra_180.0000_dec_20.0000_size_256" # Example from original script
    fits_g_path = os.path.join(base_fits_dir, f"{coord_part}_g.fits")
    fits_r_path = os.path.join(base_fits_dir, f"{coord_part}_r.fits")
    fits_z_path = os.path.join(base_fits_dir, f"{coord_part}_z.fits")

    if not (os.path.exists(fits_g_path) and os.path.exists(fits_r_path) and os.path.exists(fits_z_path)):
        print(f"Error: One or more FITS files not found at expected paths:")
        print(f"  g: {os.path.abspath(fits_g_path)}")
        print(f"  r: {os.path.abspath(fits_r_path)}")
        print(f"  z: {os.path.abspath(fits_z_path)}")
        print(f"Please ensure FITS files for g, r, and z bands are available at these locations, ")
        print(f"or modify the paths in this script. These might be outputs from 'example_download_cutouts.py'.")
        return

    print(f"Input FITS files from: {os.path.abspath(base_fits_dir)}")
    print(f"Output PNGs will be saved to: {os.path.abspath(output_base_dir)}\n")

    # Using the optimal Lupton parameters (R=z, G=r, B=g)
    # minimum=0.01, stretch=0.1, Q=1, no background subtraction
    output_filename = f"rgb_lupton_optimal_{coord_part}.png"
    output_path = os.path.join(output_base_dir, output_filename)

    print(f"\n--- Processing with optimal parameters (m=0.01, s=0.1, q=1, bg_sub=False) ---")
    print(f"Attempting to save to: {output_path}")
    
    success = create_rgb_from_fits(
        fits_g_path=fits_g_path,
        fits_r_path=fits_r_path,
        fits_z_path=fits_z_path,
        output_png_path=output_path,
        lupton_minimum=0.01, 
        lupton_stretch=0.1, 
        lupton_Q=1,
        perform_bg_subtraction=False
    )

    if success:
        print(f"Successfully created RGB image: {output_path}")
    else:
        print(f"Failed to create RGB image: {output_path}")

    # Example with background subtraction (optional)
    # output_filename_bg = f"rgb_lupton_optimal_bg_sub_{coord_part}.png"
    # output_path_bg = os.path.join(output_base_dir, output_filename_bg)
    # print(f"\n--- Processing with optimal parameters AND background subtraction ---")
    # success_bg = create_rgb_from_fits(
    #     fits_g_path=fits_g_path,
    #     fits_r_path=fits_r_path,
    #     fits_z_path=fits_z_path,
    #     output_png_path=output_path_bg,
    #     lupton_minimum=0.0, # Often, after bg sub, minimum is set near 0
    #     lupton_stretch=0.5, # Stretch might need adjustment after bg sub
    #     lupton_Q=5,         # Q might also need adjustment
    #     perform_bg_subtraction=True
    # )
    # if success_bg:
    #     print(f"Successfully created RGB image with BG subtraction: {output_path_bg}")
    # else:
    #     print(f"Failed to create RGB image with BG subtraction: {output_path_bg}")

    print("\nExample script finished.")

if __name__ == '__main__':
    # This allows running the script directly.
    # For the imports to work correctly if desi_data_processor is not installed,
    # ensure the DESI_download directory (parent of desi_data_processor and examples)
    # is in your PYTHONPATH, or run from DESI_download as: python -m examples.example_create_rgb_from_fits
    main()
