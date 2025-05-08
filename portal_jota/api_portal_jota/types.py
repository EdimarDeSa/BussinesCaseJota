from typing import Optional, TypedDict

UserId = str
NoticiaId = str

from .enums.email_type_enum import EmailTypeEnum


class EmailData(TypedDict):
    email_type: EmailTypeEnum
    to: Optional[list[UserId]]
    news_id: Optional[NoticiaId]
