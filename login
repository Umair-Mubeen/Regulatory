    if request.method == 'POST':
            username = request.POST.get('user')
            password = request.POST.get('pwd')

            # Authenticate the user with the provided username and password
            user = authenticate(request, username=username, password=password)

            if user is None:
                return render(request, 'login.html',
                              {'title': 'Invalid ', 'icon': 'error', 'message': 'Invalid Username or Password!'})
            else:
                login(request, user)
                return render(request, 'Dashboard.html',
                              {'title': 'Welcome to Dashboard !', 'icon': 'success',
                               'message': 'Login SuccessFully!'})
   
