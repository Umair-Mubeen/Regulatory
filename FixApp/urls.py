from django.urls import path
from .views import *

from FixApp import views

urlpatterns = [
    path('OrderTrails', views.OrderTrails, name='OrderTrails'),  # Order Traits
    path('', views.index, name='index'),  # Login Page
    path('login', views.userLogin, name='userLogin'),
    path('Dashboard', views.Dashboard, name='Dashboard'),
    path('Logout', views.Logout, name='Logout'),
    path('Logs', views.Logs, name='Logs'),
    path('registration', views.userRegistration, name='registration'),
    path('MEOA', views.MEOA, name='MEOA'),
    path('MEOA-Details', views.MEOA_Details, name='MEOA_Details'),
    path('EOA', views.EOA_Form, name='EOA_Form'),
    path('EOA-Details', views.EOA_Details, name='EOA_Details'),
    path('FixParser', views.FixParser, name='FixParser'),
]
