import os
import re
import pandas as pd
import snowflake.connector

# Config
folder_path = "./your_folder"  # 👈 Update this
snowflake_config = {
    "user": "your_user",
    "password": "your_password",
    "account": "your_account",
    "warehouse": "your_warehouse",
    "database": "your_database",
    "schema": "your_schema"
}
target_table = "your_table"  # 👈 Update this

# Regex pattern for lul_name
lul_pattern = re.compile(r'%let\s+ll_name\d{2}\s*=\s*(\w+)\s*;', re.IGNORECASE)

# Collect script info
rows = []
for filename in os.listdir(folder_path):
    if filename.endswith(".sas") or filename.endswith(".txt"):
        full_path = os.path.join(folder_path, filename)
        with open(full_path, "r", encoding="utf-8") as file:
            code = file.read()
            match = lul_pattern.search(code)
            lul_name = match.group(1) if match else None
            rows.append((filename, code, lul_name))

# Connect to Snowflake
conn = snowflake.connector.connect(**snowflake_config)
cs = conn.cursor()

# Optional: create table if not exists
cs.execute(f"""
    CREATE TABLE IF NOT EXISTS {target_table} (
        script_name STRING,
        code STRING,
        lul_name STRING
    )
""")

# Insert data
insert_sql = f"INSERT INTO {target_table} (script_name, code, lul_name) VALUES (%s, %s, %s)"
cs.executemany(insert_sql, rows)

# Confirm upload
print(f"Uploaded {len(rows)} rows to {target_table} in Snowflake.")

# Cleanup
cs.close()
conn.close()
