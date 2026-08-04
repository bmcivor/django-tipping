from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models.users import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin for the custom user model.

    Inherits Django's UserAdmin for its password handling — the change form
    renders a hash rather than an editable field, and setting a password goes
    through a dedicated form.

    Every attribute below replaces a default that names `username`, which this
    model does not have. `search_fields`, `list_filter` and `filter_horizontal`
    are inherited unchanged.
    """

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "display_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "usable_password", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "display_name", "first_name", "last_name", "is_staff")
    search_fields = ("email", "display_name", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("last_login", "date_joined")
