import os
import glob
import json

# Set the directory containing JSON files
directory = "C:\\Users\\umair\\Documents\\JsonFiles"  # Ensure this directory exists and has the correct permissions
json_pattern = os.path.join(directory, '*.json')
print(f"Looking for JSON files in: {json_pattern}")

# List to hold the content of all JSON files
result = []

# Loop through each JSON file in the directory
for f in glob.glob(json_pattern):
    try:
        print(f"Processing file: {f}")
        with open(f, "r") as infile:
            result.append(json.load(infile))
    except json.JSONDecodeError as jde:
        print(f"Error parsing {f}: {jde}")
    except PermissionError as pe:
        print(f"Permission denied for file {f}: {pe}")
    except Exception as e:
        print(f"Unexpected error with file {f}: {e}")

# Define the output file path
output_file = os.path.join(directory, "merged_file.json")

# Write the merged content to the output file
try:
    with open(output_file, "w") as outfile:
        json.dump(result, outfile, indent=4)
    print(f"Files merged successfully into {output_file}")
except PermissionError as pe:
    print(f"Permission denied for output file {output_file}: {pe}")
except Exception as e:
    print(f"Unexpected error while writing the output file {output_file}: {e}")
