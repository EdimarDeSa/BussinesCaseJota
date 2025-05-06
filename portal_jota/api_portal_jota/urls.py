from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.user_admin_view import UserAdminViewSet
from .views.user_editor_view import UserEditorViewSet
from .views.user_reader_view import UserReaderViewSet

router = DefaultRouter()
router.register(r"reader-user", viewset=UserReaderViewSet, basename="reader-user")
router.register(r"editor-user", viewset=UserEditorViewSet, basename="editor-user")
router.register(r"admin-user", viewset=UserAdminViewSet, basename="admin-user")

urlpatterns = router.urls
