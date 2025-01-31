from django.urls import path
from stockApp import views

from stockApp.consumers import StockConsumer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

websocket_urlpatterns = [
    path('ws/stock-prices/', StockConsumer.as_asgi())
]

urlpatterns = [
    path('users/', views.UsersList.as_view()),
    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/<int:pk>', views.UsersDetail.as_view()),
    path('stock/prices/', views.StockPrices.as_view()),
    path('stock/follow', views.FollowStock.as_view()),
    path('stock/unfollow', views.UnfollowStock.as_view()),
    path('homepage/', views.Homepage.as_view(), name="homepage"),
    path('stock/request', views.StockRequest.as_view())
]
