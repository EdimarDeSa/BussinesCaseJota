from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..serializers.user_editor_serializer import UserEditorSerializer
from ..views.user_editor_view import UserEditorViewSet

PASSWORD = "P@s5W0rd"


class TestUserEditor(TestCase):

    def _generate_user_data(self) -> dict[str, str]:
        return {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

    def _create_user_editor(self) -> UserSchema:
        return self.user_serializer.create(self._generate_user_data())

    def _create_user_admin(self) -> UserSchema:
        return self.admin_serializer.create(self._generate_user_data())

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")

        self.base_url = "/api/editor-user/"
        self.factory = APIRequestFactory()
        self.view = UserEditorViewSet.as_view(
            {
                "post": "create",
                "get": "list",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )
        self.user_serializer = UserEditorSerializer()
        self.admin_serializer = UserAdminSerializer()

    def test_create_user_editor_success(self) -> None:
        user_adm = self._create_user_admin()
        user_editor_data = self._generate_user_data()

        request = self.factory.post(self.base_url, user_editor_data, format="json")

        force_authenticate(request, user=user_adm)

        response = self.view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 201, response.data)

        response_data = response.data
        self.assertEqual(response_data["email"], user_editor_data["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.EDITOR.label, response_data)
        self.assertNotIn("plan", response_data)

    def test_user_update(self) -> None:
        user = self._create_user_editor()
        url = f"{self.base_url}{user.id}/"
        updates = self._generate_user_data()

        request = self.factory.put(url, updates, format="json")

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(response_data["email"], updates["email"], response_data)

    def test_update_user_editor_email_success(self) -> None:
        user = self._create_user_editor()
        url = f"{self.base_url}{user.id}/"
        update = {"email": self.faker.email()}

        request = self.factory.patch(url, update, format="json")

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(response_data["email"], update["email"], response_data)

    def test_delete_user_editor_success(self) -> None:
        user = self._create_user_editor()
        url = f"{self.base_url}{user.id}/"

        request = self.factory.delete(url)

        force_authenticate(request, user=user)

        response = self.view(request, pk=str(user.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 204, response.data)

    def test_get_user_editor_info_success(self) -> None:
        user = self._create_user_editor()
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
        self.assertEqual(response_data["role"], UserRoleEnum.EDITOR.label, response_data)

    def test_list_users_from_editor_user_success(self) -> None:
        user = [self._create_user_editor() for _ in range(5)][0]
        url = f"{self.base_url}"

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

    def test_list_users_from_admin_user_success(self) -> None:
        total_usuarios = 5
        user_admin = self._create_user_admin()
        [self._create_user_editor() for _ in range(total_usuarios)]
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
        user_1 = self._create_user_editor()
        user_2 = self._create_user_editor()

        url = f"{self.base_url}{user_2.id}/"

        request = self.factory.put(url, self._generate_user_data(), format="json")

        force_authenticate(request, user=user_1)

        response = self.view(request, pk=str(user_2.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 404, response.data)
