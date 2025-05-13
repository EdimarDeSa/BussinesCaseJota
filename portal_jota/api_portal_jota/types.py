from typing import Optional, TypedDict

from .enums.email_type_enum import EmailTypeEnum

UserId = str
NoticiaId = str


class EmailData(TypedDict):
    email_type: EmailTypeEnum
    to: Optional[list[UserId]]
    news_id: Optional[NoticiaId]
