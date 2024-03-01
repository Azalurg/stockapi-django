from django.db.models import Max, F, Subquery, OuterRef
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


from stockApp.models import CustomUser, StockData, StockTimeSeriesData
from stockApp.serializers import (
    CommonUserSerializer,
    UpdateUserSerializer,
    StockDataSerializer,
)


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


class StockPrices(APIView):
    def get(self, request):
        def get_query(val: str):
            return StockTimeSeriesData.objects.filter(
                stock__id=OuterRef("id"), date=OuterRef("last_time_series_update")
            ).values(val)

        result = (
            StockData.objects.all()
            .annotate(
                volume=get_query("volume"),
                open=get_query("open"),
                close=get_query("close"),
                high=get_query("high"),
                low=get_query("low"),
            )
            .order_by("-volume", "symbol")
        )

        serializer = StockDataSerializer(result, many=True)

        return Response(serializer.data)
