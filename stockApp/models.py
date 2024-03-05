from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Country(models.Model):
    name = models.CharField(unique=True)


class Currency(models.Model):
    name = models.CharField(unique=True)


class StockData(models.Model):
    class StockType(models.TextChoices):
        CLOSED_END_FUND = "Closed-end Fund"
        COMMON_STOCK = "Common Stock"
        DEPOSITARY_RECEIPT = "Depositary Receipt"
        ETF = "ETF"
        EXCHANGE_TRADED_NOTE = "Exchange-Traded Note"
        GLOBAL_DEPOSITARY_RECEIPT = "Global Depositary Receipt"
        LIMITED_PARTNERSHIP = "Limited Partnership"
        MUTUAL_FUND = "Mutual Fund"
        PREFERRED_STOCK = "Preferred Stock"
        REIT = "REIT"
        RIGHT = "Right"
        STRUCTURED_PRODUCT = "Structured Product"
        TRUST = "Trust"
        UNIT = "Unit"
        WARRANT = "Warrant"

    symbol = models.CharField(unique=True)
    name = models.CharField()
    exchange = models.CharField()
    type = models.CharField(choices=StockType)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    last_time_series_update = models.DateField(default=None, null=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class StockTimeSeriesData(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    date = models.DateField()


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    following = models.ManyToManyField(StockData)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_active

    def has_module_perms(self, app_label):
        return self.is_active

    @property
    def is_staff(self):
        return self.is_admin
