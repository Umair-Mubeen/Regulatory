import os
import glob
import json

try:
    result = []
    directory = "C:\\Users\\umair\\Downloads\\VCIN CAT APRIL\\VCIN CAT APRIL\\95049_VCIN_20240425_OrderEvents_000101.json"
    json_pattern = os.path.join(directory, '*.json')
    print(json_pattern)
    for f in glob.glob(json_pattern):
        with open(f, "rb") as infile:
            result.append(json.load(infile))

    with open("merged_file.json", "wb") as outfile:
        json.dump(result, outfile, indent=4)
except Exception as e:
    print("Error while merging files Json :" + str(e))

Error parsing C:\Users\umair\Downloads\VCIN CAT APRIL\VCIN CAT APRIL\95049_VCIN_20240425_OrderEvents_000101.json\95049_VCIN_20240404_OrderEvents_000103.json: Extra data: line 2 column 1 (char 627)
import os
import glob
import json

try:
    result = []
    directory = "C:\\Users\\umair\\Downloads\\VCIN CAT APRIL\\VCIN CAT APRIL"
    json_pattern = os.path.join(directory, '*.json')
    print(json_pattern)
    for f in glob.glob(json_pattern):
        try:
            with open(f, "r") as infile:
                result.append(json.load(infile))
        except json.JSONDecodeError as jde:
            print(f"Error parsing {f}: {jde}")
        except Exception as e:
            print(f"Unexpected error with file {f}: {e}")

    output_file = "merged_file.json"
    with open(output_file, "w") as outfile:
        json.dump(result, outfile, indent=4)

    print(f"Files merged successfully into {output_file}")
except Exception as e:
    print("Error while merging JSON files: " + str(e))
