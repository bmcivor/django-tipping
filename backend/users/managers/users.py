from typing import TYPE_CHECKING

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from psycopg2 import errors

if TYPE_CHECKING:
    from users.models import User  # noqa: F401


class CustomUserManager(BaseUserManager["User"]):
    """
    Custom user model manager that is built to handle that
    email is unique. This is used for authentication instead
    of username.
    """

    def create_user(self, email: str, password: str, **extra_fields) -> "User":
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValidationError("An email address must be provided.")

        if not password:
            raise ValidationError("A password must be provided.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        validate_password(password, user)
        user.set_password(password)

        try:
            user.save()
        except IntegrityError as exc:
            if isinstance(exc.__cause__, errors.UniqueViolation):
                constraint_name = exc.__cause__.diag.constraint_name
                if constraint_name == "user_email_unique":
                    raise ValidationError(
                        "A user is already registered with this email."
                    )
            raise exc

        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        """
        Create and save a super user with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
