from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from users.managers import CustomUserManager


class User(AbstractUser):
    """The project's user, replacing Django's default via AUTH_USER_MODEL.

    Extends AbstractUser rather than AbstractBaseUser so permissions, admin
    integration and the standard auth machinery are inherited unchanged.

    Username is removed and email is the USERNAME_FIELD. Sign-in is expected to
    be through social providers, which supply no username of their own, so
    retaining the field would mean a second unique column holding a copy of the
    address and a duplicate signup could violate either constraint.

    Email is unique and mandatory, which Django's default user does not
    enforce. Mandatory is applied in two places for different reasons —
    CustomUserManager rejects a missing address with a readable error, and the
    check constraint below makes an empty one unreachable regardless of how the
    row is written, including bulk operations and direct saves.

    Attributes:
      email: Unique address for the account. Required.
      display_name: Optional name shown to other users, so a real name need not
        be exposed.
      first_name: Given name. Optional.
      last_name: Family name. Optional.
    """

    username = None  # type: ignore[assignment]
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    email = models.EmailField()
    display_name = models.CharField(max_length=32, blank=True)
    first_name = models.CharField(blank=True)
    last_name = models.CharField(blank=True)

    objects: ClassVar[CustomUserManager] = CustomUserManager()  # type: ignore[assignment]

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["email"], name="user_email_unique"),
            models.CheckConstraint(
                condition=~Q(email=""), name="user_email_is_not_blank"
            ),
        ]

    def __str__(self):
        return self.email
