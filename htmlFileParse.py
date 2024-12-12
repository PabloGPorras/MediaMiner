import os
import pandas as pd
from bs4 import BeautifulSoup

def parse_html_to_dataframe(folder_path):
    # List to store all rules data
    all_rules = []

    # Loop through all HTML files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.html'):
            file_path = os.path.join(folder_path, file_name)
            
            # Open and parse the HTML file
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
                # Parse the data
                rules = soup.find_all('div', class_='ruleDetails')  # Replace with the actual tag/class for rules
                
                for rule in rules:
                    rule_data = {}
                    
                    # Extract relevant details from the HTML
                    rule_data['Rule ID'] = rule.find('tag', class_='ruleId').text if rule.find('tag', class_='ruleId') else None
                    rule_data['Decision Type'] = rule.find('tag', class_='decisionType').text if rule.find('tag', class_='decisionType') else None
                    rule_data['Decision'] = rule.find('tag', class_='decision').text if rule.find('tag', class_='decision') else None
                    rule_data['Reason Code'] = rule.find('tag', class_='reasonCode').text if rule.find('tag', class_='reasonCode') else None
                    rule_data['Rule Name'] = rule.find('tag', class_='ruleName').text if rule.find('tag', class_='ruleName') else None
                    rule_data['Strategy Name'] = rule.find('tag', class_='strategyName').text if rule.find('tag', class_='strategyName') else None
                    rule_data['Weight'] = rule.find('tag', class_='weight').text if rule.find('tag', class_='weight') else None
                    
                    # Append to the rules list
                    all_rules.append(rule_data)

    # Create DataFrame
    df = pd.DataFrame(all_rules)

    return df

# Define the folder containing the HTML files
folder_path = 'path_to_your_folder'

# Parse the HTML files into a DataFrame
df = parse_html_to_dataframe(folder_path)

# Save to Excel
df.to_excel('output_rules.xlsx', index=False)

# If you plan to upload to Snowflake, the DataFrame can be uploaded using the Snowflake Connector
print("Data parsing complete. Saved as 'output_rules.xlsx'.")
