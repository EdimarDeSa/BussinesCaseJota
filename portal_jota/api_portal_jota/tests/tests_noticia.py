import os
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import include, path
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from ..enums.status_noticia_enum import StatusNoticiaEnum
from ..enums.status_noticia_imagem_enum import StatusNoticiaImagemEnum
from ..enums.user_role_enum import UserRoleEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema
from ..tasks.publicar_noticia import publicar_noticia
from .aux_funcs import create_noticia, create_user, generate_noticia_data


class TestNoticia(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("api/", include("api_portal_jota.urls")),
    ]

    def setUp(self) -> None:
        self.faker = Faker("pt_BR")
        self.base_url = "/api/noticia/"

    def test_user_reader_cant_create_noticia(self) -> None:
        reader_jota_info = create_user(UserRoleEnum.READER)

        self.client.force_authenticate(user=reader_jota_info)
        response = self.client.post(
            self.base_url,
            generate_noticia_data(),
            format="multipart",
        )

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_editor_can_create_noticia_whitout_image(self) -> None:
        editor = create_user(UserRoleEnum.EDITOR)
        noticia_data = generate_noticia_data()

        self.client.force_authenticate(editor)
        response = self.client.post(self.base_url, noticia_data, format="multipart")

        status_code = response.status_code
        noticia = response.data

        self.assertEqual(status_code, status.HTTP_201_CREATED, response.data)

        self.assertEqual(noticia["titulo"], noticia_data["titulo"], noticia)
        self.assertEqual(noticia["autor_username"], editor.username, noticia)
        self.assertEqual(noticia["autor_id"], str(editor.id), noticia)

    def test_user_editor_can_create_noticia_with_image(self) -> None:
        editor = create_user(UserRoleEnum.EDITOR)
        img_bytes = self.faker.image(size=(100, 100), image_format="png")
        image_file = SimpleUploadedFile(name="test_image.png", content=img_bytes, content_type="image/png")
        noticia = generate_noticia_data(editor, image=image_file)

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
        user_editor = create_user(UserRoleEnum.EDITOR)
        noticias_por_editor = 5
        numero_de_editores = 2
        editores = [create_user(UserRoleEnum.EDITOR) for _ in range(numero_de_editores)]
        [create_noticia(editor) for _ in range(noticias_por_editor) for editor in editores]
        total_noticias = noticias_por_editor * numero_de_editores

        self.client.force_authenticate(user=user_editor)
        response = self.client.get(self.base_url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        response_data = response.data
        self.assertEqual(len(response_data), total_noticias, response_data)

    def test_user_editor_can_update_his_noticias(self) -> None:
        user_editor_1 = create_user(UserRoleEnum.EDITOR)
        noticia_1 = create_noticia(user_editor_1)
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
        user_editor = create_user(UserRoleEnum.EDITOR)
        noticia_user_editor_1 = create_noticia(user_editor)
        url = f"{self.base_url}{noticia_user_editor_1.id}/"

        self.client.force_authenticate(user=user_editor)
        response = self.client.delete(url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_user_reader_jota_info_can_read_noticias_jota_info(self) -> None:
        noticia_id = create_noticia(create_user(UserRoleEnum.EDITOR)).id
        user_reader = create_user(UserRoleEnum.READER)
        url = f"{self.base_url}{noticia_id}/"

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        noticia = response.data
        self.assertIn("conteudo", noticia, noticia)

    def test_user_reader_jota_info_cant_read_noticias_jota_pro(self) -> None:
        noticia = create_noticia(
            create_user(UserRoleEnum.EDITOR),
            is_pro=True,
        )
        user_reader = create_user(UserRoleEnum.READER)
        url = f"{self.base_url}{noticia.id}/"

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_reader_jota_pro_can_list_all_noticias(self) -> None:
        for _ in range(2):
            user_editor = create_user(UserRoleEnum.EDITOR)
            [create_noticia(user_editor) for _ in range(5)]
            [
                create_noticia(
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
        user_reader = create_user(UserRoleEnum.READER, True, [VerticalEnum.TRABALHISTA])

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(self.base_url)

        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_200_OK, response.data)

        noticias = response.data

        self.assertEqual(len(noticias), total_noticias, noticias)

    def test_noticia_status_cant_be_updated(self) -> None:
        user_editor = create_user(UserRoleEnum.EDITOR)
        noticia = create_noticia(user_editor, is_published=False)
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
        editor = create_user(UserRoleEnum.EDITOR)
        noticia = create_noticia(editor, is_published=False)

        self.assertEqual(noticia.status, StatusNoticiaEnum.RASCUNHO.value)

        publicar_noticia()
        noticia.refresh_from_db()

        self.assertEqual(noticia.status, StatusNoticiaEnum.PUBLICADO.value, noticia.status)

    def test_noticia_status_is_changed_to_rascunho_after_publicado(self) -> None:
        editor = create_user(UserRoleEnum.EDITOR)
        noticia = create_noticia(editor, is_published=True)

        self.assertEqual(noticia.status, StatusNoticiaEnum.PUBLICADO.value)

        noticia.data_publicacao = timezone.now() + timedelta(days=1)
        noticia.save(update_fields=["data_publicacao"])

        noticia.refresh_from_db()

        self.assertEqual(noticia.status, StatusNoticiaEnum.RASCUNHO.value, noticia.status)

    def test_reader_cant_access_pro_news(self) -> None:
        noticia_id = create_noticia(create_user(UserRoleEnum.EDITOR)).id
        url = f"{self.base_url}{noticia_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_news_not_found(self) -> None:
        noticia_id = "00000000-0000-0000-0000-000000000000"
        user_reader = create_user(UserRoleEnum.READER)
        url = f"{self.base_url}{noticia_id}/"

        self.client.force_authenticate(user=user_reader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_user_editor_cant_upload_invalid_image_format(self) -> None:
        editor = create_user(UserRoleEnum.EDITOR)
        invalid_img = SimpleUploadedFile("invalid.txt", b"dummy", content_type="text/plain")
        noticia_data = generate_noticia_data(image=invalid_img)

        self.client.force_authenticate(user=editor)
        response = self.client.post(self.base_url, noticia_data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("detail", response.data)
