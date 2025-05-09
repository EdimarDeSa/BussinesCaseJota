from typing import Any

from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from ..models.user_schema import UserSchema
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..serializers.user_reader_serializer import UserReaderSerializer
from ..views.user_reader_view import UserReaderViewSet

PASSWORD = "P@s5W0rd"


class TestUserReader(TestCase):
    def _create_user(self, serializer: Any) -> UserSchema:
        return serializer.create(self._generate_user_data())

    def _create_user_admin(self) -> UserSchema:
        return self.admin_serializer.create(self._generate_user_data())

    def _create_user_reader(self) -> UserSchema:
        return self.reader_serializer.create(self._generate_user_data())

    def _generate_user_data(self) -> dict[str, str]:
        return {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")
        self.base_url = "/api/reader-user/"
        self.factory = APIRequestFactory()
        self.view = UserReaderViewSet.as_view(
            {
                "post": "create",
                "get": "list",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

        self.reader_serializer = UserReaderSerializer()
        self.admin_serializer = UserAdminSerializer()

    def test_create_user_reader_success(self) -> None:
        user_data = self._generate_user_data()
        request = self.factory.post(self.base_url, user_data, format="json")

        response = self.view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 201, response.data)

        response_data = response.data

        self.assertEqual(response_data["email"], user_data["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.READER.label, response_data)
        self.assertEqual(response_data["plan"], PlanEnum.JOTA_INFO.label, response_data)

    def test_update_user_reader_success(self) -> None:
        user = self._create_user_reader()
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

    def test_update_user_reader_email_success(self) -> None:
        user = self._create_user_reader()
        update = {"email": self.faker.email()}
        url = f"{self.base_url}{user.id}/"

        request = self.factory.patch(url, update, format="json")

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        user_data = response.data
        self.assertEqual(user_data["email"], update["email"], user_data)

    def test_delete_user_reader_success(self) -> None:
        user = self._create_user_reader()
        url = f"{self.base_url}{user.id}/"

        request = self.factory.delete(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 204, response.data)

    def test_get_user_reader_info_success(self) -> None:
        user = self._create_user_reader()
        url = f"{self.base_url}{user.id}/"

        request = self.factory.get(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        user_list = response.data
        self.assertEqual(len(user_list), 1, user_list)

        user_data = user_list[0]
        self.assertEqual(user_data["email"], user.email, user_data)
        self.assertEqual(user_data["role"], UserRoleEnum.READER.label, user_data)
        self.assertEqual(user_data["plan"], PlanEnum.JOTA_INFO.label, user_data)

    def test_list_users_from_reader_user_success(self) -> None:
        user = [self._create_user_reader() for _ in range(3)][0]
        url = f"{self.base_url}"

        request = self.factory.get(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        user_list = response.data
        self.assertEqual(len(user_list), 1, user_list)

        user_data = user_list[0]
        self.assertEqual(user_data["email"], user.email, user_data)
        self.assertEqual(user_data["role"], UserRoleEnum.READER.label, user_data)
        self.assertEqual(user_data["plan"], PlanEnum.JOTA_INFO.label, user_data)

    def test_list_users_from_admin_user_success(self) -> None:
        total_usuarios = 5
        user_admin = self._create_user_admin()
        [self._create_user_reader() for _ in range(total_usuarios)]
        url = f"{self.base_url}"

        request = self.factory.get(url)

        force_authenticate(request, user=user_admin)

        response = self.view(request, pk=str(user_admin.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(len(response_data), total_usuarios, response_data)

    def test_user_1_cant_update_user_2(self) -> None:
        user_1 = self._create_user_reader()
        user_2 = self._create_user_reader()
        updates = self._generate_user_data()
        url = f"{self.base_url}{user_2.id}/"

        request = self.factory.put(url, updates, format="json")

        force_authenticate(request, user=user_1)

        response = self.view(request, pk=str(user_2.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 404, response.data)
