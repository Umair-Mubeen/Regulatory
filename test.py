def readCSV():
    try:
        with open('MENO_Creation.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            with open('MEOR_Creation.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    writer.writerow(row)
        downloadCSV(f)
        pass
    except Exception as e:
        print("Merge CSV Exception :-" + str(e))
