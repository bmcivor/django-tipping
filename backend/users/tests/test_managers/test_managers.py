import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase


class UsersManagersTests(TestCase):
    USER_EMAIL = "example@user.com"
    USER_PASSWORD = "aPassword"

    def test_create_user(self):
        """
        Setup: Create a raw user email and password to be used when
        creating the test user.

        Expectations: User is successfully created with the correct
        email and password.
        """
        User = get_user_model()
        user = User.objects.create_user(
            email=self.USER_EMAIL, password=self.USER_PASSWORD
        )

        self.assertEqual(user.email, self.USER_EMAIL)
        self.assertTrue(user.check_password(self.USER_PASSWORD))

    def test_create_user__requires_email(self):
        """
        Setup: Create a raw password and try to create a new user
        from just this.

        Expectations: User is not successfully created and the
        correct exception is used, with the correct error message.
        """
        User = get_user_model()
        with pytest.raises(ValidationError) as exc:
            User.objects.create_user(email=None, password=self.USER_PASSWORD)

        self.assertEqual(exc.value.args[0], "An email address must be provided.")

    def test_create_user__requires_unique_email(self):
        """
        Setup: Create a raw user email and password, then continue to create
        the same user twice.

        Expectations: User is not successfully created and the correct
        exception is used, with the correct error message.
        """
        User = get_user_model()
        User.objects.create_user(email=self.USER_EMAIL, password=self.USER_PASSWORD)

        with pytest.raises(ValidationError) as exc:
            User.objects.create_user(email=self.USER_EMAIL, password=self.USER_PASSWORD)

        self.assertEqual(
            exc.value.args[0], "A user is already registered with this email."
        )

    def test_create_user__successfully_handles_multiple_creations(self):
        """
        Setup: Create 2 different raw usernames and passwords, then
        attempt to create 2 new test users from this set.

        Expectations: Both users are created successfully.
        """
        second_user_email = "another@example.com"
        second_user_password = "anotherPassword"

        User = get_user_model()
        User.objects.create_user(email=self.USER_EMAIL, password=self.USER_PASSWORD)
        User.objects.create_user(email=second_user_email, password=second_user_password)

    def test_create_user__requires_password(self):
        """
        Setup: Create a raw user email to be used when creating
        the test user. Do not create a password.

        Expectations: User is not successfully created and the
        correct exception is used, with the correct error message.
        """
        User = get_user_model()

        with pytest.raises(ValidationError) as exc:
            User.objects.create_user(email=self.USER_EMAIL, password=None)

        self.assertEqual(exc.value.args[0], "A password must be provided.")

    def test_create_user__requires_minimum_length(self):
        """
        Setup: Create a raw user email to be used when creating
        the test user. As well as a password, but keep it to a
        length of 5.

        Expectations: User is not successfully created and the
        validation method provides an appropriate error message.
        """
        User = get_user_model()

        with pytest.raises(ValidationError) as exc:
            User.objects.create_user(
                email=self.USER_EMAIL, password=self.USER_PASSWORD[0:4]
            )

        self.assertEqual(
            exc.value.args[0][0].message,
            "This password is too short. It must contain at least 8 characters.",
        )

    def test_create_user__requires_non_numeric(self):
        """
        Setup: Create a raw user email to be used when creating
        the test user. As well as a password, but ensure
        it is constructed completely of numbers.

        Expectations: User is not successfully created and the
        validation method provides an appropriate error message.
        """
        User = get_user_model()

        with pytest.raises(ValidationError) as exc:
            User.objects.create_user(email=self.USER_EMAIL, password="58291046")

        self.assertEqual(
            exc.value.args[0][0].message, "This password is entirely numeric."
        )

    def test_create_user__requires_non_common_password(self):
        """
        Setup: Create a raw user email to be used when creating
        the test user. As well as a password, that is considered
        common. "password" for example.

        Expectations: User is not successfully created and the
        validation method provides an appropriate error message.
        """
        User = get_user_model()

        with pytest.raises(ValidationError) as exc:
            User.objects.create_user(email=self.USER_EMAIL, password="password")

        self.assertEqual(exc.value.args[0][0].message, "This password is too common.")

    def test_create_user__requires_non_similar_to_user_attributes(self):
        """
        Setup: Create a raw user email to be used when creating
        the test user. As well as a password, but make it the
        same as the user email. Without .com.

        Expectations: User is not successfully created and the
        validation method provides an appropriate error message.
        """
        User = get_user_model()

        with pytest.raises(ValidationError) as exc:
            User.objects.create_user(
                email=self.USER_EMAIL, password=self.USER_EMAIL[:-4]
            )

        self.assertEqual(
            exc.value.args[0][0].message,
            "The password is too similar to the %(verbose_name)s.",
        )

    def test_create_user__does_not_return_user_on_failure(self):
        """
        Setup: Create a raw user email and password to create 2
        test user, but enforce a silent IntegrityError failure
        by making a large last_name.

        Expectations: On failure a user object should not be
        created.
        """
        User = get_user_model()

        with pytest.raises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                email=self.USER_EMAIL, password=self.USER_PASSWORD, is_staff=None
            )

        self.assertEqual(User.objects.count(), 0)

    def test_create_superuser(self):
        """
        Setup: Create a raw user email and password to create
        a test superuser.

        Expectations: Superuser is successfully created with
        is_staff, is_admin and is_superuser set.
        """
        User = get_user_model()
        user = User.objects.create_superuser(
            email=self.USER_EMAIL, password=self.USER_PASSWORD
        )

        self.assertIs(user.is_staff, True)
        self.assertIs(user.is_active, True)
        self.assertIs(user.is_superuser, True)
