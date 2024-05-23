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
