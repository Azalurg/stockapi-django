from rest_framework import serializers
from stockApp.models import CustomUser, StockTimeSeriesData, StockData


class CommonUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["id", "created_at", "modified_at"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name"]

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance


class StockTimeSeriesDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockTimeSeriesData
        fields = ['open', 'high', 'low', 'close', 'volume', 'date']


class StockDataSerializer(serializers.ModelSerializer):
    timeseries = StockTimeSeriesDataSerializer(many=False, read_only=True)

    class Meta:
        model = StockData
        fields = ['timeseries', 'symbol', 'name', 'exchange', 'type', 'currency', 'country']