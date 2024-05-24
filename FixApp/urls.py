from django.urls import path
from .views import *

from FixApp import views

urlpatterns = [
    path('OrderTrails', views.OrderTrails, name='OrderTrails'),  # Order Traits
    path('', views.index, name='index'),  # Login Page
    path('login', views.login, name='login'),
    path('Dashboard', views.Dashboard, name='Dashboard'),
    path('Logout', views.Logout, name='Logout'),
    path('Logs', views.Logs, name='Logs'),
    path('registration', views.userRegistration, name='registration'),
    path('OrderEvents', views.OrderEvents, name='OrderEvents'),
    path('EOA', views.EOA, name='EOA'),
]
