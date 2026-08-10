from datetime import UTC, datetime

import pytest
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from matches import models as matches_models


class MatchesModelTests(TestCase):
    def test_seasons(self):
        """
        Setup: Create a name and a valid year for a season/
        Expectations: A Season is created.
        """
        name = "NSWRL"
        year = 1985

        matches_models.Season(name=name, year=year).save()

        season = matches_models.Season.objects.get()

        self.assertEqual(season.name, name)
        self.assertEqual(season.year, year)
        self.assertEqual(season.__str__(), "NSWRL - 1985")

    def test_seasons__can_not_create_invalid_year_lower(self):
        """
        Setup: Create a year for a season, 1899.
        Expectations: Instantiating the model should throw
        an IntegrityError.
        """
        name = "AFL"
        year = 1899

        with pytest.raises(IntegrityError), transaction.atomic():
            matches_models.Season(name=name, year=year).save()

        self.assertEqual(matches_models.Season.objects.count(), 0)

    def test_seasons__can_not_create_invalid_year_upper(self):
        """
        Setup: Create a year for a season, 2101.
        Expectations: Instantiating the model should throw
        an IntegrityError.
        """
        name = "NHL"
        year = 2101

        with pytest.raises(IntegrityError), transaction.atomic():
            matches_models.Season(name=name, year=year).save()

        self.assertEqual(matches_models.Season.objects.count(), 0)

    def test_seasons__can_have_multiple_names_per_year(self):
        """
        Setup: Create a year and 2 different names, try to create a
        season twice.
        Expectations: Creates 2 seasons, to prove that the uniqueness
        is only applying per name, and not just unique years.
        """
        name_one = "Test One"
        name_two = "Test Two"
        year = 1990

        matches_models.Season(name=name_one, year=year).save()
        matches_models.Season(name=name_two, year=year).save()

        self.assertEqual(matches_models.Season.objects.count(), 2)

    def test_seasons__enforce_year_unique_for_name(self):
        """
        Setup: Create a year and a name for a season, try to create that
        season twice.
        Expectations: Instantiating the model should throw an IntegrityError.
        No Seasons should be created as this transaction is atomic.
        """
        name = "Ping Pong"
        year = 2026

        with pytest.raises(IntegrityError), transaction.atomic():
            matches_models.Season(name=name, year=year).save()
            matches_models.Season(name=name, year=year).save()

        self.assertEqual(matches_models.Season.objects.count(), 0)

    def test_teams(self):
        """
        Setup: Create a location, mascot and abbreviation for
        a team. Allow location to be blank.
        Expectations: A team is created.
        """
        location = ""
        mascot = "Dolphins"
        abbreviation = "RED"

        matches_models.Team(
            location=location, mascot=mascot, abbreviation=abbreviation
        ).save()

        team = matches_models.Team.objects.get()

        self.assertEqual(team.location, location)
        self.assertEqual(team.mascot, mascot)
        self.assertEqual(team.abbreviation, abbreviation)
        self.assertEqual(team.__str__(), "Dolphins")

    def test_matches(self):
        """
        Setup: Create a valid match, from a season, round_number,
        home and away team, kickoff time and home and away scores.
        Expectations: A match is created.
        """
        season = matches_models.Season.objects.create(name="NRL", year=2025)
        home_team = matches_models.Team.objects.create(
            location="Brisbane", mascot="Broncos", abbreviation="BRI"
        )
        away_team = matches_models.Team.objects.create(
            location="Melbourne", mascot="Storm", abbreviation="MEL"
        )

        round_number = 22
        kickoff_time = datetime(2025, 6, 22, 11, 0, 0, 0, tzinfo=UTC)
        home_score = 56
        away_score = 0

        match = matches_models.Match.objects.create(
            season=season,
            round_number=round_number,
            home_team=home_team,
            away_team=away_team,
            kickoff_time=kickoff_time,
            home_score=home_score,
            away_score=away_score,
        )

        self.assertEqual(match.season, season)
        self.assertEqual(match.round_number, round_number)
        self.assertEqual(match.home_team, home_team)
        self.assertEqual(match.away_team, away_team)
        self.assertEqual(match.kickoff_time, kickoff_time)
        self.assertEqual(match.home_score, home_score)
        self.assertEqual(match.away_score, away_score)
        self.assertEqual(match.__str__(), "Season NRL: Round 22 -- BRI vs. MEL")
