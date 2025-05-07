from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .enums.plan_enum import PlanEnum
from .enums.user_role_enum import UserRoleEnum


class IsAdmin(BasePermission):
    """
    isAdmin Verifica se o usuário é admin de acordo com o role
    """

    def has_permission(self, request: Request, view: object) -> bool:
        return request.user.is_authenticated and request.user.role == UserRoleEnum.ADMIN

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        return request.user.role == UserRoleEnum.ADMIN


class IsSelfOrAdmin(BasePermission):
    """
    IsSelfOrAdmin Verifica se o usuário é admin de acordo com o role ou ele mesmo
    """

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        return request.user == obj or request.user.role == UserRoleEnum.ADMIN


# Class que permite alterar/deletar noticias
class CanEditNews(BasePermission):
    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        is_admin = request.user.role == UserRoleEnum.ADMIN
        is_autor = obj.autor == request.user
        return any([is_admin, is_autor])


class IsReaderOrdAdmin(BasePermission):
    """
    isReaderOdAdmin Verifica se o usuário é editor de acordo com o role
    """

    def has_permission(self, request: Request, view: object) -> bool:
        is_auth = request.user.is_authenticated
        has_role = request.user.role in [UserRoleEnum.READER, UserRoleEnum.ADMIN]
        return all([is_auth, has_role])

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        has_role = request.user.role in [UserRoleEnum.READER, UserRoleEnum.ADMIN]
        return has_role


class IsEditorOrAdmin(BasePermission):
    """
    isEditor Verifica se o usuário é editor de acordo com o role
    """

    def has_permission(self, request: Request, view: object) -> bool:
        is_auth = request.user.is_authenticated
        has_role = request.user.role in [UserRoleEnum.EDITOR, UserRoleEnum.ADMIN]
        return all([is_auth, has_role])
