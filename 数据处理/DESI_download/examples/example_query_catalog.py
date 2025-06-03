import os
from desi_data_processor import DesiArchiveHandler

# IMPORTANT: astro-datalab Authentication
# To execute catalog queries, you need to be authenticated with astro-datalab.
# The recommended way is to create a configuration file at ~/.datalab/login.config
# with your credentials. For example:
#
# mkdir -p ~/.datalab
# nano ~/.datalab/login.config
#
# Then add the following content to login.config, replacing with your details:
# [dlauth]
# user = YOUR_USERNAME  (e.g., mengjunyu)
# password = YOUR_PASSWORD
#

def main():
    # Initialize DesiArchiveHandler
    # Ensure you have valid credentials for astro-datalab as described above.
    # The 'catalog_data_release' parameter is important here.
    handler = DesiArchiveHandler(catalog_data_release='dr1') # Example: using DR1 for catalog

    print("--- Example: Querying DESI Catalog ---")

    # Example ADQL Query:
    # Select a few columns for a small number of objects from a specific catalog table.
    # This query targets the 'desi_edr.vac_gfa_targets_edr' table as an example.
    # You'll need to replace 'desi_edr.vac_gfa_targets_edr' with the actual table 
    # you intend to query based on the available DESI catalog schema for your data release.
    # This is a placeholder query and might need adjustment for your specific DESI setup and data access.
    
    # A more common example might be querying for objects in a certain RA/Dec region.
    # For instance, from the Legacy Survey DR10 object catalog (ls_dr10.tractor)
    # This example assumes 'ls_dr10.tractor' is a valid table for the handler's datalab service.
    # The handler's catalog_data_release might influence which tables are easily accessible.
    # For this example, let's try a query that should generally work with a common public table.
    # We'll use a generic query against a common table like 'ls_dr9.tractor' if 'catalog_data_release' was 'dr9' for Data Lab.
    # Since we initialized with catalog_data_release='dr1' (which is for DESI EDR/DR1 specific tables),
    # let's try a query that might be relevant to DESI EDR.
    # A common DESI EDR table for redshifts might be 'desi_edr.zcatalog_qso_edr'.
    # Limiting to top 5 results for brevity.

    # Adjust this query based on the actual tables available in your DESI Data Lab service for 'dr1'
    adql_query = """
    SELECT TOP 5 targetid, ra, dec, z, survey
    FROM desi_edr.zcatalog_main_edr 
    WHERE survey = 'sv1' AND program = 'dark'
    """
    # If the above table doesn't work, a simpler one from legacysurvey might be more robust for a generic example:
    # adql_query = "SELECT TOP 5 ra, dec, flux_g, flux_r, flux_z FROM ls_dr9.tractor WHERE ra > 150 AND ra < 150.1 AND dec > 2 AND dec < 2.1"
    # The handler is initialized with catalog_data_release='dr1', so we should aim for a DR1 related query.

    print(f"Executing ADQL Query:\n{adql_query}")

    try:
        results = handler.query_catalog(adql_query)

        if results is not None:
            if hasattr(results, 'to_pandas'): # Check if it's an Astropy Table
                results_df = results.to_pandas()
                print("\nQuery Results (as Pandas DataFrame):")
                print(results_df)
                print(f"\nRetrieved {len(results_df)} records.")
            elif hasattr(results, 'read'): # Check if it's a raw response that can be read (e.g. IOBase)
                try:
                    # Attempt to parse as CSV or plain text if it's a file-like object
                    import pandas as pd
                    from io import StringIO
                    data_str = results.read()
                    if isinstance(data_str, bytes):
                        data_str = data_str.decode('utf-8')
                    results_df = pd.read_csv(StringIO(data_str))
                    print("\nQuery Results (parsed from raw response as CSV):")
                    print(results_df)
                    print(f"\nRetrieved {len(results_df)} records.")
                except Exception as parse_err:
                    print(f"\nQuery returned data, but failed to parse into a DataFrame: {parse_err}")
                    print("Raw results might be in a different format or an error message.")
                    if 'data_str' in locals() and data_str:
                        print("First 500 chars of raw response:")
                        print(data_str[:500]) 
            else:
                # If it's already a DataFrame (less likely from datalab direct) or other format
                print("\nQuery Results:")
                print(results)
                if hasattr(results, '__len__'):
                    print(f"\nRetrieved {len(results)} records.")
        else:
            print("\nQuery executed, but returned no results (None).")

    except AttributeError as ae:
        if 'query_catalog' in str(ae):
            print("\nError: The 'query_catalog' method may not be fully implemented or 'astro-datalab' is not correctly configured/installed.")
            print("Please ensure 'astro-datalab' is installed and you can authenticate with the Data Lab services.")
        else:
            print(f"\nAn AttributeError occurred: {ae}")
    except Exception as e:
        print(f"\nAn error occurred during the catalog query: {e}")
        print("This could be due to an invalid ADQL query, network issues, problems with the Data Lab service, or authentication failure.")
        print("Please ensure your internet connection is active and that you have correctly configured your astro-datalab credentials in ~/.datalab/login.config")

    print("\nCatalog query example finished.")

if __name__ == '__main__':
    main()
