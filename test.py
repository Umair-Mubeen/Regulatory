import pandas as pd

with open('merge.csv', 'w') as new_file:
    with open('MENO_Creation.csv', 'r') as data_file:
        new_file.write(data_file.readline())
        with open('MEOR_Creation.csv', 'r') as hdr_file:
            new_file.write(hdr_file.readline())
        new_file.write(data_file.read())
