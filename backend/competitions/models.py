from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from matches.models import Match, Season, Team

if TYPE_CHECKING:
    from users.models.users import User


class Competition(models.Model):
    """
    A tipping competition that users join and enter tips into.

    Runs on a single Season, which is what determines the matches its
    members tip on. Membership is the through model rather than a plain
    many to many, so joining a competition is a row that other tables can
    point at.
    """

    name = models.CharField(max_length=255)
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name="competitions",
    )
    members: "models.ManyToManyField[User, Membership]" = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Membership",
        related_name="competitions",
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.season})"


class Membership(models.Model):
    """
    A user's place in a competition.

    The through model for Competition.members. Tips point here rather than
    at the user directly, so the database refuses a tip in a competition
    the user never joined.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "competition"],
                name="unique_membership_user_competition",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} in {self.competition.name}"


class Tip(models.Model):
    """
    One member's pick for one match.

    Constrained to a single tip per member per match. Nothing stops the
    selected team being one that is not playing in that match -- comparing
    against the match's own columns spans rows, so it is not expressible
    as a CheckConstraint.
    """

    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name="tips",
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="tips",
    )
    selected_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="tips",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["membership", "match"],
                name="unique_tip_membership_match",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.membership.user} tipped {self.selected_team.abbreviation}"
