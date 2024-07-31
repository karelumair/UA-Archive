import os
import pandas as pd
from constants import ColumnNames

# Define the directory containing the CSV files
directory = "./reports"

# Iterate over each file in the directory
for subdir, dirs, files in os.walk(directory):
    for filename in files:
        # if filename.endswith(".csv"):
        #     # Construct the full file path
        #     file_path = os.path.join(subdir, filename)

        #     # Read the CSV file into a DataFrame
        #     df = pd.read_csv(file_path)

        #     # Create a new dictionary for renaming columns
        #     # new_columns = {col: ColumnNames.get(f"ga:{col}") for col in df.columns}
        #     new_columns = {"Ecommerece Converstion Rate": "Ecommerce Converstion Rate"}

        #     # Rename the columns using the provided mapping
        #     df.rename(columns=new_columns, inplace=True)

        #     # Write the DataFrame back to a CSV file, overwriting the original file
        #     df.to_csv(file_path, index=False)

        #     print(f"Successfully saved file: {file_path}")

        if filename.startswith('yearMonth_'):
            # Construct the new filename by removing the prefix
            new_filename = filename.split("yearMonth_")[-1]
            
            # Construct full file paths
            old_file = os.path.join(subdir, filename)
            new_file = os.path.join(subdir, new_filename)
            
            # Rename the file
            os.rename(old_file, new_file)
            print(f'Renamed: {old_file} -> {new_file}')

print("Columns renamed successfully for all CSV files in the directory.")
