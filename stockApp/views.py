import requests as req
from django.db.models import F
from django.shortcuts import render
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from stockApp.models import (
    CustomUser,
    StockData,
    StockTimeSeriesData
)
from stockApp.serializers import (
    CommonUserSerializer,
    UpdateUserSerializer,
    StockDataWithPricesSerializer,
    StockRequestSerializer,
    StockDataSerializer,
)
from stockApp.tasks import get_stock_time_series

stock_values = [
    "stock__symbol",
    "stock__name",
    "stock__exchange",
    "stock__type",
    "stock__currency__name",
    "stock__country__name",
    "close",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


class IsAdminGet(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return (
                request.user and request.user.is_authenticated and request.user.is_staff
            )
        return True


class ISAccountOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user == obj


class UsersList(APIView):
    permission_classes = [IsAdminGet]

    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = CommonUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CommonUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersDetail(APIView):
    permission_classes = [ISAccountOwner]

    def get_by_id(self, request, pk) -> CustomUser:
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        return user

    def get(self, request, pk, format=None):
        user = self.get_by_id(request, pk)
        serializer = CommonUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        user = self.get_by_id(request, pk)
        serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_by_id(request, pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StockPrices(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = (
            StockTimeSeriesData.objects.filter(date=F("stock__last_time_series_update"))
            .values(*stock_values)
            .order_by("-volume", "stock__symbol")
        )

        page = self.paginate_queryset(result)
        if page is not None:
            serializer = StockDataWithPricesSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StockDataWithPricesSerializer(result, many=True)
        return Response(serializer.data)


class FollowStock(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stock_id = request.data.get("id")
        stock = get_object_or_404(StockData, pk=stock_id)
        user = request.user

        if user.following.filter(pk=stock_id).exists():
            return Response(
                {"message": "Stock already followed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.following.add(stock)
        user.save()

        return Response({"message": "Success"})


class UnfollowStock(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stock_id = request.data.get("id")
        stock = get_object_or_404(StockData, pk=stock_id)
        user = request.user

        # Check if the user is already following the stock
        if not user.following.filter(pk=stock_id).exists():
            return Response(
                {"message": "Stock not followed"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.following.remove(stock)
        user.save()

        return Response({"message": "Success"})


class Homepage(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        stocks_ids = user.following.values_list("id", flat=True)
        stocks = (
            StockTimeSeriesData.objects.filter(
                date=F("stock__last_time_series_update"), stock__id__in=stocks_ids
            )
            .values(*stock_values)
            .order_by("-volume", "stock__symbol")
        )

        return render(
            request,
            "index.html",
            {
                "user": user,
                "stocks": StockDataWithPricesSerializer(stocks, many=True).data,
            },
        )


class StockRequest(APIView):
    permission_classes = [IsAuthenticated]
    base_url = "https://api.twelvedata.com/stocks"
    params = {
        "country": "United States",
        "exchange": "NASDAQ",
        "type": "Common Stock",
        "currency": "USD",
    }

    def post(self, request):
        request_serializer = StockRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        self.params["symbol"] = request_serializer.data.get("symbol")
        response = req.get(self.base_url, params=self.params)
        data = response.json().get("data")
        if len(data) == 0:
            return Response(
                {
                    "message": f"No stock listed with provided symbol - {self.params['symbol']}"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        stock_serializer = StockDataSerializer(data=data[0])
        if stock_serializer.is_valid():
            stock_serializer.save()
            request.user.following.add(stock_serializer.data.get("id"))
            request.user.save()
            get_stock_time_series.delay(stock_serializer.data.get("symbol"))
            return Response(stock_serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            stock_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
