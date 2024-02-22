import factory.django
from django.test import Client, TestCase

from stockApp.models import CustomUser


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "stockApp.CustomUser"

    first_name = factory.Sequence(lambda n: "john%s" % n)
    last_name = factory.Sequence(lambda n: "brown%s" % n)
    email = factory.LazyAttribute(lambda u: f"{u.first_name}.{u.last_name}@example.org")
    password = factory.django.Password("password")


class TestUsersListEndpoint(TestCase):
    def setUp(self):
        self.c = Client()
        CustomUser.objects.create_superuser(
            email="admin@example.com",
            first_name="admin",
            last_name="admin",
            password="admin",
        )

    def test_get_users_list(self):
        response = self.c.get("/users/")
        self.assertEquals(response.status_code, 200)

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
        user: CustomUser = UserFactory.create()

        response = self.c.get(f"/users/{user.pk}")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data["id"], user.pk)

    def test_get_user_by_wrong_id(self):
        response = self.c.get("/users/0")

        self.assertEquals(response.status_code, 404)

    def test_patch_user(self):
        user: CustomUser = UserFactory.create()
        user_json = {
            "first_name": "Sirius",
            "last_name": "Black",
            "email": "sirius.black@example.com",
        }

        self.assertNotEquals(user_json.get("email"), user.email)

        response = self.c.patch(
            f"/users/{user.pk}", user_json, content_type="application/json"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("email"), user_json.get("email"))

    def test_patch_user_with_part_data(self):
        user: CustomUser = UserFactory.create()
        user_json = {"first_name": "George"}

        self.assertNotEquals(user_json.get("first_name"), user.first_name)

        response = self.c.patch(
            f"/users/{user.pk}", user_json, content_type="application/json"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("first_name"), user_json.get("first_name"))

    def test_patch_user_without_unique_email(self):
        user1: CustomUser = UserFactory.create()
        user2: CustomUser = UserFactory.create()

        user_json = {"email": user2.email}

        self.assertNotEquals(user1.email, user2.email)

        response = self.c.patch(
            f"/users/{user1.pk}", user_json, content_type="application/json"
        )

        self.assertEquals(response.status_code, 400)
