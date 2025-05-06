from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.user_role_enum import UserRoleEnum
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..views.user_admin_view import UserAdminViewSet

PASSWORD = "P@s5W0rd"


class TestUserAdmin(TestCase):
    def setUp(self):
        self.faker = Faker("pt_BR")
        self.user_1_data = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

        self.user_2_data = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

        self.user_updates = {
            "email": self.faker.email(),
            "username": self.faker.user_name(),
            "password": self.faker.password(length=12),
        }

        self.base_url = "/api/admin-user/"
        self.factory = APIRequestFactory()
        self.view = UserAdminViewSet.as_view(
            {
                "post": "create",
                "get": "list",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )
        self.user_serializer = UserAdminSerializer()

    def test_user_creation_success(self):
        user_admin = self.user_serializer.create(
            {"username": self.faker.user_name(), "email": self.faker.email(), "password": PASSWORD}
        )

        request = self.factory.post(self.base_url, self.user_1_data, format="json")

        force_authenticate(request, user=user_admin)

        response = self.view(request, pk=str(user_admin.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 201)

        user = response.data

        self.assertEqual(user["email"], self.user_1_data["email"])
        self.assertEqual(user["role"], UserRoleEnum.ADMIN.label)
        self.assertNotIn("plan", user)

    def test_user_update(self):
        user = self.user_serializer.create(self.user_1_data)

        url = f"{self.base_url}{user.id}/"

        request = self.factory.put(
            url,
            self.user_updates,
            format="json",
        )

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 200)

        user_data = response.data

        self.assertEqual(user_data["email"], self.user_updates["email"])

    def test_user_partial_update(self):
        user = self.user_serializer.create(self.user_1_data)

        url = f"{self.base_url}{user.id}/"

        request = self.factory.patch(
            url,
            {"email": self.user_updates["email"]},
            format="json",
        )

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 200)

        user_data = response.data

        self.assertEqual(user_data["email"], self.user_updates["email"])

    def test_user_delete(self):
        user = self.user_serializer.create(self.user_1_data)

        url = f"{self.base_url}{user.id}/"

        request = self.factory.delete(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 204)

    def test_get_user_data(self):
        user = self.user_serializer.create(self.user_1_data)

        url = f"{self.base_url}{user.id}/"

        request = self.factory.get(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 200)

        user_list = response.data

        self.assertEqual(len(user_list), 1)

        user_data = user_list[0]

        self.assertEqual(user_data["email"], self.user_1_data["email"])
        self.assertEqual(user_data["role"], UserRoleEnum.ADMIN.label)

    def test_get_user_list_from_admin_user(self):
        user_1 = self.user_serializer.create(self.user_1_data)
        self.user_serializer.create(self.user_2_data)

        url = f"{self.base_url}"

        request = self.factory.get(url)

        force_authenticate(request, user=user_1)

        response = self.view(request, pk=str(user_1.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 200)

        user_list = response.data

        self.assertEqual(len(user_list), 2)

    def test_get_user_list_from_admin_user(self):
        adm_serializer = UserAdminSerializer()
        user_adm = adm_serializer.create(
            {"username": self.faker.user_name(), "email": self.faker.email(), "password": PASSWORD}
        )

        self.user_serializer.create(self.user_1_data)
        self.user_serializer.create(self.user_2_data)

        url = f"{self.base_url}"

        request = self.factory.get(url)

        force_authenticate(request, user=user_adm)

        response = self.view(request, pk=str(user_adm.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 200)

        user_list = response.data

        self.assertEqual(len(user_list), 3)
