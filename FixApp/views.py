from io import StringIO
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
import pandas as pd
import numpy as np
from .models import Employee, OrderEvent, Reports
import os


def index(request):
    try:
        if 'UserName' not in request.session:
            return render(request, 'login.html')
        else:
            return redirect('Dashboard')
    except Exception as e:
        return HttpResponse(str(e))


def login(request):
    try:
        if 'UserName' in request.session:
            return redirect('Dashboard')

        if request.method == 'POST':
            user = request.POST['user']
            pwd = request.POST['pwd']
            Emp = Employee.objects.filter(Emp_Name=user, Emp_Pwd=pwd).exists()
            if Emp:
                print("login success")
                if 'UserName' not in request.session:
                    request.session['UserName'] = user
                return render(request, 'Dashboard.html',
                              {'title': 'Welcome to Dashboard !', 'icon': 'success', 'message': 'Login SuccessFully!'})
            else:
                request.session['message'] = "Invalid Username or Password"
                return render(request, 'login.html',
                              {'title': 'Invalid ', 'icon': 'error', 'message': 'Invalid Username or Password!'})
        else:
            request.session['message'] = "Method shall be POST rather than GET !"
            return render(request, 'login.html')
    except Exception as e:
        request.session['message'] = "Exception :- " + str(e)
        return render(request, 'login.html')


def Dashboard(request):
    if 'UserName' not in request.session:
        return render(request, 'login.html')
    else:
        return render(request, 'Dashboard.html')


def Logs(request):
    try:
        if 'UserName' not in request.session:
            return render(request, 'login.html')

        if request.method == 'POST':
            logs = request.POST['FixLogs']
            fileName = "T3Logs.txt"
            with open(fileName, "w", newline='') as file:
                file.write(logs + "\n")
            trail_dict = find_ord_trails(file)
            return render(request, 'OrderTrails.html', {'order_trails': trail_dict})
        else:
            return render(request, 'OrderTrails.html', {'order_trails': ''})
    except IOError as e:
        print("Error Exception:", e)
        return HttpResponse("Internal Server Error", status=500)


def userRegistration(request):
    try:
        if request.method == 'POST':
            fileName = request.POST['file']
            return render(request, 'userRegistration.html')
        else:
            return render(request, 'userRegistration.html')
    except Exception as e:
        print("Error Exception:", e)
        return HttpResponse("Internal Server Error", status=500)


def OrderEvents(request):
    try:
        if 'UserName' not in request.session:
            return render(request, 'login.html')

        if request.method == 'POST':
            CAT_IM_ID = request.POST['CAT_IM_ID']
            FD_ID = request.POST['FD_ID']
            Trading_Session = request.POST['Trading_Session']
            uploaded_file = request.FILES.get('file')  # Access uploaded file through request.FILES
            directory = 'uploads'

            if not os.path.exists(directory):  # Check if the directory exists, create it if it doesn't
                os.makedirs(directory)

            if CAT_IM_ID == '' or FD_ID == '' or Trading_Session == '':
                return render(request, 'OrderEvents.html',
                              {'title': 'Required !', 'icon': 'error', 'message': 'One or more fields are missing!'})

            if uploaded_file.size == 0:
                return render(request, 'OrderEvents.html',
                              {'title': 'Required !', 'icon': 'error', 'message': 'Uploaded File Size is Empty!'})

            if not uploaded_file:
                return render(request, 'OrderEvents.html',
                              {'title': 'No File Uploaded!', 'icon': 'error', 'message': 'Please upload a file!'})

            file_name = uploaded_file.name
            file_path = os.path.join(directory, uploaded_file.name)  # Define the file path where the file will be save
            # Save the file to the desired location
            if file_name.endswith('.csv'):
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

            if not file_name.endswith('.csv'):
                return render(request, 'OrderEvents.html',
                              {'title': 'Invalid File Type!', 'icon': 'error', 'message': 'File must be a CSV!'})
            result_MENO = readCSV_MENO(file_path, CAT_IM_ID, FD_ID, Trading_Session)
            result_MEOR = readCSV_MEOR(file_path, CAT_IM_ID, FD_ID, Trading_Session)
            result = pd.concat([result_MENO, result_MEOR], axis=0, ignore_index=True)

            try:
                return downloadCSV(result)
            except Exception as e:
                print("Error Exception :" + str(e))
                return render(request, 'OrderEvents.html', {'message': "Error Occur while reading file!"})

        else:
            return render(request, 'OrderEvents.html', {'message': ""})
    except Exception as e:
        print("Error Exception :" + str(e))
        return render(request, 'OrderEvents.html', {'message': "File or CSV Error Exception :" + str(e)})


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
        try:
            new_df.to_csv('MENO_Creation.csv', index=False)
            report = Reports(Report_Name='MENO', CAT_IMID=CAT_IM_ID, FD_ID=FD_ID, Train_Session=Trading_Session,
                             FileType='CSV', Status='Completed', FileName=fileName)
            report.save()
            orderEventInsertion(new_df)
            return new_df
        except Exception as e:
            print("CSV to DataFrame Exception :-" + str(e))
            return str("CSV to DataFrame Exception :- " + str(e))

    except Exception as e:
        print("Read CSV Error Exception :" + str(e))
        return str("Read CSV Exception :- " + str(e))


def orderEventInsertion(dataframe):
    try:
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
                Trading_Session=row['Trading Session'],
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

    except Exception as e:
        print("Bulk Insertion Exception: - " + str(e))
        return str("Bulk Insertion Exception: - " + str(e))


def OrderTrails(request):
    try:
        if 'UserName' not in request.session:
            return render(request, 'login.html')

        return render(request, 'orderTrailsForm.html')
    except Exception as e:
        print(e)


def find_ord_trails(file):
    try:
        file = "T3Logs.txt"
        with open(file, 'r') as logFile:
            orders = {}
            lines = logFile.readlines()
            lines = [x for x in lines if x.strip()]  # removing blank lines
            lines = [x.replace('', ' | ') for x in lines]
            for line in lines:
                if line.startswith('8=') or line.startswith('202'):
                    line_dict = {}
                    message = line.split(' | ')[
                              :-1]  # converting a single FIX Message into a list and removing newline character a.t.e of each line
                    for tag in message:
                        if '=' in tag:
                            line_dict[tag.split('=')[0]] = tag.split('=')[1]
                        elif tag in ('IN', 'OUT'):
                            line_dict['Flow'] = tag
                        else:
                            line_dict['Log Time'] = tag
                    if line_dict['35'] == '9' and line_dict['11'] in orders:  # Order Cancel Reject
                        orders[line_dict['11']].append(line.strip('\n'))
                        orders[line_dict['41']] = orders.pop(line_dict['11'])
                    elif line_dict['35'] in ['G', 'F', 'AC'] and line_dict[
                        '41'] in orders:  # Order Cancel/Cancel-Replace Request (35=G, 35=AC, 35=F)
                        orders[line_dict['41']].append(line.strip('\n'))
                        orders[line_dict['11']] = orders.pop(line_dict['41'])
                    elif '11' in line_dict and line_dict['11'] in orders:  # ignoring Heartbeats
                        orders[line_dict['11']].append(line.strip('\n'))
                    elif line_dict['35'] in ['D', 'AB']:  # checking if the Message is a NSO or a NMLegO
                        orders[line_dict['11']] = [line.strip('\n')]  # initializing order trail
            return orders
    except Exception as e:
        print("IO Exception :" + str(e))


def readCSV_MEOR(filePath, CAT_IM_ID, FD_ID, Trading_Session):
    try:
        df = pd.read_csv(filePath)
        df_MENO = pd.read_csv('MENO_Creation.csv')
        num_rows = len(df_MENO)
        last_FirmROID_MENO = df_MENO.tail(1)

        lastID = last_FirmROID_MENO['FirmROID'].str.split('-').str[-1].iloc[-1]  # 20240513_CAT-VCVW-41 # 41
        print("Last Item RowID is :- " + str(lastID))  # 41
        fileName = filePath.split("\\")[-1]
        columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID', 'Date', 'Order ID', 'Symbol',
                   'Fix_Col_1', 'Date TimeStamp', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4', 'Sender_IM_ID',
                   'Receiver_IM_ID', 'Firm_Exchange', 'Routed_OrderID', 'Fix_Col_5', 'SideType', 'Price', 'Quantity',
                   'Fix_Col_6', 'OrderType', 'TIF', 'Trading_Session', 'Fix_Col_7', 'Fix_Col_8', 'Fix_Col_9',
                   'Fix_Col_10', 'Fix_Col_11', 'Fix_Col_12', 'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16',
                   'Fix_Col_17']

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
        new_df['Date TimeStamp'] = df['Event Timestamp']
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
        new_df['Fix_Col_17'] = ''
        try:
            new_df.to_csv('MEOR_Creation.csv', index=False)
            report = Reports(Report_Name='MEOR', CAT_IMID=CAT_IM_ID, FD_ID=FD_ID, Train_Session=Trading_Session,
                             FileType='CSV', Status='Completed', FileName=fileName)
            report.save()
            orderEventInsertion(new_df)
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
        response['Content-Disposition'] = f'attachment; filename="MENO_MEOR_File.csv"'
        return response
    except Exception as e:
        print("Error while Downloading CSV Exception :-" + str(e))
        return str("Error while Downloading CSV Exception")


def Logout(request):
    if 'UserName' not in request.session:
        return HttpResponseRedirect('/')

    del request.session['UserName']
    return HttpResponseRedirect('Dashboard')
