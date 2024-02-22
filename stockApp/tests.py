import factory.django
from django.test import Client, TestCase

from stockApp.models import CustomUser


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "stockApp.CustomUser"


class TestUsersListEndpoint(TestCase):
    def setUp(self):
        self.c = Client()
        CustomUser.objects.create_superuser(email="admin@example.com", first_name="admin", last_name="admin", password="admin")

    def test_get_users_list(self):
        response = self.c.get("/users/")
        self.assertEquals(response.status_code, 200)

    def test_create_new_user(self):
        user_json = {
            "first_name": "Harry",
            "last_name": "Potter",
            "email": "harry.potter@example.com",
            "password": "Harry-Potter"
        }

        response = self.c.post("/users/", user_json)

        self.assertEqual(response.status_code, 201)
        self.assertEquals(response.data["first_name"], "Harry")

    def test_create_user_without_data(self):
        user_json = {
            "first_name": "Scorpius",
            "last_name": "Malfoy",
            "password": "Scorpius-Malfoy"
        }

        response = self.c.post("/users/", user_json)

        self.assertEqual(response.status_code, 400)

    def test_create_user_with_non_unique_email(self):
        user: CustomUser = UserFactory.create()
        user_json = {
            "first_name": "Rubeus",
            "last_name": "Hagrid",
            "email": user.email,
            "password": "Rubeus-Hagrid"
        }

        response = self.c.post("/users/", user_json)

        self.assertEqual(response.status_code, 400)

    def test_get_user_by_id(self):
        user: CustomUser = UserFactory.create()

        response = self.c.get(f"/users/{user.pk}")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data["id"], user.pk)

    def test_get_user_by_wrong_id(self):
        response = self.c.get("/users/0")

        self.assertEquals(response.status_code, 404)