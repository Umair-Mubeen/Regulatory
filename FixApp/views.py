from io import StringIO
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
import pandas as pd
import numpy as np
from django.http import FileResponse
from .models import Employee, OrderEvent, Reports, EOA
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .Utilities import readCSV_MEOR, readCSV_MENO, generateMEOR, downloadCSV, readCSV, from_EOA_to_MENO, \
    from_EOA_to_MEOR, merge_MENO_MEOR


def index(request):
    try:
        if isLoggedIn(request):
            return redirect('Dashboard')
        else:
            return render(request, 'login.html')
    except Exception as e:
        return HttpResponse(str(e))


def userLogin(request):
    try:
        if isLoggedIn(request):
            return redirect('Dashboard')

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['UserName'] = username
                return render(request, 'Dashboard.html',
                              {'title': 'Welcome to Dashboard !', 'icon': 'success',
                               'message': 'Login SuccessFully!'})

            else:
                return render(request, 'login.html',
                              {'title': 'Invalid ', 'icon': 'error', 'message': 'Invalid Username or Password!'})

        else:
            render(request, 'login.html',
                   {'title': 'Invalid Method ', 'icon': 'error', 'message': 'Method shall be POST rather than GET !'})
    except Exception as e:
        return render(request, 'login.html')


def Dashboard(request):
    if isLoggedIn(request) is False:
        return redirect('/')

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


def MEOA(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')

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
                return render(request, 'MEOA.html',
                              {'title': 'Invalid File Type!', 'icon': 'error', 'message': 'File must be a CSV!'})

            result_MENO = readCSV_MENO(file_path, CAT_IM_ID, FD_ID, Trading_Session)
            generateMEOR(file_path, CAT_IM_ID, FD_ID, Trading_Session)
            result_MEOR = readCSV_MEOR(file_path, CAT_IM_ID, FD_ID, Trading_Session)
            # result = pd.concat([result_MENO, result_MEOR], axis=0, ignore_index=True)
            try:
                readCSV()
                response = FileResponse(open('MENO_Creation.csv', 'rb'), as_attachment=True,
                                        filename='From_MEOA_Merge_To_MENO_MEOR.csv')
                return response
            except Exception as e:
                print("Error Exception :" + str(e))
                return render(request, 'MEOA.html', {'message': "Error Occur while Downloading file!"})
           

        else:
            return render(request, 'MEOA.html', {'message': ""})
    except Exception as e:
        print("Error Exception :" + str(e))
        return render(request, 'MEOA.html', {'message': "File or CSV Error Exception :" + str(e)})


def MEOA_Details(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')

        result = OrderEvent.objects.all()
        paginator = Paginator(result, 20)
        page = request.GET.get('page')
        MEOA = paginator.get_page(page)

        return render(request, 'MEOA_Details.html', {'item': MEOA})

    except Exception as e:
        print("Error Exception :" + str(e))
        return render(request, 'MEOA_Details.html', {'message': "Error Exception :" + str(e)})


def EOA_Details(request, ):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')

        result = EOA.objects.all()
        paginator = Paginator(result, 20)
        page = request.GET.get('page')
        EOA_result = paginator.get_page(page)

        return render(request, 'EOA_Details.html', {'item': EOA_result})

    except Exception as e:
        print("Error Exception :" + str(e))
        return render(request, 'MEOA_Details.html', {'message': "Error Exception :" + str(e)})


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


def EOA_Form(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')

        if request.method == 'POST':
            CAT_IM_ID = request.POST['CAT_IM_ID']
            FD_ID = request.POST['FD_ID']
            Trading_Session = request.POST['Trading_Session']
            uploaded_file = request.FILES.get('file')  # Access uploaded file through request.FILES
            directory = 'EOA'

            if not os.path.exists(directory):  # Check if the directory exists, create it if it doesn't
                os.makedirs(directory)

            if CAT_IM_ID == '' or FD_ID == '' or Trading_Session == '':
                return render(request, 'EOA.html',
                              {'title': 'Required !', 'icon': 'error', 'message': 'One or more fields are missing!'})

            if uploaded_file.size == 0:
                return render(request, 'EOA.html',
                              {'title': 'Required !', 'icon': 'error', 'message': 'Uploaded File Size is Empty!'})

            if not uploaded_file:
                return render(request, 'EOA.html',
                              {'title': 'No File Uploaded!', 'icon': 'error', 'message': 'Please upload a file!'})

            file_name = uploaded_file.name
            file_path = os.path.join(directory, uploaded_file.name)  # Define the file path where the file will be save
            # Save the file to the desired location
            if file_name.endswith('.csv'):
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

            if not file_name.endswith('.csv'):
                return render(request, 'EOA.html',
                              {'title': 'Invalid File Type!', 'icon': 'error', 'message': 'File must be a CSV!'})

            result_MENO = from_EOA_to_MENO(file_path, CAT_IM_ID, FD_ID, Trading_Session)
            result_MEOR = from_EOA_to_MEOR(file_path, CAT_IM_ID, FD_ID, Trading_Session)

            try:
                # return downloadCSV(result_MENO)
                merge_MENO_MEOR()
                response = FileResponse(open('EOA_To_MENO.csv', 'rb'), as_attachment=True,
                                        filename='From_EOA_Merge_To_MENO_MEOR.csv')
                return response

            except Exception as e:
                print("Error Exception :" + str(e))
                return render(request, 'EOA.html', {'message': "Error Occur while Downloading file!"})

        else:
            return render(request, 'EOA.html', {'message': ""})
    except Exception as e:
        print("Error Exception :" + str(e))
        return render(request, 'EOA.html', {'message': "File or CSV Error Exception :" + str(e)})


def Logout(request):
    logout(request)
    return redirect('/')


def isLoggedIn(request):
    if 'UserName' not in request.session:
        return False
    else:
        print("True Logged In")
        return True
