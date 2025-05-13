from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .enums.user_role_enum import UserRoleEnum
from .models.user_schema import UserSchema


class IsAdmin(BasePermission):
    def has_permission(self, request: Request, view: object) -> bool:
        return request.user.is_authenticated and request.user.role == UserRoleEnum.ADMIN

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        return request.user.role == UserRoleEnum.ADMIN


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        return request.user == obj or request.user.role == UserRoleEnum.ADMIN


class IsReaderOrdAdmin(BasePermission):
    def has_permission(self, request: Request, view: object) -> bool:
        is_auth = request.user.is_authenticated
        user_role = request.user.role if is_auth else None
        has_role = user_role in [UserRoleEnum.EDITOR, UserRoleEnum.ADMIN]
        return all([is_auth, has_role])

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        is_auth = request.user.is_authenticated
        user_role = request.user.role if is_auth else None
        has_role = user_role in [UserRoleEnum.EDITOR, UserRoleEnum.ADMIN]
        return has_role


class IsEditorOrAdmin(BasePermission):
    def has_permission(self, request: Request, view: object) -> bool:
        is_auth = request.user.is_authenticated
        user_role = request.user.role if is_auth else None
        has_role = user_role in [UserRoleEnum.EDITOR, UserRoleEnum.ADMIN]
        return all([is_auth, has_role])

    def has_object_permission(self, request: Request, view: object, obj: UserSchema) -> bool:
        is_admin = request.user.role == UserRoleEnum.ADMIN
        is_autor = obj.autor == request.user
        return any([is_admin, is_autor])
