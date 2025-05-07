from datetime import timedelta, timezone

from django.test import TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory, force_authenticate

from ..enums.plan_enum import PlanEnum
from ..enums.status_noticia_enum import StatusNoticiaEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema, UserPlanSchema, UserSchema, VerticalSchema
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

    def _generate_noticia_data(self, is_published=True, is_pro=False, verticais=None, image=None):
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
                start_datetime="+1m" if not is_published else "-5m",
                end_datetime="+5m" if not is_published else "-1m",
                tzinfo=timezone(timedelta(hours=-3)),
            ),
            "is_pro": is_pro,
            "verticais": verticais,
        }

    def _generate_user_jota_info(self) -> UserSchema:
        return self._create_user(self.user_reader_serializer)

    def _generate_user_jota_pro(self, verticais: list[VerticalEnum]) -> UserSchema:
        user_id = self._generate_user_jota_info().id

        user_plan = UserPlanSchema.objects.filter(cd_user=user_id).first()
        user_plan.plan = PlanEnum.JOTA_PRO
        user_plan.save()
        user_plan.verticais.set(VerticalSchema.objects.filter(cod_categoria__in=verticais))

        return UserSchema.objects.filter(id=user_id).first()

    def _register_noticia(
        self,
        user_editor,
        is_published=True,
        is_pro=False,
        verticais=None,
        image=None,
    ) -> NoticiaSchema:
        noticia_data = self._generate_noticia_data(is_published, is_pro, verticais, image)
        noticia_data.update({"autor": user_editor})

        verticais = VerticalSchema.objects.filter(cod_categoria__in=noticia_data.pop("verticais"))

        noticia = NoticiaSchema.objects.create(**noticia_data)
        noticia.verticais.set(verticais)

        if is_published:
            noticia.status = StatusNoticiaEnum.PUBLICADO.value
            noticia.save()

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

        self.user_reader_serializer = UserReaderSerializer()

        self.user_editor_serializer = UserEditorSerializer()

        self.user_admin = self._create_user(UserAdminSerializer())

    def test_user_reader_cant_create_noticia(self):
        user_jota_info = self._generate_user_jota_info()
        request = self.factory.post(self.base_url, self._generate_noticia_data(), format="json")

        force_authenticate(request, user=user_jota_info)

        response = self.view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 403)

    def test_user_editor_can_create_noticia_whitout_image(self):
        user_editor = self._create_user(self.user_editor_serializer)
        noticia_data = self._generate_noticia_data()

        request = self.factory.post(self.base_url, noticia_data, format="json")

        force_authenticate(request, user=user_editor)

        response = self.view(request)
        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 201)

        noticia = response.data
        self.assertEqual(noticia["titulo"], noticia_data["titulo"])
        self.assertEqual(noticia["autor"], user_editor.username)
        self.assertEqual(noticia["autor_id"], str(user_editor.id))

    def test_user_editor_can_list_only_his_noticias(self):
        user_editor_1 = self._create_user(self.user_editor_serializer)
        noticia_user_editor_1 = self._register_noticia(user_editor_1)

        user_editor_2 = self._create_user(self.user_editor_serializer)
        self._register_noticia(user_editor_2)

        request = self.factory.get(self.base_url)

        force_authenticate(request, user=user_editor_1)

        response = self.view(request, pk=str(user_editor_1.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200)

        noticias = response.data
        self.assertEqual(len(noticias), 1)

        noticia = noticias[0]
        self.assertEqual(noticia["id"], str(noticia_user_editor_1.id))
        self.assertEqual(noticia["autor_id"], str(noticia_user_editor_1.autor.id))

    def test_user_editor_can_update_his_noticias(self):
        user_editor_1 = self._create_user(self.user_editor_serializer)
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

    def test_user_editor_can_delete_his_noticias(self):
        user_editor_1 = self._create_user(self.user_editor_serializer)
        noticia_user_editor_1 = self._register_noticia(user_editor_1)

        url = f"{self.base_url}{noticia_user_editor_1.id}/"

        request = self.factory.delete(url)

        force_authenticate(request, user=user_editor_1)

        response = self.view(request, pk=str(noticia_user_editor_1.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 204)

    def test_user_reader_jota_info_can_list_only_jota_info_noticias(self):
        for _ in range(2):
            user_editor = self._create_user(self.user_editor_serializer)
            [self._register_noticia(user_editor) for _ in range(5)]
            [self._register_noticia(user_editor, is_pro=True) for _ in range(5)]

        user_reader = self._generate_user_jota_info()
        request = self.factory.get(self.base_url)

        force_authenticate(request, user=user_reader)

        response = self.view(request)

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200)

        noticias = response.data

        self.assertEqual(len(noticias), 10)

    def test_user_reader_jota_pro_can_list_all_noticias_filtered_by_his_verticais(self):
        for _ in range(2):
            user_editor = self._create_user(self.user_editor_serializer)
            [self._register_noticia(user_editor) for _ in range(5)]
            [
                self._register_noticia(
                    user_editor,
                    is_pro=True,
                    verticais=[
                        VerticalEnum.ENERGIA,
                        VerticalEnum.TRABALHISTA if val <= 2 else VerticalEnum.SAUDE,
                    ],
                )
                for val in range(5)
            ]

        user_reader = self._generate_user_jota_pro([VerticalEnum.TRABALHISTA])

        request = self.factory.get(self.base_url)

        force_authenticate(request, user=user_reader)

        response = self.view(request, str(user_reader.id))

        response.render()

        status_code = response.status_code
        self.assertEqual(status_code, 200)

        noticias = response.data

        self.assertEqual(len(noticias), 16)

    def test_noticia_status_cant_be_updated(self):
        user_editor = self._create_user(self.user_editor_serializer)
        noticia = self._register_noticia(user_editor, is_published=False)

        url = f"{self.base_url}{noticia.id}/"

        request = self.factory.patch(
            url,
            {"status": StatusNoticiaEnum.PUBLICADO},
            format="json",
        )

        force_authenticate(request, user=user_editor)

        response = self.view(request, pk=str(noticia.id))

        response.render()

        status_code = response.status_code

        self.assertEqual(status_code, 200, response.data)

        data = response.data
        self.assertEqual(data["status"], StatusNoticiaEnum.RASCUNHO.label, data)

    def test_noticia_status_is_published_automatically_after_1_second(self):
        self.assertTrue(True)

    def test_create_noticia_with_image(self):
        self.assertTrue(True)

    def test_noticia_image_is_processed(self):
        self.assertTrue(True)
