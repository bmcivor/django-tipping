from datetime import UTC, datetime

import pytest
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from competitions import models as competitions_models
from matches import models as matches_models

User = get_user_model()


class CompetitionsModelTests(TestCase):
    def setUp(self):
        self.season = matches_models.Season.objects.create(name="NRL", year=2026)
        self.home_team = matches_models.Team.objects.create(
            location="Penrith", mascot="Panthers", abbreviation="PEN"
        )
        self.away_team = matches_models.Team.objects.create(
            location="Melbourne", mascot="Storm", abbreviation="MEL"
        )
        self.match = matches_models.Match.objects.create(
            season=self.season,
            round_number=1,
            home_team=self.home_team,
            away_team=self.away_team,
            kickoff_time=datetime(2026, 3, 5, 19, 50, tzinfo=UTC),
        )
        self.user = User.objects.create_user(
            email="tipper@example.com", password="Rhubarb!Custard42"
        )

    def test_competitions(self):
        """
        Setup: Create a competition against a season.
        Expectations: A Competition is created and reports its season.
        """
        name = "McIvor family"

        competitions_models.Competition.objects.create(name=name, season=self.season)

        competition = competitions_models.Competition.objects.get()

        self.assertEqual(competition.name, name)
        self.assertEqual(competition.season, self.season)
        self.assertEqual(competition.__str__(), "McIvor family (NRL - 2026)")

    def test_memberships(self):
        """
        Setup: Join a user to a competition.
        Expectations: A Membership is created and is reachable from both
        sides of the many to many.
        """
        competition = competitions_models.Competition.objects.create(
            name="McIvor family", season=self.season
        )

        competitions_models.Membership.objects.create(
            user=self.user, competition=competition
        )

        membership = competitions_models.Membership.objects.get()

        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.competition, competition)
        self.assertEqual(list(competition.members.all()), [self.user])
        self.assertEqual(list(self.user.competitions.all()), [competition])

    def test_memberships__enforce_unique_user_per_competition(self):
        """
        Setup: Join the same user to the same competition twice.
        Expectations: The second save should throw an IntegrityError. No
        Memberships should be created as this transaction is atomic.
        """
        competition = competitions_models.Competition.objects.create(
            name="McIvor family", season=self.season
        )

        with pytest.raises(IntegrityError), transaction.atomic():
            competitions_models.Membership.objects.create(
                user=self.user, competition=competition
            )
            competitions_models.Membership.objects.create(
                user=self.user, competition=competition
            )

        self.assertEqual(competitions_models.Membership.objects.count(), 0)

    def test_memberships__can_join_multiple_competitions(self):
        """
        Setup: Join one user to two different competitions.
        Expectations: Creates 2 memberships, to prove the uniqueness applies
        per competition and not per user.
        """
        competition_one = competitions_models.Competition.objects.create(
            name="McIvor family", season=self.season
        )
        competition_two = competitions_models.Competition.objects.create(
            name="Work comp", season=self.season
        )

        competitions_models.Membership.objects.create(
            user=self.user, competition=competition_one
        )
        competitions_models.Membership.objects.create(
            user=self.user, competition=competition_two
        )

        self.assertEqual(competitions_models.Membership.objects.count(), 2)

    def test_tips(self):
        """
        Setup: Record a tip for a match from a member of a competition.
        Expectations: A Tip is created against the membership, not the user.
        """
        competition = competitions_models.Competition.objects.create(
            name="McIvor family", season=self.season
        )
        membership = competitions_models.Membership.objects.create(
            user=self.user, competition=competition
        )

        competitions_models.Tip.objects.create(
            membership=membership, match=self.match, selected_team=self.home_team
        )

        tip = competitions_models.Tip.objects.get()

        self.assertEqual(tip.membership, membership)
        self.assertEqual(tip.match, self.match)
        self.assertEqual(tip.selected_team, self.home_team)
        self.assertEqual(tip.__str__(), "tipper@example.com tipped PEN")

    def test_tips__enforce_one_tip_per_match(self):
        """
        Setup: Record two tips from the same membership for the same match.
        Expectations: The second save should throw an IntegrityError. No Tips
        should be created as this transaction is atomic.
        """
        competition = competitions_models.Competition.objects.create(
            name="McIvor family", season=self.season
        )
        membership = competitions_models.Membership.objects.create(
            user=self.user, competition=competition
        )

        with pytest.raises(IntegrityError), transaction.atomic():
            competitions_models.Tip.objects.create(
                membership=membership, match=self.match, selected_team=self.home_team
            )
            competitions_models.Tip.objects.create(
                membership=membership, match=self.match, selected_team=self.away_team
            )

        self.assertEqual(competitions_models.Tip.objects.count(), 0)

    def test_tips__different_members_can_tip_the_same_match(self):
        """
        Setup: Two members of one competition each tip the same match.
        Expectations: Creates 2 tips, to prove the uniqueness applies per
        membership and not per match.
        """
        competition = competitions_models.Competition.objects.create(
            name="McIvor family", season=self.season
        )
        other_user = User.objects.create_user(
            email="other@example.com", password="Rhubarb!Custard42"
        )

        membership_one = competitions_models.Membership.objects.create(
            user=self.user, competition=competition
        )
        membership_two = competitions_models.Membership.objects.create(
            user=other_user, competition=competition
        )

        competitions_models.Tip.objects.create(
            membership=membership_one, match=self.match, selected_team=self.home_team
        )
        competitions_models.Tip.objects.create(
            membership=membership_two, match=self.match, selected_team=self.away_team
        )

        self.assertEqual(competitions_models.Tip.objects.count(), 2)
