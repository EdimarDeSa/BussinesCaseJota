from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..models import UserSchema


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: UserSchema):
        token = super().get_token(user)

        token["username"] = user.username
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs) -> dict:
        data = super().validate(attrs)

        data["user_id"] = self.user.id
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["role"] = self.user.get_role_display()
        data["id_user_plan"] = self.user.user_plan.id
        data["plan"] = self.user.user_plan.get_plan_display()

        return data
