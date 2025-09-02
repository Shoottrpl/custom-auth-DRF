import re
from typing import List
from django.core.exceptions import ValidationError


class BcryptPasswordValidator:
    def validate(self, password: str, user=None) -> None:
        errors: List[str] = []
        warnings: List[str] = []

        if not password:
            errors.append("Password cannot be empty")
            raise ValidationError(errors)

        if len(password) < 8:
            errors.append("Пароль должен содержать как минимум 8 символов.")
       
        if not re.search(r'\d', password):
            errors.append("Пароль должен содержать хотя бы одну цифру.")

        if not re.search(r'[a-zA-Z]', password):
            errors.append("Пароль должен содержать хотя бы одну букву.")

        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self) -> str:
        return (
            "Ваш пароль должен содержать минимум 8 символов, "
            "включать буквы и цифры, а также желательно специальные символы."
            )
