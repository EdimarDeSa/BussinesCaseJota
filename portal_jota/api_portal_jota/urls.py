from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import token_refresh, token_verify

from .views.noticia_view import NoticiaViewSet
from .views.token_view import TokenView
from .views.user_plan_view import UserPlanViewSet
from .views.user_view import UserViewSet

router = DefaultRouter()
router.register(r"user", viewset=UserViewSet, basename="user")

router.register(r"user-plan", viewset=UserPlanViewSet, basename="user-plan")

router.register(r"noticia", viewset=NoticiaViewSet, basename="noticia")


urlpatterns = [
    path("token/", TokenView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", token_refresh, name="token_refresh"),
    path("token/verify/", token_verify, name="token_verify"),
]

urlpatterns += router.urls
