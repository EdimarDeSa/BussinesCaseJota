from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.user_role_enum import UserRoleEnum
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..serializers.user_editor_serializer import UserEditorSerializer
from ..views.user_editor_view import UserEditorViewSet

PASSWORD = "P@s5W0rd"


class TestUserEditor(TestCase):
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

    def test_user_creation_success(self):
        user_adm = UserAdminSerializer().create(
            {"username": self.faker.user_name(), "email": self.faker.email(), "password": PASSWORD}
        )

        request = self.factory.post(self.base_url, self.user_1_data, format="json")

        force_authenticate(request, user=user_adm)

        response = self.view(request, pk=str(user_adm.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 201)

        user = response.data

        self.assertEqual(user["email"], self.user_1_data["email"])
        self.assertEqual(user["role"], UserRoleEnum.EDITOR.label)
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
        self.assertEqual(user_data["role"], UserRoleEnum.EDITOR.label)

    def test_get_user_list_from_editor_user(self):
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

        self.assertEqual(len(user_list), 1)

        user_data = user_list[0]

        self.assertEqual(user_data["email"], self.user_1_data["email"])
        self.assertEqual(user_data["role"], UserRoleEnum.EDITOR.label)

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

        self.assertEqual(len(user_list), 2)

    def test_user_1_cant_update_user_2(self):
        user_1 = self.user_serializer.create(self.user_1_data)
        user_2 = self.user_serializer.create(self.user_2_data)

        url = f"{self.base_url}{user_2.id}/"

        request = self.factory.put(
            url,
            self.user_updates,
            format="json",
        )

        force_authenticate(request, user=user_1)

        response = self.view(request, pk=str(user_2.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 404)
