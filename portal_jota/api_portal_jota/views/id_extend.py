from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema


def extend_uuid_schema(description: str = "ID do usuário") -> dict[str, Any]:
    prameters = extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description=description,
            )
        ]
    )
    return {
        "retrieve": prameters,
        "update": prameters,
        "partial_update": prameters,
        "destroy": prameters,
    }
