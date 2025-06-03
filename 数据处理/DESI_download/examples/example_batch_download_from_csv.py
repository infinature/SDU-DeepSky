import os
import csv
from desi_data_processor import DesiArchiveHandler

def main():
    # Path to the CSV file containing cutout parameters
    # Assumes the script is run from the 'examples' directory
    csv_file_path = os.path.join('data', 'cutout_batch_template.csv')

    # Base directory for all batch downloads
    base_output_dir = '../batch_cutout_downloads/'
    os.makedirs(base_output_dir, exist_ok=True)

    # Initialize DesiArchiveHandler
    # Adjust data_release and catalog_data_release as needed
    handler = DesiArchiveHandler(data_release='dr10', catalog_data_release='dr1')

    print(f"Starting batch download of cutouts from: {csv_file_path}")

    try:
        with open(csv_file_path, mode='r', newline='') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames or not all(field in reader.fieldnames for field in ['ra', 'dec', 'size_pixels', 'bands', 'img_format', 'output_subdir', 'filename_prefix']):
                print(f"Error: CSV file {csv_file_path} is missing required columns.")
                print("Required columns: ra, dec, size_pixels, bands, img_format, output_subdir, filename_prefix")
                return

            for row_num, row in enumerate(reader, start=1):
                try:
                    ra = float(row['ra'])
                    dec = float(row['dec'])
                    size_pixels = int(row['size_pixels'])
                    bands = row['bands']
                    img_format = row['img_format'].lower()
                    output_subdir = row['output_subdir']
                    filename_prefix = row['filename_prefix']

                    print(f"\nProcessing row {row_num}: RA={ra}, Dec={dec}, Size={size_pixels}px, Bands='{bands}', Format='{img_format}'")

                    # Construct full save directory
                    current_save_dir = os.path.join(base_output_dir, output_subdir)
                    os.makedirs(current_save_dir, exist_ok=True)

                    # Construct filename
                    # Example: obj1_grz_150.0776_2.2169_64px.fits
                    # You might want to customize this further based on your needs
                    filename = f"{filename_prefix}_{ra}_{dec}_{bands}_{size_pixels}pix.{img_format}"
                    if img_format == 'jpeg': # jpeg is often .jpg
                        filename = f"{filename_prefix}_{ra}_{dec}_{bands}_{size_pixels}pix.jpg"
                    

                    downloaded_path = handler.download_cutout(
                        ra=ra,
                        dec=dec,
                        size=size_pixels,
                        bands=bands,
                        img_format=img_format,
                        save_dir=current_save_dir,
                        filename=filename
                        # layer can be specified if not using default from handler's data_release
                    )

                    if downloaded_path:
                        print(f"Successfully downloaded: {os.path.abspath(downloaded_path)}")
                    else:
                        print(f"Failed to download cutout for row {row_num}.")

                except ValueError as ve:
                    print(f"Skipping row {row_num} due to invalid data: {ve}. Row content: {row}")
                except KeyError as ke:
                    print(f"Skipping row {row_num} due to missing column: {ke}. Row content: {row}")
                except Exception as e:
                    print(f"An unexpected error occurred processing row {row_num}: {e}. Row content: {row}")

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
    except Exception as e:
        print(f"An error occurred while reading or processing the CSV file: {e}")

    print("\nBatch cutout download script finished.")

if __name__ == '__main__':
    main()
