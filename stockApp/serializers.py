from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from stockApp.models import CustomUser, StockData, Country, Currency


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


class StockDataWithPricesSerializer(serializers.Serializer):
    symbol = serializers.CharField(source="stock__symbol")
    name = serializers.CharField(source="stock__name")
    exchange = serializers.CharField(source="stock__exchange")
    type = serializers.CharField(source="stock__type")
    currency = serializers.CharField(source="stock__currency__name")
    country = serializers.CharField(source="stock__country__name")
    open = serializers.FloatField()
    close = serializers.FloatField()
    high = serializers.FloatField()
    low = serializers.FloatField()
    volume = serializers.FloatField()


class StockRequestSerializer(serializers.Serializer):
    symbol = serializers.CharField()

    class Meta:
        validators = [
            UniqueTogetherValidator(queryset=StockData.objects.all(), fields=["symbol"])
        ]


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = [
            "symbol",
            "name",
            "exchange",
            "type",
        ]

    def create(self, validated_data):
        country = Country.objects.get(name="United States")
        currency = Currency.objects.get(name="USD")
        return StockData.objects.create(
            country=country, currency=currency, **validated_data
        )
