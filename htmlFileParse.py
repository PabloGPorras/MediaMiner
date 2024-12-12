import os
import pandas as pd
from bs4 import BeautifulSoup

def parse_html_to_dataframe(folder_path):
    # List to store all extracted rule data
    all_rules = []

    # Loop through each HTML file in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.html'):
            file_path = os.path.join(folder_path, file_name)

            # Parse the HTML file
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'lxml')

                # Find all rules by their structure
                rules = soup.find_all('a', attrs={'name': True})

                for rule in rules:
                    rule_data = {}

                    # Rule ID
                    rule_data['Rule Name'] = rule.text.strip() if rule.text else None

                    # Find related details
                    blockquote = rule.find_next('blockquote')

                    if blockquote:
                        details = blockquote.find_next('dl')
                        if details:
                            detail_tags = details.find_all('dt')
                            value_tags = details.find_all('dd')

                            for dt, dd in zip(detail_tags, value_tags):
                                key = dt.text.strip() if dt else None
                                value = dd.text.strip() if dd else None
                                if key and value:
                                    rule_data[key] = value

                    # Add rule to the list
                    all_rules.append(rule_data)

    # Convert list of rules to DataFrame
    df = pd.DataFrame(all_rules)

    return df

# Define the folder path containing the HTML files
folder_path = 'path_to_your_folder'

# Parse the files and create a DataFrame
df = parse_html_to_dataframe(folder_path)

# Save the DataFrame to an Excel file
df.to_excel('output_rules.xlsx', index=False)

print("Data parsing complete. Saved as 'output_rules.xlsx'.")
