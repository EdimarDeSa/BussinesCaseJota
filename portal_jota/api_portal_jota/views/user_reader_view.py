from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsAdmin
from ..serializers.user_reader_serializer import UserReaderSerializer


class UserReaderViewSet(viewsets.ModelViewSet):
    queryset = UserSchema.objects.filter(role=UserRoleEnum.READER)
    serializer_class = UserReaderSerializer

    def list(self, request, *args, **kwargs):
        # Para acessar essa função deve estar logado e ser um admin
        is_auth = IsAuthenticated().has_permission(request, self)
        is_admin = IsAdmin().has_permission(request, self)

        if not is_auth or not is_admin:
            return Response({"detail": "Listar usuários somente para admin."}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
