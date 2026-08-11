from django.contrib import admin

from .models import Competition, Membership, Tip


class MembershipInline(admin.TabularInline):
    """Members of a competition, edited from the competition itself.

    `Competition.members` has an explicit `through`, so Django excludes it
    from the default form -- an inline over `Membership` is what makes
    members editable from here.
    """

    model = Membership
    extra = 1


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """Admin for competitions."""

    list_display = ("name", "season")
    list_filter = ("season",)
    inlines = (MembershipInline,)
    ordering = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Admin for memberships.

    Registered in its own right as well as inlined on `Competition`, so a
    single membership can be found without going through the competition.
    """

    list_display = ("user", "competition")
    list_filter = ("competition",)


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    """Admin for tips.

    `membership` renders as the member and their competition, which is what
    identifies who tipped.
    """

    list_display = ("membership", "match", "selected_team")
    list_filter = ("match__season", "membership__competition")
