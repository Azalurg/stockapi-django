from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView


from stockApp.models import CustomUser
from stockApp.serializers import UserSerializer


class CustomUserListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            if request.user and request.user.is_authenticated:
                return request.user.is_admin
            return False
        return True


class CustomUserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            return obj == request.user
        return False

class UsersList(APIView):
    permission_classes = [CustomUserListPermission]

    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersDetail(APIView):
    permission_classes = [CustomUserPermission]

    def get_by_id(self, request, pk) -> CustomUser:
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        return user

    def get(self, request, pk, format=None):
        user = self.get_by_id(request, pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        user = self.get_by_id(request, pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_by_id(request, pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
