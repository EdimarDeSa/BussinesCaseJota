import os
import stat
from datetime import timedelta
from typing import Any

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import include, path
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from ..enums.plan_enum import PlanEnum
from ..enums.status_noticia_enum import StatusNoticiaEnum
from ..enums.status_noticia_imagem_enum import StatusNoticiaImagemEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema, UserPlanSchema, UserSchema, VerticalSchema
from ..serializers.noticia_serializer import NoticiaSerializer
from ..serializers.user_admin_serializer import UserAdminSerializer
from ..serializers.user_editor_serializer import UserEditorSerializer
from ..serializers.user_reader_serializer import UserReaderSerializer
from ..tasks.publicar_noticia import publicar_noticia
from ..views.noticia_view import NoticiaViewSet

PASSWORD = "P@s5W0rd"


class TestNoticia(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("api/", include("api_portal_jota.urls")),
    ]

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")
        self.base_url = "/api/noticia/"

        self.user_admin = self._create_user(UserAdminSerializer)
        self.user_editor_serializer = UserEditorSerializer
        self.user_reader_serializer = UserReaderSerializer

        self.noticias_serializer = NoticiaSerializer()

        self.user_admin = self._create_user(UserAdminSerializer)

    def _generate_user_jota_info(self) -> UserSchema:
        return self._create_user(self.user_reader_serializer)

    def _generate_user_jota_pro(self, verticais: list[VerticalEnum]) -> UserSchema:
        user = self._generate_user_jota_info()

        user_plan = UserPlanSchema.objects.filter(cd_user=user.id).first()
        user_plan.plan = PlanEnum.JOTA_PRO
        user_plan.save()
        user_plan.verticais.set(VerticalSchema.objects.filter(cod_categoria__in=verticais))

        user.refresh_from_db()

        return user

    def _create_user(self, serializer_class: Any) -> UserSchema:
        user_data = {"username": self.faker.user_name(), "email": self.faker.email(), "password": PASSWORD}
        serializer = serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def _register_noticia(
        self,
        user_editor: UserSchema,
        is_published: bool = True,
        is_pro: bool = False,
        verticais: list | None = None,
        image: str = "",
    ) -> NoticiaSchema:
        noticia_data = self._generate_noticia_data(is_published, is_pro, verticais, image)
        noticia_data.update({"autor": user_editor})

        verticais = VerticalSchema.objects.filter(cod_categoria__in=noticia_data.pop("verticais", []))

        noticia = NoticiaSchema.objects.create(**noticia_data)
        noticia.verticais.set(verticais)

        if is_published:
            noticia.status = StatusNoticiaEnum.PUBLICADO.value
            noticia.save()
        noticia.refresh_from_db()
        return noticia

    def _generate_noticia_data(
        self,
        is_published: bool = True,
        is_pro: bool = False,
        verticais: list | None = None,
        image: str = "",
    ) -> dict[str, Any]:
        if verticais is None:
            verticais = self.faker.random_choices(
                elements=VerticalEnum.labels, length=self.faker.random_int(min=1, max=3)
            )

        if not is_published:
            data_publicacao = timezone.now()
        else:
            data_publicacao = self.faker.date_time_ad(
                start_datetime="+1s", end_datetime="+30s", tzinfo=timezone.get_current_timezone()
            )
        return {
            "titulo": self.faker.sentence(nb_words=3),
            "subtitulo": self.faker.sentence(nb_words=5),
            "imagem": image,
            "conteudo": self.faker.text(),
            "data_publicacao": data_publicacao,
            "is_pro": is_pro,
            "verticais": verticais,
        }

    def test_user_reader_cant_create_noticia(self) -> None:
        user_jota_info = self._generate_user_jota_info()

        self.client.force_authenticate(user=user_jota_info)
        response = self.client.post(
            self.base_url,
            self._generate_noticia_data(),
            format="multipart",
        )

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_editor_can_create_noticia_whitout_image(self) -> None:
        user_editor = self._create_user(self.user_editor_serializer)
        noticia_data = self._generate_noticia_data()

        self.client.force_authenticate(user_editor)
        response = self.client.post(self.base_url, noticia_data, format="multipart")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_201_CREATED, response.data)

        noticia = response.data
        self.assertEqual(noticia["titulo"], noticia_data["titulo"], noticia)
        self.assertEqual(noticia["autor_username"], user_editor.username, noticia)
        self.assertEqual(noticia["autor_id"], str(user_editor.id), noticia)

    def test_user_editor_can_create_noticia_with_image(self) -> None:
        editor = self._create_user(self.user_editor_serializer)
        img_bytes = self.faker.image(size=(100, 100), image_format="png")
        image_file = SimpleUploadedFile(name="test_image.png", content=img_bytes, content_type="image/png")
        noticia = self._generate_noticia_data(editor, image=image_file)

        self.client.force_authenticate(user=editor)
        response = self.client.post(self.base_url, noticia, format="multipart")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_201_CREATED, response.data)

        updated_noticia = NoticiaSchema.objects.get(id=response.data["id"])
        self.assertEqual(updated_noticia.status_imagem, StatusNoticiaImagemEnum.OK, updated_noticia.status_imagem)

        nome_imagem = updated_noticia.imagem.name.split("/")[-1]
        self.assertEqual(nome_imagem, "test_image.webp", nome_imagem)

        os.remove(updated_noticia.imagem.path)
        os.rmdir(updated_noticia.imagem.path.replace("test_image.webp", ""))

    def test_user_editor_can_list_all_noticias(self) -> None:
        user_editor = self._create_user(self.user_editor_serializer)
        noticias_por_editor = 5
        numero_de_editores = 2
        editores = [self._create_user(self.user_editor_serializer) for _ in range(numero_de_editores)]
        [self._register_noticia(editor) for _ in range(noticias_por_editor) for editor in editores]
        total_noticias = noticias_por_editor * numero_de_editores

        self.client.force_authenticate(user=user_editor)
        response = self.client.get(self.base_url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        response_data = response.data
        self.assertEqual(len(response_data), total_noticias, response_data)

    def test_user_editor_can_update_his_noticias(self) -> None:
        user_editor_1 = self._create_user(self.user_editor_serializer)
        noticia_1 = self._register_noticia(user_editor_1)
        noticia_1_updates = {
            "titulo": self.faker.sentence(nb_words=3),
            "subtitulo": self.faker.sentence(nb_words=5),
        }

        url = f"{self.base_url}{noticia_1.id}/"

        self.client.force_authenticate(user=user_editor_1)
        response = self.client.patch(url, noticia_1_updates, format="multipart")

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        noticia_data = response.data
        self.assertEqual(noticia_data["titulo"], noticia_1_updates["titulo"])
        self.assertEqual(noticia_data["subtitulo"], noticia_1_updates["subtitulo"])

    def test_user_editor_can_delete_his_noticias(self) -> None:
        user_editor = self._create_user(self.user_editor_serializer)
        noticia_user_editor_1 = self._register_noticia(user_editor)
        url = f"{self.base_url}{noticia_user_editor_1.id}/"

        self.client.force_authenticate(user=user_editor)
        response = self.client.delete(url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_user_reader_jota_info_can_read_noticias_jota_info(self) -> None:
        noticia_id = self._register_noticia(self._create_user(self.user_editor_serializer)).id
        user_reader = self._generate_user_jota_info()
        url = f"{self.base_url}{noticia_id}/"

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        noticia = response.data
        self.assertIn("conteudo", noticia, noticia)

    def test_user_reader_jota_info_cant_read_noticias_jota_pro(self) -> None:
        noticia = self._register_noticia(
            self._create_user(self.user_editor_serializer),
            is_pro=True,
        )
        user_reader = self._generate_user_jota_info()
        url = f"{self.base_url}{noticia.id}/"

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_reader_jota_pro_can_list_all_noticias(self) -> None:
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
        total_noticias = (5 + 5) * 2
        user_reader = self._generate_user_jota_pro([VerticalEnum.TRABALHISTA])

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(self.base_url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        noticias = response.data

        self.assertEqual(len(noticias), total_noticias, noticias)

    def test_noticia_status_cant_be_updated(self) -> None:
        user_editor = self._create_user(self.user_editor_serializer)
        noticia = self._register_noticia(user_editor, is_published=False)
        url = f"{self.base_url}{noticia.id}/"

        self.client.force_authenticate(user=user_editor)
        response = self.client.patch(
            url,
            {"status": StatusNoticiaEnum.PUBLICADO},
            format="multipart",
        )

        status_code = response.status_code
        self.assertEqual(status_code, 200, response.data)

        data = response.data
        self.assertEqual(data["status"], StatusNoticiaEnum.RASCUNHO.label, data)

    def test_noticia_status_is_published_automatically_after_1_second(self) -> None:
        editor = self._create_user(self.user_editor_serializer)
        noticia = self._register_noticia(editor, is_published=False)

        self.assertEqual(noticia.status, StatusNoticiaEnum.RASCUNHO.value)

        publicar_noticia()
        noticia.refresh_from_db()

        self.assertEqual(noticia.status, StatusNoticiaEnum.PUBLICADO.value, noticia.status)

    def test_noticia_status_is_changed_to_rascunho_after_publicado(self) -> None:
        editor = self._create_user(self.user_editor_serializer)
        noticia = self._register_noticia(editor, is_published=True)

        self.assertEqual(noticia.status, StatusNoticiaEnum.PUBLICADO.value)

        noticia.data_publicacao = timezone.now() + timedelta(days=1)
        noticia.save(update_fields=["data_publicacao"])

        noticia.refresh_from_db()

        self.assertEqual(noticia.status, StatusNoticiaEnum.RASCUNHO.value, noticia.status)

    def test_reader_cant_access_pro_news(self) -> None:
        noticia_id = self._register_noticia(self._create_user(self.user_editor_serializer)).id
        url = f"{self.base_url}{noticia_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_news_not_found(self) -> None:
        noticia_id = "00000000-0000-0000-0000-000000000000"
        user_reader = self._generate_user_jota_info()
        url = f"{self.base_url}{noticia_id}/"

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_user_editor_cant_upload_invalid_image_format(self) -> None:
        editor = self._create_user(self.user_editor_serializer)
        invalid_img = SimpleUploadedFile("invalid.txt", b"dummy", content_type="text/plain")
        noticia_data = self._generate_noticia_data(image=invalid_img)

        self.client.force_authenticate(user=editor)
        response = self.client.post(self.base_url, noticia_data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("detail", response.data)
