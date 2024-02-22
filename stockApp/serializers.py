from rest_framework import serializers
from stockApp.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name", "created_at", "modified_at"]
        read_only_fields = ["id", "created_at", "modified_at"]