from datetime import datetime
from unittest.mock import patch, MagicMock

import factory.django
from django.conf import settings
from django.test import Client
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from stockApp.models import CustomUser, Country, Currency
from stockApp.models import StockData, StockTimeSeriesData
from stockApp.tasks import get_stock_time_series


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "stockApp.CustomUser"

    first_name = factory.Sequence(lambda n: "john%s" % n)
    last_name = factory.Sequence(lambda n: "brown%s" % n)
    email = factory.LazyAttribute(lambda u: f"{u.first_name}.{u.last_name}@example.org")
    password = factory.django.Password("password")


class TestUsersEndpoint(TestCase):
    def setUp(self):
        self.c = Client()
        self.admin_user: CustomUser = CustomUser.objects.create_superuser(
            email="admin@example.com",
            first_name="admin",
            last_name="admin",
            password="admin",
        )

        self.no_admin_user: CustomUser = CustomUser.objects.create_user(
            email="noadmin@example.com",
            first_name="noadmin",
            last_name="noadmin",
            password="noadmin",
        )

        self.admin_token = AccessToken.for_user(self.admin_user)
        self.no_admin_token = AccessToken.for_user(self.no_admin_user)

    def test_get_users_list(self):
        response = self.c.get(
            "/users/", headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEquals(response.status_code, 200)

    def test_get_users_list_without_admin(self):
        response = self.c.get(
            "/users/", headers={"Authorization": f"Bearer {self.no_admin_token}"}
        )
        self.assertEquals(response.status_code, 403)

    def test_get_users_list_without_token(self):
        response = self.c.get("/users/")
        self.assertEquals(response.status_code, 401)

    def test_create_new_user(self):
        user_json = {
            "first_name": "Harry",
            "last_name": "Potter",
            "email": "harry.potter@example.com",
            "password": "Harry-Potter",
        }

        response = self.c.post("/users/", user_json)

        self.assertEqual(response.status_code, 201)
        self.assertEquals(response.data["first_name"], "Harry")

    def test_create_user_without_data(self):
        user_json = {
            "first_name": "Scorpius",
            "last_name": "Malfoy",
            "password": "Scorpius-Malfoy",
        }

        response = self.c.post("/users/", user_json)

        self.assertEqual(response.status_code, 400)

    def test_create_user_with_non_unique_email(self):
        user: CustomUser = UserFactory.create()
        user_json = {
            "first_name": "Rubeus",
            "last_name": "Hagrid",
            "email": user.email,
            "password": "Rubeus-Hagrid",
        }

        response = self.c.post("/users/", user_json)

        self.assertEqual(response.status_code, 400)

    def test_get_user_by_id(self):
        response = self.c.get(
            f"/users/{self.admin_user.pk}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data["id"], self.admin_user.pk)

    def test_get_user_by_wrong_id(self):
        response = self.c.get("/users/0")

        self.assertEquals(response.status_code, 404)

    def test_get_user_without_token(self):
        response = self.c.get(f"/users/{self.admin_user.pk}")

        self.assertEquals(response.status_code, 401)

    def test_get_user_with_wrong_token(self):
        response = self.c.get(
            f"/users/{self.no_admin_user.pk}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        self.assertEquals(response.status_code, 403)

    def test_patch_user(self):
        user: CustomUser = UserFactory.create()
        access_token = AccessToken.for_user(user)
        user_json = {
            "first_name": "Sirius",
            "last_name": "Black",
            "email": "sirius.black@example.com",
            "password": "SiriusBlack",
        }
        old_password = user.password

        self.assertNotEquals(user_json.get("email"), user.email)

        response = self.c.patch(
            f"/users/{user.pk}",
            user_json,
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("email"), user_json.get("email"))

        user_from_db: CustomUser = CustomUser.objects.get_by_natural_key(
            user_json.get("email")
        )

        self.assertEquals(user_from_db.password, old_password)

    def test_patch_user_with_part_data(self):
        user: CustomUser = UserFactory.create()
        user_json = {"first_name": "George"}
        access_token = AccessToken.for_user(user)

        self.assertNotEquals(user_json.get("first_name"), user.first_name)

        response = self.c.patch(
            f"/users/{user.pk}",
            user_json,
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("first_name"), user_json.get("first_name"))

    def test_patch_user_without_unique_email(self):
        user1: CustomUser = UserFactory.create()
        user2: CustomUser = UserFactory.create()
        access_token = AccessToken.for_user(user1)
        user_json = {"email": user2.email}

        self.assertNotEquals(user1.email, user2.email)

        response = self.c.patch(
            f"/users/{user1.pk}",
            user_json,
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEquals(response.status_code, 400)

    def test_patch_user_without_token(self):
        response = self.c.patch(f"/users/{self.admin_user.pk}")

        self.assertEquals(response.status_code, 401)

    def test_patch_user_with_wrong_token(self):
        response = self.c.patch(
            f"/users/{self.no_admin_user.pk}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        self.assertEquals(response.status_code, 403)

    def test_delete_user(self):
        user: CustomUser = UserFactory.create()
        access_token = AccessToken.for_user(user)

        response = self.c.delete(
            f"/users/{user.pk}", headers={"Authorization": f"Bearer {access_token}"}
        )

        self.assertEquals(response.status_code, 204)

    def test_delete_non_existing_user(self):
        response = self.c.delete("/users/0")

        self.assertEquals(response.status_code, 404)

    def test_delete_user_without_token(self):
        response = self.c.delete(f"/users/{self.admin_user.pk}")

        self.assertEquals(response.status_code, 401)

    def test_delete_user_with_wrong_token(self):
        response = self.c.delete(
            f"/users/{self.no_admin_user.pk}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        self.assertEquals(response.status_code, 403)


class TestGetStockTimeSeries(TestCase):
    def setUp(self):
        settings.CELERY_TASK_ALWAYS_EAGER = True

        self.country, created = Country.objects.get_or_create(name="United States")
        self.currency, created = Currency.objects.get_or_create(name="USD")
        StockData.objects.get_or_create(
            symbol="AAPL", country=self.country, currency=self.currency
        )

        self.response_result = {
            "values": [
                {
                    "open": 100.0,
                    "high": 110.0,
                    "low": 90.0,
                    "close": 105.0,
                    "volume": 100000,
                    "datetime": "2020-01-01",
                }
            ]
        }

    @patch("stockApp.tasks.requests.get")
    @patch("stockApp.tasks.sleep")
    def test_get_stock_time_series_success(self, mock_sleep, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.response_result
        mock_get.return_value = mock_response

        get_stock_time_series()

        stock_time_series = StockTimeSeriesData.objects.get(stock__symbol="AAPL")
        stock = StockData.objects.get(symbol="AAPL")

        self.assertEqual(stock_time_series.open, 100.0)
        self.assertEqual(
            stock_time_series.date, datetime.strptime("2020-01-01", "%Y-%m-%d").date()
        )
        self.assertEquals(
            stock.last_time_series_update,
            datetime.strptime("2020-01-01", "%Y-%m-%d").date(),
        )
