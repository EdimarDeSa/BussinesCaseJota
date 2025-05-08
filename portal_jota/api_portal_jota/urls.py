from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views.noticia_view import NoticiaViewSet
from .views.token_view import TokenView
from .views.user_admin_view import UserAdminViewSet
from .views.user_editor_view import UserEditorViewSet
from .views.user_plan_view import UserPlanViewSet
from .views.user_reader_view import UserReaderViewSet

router = DefaultRouter()
router.register(r"reader-user", viewset=UserReaderViewSet, basename="reader-user")
router.register(r"editor-user", viewset=UserEditorViewSet, basename="editor-user")
router.register(r"admin-user", viewset=UserAdminViewSet, basename="admin-user")

router.register(r"user-plan", viewset=UserPlanViewSet, basename="user-plan")

router.register(r"noticia", viewset=NoticiaViewSet, basename="noticia")

urlpatterns = [
    path("token/", TokenView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

urlpatterns += router.urls
