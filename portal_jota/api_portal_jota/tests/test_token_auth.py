from django.test import Client, TestCase
from faker import Faker
from rest_framework import status

from ..enums.user_role_enum import UserRoleEnum
from ..enums.vertical_enum import VerticalEnum
from ..models.user_schema import UserSchema
from ..serializers.token_serializer import TokenSerializer
from ..serializers.user_serializer import UserSerializer
from ..tests.aux_funcs import PASSWORD, create_user
from ..views.token_view import TokenView


class TestTokenAuth(TestCase, Client):
    def setUp(self) -> None:
        self.faker = Faker("pt_BR")

        self.get_token_url = "/api/token/"
        self.refresh_url = "/api/token/refresh/"
        self.verify_url = "/api/token/verify/"

    def test_login_success(self) -> None:
        user = create_user(UserRoleEnum.READER)
        login_data = {
            "username": user.username,
            "password": PASSWORD,
        }

        response = self.client.post(self.get_token_url, login_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        response_data = response.data
        response_must_be = {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.label,
            "plan_id": str(user.user_plan.id),
            "plan": user.user_plan.get_plan_display(),
            "verticais": [v.name for v in user.user_plan.verticais.all()],
            "access": response_data["access"],
            "refresh": response_data["refresh"],
        }

        self.assertDictEqual(response_data, response_must_be, response_data)

    def test_login_fail_username(self) -> None:
        create_user(UserRoleEnum.READER)
        login_data = {
            "username": self.faker.user_name(),
            "password": PASSWORD,
        }

        response = self.client.post(self.get_token_url, login_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_login_fail_passwword(self) -> None:
        user = create_user(UserRoleEnum.READER)
        login_data = {
            "username": user.username,
            "password": self.faker.password(),
        }

        response = self.client.post(self.get_token_url, login_data, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_refresh_token(self) -> None:
        user = create_user(UserRoleEnum.READER)
        login_data = {
            "username": user.username,
            "password": PASSWORD,
        }

        response = self.client.post(self.get_token_url, login_data, format="json")
        refresh_token = response.data["refresh"]

        response = self.client.post(self.refresh_url, {"refresh": refresh_token}, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)

    def test_token_verify(self) -> None:
        user = create_user(UserRoleEnum.READER)
        login_data = {
            "username": user.username,
            "password": PASSWORD,
        }

        response = self.client.post(self.get_token_url, login_data, format="json")
        access_token = response.data["access"]

        response = self.client.post(self.verify_url, {"token": access_token}, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        self.assertEqual(1, 1)
