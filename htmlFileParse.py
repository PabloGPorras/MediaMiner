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

                # Find all rules by their anchor tags
                rules = soup.find_all('a', attrs={'name': True})

                for rule in rules:
                    rule_data = {}

                    # Rule Name (e.g., rule1, rule2)
                    rule_data['Rule Name'] = rule.text.strip() if rule.text else None

                    # Find associated blockquote and parse details
                    blockquote = rule.find_next('blockquote')
                    if blockquote:
                        # Extract text from <PRE> tags for rule logic
                        pre = blockquote.find('pre')
                        if pre:
                            rule_data['Rule Logic'] = pre.text.strip()

                        # Extract additional details from <dl> if available
                        details = blockquote.find_next('dl')
                        if details:
                            for dt, dd in zip(details.find_all('dt'), details.find_all('dd')):
                                key = dt.text.strip() if dt else None
                                value = dd.text.strip() if dd else None
                                if key and value:
                                    rule_data[key] = value

                    # Append to all_rules
                    all_rules.append(rule_data)

    # Convert list of rules to a DataFrame
    df = pd.DataFrame(all_rules)

    return df

# Define the folder path containing the HTML files
folder_path = 'path_to_your_folder'

# Parse the files and create a DataFrame
df = parse_html_to_dataframe(folder_path)

# Save the DataFrame to an Excel file
df.to_excel('output_rules.xlsx', index=False)

print("Data parsing complete. Saved as 'output_rules.xlsx'.")
