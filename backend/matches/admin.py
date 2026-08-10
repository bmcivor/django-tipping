from django.contrib import admin

from .models import Match, Season, Team


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    """Admin for seasons."""

    list_display = ("name", "year")
    list_filter = ("year",)
    ordering = ("-year", "name")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin for teams."""

    list_display = ("abbreviation", "location", "mascot")
    search_fields = ("location", "mascot", "abbreviation")
    ordering = ("mascot",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Admin for matches.

    `season` and both teams are selects over every row, which is fine at the
    scale of one competition's draw. `autocomplete_fields` becomes worth it if
    a season's worth of matches makes the page slow.
    """

    list_display = (
        "season",
        "round_number",
        "home_team",
        "away_team",
        "kickoff_time",
        "home_score",
        "away_score",
    )
    list_filter = ("season", "round_number")
    ordering = ("-kickoff_time",)
