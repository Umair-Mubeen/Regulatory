 new_df.to_csv('MENO_Creation.csv', index=False)
import os
import pandas as pd

# Sample DataFrame
data = {
    'Column1': [1, 2, 3],
    'Column2': ['A', 'B', 'C']
}
new_df = pd.DataFrame(data)

# Define the directory path
directory = '/path/to/your/directory'

# Ensure the directory exists
os.makedirs(directory, exist_ok=True)

# Define the file path
file_path = os.path.join(directory, 'MENO_Creation.csv')

# Save the DataFrame to CSV
new_df.to_csv(file_path, index=False)

print(f"File saved to {file_path}")
