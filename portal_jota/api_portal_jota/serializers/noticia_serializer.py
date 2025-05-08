from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums.status_noticia_imagem_enum import StatusNoticiaImagemEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema, VerticalSchema
from ..tasks.process_image import process_image


class NoticiaSerializer(serializers.ModelSerializer):
    verticais = serializers.ListField(
        child=serializers.ChoiceField(choices=VerticalEnum.labels),
        required=True,
        write_only=True,
        help_text=f"Lista de verticais. Valores possíveis: {[v.value for v in VerticalEnum]}",
    )

    class Meta:
        model = NoticiaSchema
        fields = [
            "id",
            "titulo",
            "subtitulo",
            "imagem",
            "status_imagem",
            "conteudo",
            "data_publicacao",
            "autor",
            "status",
            "is_pro",
            "verticais",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "autor": {"read_only": True},
            "status": {"read_only": True},
            "imagem": {"write_only": True},
            "status_imagem": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data):
        verticais = validated_data.pop("verticais")
        # imagem = validated_data.pop("imagem")

        validated_data["autor"] = self.context["request"].user

        noticia = super().create(validated_data)

        # if imagem:
        #     process_image.delay(str(noticia.id))

        verticais_objects = VerticalSchema.objects.filter(name__in=verticais)
        noticia.verticais.set(verticais_objects)
        return noticia

    @extend_schema_field(serializers.CharField())
    def get_autor_username(self, instance: NoticiaSchema) -> str:
        return instance.autor.username

    @extend_schema_field(serializers.CharField())
    def get_autor_id(self, instance: NoticiaSchema) -> str:
        return str(instance.autor.id)

    def to_representation(self, instance: NoticiaSchema) -> dict:
        data = super().to_representation(instance)
        data["autor_id"] = self.get_autor_id(instance)
        data["autor"] = self.get_autor_username(instance)
        data["status"] = instance.get_status_display()
        data["verticais"] = [v.name for v in instance.verticais.all()]

        if data["status_imagem"] == StatusNoticiaImagemEnum.OK.label:
            data["imagem"] = instance.imagem.url

        return data
