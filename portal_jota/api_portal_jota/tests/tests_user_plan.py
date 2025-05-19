from django.urls import include, path
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from ..enums.vertical_enum import VerticalEnum
from .aux_funcs import create_user


class TestUserPlan(APITestCase, URLPatternsTestCase):
    urlpatterns = (
        path("api/", include("api_portal_jota.urls")),
    )

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")
        self.base_url = "/api/user-plan/"

    def test_user_plan_cant_be_created_manually(self) -> None:
        user_admin = create_user(UserRoleEnum.ADMIN)

        self.client.force_authenticate(user=user_admin)
        response = self.client.post(self.base_url, {"plan": PlanEnum.JOTA_PRO.label}, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

    def test_user_plan_cant_be_deleted_manually(self) -> None:
        user_admin = create_user(UserRoleEnum.ADMIN)
        user_reader = create_user(UserRoleEnum.READER)
        url = f"{self.base_url}{user_reader.id}/"

        self.client.force_authenticate(user=user_admin)
        response = self.client.delete(url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

    def test_user_plan_cant_be_updated_from_user_reader(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        updates = {"plan": PlanEnum.JOTA_PRO.label}
        url = f"{self.base_url}{user_reader.id}/"

        self.client.force_authenticate(user=user_reader)
        response = self.client.patch(url, updates, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_plan_cant_be_updated_from_user_editor(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        user_editor = create_user(UserRoleEnum.EDITOR)
        updates = {"plan": PlanEnum.JOTA_PRO.label}
        url = f"{self.base_url}{user_reader.id}/"

        self.client.force_authenticate(user=user_editor)
        response = self.client.patch(url, updates, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_plan_can_be_updated_from_user_admin_success(self) -> None:
        user_reader = create_user(UserRoleEnum.READER)
        user_admin = create_user(UserRoleEnum.ADMIN)
        plan_id = user_reader.user_plan.id
        url = f"{self.base_url}{plan_id}/"
        plan_updates = {
            "plan": PlanEnum.JOTA_PRO.label,
            "verticais": [VerticalEnum.PODER.label, VerticalEnum.SAUDE.label],
        }

        self.client.force_authenticate(user=user_admin)
        response = self.client.patch(url, plan_updates, format="json")

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        response_data = response.data
        self.assertEqual(response_data["plan"], PlanEnum.JOTA_PRO.label, response_data)
        self.assertEqual(response_data["verticais"], plan_updates["verticais"], response_data)

        user_reader.refresh_from_db()
        self.assertEqual(user_reader.user_plan.plan, PlanEnum.JOTA_PRO)
        self.assertEqual([v.name for v in user_reader.user_plan.verticais.all()], plan_updates["verticais"])

    def test_user_reader_can_list_only_his_user_plan(self) -> None:
        user_reader = [create_user(UserRoleEnum.READER) for _ in range(2)][0]

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(self.base_url)

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
        user_editor = create_user(UserRoleEnum.EDITOR)

        self.client.force_authenticate(user=user_editor)
        response = self.client.get(self.base_url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_all_user_plans_can_be_listed_from_user_admin(self) -> None:
        total_plans = 5
        user_admin = create_user(UserRoleEnum.ADMIN)
        [create_user(UserRoleEnum.READER) for _ in range(total_plans)]

        self.client.force_authenticate(user=user_admin)
        response = self.client.get(self.base_url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        user_list = response.data
        self.assertEqual(len(user_list), total_plans, user_list)
