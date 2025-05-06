from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .enums.plan_enum import PlanEnum
from .enums.user_role_enum import UserRoleEnum


class IsAdmin(BasePermission):
    """
    isAdmin Verifica se o usuário é admin de acordo com o role
    """

    def has_permission(self, request: Request, view: object) -> bool:
        user = request.user
        return user.is_authenticated and getattr(user, "role", None) == UserRoleEnum.ADMIN


class IsSelfOrAdmin(BasePermission):
    """
    IsSelfOrAdmin Verifica se o usuário é admin de acordo com o role ou ele mesmo
    """

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        return request.user == obj or request.user.role == UserRoleEnum.ADMIN


class IsEditor(BasePermission):
    """
    isEditor Verifica se o usuário é editor de acordo com o role
    """

    def has_permission(self, request: Request, view: object) -> bool:
        user = request.user
        return user.is_authenticated and getattr(user, "role", None) == UserRoleEnum.EDITOR


class IsReaderPro(BasePermission):
    """
    isReaderPro Verifica se o usuário é editor de acordo com o role
    """

    def has_permission(self, request: Request, view: object) -> bool:
        user = request.user
        is_pro = user.user_plan.plan == PlanEnum.JOTA_PRO
        return user.is_authenticated and getattr(user, "role", None) == UserRoleEnum.READER
