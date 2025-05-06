from api_portal_jota.models import UserSchema
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: UserSchema):
        token = super().get_token(user)

        token["username"] = user.username
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user_id"] = self.user.id
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["role"] = self.user.get_role_display()
        data["id_user_plan"] = self.user.user_plan.id
        data["plan"] = self.user.user_plan.get_plan_display()

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
