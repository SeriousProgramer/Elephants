# app/chatbot/urls.py
from django.urls import path
from .views import chat_page, store_answer   #  ← import the names that exist

urlpatterns = [
    path("",        chat_page,    name="chat_page"),     # GET
    path("ask/",    store_answer, name="store_answer"),  # POST
]
