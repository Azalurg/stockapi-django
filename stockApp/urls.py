from django.urls import path
from stockApp import views

urlpatterns = [
    path('', views.UsersList.as_view()),
    path('<int:pk>', views.UsersDetail.as_view())
]
