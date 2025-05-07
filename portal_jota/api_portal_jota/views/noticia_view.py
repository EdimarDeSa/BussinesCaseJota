from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from ..models import NoticiaSchema
from ..permissions import CanEditNews, IsEditorOrAdmin
from ..serializers.noticia_serializer import NoticiaSerializer


class NoticiaViewSet(viewsets.ModelViewSet):
    serializer_class = NoticiaSerializer

    def get_queryset(self):
        """
        get_queryset Filtra as noticias de acordo com o perfil do usuário
        >>> Admin: Todas as noticias
        >>> Editor: Todas as noticias do usuário
        >>> Reader: Notas de acordo com o plano e verticais
        """
        user = self.request.user
        match user.role:
            case UserRoleEnum.ADMIN:
                return NoticiaSchema.objects.all()

            case UserRoleEnum.EDITOR:
                return NoticiaSchema.objects.filter(autor=user.id)

            case UserRoleEnum.READER:
                jota_info_noticias = NoticiaSchema.objects.filter(is_pro=False)

                match self.request.user.user_plan.plan:
                    case PlanEnum.JOTA_INFO:
                        return jota_info_noticias

                    case PlanEnum.JOTA_PRO:
                        jota_pro_noticias = NoticiaSchema.objects.filter(
                            is_pro=True,
                            verticais__in=user.user_plan.verticais.all(),
                        ).distinct()
                        return jota_info_noticias.union(jota_pro_noticias)

    def get_permissions(self):
        """
        get_permissions Define as permissões de acordo com a ação
        >>> create: Editor ou Admin
        >>> list, retrieve: Autenticado
        >>> update, partial_update, destroy: Editor autor ou Admin
        """
        if self.action == "create":
            return [IsAuthenticated(), IsEditorOrAdmin()]

        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), CanEditNews()]

        return super().get_permissions()
