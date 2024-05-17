from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
import pandas as pd
import numpy as np
from .models import Employee, OrderEvent
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
        if request.method == 'POST':
            user = request.POST['user']
            pwd = request.POST['pwd']
            Emp = Employee.objects.filter(Emp_Name=user, Emp_Pwd=pwd).exists()
            if Emp:
                print("login success")
                if 'UserName' not in request.session:
                    request.session['UserName'] = user
                    request.session['message'] = "Login Successful"
                return redirect('Dashboard')
            else:
                request.session['message'] = "Invalid Username or Password"
                return render(request, 'login.html')
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
            if CAT_IM_ID == '' or FD_ID == '' or Trading_Session == '':
                return render(request, 'OrderEvents.html',
                              {'title': 'Required !', 'icon': 'error', 'message': 'One or more fields are missing!'})
            file_Name = request.POST['file']
            result = readCSV(file_Name, CAT_IM_ID, FD_ID, Trading_Session)

            try:
                return render(request, 'OrderEvents.html',
                              {'title': 'Required !', 'icon': 'success', 'message': result})
            except Exception as e:
                return render(request, 'OrderEvents.html', {'message': "Exception CSV File :" + str(e)})
        else:
            return render(request, 'OrderEvents.html', {'message': ""})
    except Exception as e:
        return render(request, 'OrderEvents.html', {'message': "Error Exception :" + str(e)})


def readCSV(fileName, CAT_IM_ID, FD_ID, Trading_Session):
    try:
        filePath = "E:\\CAT Task\\" + fileName
        df = pd.read_csv(filePath)
        columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID',
                   'Date', 'Order ID', 'Symbol', 'TimeStamp', 'Fix_Col_1', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4',
                   'Fix_Col_5', 'Fix_Col_6', 'Fix_Col_7', 'Fix_Col_8', 'SideType', 'Price', 'Quantity', 'Fix_Col_9',
                   'OrderType', 'TIF', 'Trading Session', 'Fix_Col_10', 'Fix_Col_11', 'FDID', 'Acc Type', 'Fix_Col_12',
                   'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16', 'Fix_Col_17', 'Fix_Col_18', 'Fix_Col_19',
                   'Fix_Col_20', 'Fix_Col_21', 'Fix_Col_22', 'Fix_Col_23', 'Fix_Col_24', 'Fix_Col_25', 'Fix_Col_26',
                   'Fix_Col_27', 'Fix_Col_28']
        new_df = pd.DataFrame(columns=columns)
        new_df['Fix_Col_0'] = ''
        new_df['FirmROID'] = (
                pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "_CAT-" + CAT_IM_ID + "-"
                + (df.index + 1).astype(str))
        # new_df['Firm Row ID'] = pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "_MVC_"
        # new_df['Firm Row ID'] = pd.to_datetime(df['Event Timestamp']).dt.date  # update date
        new_df['Order Event'] = 'NEW'

        if df['Event Type'].eq('MEOA').all():  # check if Event Type has value MEOA replace with MENO
            df.loc[df['Event Type'] == 'MEOA', 'Event Type'] = 'MENO'
        new_df['MsgType'] = df['Event Type']
        new_df['CAT_IM_ID'] = f'{CAT_IM_ID}'
        new_df['Date'] = pd.to_datetime(df['Event Timestamp']).dt.strftime('%Y%m%d').astype(str) + "T000000.00000000"

        # new_df['Date'] = pd.to_datetime(df['Event Timestamp']).dt.date
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
        new_df['Trading Session'] = Trading_Session
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
        new_df.to_csv('testing.csv', index=False)
        orderEventInsertion(new_df)
        return "Csv File has been Created !"
    except Exception as e:
        return str(e)


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
        print("Bulk : - " + str(e))
        return str(e)


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


def Logout(request):
    if 'UserName' not in request.session:
        return HttpResponseRedirect('/')

    del request.session['UserName']
    return HttpResponseRedirect('Dashboard')
