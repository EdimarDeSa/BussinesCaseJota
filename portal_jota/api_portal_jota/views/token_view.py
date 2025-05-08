from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers.token_serializer import TokenSerializer


class TokenView(TokenObtainPairView):
    serializer_class = TokenSerializer
