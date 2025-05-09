from os import access

from django.test import RequestFactory, TestCase
from faker import Faker
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from ..models.user_schema import UserSchema
from ..serializers.token_serializer import TokenSerializer
from ..serializers.user_reader_serializer import UserReaderSerializer
from ..views.token_view import TokenView

PASSWORD = "P@s5W0rd"


class TestTokenAuth(TestCase):
    def _create_user(self, user_data: dict[str, str]) -> UserSchema:
        return self.reader_serializer.create(user_data)

    def _generate_user_data(self) -> dict[str, str]:
        return {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")

        self.base_url = "/api/token/"
        self.refresh_url = "/api/token/refresh/"
        self.verify_url = "/api/token/verify/"

        self.factory = RequestFactory()

        self.token_view = TokenView.as_view()
        self.refresh_view = TokenRefreshView.as_view()
        self.verify_view = TokenVerifyView.as_view()

        self.reader_serializer = UserReaderSerializer()
        self.token_serializer = TokenSerializer

    def test_login_success(self) -> None:
        user_data = self._generate_user_data()
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        user = self._create_user(user_data)

        request = self.factory.post(self.base_url, login_data, format="json")

        response = self.token_view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

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
        user_data = self._generate_user_data()
        login_data = {
            "username": self.faker.user_name(),
            "password": user_data["password"],
        }
        self._create_user(user_data)

        request = self.factory.post(self.base_url, login_data, format="json")

        response = self.token_view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 401, response.data)

    def test_login_fail_passwword(self) -> None:
        user_data = self._generate_user_data()
        login_data = {
            "username": user_data["username"],
            "password": self.faker.password(),
        }
        self._create_user(user_data)

        request = self.factory.post(self.base_url, login_data, format="json")

        response = self.token_view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 401, response.data)

    def test_refresh_token(self) -> None:
        user_data = self._generate_user_data()
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        self._create_user(user_data)
        serializer = self.token_serializer(data=login_data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]

        request = self.factory.post(self.refresh_url, {"refresh": refresh_token}, format="json")

        response = self.refresh_view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)
        self.assertIn("access", response.data)

    def test_token_verify(self) -> None:
        user_data = self._generate_user_data()
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        self._create_user(user_data)
        serializer = self.token_serializer(data=login_data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data["access"]

        request = self.factory.post(self.verify_url, {"token": access_token}, format="json")

        response = self.verify_view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        self.assertEqual(1, 1)
