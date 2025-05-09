from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..views.user_admin_view import UserAdminViewSet

PASSWORD = "P@s5W0rd"


class TestUserAdmin(TestCase):

    def _generate_user_data(self) -> dict[str, str]:

        return {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

    def _create_user(self) -> UserSchema:
        return self.user_serializer.create(self._generate_user_data())

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")
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

    def test_create_user_admin_success(self) -> None:
        user_admin = self._create_user()
        new_user_data = self._generate_user_data()

        request = self.factory.post(self.base_url, new_user_data, format="json")

        force_authenticate(request, user=user_admin)

        response = self.view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 201, response.data)

        response_data = response.data

        self.assertEqual(response_data["email"], new_user_data["email"])
        self.assertEqual(response_data["role"], UserRoleEnum.ADMIN.label)
        self.assertNotIn("plan", response_data)

    def test_update_user_admin_success(self) -> None:
        user = self._create_user()
        updates = self._generate_user_data()
        url = f"{self.base_url}{user.id}/"

        request = self.factory.put(url, updates, format="json")

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(response_data["email"], updates["email"], response_data)

    def test_update_user_admin_email_success(self) -> None:
        user = self._create_user()
        update = {"email": self.faker.email()}
        url = f"{self.base_url}{user.id}/"

        request = self.factory.patch(url, update, format="json")

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(response_data["email"], update["email"], response_data)

    def test_delete_user_admin_success(self) -> None:
        user = self._create_user()
        url = f"{self.base_url}{user.id}/"

        request = self.factory.delete(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 204, response.data)

    def test_get_user_admin_info_success(self) -> None:
        user = self._create_user()
        url = f"{self.base_url}{user.id}/"

        request = self.factory.get(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        user_list = response.data
        self.assertEqual(len(user_list), 1, user_list)

        response_data = user_list[0]
        self.assertEqual(response_data["email"], user.email, response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.ADMIN.label, response_data)

    def test_list_users_from_admin_user_success(self) -> None:
        total_usuarios = 5
        user = [self._create_user() for _ in range(total_usuarios)][0]

        request = self.factory.get(self.base_url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        user_list = response.data
        self.assertEqual(len(user_list), total_usuarios, user_list)
