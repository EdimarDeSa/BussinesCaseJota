from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import UserSchema
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..serializers.user_editor_serializer import UserEditorSerializer
from ..serializers.user_plan_serializer import UserPlanSerializer
from ..serializers.user_reader_serializer import UserReaderSerializer
from ..views.user_plan_view import UserPlanViewSet

PASSWORD = "P@s5W0rd"


class TestUserPlan(TestCase):
    def _create_user(self, serializer) -> UserSchema:
        return serializer.create(self._generate_user_data())

    def _generate_user_data(self):
        return {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

    def setUp(self):
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

        self.user_reader = self._create_user(UserReaderSerializer())

        user_reader_serializers = UserReaderSerializer()
        self.user_readers = [self._create_user(user_reader_serializers) for _ in range(5)]

        self.user_editor = self._create_user(UserEditorSerializer())

        self.user_admin = self._create_user(UserAdminSerializer())

    def test_user_plan_cant_be_created_manually(self):
        request = self.factory.post(self.base_url, {"plan": PlanEnum.JOTA_PRO.label}, format="json")

        force_authenticate(request, user=self.user_admin)

        response = self.view(request, pk=str(self.user_admin.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 405)

    def test_user_plan_cant_be_deleted_manually(self):
        request = self.factory.delete(self.base_url, {"plan": PlanEnum.JOTA_PRO.label}, format="json")

        force_authenticate(request, user=self.user_admin)

        response = self.view(request, pk=str(self.user_admin.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 405)

    def test_user_plan_cant_be_updated_from_user_reader(self):
        request = self.factory.patch(
            self.base_url,
            {"plan": PlanEnum.JOTA_PRO.label},
            format="json",
        )

        force_authenticate(request, user=self.user_reader)

        response = self.view(request, pk=str(self.user_reader.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 403)

    def test_user_plan_cant_be_updated_from_user_editor(self):
        request = self.factory.patch(
            self.base_url,
            {"plan": PlanEnum.JOTA_PRO.label},
            format="json",
        )

        force_authenticate(request, user=self.user_editor)

        response = self.view(request, pk=str(self.user_editor.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 403)
        self.assertTrue(True)

    def test_user_plan_can_be_updated_from_user_admin(self):
        url = f"{self.base_url}{self.user_reader.user_plan.id}/"

        plan_updates = {
            "plan": PlanEnum.JOTA_PRO.value,
            "verticais": [VerticalEnum.PODER.label, VerticalEnum.SAUDE.label],
        }

        request = self.factory.patch(url, plan_updates, format="json")

        force_authenticate(request, user=self.user_admin)

        response = self.view(request, pk=str(self.user_reader.user_plan.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200)

        plan_data = response.data

        self.assertEqual(plan_data["plan"], PlanEnum.JOTA_PRO.label)
        self.assertEqual(plan_data["verticais"], plan_updates["verticais"])

    def test_user_reader_can_list_only_his_user_plan(self):
        request = self.factory.get(self.base_url)

        force_authenticate(request, user=self.user_reader)

        response = self.view(request, pk=str(self.user_reader.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200)

        user_list = response.data

        self.assertEqual(len(user_list), 1)

        user_data = user_list[0]

        self.assertEqual(user_data["id"], str(self.user_reader.user_plan.id))

    def test_user_plan_cant_be_listed_from_user_editor(self):
        request = self.factory.get(self.base_url)

        force_authenticate(request, user=self.user_editor)

        response = self.view(request, pk=str(self.user_editor.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 403)

    def test_all_user_plans_can_be_listed_from_user_admin(self):
        request = self.factory.get(self.base_url)

        force_authenticate(request, user=self.user_admin)

        response = self.view(request, pk=str(self.user_admin.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200)

        user_list = response.data

        self.assertEqual(len(user_list), 6)
