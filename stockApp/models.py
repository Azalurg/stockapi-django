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


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

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


class Country(models.Model):
    name = models.CharField(unique=True)


class Currency(models.Model):
    name = models.CharField(unique=True)


class StockData(models.Model):
    TYPE_CHOICES = [
        (0, "Closed-end Fund"),
        (1, "Common Stock"),
        (2, "Depositary Receipt"),
        (3, "ETF"),
        (4, "Exchange-Traded Note"),
        (5, "Global Depositary Receipt"),
        (6, "Limited Partnership"),
        (7, "Mutual Fund"),
        (8, "Preferred Stock"),
        (9, "REIT"),
        (10, "Right"),
        (11, "Structured Product"),
        (12, "Trust"),
        (13, "Unit"),
        (14, "Warrant"),
    ]
    symbol = models.CharField(unique=True)
    name = models.CharField()
    exchange = models.CharField()
    type = models.CharField(choices=TYPE_CHOICES)
    currency = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
    country = models.ForeignKey(Currency, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField(auto_now=True)


class StockTimeSeriesData(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    date = models.DateField()
