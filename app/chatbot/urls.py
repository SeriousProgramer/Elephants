# app/chatbot/urls.py
from django.urls import path
from .views import   simulate_hundred_convos, veg_api   #  ← import the names that exist

urlpatterns = [
    
    path("simulate/",   simulate_hundred_convos, name="simulate"),   # POST
    path("veg/",        veg_api,                 name="veg_api"),    # GET, auth
]