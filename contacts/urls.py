# contacts/urls.py
from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contact_view, name='contact'),
    path('send/', views.send_message, name='send_message'),
]