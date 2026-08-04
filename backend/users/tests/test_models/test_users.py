from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from users.models import User


class UsersModelTests(TestCase):
    def test_users__email_can_not_be_empty(self):
        """
        Setup: Attempt to create a user with an empty email.

        Expectations: On failure a user object should not be
        created.
        """
        with self.assertRaises(IntegrityError), transaction.atomic():
            User(email="", first_name="A", last_name="B").save()

        self.assertEqual(User.objects.count(), 0)

    def test_users__str_display(self):
        """
        Setup: Create a raw user email and password to be used when
        creating the test user.

        Expectations: When printing a User object the email is
        displayed.
        """
        user = User.objects.create_user(email="user@example.com", password="aPassword")

        self.assertEqual(user.__str__(), user.email)
