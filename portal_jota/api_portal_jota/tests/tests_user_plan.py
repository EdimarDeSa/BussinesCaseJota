from datetime import datetime, timedelta
from typing import Any

from django.test import TestCase
from django.utils import timezone
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.plan_enum import PlanEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import UserSchema
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..serializers.user_editor_serializer import UserEditorSerializer
from ..serializers.user_plan_serializer import UserPlanSerializer
from ..serializers.user_reader_serializer import UserReaderSerializer
from ..views.user_plan_view import UserPlanViewSet

PASSWORD = "P@s5W0rd"


class TestUserPlan(TestCase):
    def _create_user(self, serializer: Any) -> UserSchema:
        return serializer.create(self._generate_user_data())

    def _generate_user_data(self) -> dict[str, str]:
        return {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

    def _create_user_reader(self) -> UserSchema:
        return self.reader_serializers.create(self._generate_user_data())

    def _create_user_editor(self) -> UserSchema:
        return self.editor_serializers.create(self._generate_user_data())

    def _create_user_admin(self) -> UserSchema:
        return self.admin_serializers.create(self._generate_user_data())

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")

        self.base_url = "/api/user-plan/"
        self.factory = APIRequestFactory()
        self.view = UserPlanViewSet.as_view(
            {
                "get": "list",
                "put": "update",
                "patch": "partial_update",
            }
        )
        self.plan_serializer = UserPlanSerializer()

        self.reader_serializers = UserReaderSerializer()
        self.editor_serializers = UserEditorSerializer()
        self.admin_serializers = UserAdminSerializer()

    def test_user_plan_cant_be_created_manually(self) -> None:
        user_admin = self._create_user_admin()

        request = self.factory.post(self.base_url, {"plan": PlanEnum.JOTA_PRO.label}, format="json")

        force_authenticate(request, user=user_admin)

        response = self.view(request, pk=str(user_admin.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 405, response.data)

    def test_user_plan_cant_be_deleted_manually(self) -> None:
        user_admin = self._create_user_admin()
        user_reader = self._create_user_reader()
        url = f"{self.base_url}{user_reader.id}/"

        request = self.factory.delete(url)

        force_authenticate(request, user=user_admin)

        response = self.view(request, pk=str(user_admin.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 405, response.data)

    def test_user_plan_cant_be_updated_from_user_reader(self) -> None:
        user_reader = self._create_user_reader()
        updates = {"plan": PlanEnum.JOTA_PRO.label}
        url = f"{self.base_url}{user_reader.id}/"

        request = self.factory.patch(url, updates, format="json")

        force_authenticate(request, user=user_reader)

        response = self.view(request, pk=str(user_reader.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 403, response.data)

    def test_user_plan_cant_be_updated_from_user_editor(self) -> None:
        user_reader = self._create_user_reader()
        user_editor = self._create_user_editor()
        updates = {"plan": PlanEnum.JOTA_PRO.label}
        url = f"{self.base_url}{user_reader.id}/"

        request = self.factory.patch(url, updates, format="json")

        force_authenticate(request, user=user_editor)

        response = self.view(request, pk=str(user_reader.user_plan.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 403, response.data)

    def test_user_plan_can_be_updated_from_user_admin_success(self) -> None:
        user_reader = self._create_user_reader()
        user_admin = self._create_user_admin()
        plan_id = user_reader.user_plan.id
        url = f"{self.base_url}{plan_id}/"
        plan_updates = {
            "plan": PlanEnum.JOTA_PRO.label,
            "verticais": [VerticalEnum.PODER.label, VerticalEnum.SAUDE.label],
        }

        request = self.factory.patch(url, plan_updates, format="json")

        force_authenticate(request, user=user_admin)

        response = self.view(request, pk=str(plan_id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(response_data["plan"], PlanEnum.JOTA_PRO.label, response_data)
        self.assertEqual(response_data["verticais"], plan_updates["verticais"], response_data)

        user_reader.refresh_from_db()
        self.assertEqual(user_reader.user_plan.plan, PlanEnum.JOTA_PRO)
        self.assertEqual([v.name for v in user_reader.user_plan.verticais.all()], plan_updates["verticais"])

    def test_user_reader_can_list_only_his_user_plan(self) -> None:
        user_reader = [self._create_user_reader() for _ in range(2)][0]

        request = self.factory.get(self.base_url)

        force_authenticate(request, user=user_reader)

        response = self.view(request, pk=str(user_reader.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(len(response_data), 1, response_data)

        user_data = response_data[0]
        user_reader.refresh_from_db()
        user_data_must_be = {
            "id": str(user_reader.user_plan.id),
            "plan": PlanEnum.JOTA_INFO.label,
            "user_id": str(user_reader.id),
            "user_name": user_reader.username,
            "verticais": [],
            "created_at": user_reader.user_plan.created_at.astimezone().isoformat(),
            "updated_at": user_reader.user_plan.updated_at.astimezone().isoformat(),
        }
        self.assertEqual(user_data, user_data_must_be, user_data)

    def test_user_plan_cant_be_listed_from_user_editor(self) -> None:
        user_editor = self._create_user_editor()

        request = self.factory.get(self.base_url)

        force_authenticate(request, user=user_editor)

        response = self.view(request, pk=str(user_editor.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 403, response.data)

    def test_all_user_plans_can_be_listed_from_user_admin(self) -> None:
        total_plans = 5
        user_admin = self._create_user_admin()
        [self._create_user_reader() for _ in range(total_plans)]

        request = self.factory.get(self.base_url)

        force_authenticate(request, user=user_admin)

        response = self.view(request, pk=str(user_admin.id))
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        user_list = response.data
        self.assertEqual(len(user_list), total_plans, user_list)
