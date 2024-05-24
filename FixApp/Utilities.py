import csv
from io import StringIO
import pandas as pd
import numpy as np
from django.http import request
from django.shortcuts import HttpResponse, render
from .models import Employee, OrderEvent, Reports
import os


def readCSV_MEOR(filePath, CAT_IM_ID, FD_ID, Trading_Session):
    try:
        df = pd.read_csv(filePath)
        df_MENO = pd.read_csv('MENO_Creation.csv')
        last_FirmROID_MENO = df_MENO.tail(1)

        lastID = last_FirmROID_MENO['FirmROID'].str.split('-').str[-1].iloc[-1]  # 20240513_CAT-VCVW-41 # 41
        fileName = filePath.split("\\")[-1]
        columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID', 'Date', 'Order ID', 'Symbol',
                   'Fix_Col_1', 'TimeStamp', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4', 'Fix_Col_5', 'SideType', 'Price',
                   'Quantity', 'Fix_Col_6', 'OrderType', 'TIF', 'Trading_Session', 'FDID', 'Fix_Col_7', 'Fix_Col_8',
                   'Fix_Col_9', 'Fix_Col_10', 'Fix_Col_11', 'Fix_Col_12', 'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15',
                   'Fix_Col_16']

        new_df = pd.DataFrame(columns=columns)
        new_df['Fix_Col_0'] = ''
        for i, row in df.iterrows():
            new_df.loc[i, 'FirmROID'] = (
                    pd.to_datetime(row['Event Timestamp']).strftime('%Y%m%d') + "_CAT-" + CAT_IM_ID + "-"
                    + str(int(lastID) + 1))
            lastID = int(pd.Series(new_df.loc[i, 'FirmROID']).str.split('-').str[-1])

        new_df['Order Event'] = 'NEW'

        filtered_df = df[df['Event Type'] == 'MEOA']
        # Check if all rows in the filtered DataFrame have Event Type as MEOA
        if (filtered_df['Event Type'] == 'MEOA').all():
            # Replace Event Type with MENO
            filtered_df['Event Type'] = 'MEOR'

        new_df['MsgType'] = filtered_df['Event Type']
        new_df['CAT_IM_ID'] = f'{CAT_IM_ID}'
        new_df['Date'] = pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "T000000.00000000"

        counter = 1
        for index, row in df.iterrows():
            new_df.loc[index, 'Order ID'] = "CAT-" + CAT_IM_ID + '-' + "OrderID-" + f'{counter}'
            counter += 1
        new_df['Symbol'] = df['Symbol']
        new_df['Fix_Col_1'] = df['Event Timestamp']
        new_df['TimeStamp'] = ''
        new_df['Fix_Col_2'] = 'False'
        new_df['Fix_Col_3'] = 'False'
        new_df['Fix_Col_4'] = ''

        new_df['Fix_Col_5'] = df['Sender IMID']
        new_df['SideType'] = ''
        new_df['Price'] = df['Side']

        if df['Price'].eq('').all():  # check if Price has no value then replace with empty
            df.loc[df['Price'] == '', 'Price'] = ''
        # new_df['Price'] = df['Price']
        new_df['Quantity'] = df['Price']

        # new_df['Quantity'] = df['Quantity']
        new_df['Fix_Col_6'] = df['Receiver IMID']
        # new_df['OrderType'] = np.where(df['Price'].notnull(), 'LMT', 'MKT')
        new_df['OrderType'] = ''

        # new_df['TIF'] = "GTX=" + pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str)

        new_df['TIF'] = np.where(df['Price'].notnull(), 'LMT', 'MKT')

        # new_df['Trading_Session'] = Trading_Session
        new_df['Trading_Session'] = "GTX=" + pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str)
        new_df['Fix_Col_7'] = 'F'
        new_df['Fix_Col_8'] = df['Routed Order ID']
        new_df['Fix_Col_9'] = df['Quantity']
        new_df['Fix_Col_10'] = Trading_Session
        new_df['Fix_Col_11'] = 'False'
        new_df['FDID'] = 'NA'
        new_df['Acc Type'] = ''
        new_df['Fix_Col_12'] = 'False'
        new_df['Fix_Col_13'] = 'False'
        new_df['Fix_Col_14'] = ''
        new_df['Fix_Col_15'] = 'False'
        new_df['Fix_Col_16'] = ''
        try:
            report = Reports(Report_Name='MEOR', CAT_IMID=CAT_IM_ID, FD_ID=FD_ID, Train_Session=Trading_Session,
                             FileType='CSV', Status='Completed', FileName=fileName)
            report.save()

            orderEventInsertion(new_df, 'MEOR')
            return new_df
        except Exception as e:
            print("CSV to DataFrame Exception :-" + str(e))
            return str("CSV to DataFrame Exception :- " + str(e))

    except Exception as e:
        print("Read CSV Error Exception :" + str(e))
        return str("Read CSV Exception :- " + str(e))


def generateMEOR(filePath, CAT_IM_ID, FD_ID, Trading_Session):
    try:
        df = pd.read_csv(filePath)
        df_MENO = pd.read_csv('MENO_Creation.csv')
        num_rows = len(df_MENO)
        last_FirmROID_MENO = df_MENO.tail(1)

        lastID = last_FirmROID_MENO['FirmROID'].str.split('-').str[-1].iloc[-1]  # 20240513_CAT-VCVW-41 # 41
        print("Last Item RowID is :- " + str(lastID))  # 41
        fileName = filePath.split("\\")[-1]
        columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID', 'Date', 'Order ID', 'Symbol',
                   'Fix_Col_1', 'TimeStamp', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4', 'Sender_IM_ID',
                   'Receiver_IM_ID', 'Firm_Exchange', 'Routed_OrderID', 'Fix_Col_5', 'SideType', 'Price', 'Quantity',
                   'Fix_Col_6', 'OrderType', 'TIF', 'Trading_Session', 'Fix_Col_7', 'Fix_Col_8', 'Fix_Col_9',
                   'Fix_Col_10', 'Fix_Col_11', 'Fix_Col_12', 'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16']

        new_df = pd.DataFrame(columns=columns)
        new_df['Fix_Col_0'] = ''
        for i, row in df.iterrows():
            new_df.loc[i, 'FirmROID'] = (
                    pd.to_datetime(row['Event Timestamp']).strftime('%Y%m%d') + "_CAT-" + CAT_IM_ID + "-"
                    + str(int(lastID) + 1))
            lastID = int(pd.Series(new_df.loc[i, 'FirmROID']).str.split('-').str[-1])

        new_df['Order Event'] = 'NEW'

        filtered_df = df[df['Event Type'] == 'MEOA']
        # Check if all rows in the filtered DataFrame have Event Type as MEOA
        if (filtered_df['Event Type'] == 'MEOA').all():
            # Replace Event Type with MENO
            filtered_df['Event Type'] = 'MEOR'

        new_df['MsgType'] = filtered_df['Event Type']
        new_df['CAT_IM_ID'] = f'{CAT_IM_ID}'
        new_df['Date'] = pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "T000000.00000000"

        counter = 1
        for index, row in df.iterrows():
            new_df.loc[index, 'Order ID'] = "CAT-" + CAT_IM_ID + '-' + "OrderID-" + f'{counter}'
            counter += 1
        new_df['Symbol'] = df['Symbol']
        new_df['Fix_Col_1'] = ''
        new_df['TimeStamp'] = df['Event Timestamp']
        new_df['Fix_Col_2'] = 'False'
        new_df['Fix_Col_3'] = 'False'
        new_df['Fix_Col_4'] = ''
        new_df['Sender_IM_ID'] = df['Sender IMID']
        new_df['Receiver_IM_ID'] = df['Receiver IMID']
        new_df['Firm_Exchange'] = 'F'

        new_df['Routed_OrderID'] = df['Routed Order ID']
        new_df['Fix_Col_5'] = ''
        new_df['SideType'] = df['Side']
        if df['Price'].eq('').all():  # check if Price has no value then replace with empty
            df.loc[df['Price'] == '', 'Price'] = ''
        new_df['Price'] = df['Price']
        new_df['Quantity'] = df['Quantity']
        new_df['Fix_Col_6'] = ''
        new_df['OrderType'] = np.where(df['Price'].notnull(), 'LMT', 'MKT')
        new_df['TIF'] = "GTX=" + pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str)
        new_df['Trading_Session'] = Trading_Session
        new_df['Fix_Col_7'] = 'False'
        new_df['Fix_Col_8'] = 'NA'
        new_df['Fix_Col_9'] = 'False'
        new_df['Fix_Col_10'] = 'False'
        new_df['Fix_Col_11'] = ''
        new_df['Fix_Col_12'] = 'False'
        new_df['Fix_Col_13'] = ''
        new_df['Fix_Col_14'] = ''
        new_df['Fix_Col_15'] = ''
        new_df['Fix_Col_16'] = ''
        try:
            new_df.to_csv('MEOR_Creation.csv', index=False)
            report = Reports(Report_Name='MEOR', CAT_IMID=CAT_IM_ID, FD_ID=FD_ID, Train_Session=Trading_Session,
                             FileType='CSV', Status='Completed', FileName=fileName)
            report.save()
            print("MEOR Reports Saved Successfully")

            return new_df
        except Exception as e:
            print("CSV to DataFrame Exception :-" + str(e))
            return str("CSV to DataFrame Exception :- " + str(e))

    except Exception as e:
        print("Read CSV Error Exception :" + str(e))
        return str("Read CSV Exception :- " + str(e))


def downloadCSV(result):
    try:

        csv_buffer = StringIO()
        result.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        response = HttpResponse(csv_buffer, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="EOA_To_MENO.csv"'
        return response
    except Exception as e:
        print("Error while Downloading  :-" + str(e))
        return render(request, 'OrderEvents.html', {'message': f"Error Occur while Downloading"})


def readCSV_MENO(filePath, CAT_IM_ID, FD_ID, Trading_Session):
    try:
        df = pd.read_csv(filePath)
        fileName = filePath.split("\\")[-1]
        columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID',
                   'Date', 'Order ID', 'Symbol', 'TimeStamp', 'Fix_Col_1', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4',
                   'Fix_Col_5', 'Fix_Col_6', 'Fix_Col_7', 'Fix_Col_8', 'SideType', 'Price', 'Quantity', 'Fix_Col_9',
                   'OrderType', 'TIF', 'Trading_Session', 'Fix_Col_10', 'Fix_Col_11', 'FDID', 'Acc Type', 'Fix_Col_12',
                   'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16', 'Fix_Col_17', 'Fix_Col_18', 'Fix_Col_19',
                   'Fix_Col_20', 'Fix_Col_21', 'Fix_Col_22', 'Fix_Col_23', 'Fix_Col_24', 'Fix_Col_25', 'Fix_Col_26',
                   'Fix_Col_27', 'Fix_Col_28', 'Fix_Col_29']

        new_df = pd.DataFrame(columns=columns)
        new_df['Fix_Col_0'] = ''
        new_df['FirmROID'] = (
                pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "_CAT-" + CAT_IM_ID + "-"
                + (df.index + 1).astype(str))
        new_df['Order Event'] = 'NEW'

        filtered_df = df[df['Event Type'] != 'MOOA']
        # Check if all rows in the filtered DataFrame have Event Type as MEOA
        if (filtered_df['Event Type'] == 'MEOA').all():
            # Replace Event Type with MENO
            filtered_df['Event Type'] = 'MENO'

        # if df['Event Type'].eq('MEOA').all():  # check if Event Type has value MEOA replace with MENO
        #     df.loc[df['Event Type'] == 'MEOA', 'Event Type'] = 'MENO'
        new_df['MsgType'] = filtered_df['Event Type']
        new_df['CAT_IM_ID'] = f'{CAT_IM_ID}'
        new_df['Date'] = pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "T000000.00000000"

        counter = 1
        for index, row in df.iterrows():
            new_df.loc[index, 'Order ID'] = "CAT-" + CAT_IM_ID + '-' + "OrderID-" + f'{counter}'
            counter += 1
        new_df['TimeStamp'] = df['Event Timestamp']
        new_df['Fix_Col_1'] = 'False'
        new_df['Fix_Col_2'] = 'False'
        new_df['Fix_Col_3'] = ''
        new_df['Fix_Col_4'] = ''
        new_df['Fix_Col_5'] = ''
        new_df['Fix_Col_6'] = 'T'
        new_df['Fix_Col_7'] = 'False'
        new_df['Fix_Col_8'] = ''
        new_df['SideType'] = df['Side']
        if df['Price'].eq('').all():  # check if Price has no value then replace with empty
            df.loc[df['Price'] == '', 'Price'] = ''
        new_df['Symbol'] = df['Symbol']
        new_df['Price'] = df['Price']
        new_df['Quantity'] = df['Quantity']
        new_df['Fix_Col_9'] = ''
        new_df['OrderType'] = np.where(df['Price'].notnull(), 'LMT', 'MKT')
        new_df['TIF'] = "GTX=" + pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str)
        new_df['Trading_Session'] = Trading_Session
        new_df['Fix_Col_10'] = ''
        new_df['Fix_Col_11'] = 'False'
        new_df['FDID'] = FD_ID
        new_df['Acc Type'] = 'A'
        new_df['Fix_Col_12'] = 'False'
        new_df['Fix_Col_13'] = ''
        new_df['Fix_Col_14'] = ''
        new_df['Fix_Col_15'] = 'False'
        new_df['Fix_Col_16'] = 'N'
        new_df['Fix_Col_17'] = ''
        new_df['Fix_Col_18'] = ''
        new_df['Fix_Col_19'] = ''
        new_df['Fix_Col_20'] = ''
        new_df['Fix_Col_21'] = ''
        new_df['Fix_Col_22'] = ''
        new_df['Fix_Col_23'] = ''
        new_df['Fix_Col_24'] = ''
        new_df['Fix_Col_25'] = ''
        new_df['Fix_Col_26'] = ''
        new_df['Fix_Col_27'] = ''
        new_df['Fix_Col_28'] = ''
        new_df['Fix_Col_29'] = ''
        try:

            new_df.to_csv('MENO_Creation.csv', index=False)
            report = Reports(Report_Name='MENO', CAT_IMID=CAT_IM_ID, FD_ID=FD_ID, Train_Session=Trading_Session,
                             FileType='CSV', Status='Completed', FileName=fileName)
            report.save()
            orderEventInsertion(new_df, 'MENO')
            return new_df
        except Exception as e:
            print("CSV to DataFrame Exception :-" + str(e))
            return str("CSV to DataFrame Exception :- " + str(e))

    except Exception as e:
        print("Read CSV Error Exception :" + str(e))
        return str("Read CSV Exception :- " + str(e))


def orderEventInsertion(dataframe, type):
    try:
        if type == 'MENO':
            OrderEvent.objects.bulk_create([
                OrderEvent(
                    Order_Event=row['Order Event'],
                    Fix_Col_0=row['Fix_Col_0'],
                    FirmROID=row['FirmROID'],
                    MsgType=row['MsgType'],
                    CAT_IM_ID=row['CAT_IM_ID'],
                    Date=row['Date'],
                    Order_ID=row['Order ID'],
                    Symbol=row['Symbol'],
                    TimeStamp=row['TimeStamp'],
                    Fix_Col_1=row['Fix_Col_1'],
                    Fix_Col_2=row['Fix_Col_2'],
                    Fix_Col_3=row['Fix_Col_3'],
                    Fix_Col_4=row['Fix_Col_4'],
                    Fix_Col_5=row['Fix_Col_5'],
                    Fix_Col_6=row['Fix_Col_6'],
                    Fix_Col_7=row['Fix_Col_7'],
                    Fix_Col_8=row['Fix_Col_8'],
                    SideType=row['SideType'],
                    Price=row['Price'],
                    Quantity=row['Quantity'],
                    Fix_Col_9=row['Fix_Col_9'],
                    OrderType=row['OrderType'],
                    TIF=row['TIF'],
                    Trading_Session=row['Trading_Session'],
                    Fix_Col_10=row['Fix_Col_10'],
                    Fix_Col_11=row['Fix_Col_11'],
                    FD_ID=row['FDID'],
                    Acc_Type=row['Acc Type'],
                    Fix_Col_12=row['Fix_Col_12'],
                    Fix_Col_13=row['Fix_Col_13'],
                    Fix_Col_14=row['Fix_Col_14'],
                    Fix_Col_15=row['Fix_Col_15'],
                    Fix_Col_16=row['Fix_Col_16'],
                    Fix_Col_17=row['Fix_Col_17'],
                    Fix_Col_18=row['Fix_Col_18'],
                    Fix_Col_19=row['Fix_Col_19'],
                    Fix_Col_20=row['Fix_Col_20'],
                    Fix_Col_21=row['Fix_Col_21'],
                    Fix_Col_22=row['Fix_Col_22'],
                    Fix_Col_23=row['Fix_Col_23'],
                    Fix_Col_24=row['Fix_Col_24'],
                    Fix_Col_25=row['Fix_Col_25'],
                    Fix_Col_26=row['Fix_Col_26'],
                    Fix_Col_27=row['Fix_Col_27'],
                    Fix_Col_28=row['Fix_Col_28'],

                ) for _, row in dataframe.iterrows()
            ])
        else:

            OrderEvent.objects.bulk_create([
                OrderEvent(
                    Order_Event=row['Order Event'],
                    Fix_Col_0=row['Fix_Col_0'],
                    FirmROID=row['FirmROID'],
                    MsgType=row['MsgType'],
                    CAT_IM_ID=row['CAT_IM_ID'],
                    Date=row['Date'],
                    Order_ID=row['Order ID'],
                    Symbol=row['Symbol'],
                    TimeStamp=row['TimeStamp'],
                    Fix_Col_1=row['Fix_Col_1'],
                    Fix_Col_2=row['Fix_Col_2'],
                    Fix_Col_3=row['Fix_Col_3'],
                    Fix_Col_4=row['Fix_Col_4'],
                    Fix_Col_5=row['Fix_Col_5'],
                    Fix_Col_6=row['Fix_Col_6'],
                    Fix_Col_7=row['Fix_Col_7'],
                    Fix_Col_8=row['Fix_Col_8'],
                    SideType=row['SideType'],
                    Price=row['Price'],
                    Quantity=row['Quantity'],
                    Fix_Col_9=row['Fix_Col_9'],
                    OrderType=row['OrderType'],
                    TIF=row['TIF'],
                    Trading_Session=row['Trading_Session'],
                    Fix_Col_10=row['Fix_Col_10'],
                    Fix_Col_11=row['Fix_Col_11'],
                    FD_ID='',
                    Acc_Type='',
                    Fix_Col_12=row['Fix_Col_12'],
                    Fix_Col_13=row['Fix_Col_13'],
                    Fix_Col_14=row['Fix_Col_14'],
                    Fix_Col_15=row['Fix_Col_15'],
                    Fix_Col_16=row['Fix_Col_16'],

                ) for _, row in dataframe.iterrows()
            ])

    except Exception as e:
        print("Bulk Insertion Exception: - " + str(e))
        return str("Bulk Insertion Exception: - " + str(e))


def readCSV():
    try:

        with open('MENO_Creation.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            with open('MEOR_Creation.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    writer.writerow(row)

        pass
    except Exception as e:
        print("Merge CSV Exception :-" + str(e))


def from_EOA_to_MENO(filePath, CAT_IM_ID, FD_ID, Trading_Session):
    try:
        df = pd.read_csv(filePath)
        df = df[df['Event Type'] == 'EOA']
        fileName = filePath.split("\\")[-1]
        columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID',
                   'Date', 'Order ID', 'Symbol', 'TimeStamp', 'Fix_Col_1', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4',
                   'Fix_Col_5', 'Fix_Col_6', 'Fix_Col_7', 'Fix_Col_8', 'SideType', 'Price', 'Quantity', 'Fix_Col_9',
                   'OrderType', 'TIF', 'Trading_Session', 'Fix_Col_10', 'Fix_Col_11', 'FDID', 'Acc Type', 'Fix_Col_12',
                   'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16', 'Fix_Col_17', 'Fix_Col_18', 'Fix_Col_19',
                   'Fix_Col_20', 'Fix_Col_21', 'Fix_Col_22', 'Fix_Col_23', 'Fix_Col_24', 'Fix_Col_25', 'Fix_Col_26',
                   'Fix_Col_27', 'Fix_Col_28']

        new_df = pd.DataFrame(columns=columns)
        new_df['Fix_Col_0'] = ''
        new_df['FirmROID'] = (
                pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "_CAT-" + CAT_IM_ID + "-"
                + (df.index + 0).astype(str))
        new_df['Order Event'] = 'NEW'

        filtered_df = df[df['Event Type'] != 'EOM']
        # Check if all rows in the filtered DataFrame have Event Type as MEOA
        if (filtered_df['Event Type'] == 'EOA').all():
            # Replace Event Type with MENO
            filtered_df['Event Type'] = 'MENO'

        # if df['Event Type'].eq('MEOA').all():  # check if Event Type has value MEOA replace with MENO
        #     df.loc[df['Event Type'] == 'MEOA', 'Event Type'] = 'MENO'
        new_df['MsgType'] = filtered_df['Event Type']
        new_df['CAT_IM_ID'] = f'{CAT_IM_ID}'
        new_df['Date'] = pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "T000000.00000000"

        counter = 1
        for index, row in df.iterrows():
            new_df.loc[index, 'Order ID'] = "CAT-" + CAT_IM_ID + '-' + "OrderID-" + f'{counter}'
            counter += 1
        new_df['TimeStamp'] = df['Event Timestamp']
        new_df['Fix_Col_1'] = 'False'
        new_df['Fix_Col_2'] = 'False'
        new_df['Fix_Col_3'] = ''
        new_df['Fix_Col_4'] = ''
        new_df['Fix_Col_5'] = ''
        new_df['Fix_Col_6'] = 'T'
        new_df['Fix_Col_7'] = 'False'
        new_df['Fix_Col_8'] = ''
        # new_df['SideType'] = df['Side']
        filtered_df = df[(df['Side'] == 'Sh') | (df['Side'] == 'Bu') | (df['Side'] == 'Se')]
        new_df.loc[filtered_df['Side'] == 'Sh', 'SideType'] = 'SS'
        new_df.loc[filtered_df['Side'] == 'Bu', 'SideType'] = 'B'
        new_df.loc[filtered_df['Side'] == 'Se', 'SideType'] = 'SL'

        if df['Price'].eq('').all():  # check if Price has no value then replace with empty
            df.loc[df['Price'] == '', 'Price'] = ''
        new_df['Symbol'] = df['Symbol'].apply(lambda x: x.replace('p', 'PR') if 'p' in x else x)
        # new_df['Symbol'] = df['Symbol']
        new_df['Price'] = df['Price']
        new_df['Quantity'] = df['Quantity']
        new_df['Fix_Col_9'] = ''
        new_df['OrderType'] = np.where(df['Price'].notnull(), 'LMT', 'MKT')
        new_df['TIF'] = "DAY=" + pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str)
        new_df['Trading_Session'] = Trading_Session
        new_df['Fix_Col_10'] = ''
        new_df['Fix_Col_11'] = 'False'
        new_df['FDID'] = FD_ID
        new_df['Acc Type'] = 'A'
        new_df['Fix_Col_12'] = 'False'
        new_df['Fix_Col_13'] = ''
        new_df['Fix_Col_14'] = ''
        new_df['Fix_Col_15'] = 'False'
        new_df['Fix_Col_16'] = 'N'
        new_df['Fix_Col_17'] = ''
        new_df['Fix_Col_18'] = ''
        new_df['Fix_Col_19'] = ''
        new_df['Fix_Col_20'] = ''
        new_df['Fix_Col_21'] = ''
        new_df['Fix_Col_22'] = ''
        new_df['Fix_Col_23'] = ''
        new_df['Fix_Col_24'] = ''
        new_df['Fix_Col_25'] = ''
        new_df['Fix_Col_26'] = ''
        new_df['Fix_Col_27'] = ''
        new_df['Fix_Col_28'] = ''
        new_df['Fix_Col_29'] = ''
        try:

            new_df.to_csv('EOA_To_MENO.csv', index=False)
            report = Reports(Report_Name='EOA_TO_MENO', CAT_IMID=CAT_IM_ID, FD_ID=FD_ID, Train_Session=Trading_Session,
                             FileType='CSV', Status='Completed', FileName=fileName)
            report.save()
            # try:
            #     return downloadCSV(new_df, 'EOA_TO_MENO.csv')
            # except Exception as e:
            #     print("Error Occur while Downloading file EOA_TO_MENO ! :" + str(e))
            #     return render(request, 'EOA.html', {'message': "Error Occur while Downloading file EOA_TO_MENO !"})

            return new_df
        except Exception as e:
            print("CSV to DataFrame Exception :-" + str(e))
            return str("CSV to DataFrame Exception :- " + str(e))

    except Exception as e:
        print("Read CSV Error Exception :" + str(e))
        return str("Read CSV Exception :- " + str(e))


def from_EOA_to_MEOR(filePath, CAT_IM_ID, FD_ID, Trading_Session):
    try:
        print("File Path", str(filePath))
        df = pd.read_csv(filePath)
        print(df['Event Type'])
        df = df[df['Event Type'] == 'EOA']
        df_MENO = pd.read_csv("EOA_To_MENO.csv")
        last_FirmROID_MENO = df_MENO.tail(1)

        lastID = last_FirmROID_MENO['FirmROID'].str.split('-').str[-1].iloc[-1]  # 20240515_CAT-VCVW-21# 21
        print("from_EOA_to_MEOR Last Item RowID is :- " + str(lastID))  # 41
        fileName = filePath.split("\\")[-1]
        columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID', 'Date', 'Order ID', 'Symbol',
                   'Fix_Col_1', 'TimeStamp', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4', 'Sender_IM_ID',
                   'Receiver_IM_ID', 'Firm_Exchange', 'Routed_OrderID', 'Session', 'SideType', 'Price', 'Quantity',
                   'Fix_Col_6', 'OrderType', 'TIF', 'Trading_Session', 'Fix_Col_7', 'Fix_Col_8', 'Fix_Col_9',
                   'Fix_Col_10', 'Fix_Col_11', 'Fix_Col_12', 'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16',
                   'Fix_Col_17', 'Fix_Col_18']

        new_df = pd.DataFrame(columns=columns)
        new_df['Fix_Col_0'] = ''
        for i, row in df.iterrows():
            new_df.loc[i, 'FirmROID'] = (
                    pd.to_datetime(row['Event Timestamp']).strftime('%Y%m%d') + "_CAT-" + CAT_IM_ID + "-"
                    + str(int(lastID) + 1))
            lastID = int(pd.Series(new_df.loc[i, 'FirmROID']).str.split('-').str[-1])

        new_df['Order Event'] = 'NEW'

        filtered_df = df[df['Event Type'] != 'EOM']
        # Check if all rows in the filtered DataFrame have Event Type as EOA
        if (filtered_df['Event Type'] == 'EOA').all():
            # Replace Event Type with MENO
            filtered_df['Event Type'] = 'MEOR'

        new_df['MsgType'] = filtered_df['Event Type']
        new_df['CAT_IM_ID'] = f'{CAT_IM_ID}'
        new_df['Date'] = pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "T000000.00000000"

        counter = 1
        for index, row in df.iterrows():
            new_df.loc[index, 'Order ID'] = "CAT-" + CAT_IM_ID + '-' + "OrderID-" + f'{counter}'
            counter += 1

        new_df['Symbol'] = df['Symbol'].apply(lambda x: x.replace('p', 'PR') if 'p' in x else x)
        # new_df['Symbol'] = df['Symbol']
        new_df['Fix_Col_1'] = ''
        new_df['TimeStamp'] = df['Event Timestamp']
        new_df['Fix_Col_2'] = 'False'
        new_df['Fix_Col_3'] = 'False'
        new_df['Fix_Col_4'] = ''
        new_df['Sender_IM_ID'] = "126588:" + df['Sender IMID']
        new_df['Receiver_IM_ID'] = df['Receiver IMID']
        new_df['Firm_Exchange'] = 'E'

        new_df['Routed_OrderID'] = df['Routed Order ID']
        # new_df['Session'] = ''

        filtered_df = df[
            (df['Receiver IMID'] == 'ARCA') | (df['Receiver IMID'] == 'BYX') | (df['Receiver IMID'] == 'BZX') | (
                    df['Receiver IMID'] == 'EDGA')
            | (df['Receiver IMID'] == 'EDGX') | (df['Receiver IMID'] == 'NSDQ') | (df['Receiver IMID'] == 'BX') | (
                    df['Receiver IMID'] == 'MEMX')
            | (df['Receiver IMID'] == 'IEX') | (df['Receiver IMID'] == 'NYSE') | (df['Receiver IMID'] == 'PSX')]

        new_df['Session'] = df['Receiver IMID']
        new_df.loc[filtered_df['Receiver IMID'] == 'ARCA', 'Session'] = 'PFSUCSSB01'
        new_df.loc[filtered_df['Receiver IMID'] == 'BYX', 'Session'] = 'BYX'
        new_df.loc[filtered_df['Receiver IMID'] == 'BZX', 'Session'] = 'SCSY0002'
        new_df.loc[filtered_df['Receiver IMID'] == 'EDGA', 'Session'] = 'SCSY0005'
        new_df.loc[filtered_df['Receiver IMID'] == 'EDGX', 'Session'] = 'SCSY0005'
        new_df.loc[filtered_df['Receiver IMID'] == 'NSDQ', 'Session'] = 'S160R0'
        new_df.loc[filtered_df['Receiver IMID'] == 'BX', 'Session'] = 'S161B1'
        new_df.loc[filtered_df['Receiver IMID'] == 'MEMX', 'Session'] = 'VELOC001'
        new_df.loc[filtered_df['Receiver IMID'] == 'IEX', 'Session'] = 'SSUCS001'
        new_df.loc[filtered_df['Receiver IMID'] == 'NYSE', 'Session'] = 'NFVELSB01'
        new_df.loc[filtered_df['Receiver IMID'] == 'PSX', 'Session'] = 'S161P0'

        filtered_df = df[(df['Side'] == 'Sh') | (df['Side'] == 'Bu') | (df['Side'] == 'Se')]
        new_df.loc[filtered_df['Side'] == 'Sh', 'SideType'] = 'SS'
        new_df.loc[filtered_df['Side'] == 'Bu', 'SideType'] = 'B'
        new_df.loc[filtered_df['Side'] == 'Se', 'SideType'] = 'SL'

        if df['Price'].eq('').all():  # check if Price has no value then replace with empty
            df.loc[df['Price'] == '', 'Price'] = ''
        new_df['Price'] = df['Price']
        new_df['Quantity'] = df['Quantity']
        new_df['Fix_Col_6'] = ''
        new_df['OrderType'] = np.where(df['Price'].notnull(), 'LMT', 'MKT')
        new_df['TIF'] = "DAY=" + pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str)
        new_df['Trading_Session'] = Trading_Session
        new_df['Fix_Col_7'] = 'False'
        new_df['Fix_Col_8'] = 'NA'
        new_df['Fix_Col_9'] = ''
        new_df['Fix_Col_10'] = 'False'
        new_df['Fix_Col_11'] = 'False'
        new_df['Fix_Col_12'] = ''
        new_df['Fix_Col_13'] = 'False'
        new_df['Fix_Col_14'] = ''
        new_df['Fix_Col_15'] = ''
        new_df['Fix_Col_16'] = ''
        new_df['Fix_Col_17'] = ''
        new_df['Fix_Col_18'] = ''
        try:
            report = Reports(Report_Name='MEOR', CAT_IMID=CAT_IM_ID, FD_ID=FD_ID, Train_Session=Trading_Session,
                             FileType='CSV', Status='Completed', FileName=fileName)
            report.save()
            new_df.to_csv('EOA_To_MEOR.csv', header=False, index=False)
            orderEventInsertion(new_df, 'MEOR')
            # try:
            #     return downloadCSV(new_df, 'EOA_To_MEOR.csv')
            # except Exception as e:
            #     print("Error Occur while Downloading file EOA_To_MEOR ! :" + str(e))
            #     return render(request, 'EOA.html', {'message': "Error Occur while Downloading file EOA_To_MEOR !"})
            return new_df
        except Exception as e:
            print("CSV to DataFrame Exception EOA TO MEOR :-" + str(e))
            return str("CSV to DataFrame Exception  EOA TO MEOR :- " + str(e))

    except Exception as e:
        print("Read CSV Error Exception EOA TO MEOR :" + str(e))
        return str("Read CSV Exception EOA TO MEOR :- " + str(e))


def merge_MENO_MEOR():
    try:
        print("EOA_To_MENO")
        with open('EOA_To_MENO.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            with open('EOA_To_MEOR.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    writer.writerow(row)

        pass
    except Exception as e:
        print("Merge CSV Exception :-" + str(e))
