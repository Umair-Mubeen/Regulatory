# import os
# import glob
# import json
#
# result = []
# directory = "C:\\Users\\umair\\Downloads\\VCIN CAT APRIL\\VCIN CAT APRIL\\95049_VCIN_20240425_OrderEvents_000101.json\\"
# json_pattern = os.path.join(directory, '*.json')
#
# for i, f in enumerate(glob.glob(json_pattern)):
#     try:
#         with open(f, "r") as infile:
#             data = json.load(infile)
#             print("Index {}".format(i))
#             data["index"] = i
#             result.append(data)
#     except json.JSONDecodeError as e:
#         print(f"Error parsing {f}: {e}")
#         pass
# with open("merged_file.json", "w") as outfile:
#     json.dump(result, outfile, indent=4)
#
#
# import os
# import glob
# import json
#
# try:
#     result = []
#     directory = "C:\\Users\\umair\\Documents\\JsonFiles"
#     json_pattern = os.path.join(directory, '*.json')
#     print(json_pattern)
#     for f in glob.glob(json_pattern):
#         try:
#             with open(f, "r") as infile:
#                 result.append(json.load(infile))
#         except json.JSONDecodeError as jde:
#             print(f"Error parsing {f}: {jde}")
#         except Exception as e:
#             print(f"Unexpected error with file {f}: {e}")
#
#     output_file = "merged_file.json"
#     with open(output_file, "w") as outfile:
#         json.dump(result, outfile, indent=4)
#
#     print(f"Files merged successfully into {output_file}")
# except Exception as e:
#     print("Error while merging JSON files: " + str(e))

import os
import glob
import json

try:
    result = []
    directory = "C:\\Users\\umair\\Documents\\JsonFiles"  # Change to a directory with known permissions
    json_pattern = os.path.join(directory, '*.json')

    for f in glob.glob(json_pattern):
        try:
            print(f)
            with open(f, "r") as infile:
                for line in infile:
                    result.append(json.loads(line))
                # result.append(json.load(infile))
        except json.JSONDecodeError as jde:
            print(f"Error parsing {f}: {jde}")
        except PermissionError as pe:
            print(f"Permission denied for file {f}: {pe}")
        except Exception as e:
            print(f"Unexpected error with file {f}: {e}")

    output_file = os.path.join(directory, "merged_file.json")

    try:
        with open(output_file, "w") as outfile:
            json.dump(result, outfile, indent=4)
        print(f"Files merged successfully into {output_file}")
    except PermissionError as pe:
        print(f"Permission denied for output file {output_file}: {pe}")
    except Exception as e:
        print(f"Unexpected error while writing the output file {output_file}: {e}")

except Exception as e:
    print("Error while merging JSON files: " + str(e))
