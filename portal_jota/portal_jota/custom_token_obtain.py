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

        user = UserSchema.objects.get(username=attrs["username"])

        data["user_id"] = user.id
        data["username"] = user.username
        data["email"] = user.email
        data["role"] = user.get_role_display()
        data["id_user_plan"] = user.user_plan.id
        data["plan"] = user.user_plan.get_plan_display()

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
