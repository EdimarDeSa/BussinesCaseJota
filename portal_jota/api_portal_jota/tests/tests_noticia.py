from datetime import timedelta, timezone

from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema, UserSchema, VerticalSchema
from ..serializers.noticia_serializer import NoticiaSerializer
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..serializers.user_editor_serializer import UserEditorSerializer
from ..serializers.user_reader_serializer import UserReaderSerializer
from ..views.noticia_view import NoticiaViewSet

PASSWORD = "P@s5W0rd"


class TestNoticia(TestCase):
    def _create_user(self, serializer) -> UserSchema:
        return serializer.create(self._generate_user_data())

    def _generate_user_data(self):
        return {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": PASSWORD,
        }

    def _generate_noticia_data(self, is_pro=False, verticais=None, image=None):
        if verticais is None:
            verticais = self.faker.random_choices(
                elements=VerticalEnum.labels, length=self.faker.random_int(min=1, max=3)
            )
        return {
            "titulo": self.faker.sentence(nb_words=3),
            "subtitulo": self.faker.sentence(nb_words=5),
            "imagem": image,
            "conteudo": self.faker.text(),
            "data_publicacao": self.faker.date_time_ad(
                start_datetime="+1m",
                end_datetime="+5m",
                tzinfo=timezone(timedelta(hours=-3)),
            ),
            "is_pro": is_pro,
            "verticais": verticais,
        }

    def _generate_user_jota_info(self) -> UserSchema:
        return self._create_user(self.user_reader_serializers)

    def _generate_user_jota_pro(self, verticais: list[VerticalEnum]) -> UserSchema:
        user = self._create_user(self.user_reader_serializers)
        self.user_reader_serializers.update(
            user,
            {
                "plan": PlanEnum.JOTA_PRO,
                "verticais": verticais,
            },
        )
        return user

    def _register_noticia(self, user_editor) -> NoticiaSchema:
        noticia_data = self._generate_noticia_data()
        noticia_data.update({"autor": user_editor})

        verticais = VerticalSchema.objects.filter(name__in=noticia_data.pop("verticais"))

        noticia = NoticiaSchema.objects.create(**noticia_data)
        noticia.verticais.set(verticais)

        return noticia

    def setUp(self):
        self.faker = Faker("pt_BR")

        self.base_url = "/api/noticia/"
        self.factory = APIRequestFactory()
        self.view = NoticiaViewSet.as_view(
            {
                "post": "create",
                "get": "list",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )
        self.noticias_serializer = NoticiaSerializer()

        self.user_reader_serializers = UserReaderSerializer()

        self.user_editor_serializers = UserEditorSerializer()

        self.user_admin = self._create_user(UserAdminSerializer())

    # def test_user_reader_cant_create_noticia(self):
    #     user_jota_info = self._generate_user_jota_info()
    #     request = self.factory.post(self.base_url, self._generate_noticia_data(), format="json")

    #     force_authenticate(request, user=user_jota_info)

    #     response = self.view(request)
    #     response.render()

    #     status_code = response.status_code
    #     self.assertEqual(status_code, 403)

    # def test_user_editor_can_create_noticia_whitout_image(self):
    #     user_editor = self._create_user(self.user_editor_serializers)
    #     noticia_data = self._generate_noticia_data()

    #     request = self.factory.post(self.base_url, noticia_data, format="json")

    #     force_authenticate(request, user=user_editor)

    #     response = self.view(request)
    #     response.render()

    #     status_code = response.status_code
    #     self.assertEqual(status_code, 201)

    #     noticia = response.data
    #     self.assertEqual(noticia["titulo"], noticia_data["titulo"])
    #     self.assertEqual(noticia["autor"], user_editor.username)
    #     self.assertEqual(noticia["autor_id"], str(user_editor.id))

    # def test_user_editor_can_list_only_his_noticias(self):
    #     user_editor_1 = self._create_user(self.user_editor_serializers)
    #     noticia_user_editor_1 = self._register_noticia(user_editor_1)

    #     user_editor_2 = self._create_user(self.user_editor_serializers)
    #     self._register_noticia(user_editor_2)

    #     request = self.factory.get(self.base_url)

    #     force_authenticate(request, user=user_editor_1)

    #     response = self.view(request, pk=str(user_editor_1.id))

    #     response.render()

    #     status_code = response.status_code
    #     self.assertEqual(status_code, 200)

    #     noticias = response.data
    #     self.assertEqual(len(noticias), 1)

    #     noticia = noticias[0]
    #     self.assertEqual(noticia["id"], str(noticia_user_editor_1.id))
    #     self.assertEqual(noticia["autor_id"], str(noticia_user_editor_1.autor.id))

    def test_user_editor_can_update_his_noticias(self):
        user_editor_1 = self._create_user(self.user_editor_serializers)
        noticia_user_editor_1 = self._register_noticia(user_editor_1)
        noticia_user_editor_1_updates = {
            "titulo": self.faker.sentence(nb_words=3),
            "subtitulo": self.faker.sentence(nb_words=5),
        }

        url = f"{self.base_url}{noticia_user_editor_1.id}/"

        request = self.factory.patch(
            url,
            noticia_user_editor_1_updates,
            format="json",
        )

        force_authenticate(request, user=user_editor_1)

        response = self.view(request, pk=str(noticia_user_editor_1.id))

        response.render()

        status_code = response.status_code
        noticia_data = response.data

        self.assertEqual(status_code, 200, str(noticia_data))

        self.assertEqual(noticia_data["titulo"], noticia_user_editor_1_updates["titulo"])
        self.assertEqual(noticia_data["subtitulo"], noticia_user_editor_1_updates["subtitulo"])

    # def test_user_editor_can_delete_his_noticias(self):
    #     self.assertTrue(True)

    # def test_user_reader_jota_info_can_list_only_free_noticias(self):
    #     self.assertTrue(True)

    # def test_user_reader_jota_pro_can_list_all_noticias_filtered_by_his_verticais(self):
    #     self.assertTrue(True)
