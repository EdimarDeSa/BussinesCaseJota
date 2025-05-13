from ..enums.better_text_choices import BetterTextChoices


class UserRoleEnum(BetterTextChoices):
    ADMIN = "A", "Admin"
    EDITOR = "E", "Editor"
    READER = "R", "Leitor"
