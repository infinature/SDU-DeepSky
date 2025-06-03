import os
from desi_data_processor.imaging_utils import combine_rgb_jpegs

def main():
    # Define base directories for input JPEG files and output PNG
    # Users should adjust these paths according to their setup.
    # These paths assume the example is run from the 'examples' directory
    # or that the 'test_downloads' directory is accessible relative to CWD.
    base_jpeg_dir = '../test_downloads/image_cutouts_jpeg/' # Adjust if your JPEGs are elsewhere
    output_image_dir = '../test_downloads/combined_jpeg_examples/' # Output directory
    os.makedirs(output_image_dir, exist_ok=True)

    # Example JPEG file paths (these would typically be outputs from DesiArchiveHandler.download_cutout)
    # Replace with actual paths to your r, g, b band JPEG files.
    # The original script used specific names. For DESI, typically R=z, G=r, B=g.
    # However, the combine_jpegs script used r_file, g_file, b_file (where b_file was actually z-band FITS converted to JPEG).
    # For this example, let's assume you have JPEGs for r, g, and b (e.g., z-band for blue).
    
    # Example: Using r, g, z band JPEGs (where z is used for blue channel)
    # These filenames are illustrative. Adjust to your actual downloaded JPEG filenames.
    ra_dec_layer_part = "ra150.0_dec2.0_ls-dr10" # Example from original script
    r_file_name = f"cutout_{ra_dec_layer_part}_r.jpg"
    g_file_name = f"cutout_{ra_dec_layer_part}_g.jpg"
    # For the blue channel, we'll use the z-band JPEG, following common astronomical practice for RGB images.
    b_file_name = f"cutout_{ra_dec_layer_part}_z.jpg" 

    r_file_path = os.path.join(base_jpeg_dir, r_file_name)
    g_file_path = os.path.join(base_jpeg_dir, g_file_name)
    b_file_path = os.path.join(base_jpeg_dir, b_file_name)

    output_filename = f"rgb_combined_{ra_dec_layer_part}.png"
    output_file_path = os.path.join(output_image_dir, output_filename)

    # Check if files exist
    missing_files = False
    for f_path, band in zip([r_file_path, g_file_path, b_file_path], ['Red (r-band)', 'Green (g-band)', 'Blue (z-band)']):
        if not os.path.exists(f_path):
            print(f"Error: {band} channel JPEG image not found at {os.path.abspath(f_path)}")
            missing_files = True
    
    if missing_files:
        print(f"Please ensure JPEG files for r, g, and z bands are available at these locations, ")
        print(f"or modify the paths in this script. These might be outputs from 'example_download_cutouts.py'.")
        return

    print(f"Input JPEG files from: {os.path.abspath(base_jpeg_dir)}")
    print(f"Output PNG will be saved to: {os.path.abspath(output_image_dir)}\n")

    print(f"--- Combining JPEGs for {ra_dec_layer_part} ---")
    print(f"  R channel: {r_file_path}")
    print(f"  G channel: {g_file_path}")
    print(f"  B channel (using z-band): {b_file_path}")
    print(f"  Output: {output_file_path}")

    success = combine_rgb_jpegs(r_path=r_file_path, 
                                g_path=g_file_path, 
                                b_path=b_file_path, 
                                output_path=output_file_path)

    if success:
        print(f"Successfully combined JPEG images into: {output_file_path}")
    else:
        print(f"Failed to combine JPEG images.")

    print("\nExample script finished.")

if __name__ == '__main__':
    # This allows running the script directly.
    # For the imports to work correctly if desi_data_processor is not installed,
    # ensure the DESI_download directory (parent of desi_data_processor and examples)
    # is in your PYTHONPATH, or run from DESI_download as: python -m examples.example_combine_jpegs
    main()
