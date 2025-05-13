from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..enums.user_role_enum import UserRoleEnum


class TokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)

        data["user_id"] = str(self.user.id)
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["role"] = self.user.get_role_display()

        if self.user.role == UserRoleEnum.READER:
            data["plan_id"] = str(self.user.user_plan.id)
            data["plan"] = self.user.user_plan.get_plan_display()
            data["verticais"] = [v.name for v in self.user.user_plan.verticais.all()]

        return data
