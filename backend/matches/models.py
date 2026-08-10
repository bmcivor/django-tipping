from django.db import models
from django.db.models import Q


class Season(models.Model):
    """
    The projects entity for keeping track of what year and season
    a Match belongs to.

    The season model does have some basic constraints to defend from bad
    year data going in. Only acceptable years are from 1900 onwards to
    2100.
    """

    name = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "year"],
                name="unique_season_name_year",
            ),
            models.CheckConstraint(
                condition=Q(year__gte=1900, year__lte=2100),
                name="season_year_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.year}"


class Team(models.Model):
    """
    Externally sourced Team data should land here eventually so
    Team is its own model for now.

    Again, this isn't necessary for the smaller design. A simpler
    design would be to have the home and away team names on Match
    and call it a day.
    """

    location = models.CharField(max_length=255, blank=True)
    mascot = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=3)

    def __str__(self) -> str:
        return " - ".join(filter(None, [self.location, self.mascot]))


class Match(models.Model):
    """
    The entity to encapsulate all relevant data with a particular
    match. Which users perform their tipping bets onto. Relates to
    the team model, however team modifications are not intended to
    be performed by match data.

    Each Match is expected to have its own round number, while
    belonging to a related season which keeps track of which
    year and season it's been played in.
    """

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matches")
    round_number = models.PositiveSmallIntegerField()
    home_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="home_matches",
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="away_matches",
    )
    kickoff_time = models.DateTimeField()

    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Season {self.season.name}: Round {self.round_number} -- {self.home_team.abbreviation} vs. {self.away_team.abbreviation}"
