from rest_framework import mixins, viewsets

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..serializers.user_reader_serializer import UserReaderSerializer


class UserReaderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserSchema.objects.filter(role=UserRoleEnum.READER)
    serializer_class = UserReaderSerializer
