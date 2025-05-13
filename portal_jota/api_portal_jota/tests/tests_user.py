from typing import Optional

from django.urls import include, path
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from .aux_funcs import create_user, generate_user_data


class TestUser(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("api/", include("api_portal_jota.urls")),
    ]

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")
        self.base_url = "/api/user/"

    def test_create_user_reader_success(self) -> None:
        """Aqui só testamos o user reader pois a atualização do plano para pro é feita em UserPlanView"""
        user_data = generate_user_data(UserRoleEnum.READER)

        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_201_CREATED, response_data)
        self.assertEqual(response_data["email"], user_data["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.READER.label, response_data)
        self.assertEqual(response_data["plan"], PlanEnum.JOTA_INFO.label, response_data)

    def test_create_user_editor_success(self) -> None:
        admin = create_user(UserRoleEnum.ADMIN)
        user_data = generate_user_data(UserRoleEnum.EDITOR)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_201_CREATED, response_data)
        self.assertEqual(response_data["email"], user_data["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.EDITOR.label, response_data)
        self.assertNotIn("plan", response_data)
        self.assertNotIn("plan_id", response_data)

    def test_create_user_admin_success(self) -> None:
        admin = create_user(UserRoleEnum.ADMIN)
        user_data = generate_user_data(UserRoleEnum.ADMIN)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_201_CREATED, response_data)
        self.assertEqual(response_data["email"], user_data["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.ADMIN.label, response_data)
        self.assertNotIn("plan", response_data)
        self.assertNotIn("plan_id", response_data)

    def test_undefined_user_cant_create_user_editor(self) -> None:
        user_data = generate_user_data(UserRoleEnum.EDITOR)

        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_undefined_user_cant_create_user_admin(self) -> None:
        user_data = generate_user_data(UserRoleEnum.ADMIN)

        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_reader_cant_create_user_editor(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        user_data = generate_user_data(UserRoleEnum.EDITOR)

        self.client.force_authenticate(user_reader)
        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_reader_cant_create_user_admin(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        user_data = generate_user_data(UserRoleEnum.ADMIN)

        self.client.force_authenticate(user_reader)
        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_editor_cant_create_user_admin(self) -> None:
        user_editor = create_user(UserRoleEnum.EDITOR)
        user_data = generate_user_data(UserRoleEnum.ADMIN)

        self.client.force_authenticate(user_editor)
        response = self.client.post(self.base_url, user_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_undefined_cant_update_user_reader(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        user_data = generate_user_data(UserRoleEnum.READER)
        url = self.base_url + f"{user_reader.id}/"

        self.client.force_authenticate(user_reader)
        response = self.client.patch(url, user_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_reader_put_updates_success(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        updates = generate_user_data()
        updates.pop("role")
        url = self.base_url + f"{user_reader.id}/"

        self.client.force_authenticate(user_reader)
        response = self.client.put(url, updates, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response_data["email"], updates["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.READER.label, response_data)
        self.assertEqual(response_data["plan"], PlanEnum.JOTA_INFO.label, response_data)

    def test_user_reader_path_updates_success(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        updates = {"email": self.faker.email()}
        url = self.base_url + f"{user_reader.id}/"

        self.client.force_authenticate(user_reader)
        response = self.client.patch(url, updates, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response_data["email"], updates["email"], response_data)

    def test_user_editor_put_updates_success(self) -> None:
        user_editor = create_user(UserRoleEnum.EDITOR)
        updates = generate_user_data()
        updates.pop("role")
        url = self.base_url + f"{user_editor.id}/"

        self.client.force_authenticate(user_editor)
        response = self.client.put(url, updates, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response_data["email"], updates["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.EDITOR.label, response_data)
        self.assertNotIn("plan", response_data)
        self.assertNotIn("plan_id", response_data)

    def test_user_editor_patch_updates_success(self) -> None:
        user_editor = create_user(UserRoleEnum.EDITOR)
        updates = {"email": self.faker.email()}
        url = self.base_url + f"{user_editor.id}/"

        self.client.force_authenticate(user_editor)
        response = self.client.patch(url, updates, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response_data["email"], updates["email"], response_data)

    def test_user_admin_put_updates_success(self) -> None:
        user_admin = create_user(UserRoleEnum.ADMIN)
        updates = generate_user_data(UserRoleEnum.ADMIN)
        url = self.base_url + f"{user_admin.id}/"

        self.client.force_authenticate(user_admin)
        response = self.client.put(url, updates, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response_data["email"], updates["email"], response_data)
        self.assertEqual(response_data["role"], UserRoleEnum.ADMIN.label, response_data)
        self.assertNotIn("plan", response_data)
        self.assertNotIn("plan_id", response_data)

    def test_user_admin_patch_updates_success(self) -> None:
        user_admin = create_user(UserRoleEnum.ADMIN)
        updates = {"email": self.faker.email()}
        url = self.base_url + f"{user_admin.id}/"

        self.client.force_authenticate(user_admin)
        response = self.client.patch(url, updates, format="json")

        status_code = response.status_code
        response_data = response.data

        self.assertEqual(status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response_data["email"], updates["email"], response_data)

    def test_user_reader_cant_update_roles(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        updates = generate_user_data(UserRoleEnum.ADMIN)
        url = self.base_url + f"{user_reader.id}/"

        self.client.force_authenticate(user_reader)
        response = self.client.patch(url, updates, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

        updates = {"role": UserRoleEnum.ADMIN}
        response = self.client.put(url, updates, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_editor_cant_update_roles(self) -> None:
        user_editor = create_user(UserRoleEnum.EDITOR)
        updates = generate_user_data(UserRoleEnum.ADMIN)
        url = self.base_url + f"{user_editor.id}/"

        self.client.force_authenticate(user_editor)
        response = self.client.patch(url, updates, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

        updates = {"role": UserRoleEnum.ADMIN}
        response = self.client.put(url, updates, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)
