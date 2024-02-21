from django.urls import path
from stockApp import views

urlpatterns = [
    path('', views.users_list),
]
