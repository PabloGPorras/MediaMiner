import os
import re
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# Configuration
folder_path = "./your_folder"  # Change this to your actual path
snowflake_config = {
    "user": "your_user",
    "password": "your_password",
    "account": "your_account",
    "warehouse": "your_warehouse",
    "database": "your_database",
    "schema": "your_schema"
}
target_table = "your_table"

# Regex pattern to find the lul_name
lul_pattern = re.compile(r'%let\s+ll_name\d{2}\s*=\s*(\w+)\s*;', re.IGNORECASE)

# List to hold extracted data
data = []

# Loop through files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".sas") or filename.endswith(".txt"):  # adjust as needed
        full_path = os.path.join(folder_path, filename)
        with open(full_path, "r", encoding="utf-8") as file:
            code = file.read()
            match = lul_pattern.search(code)
            lul_name = match.group(1) if match else None
            data.append({
                "script_name": filename,
                "code": code,
                "lul_name": lul_name
            })

# Create a DataFrame
df = pd.DataFrame(data)

# Connect to Snowflake and upload
conn = snowflake.connector.connect(**snowflake_config)
success, nchunks, nrows, _ = write_pandas(conn, df, target_table)

print(f"Uploaded {nrows} rows to {target_table} in Snowflake.")
