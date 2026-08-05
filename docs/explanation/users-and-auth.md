# Users and authentication

## The user model

`AUTH_USER_MODEL` is `users.User`, not Django's default. Email is the login
identifier — `username` is removed and `USERNAME_FIELD` is `email`, since
sign-in is expected to go through social providers that supply no username.

Email is unique and mandatory. `CustomUserManager` rejects a missing address
with a readable error, and a check constraint makes an empty one unreachable
regardless of how the row is written. The reasoning is in the model's
docstring.

## Admin

`django.contrib.auth.admin.UserAdmin` handles passwords properly but is written
for Django's default user, so its `fieldsets`, `add_fieldsets`, `list_display`,
`search_fields` and `ordering` all name `username`, as do `UserChangeForm` and
`UserCreationForm`. All of those are overridden. A plain `ModelAdmin` would
avoid that work but renders `password` as an editable text field and saves
whatever is typed into it directly.

## allauth

[django-allauth](https://docs.allauth.org/) provides the signup, verification
and login flows, including its own views and templates. It ships its own
migrations, so its tables come from `migrate`.

`EmailAddress` is the table that matters: it tracks addresses and their
verified state, and is the source of truth for verification rather than
`User.email`.

### Configuring it against a model with no username

allauth defaults to username-based auth, and three settings have to move off
those defaults or signup fails outright:

- `ACCOUNT_LOGIN_METHODS` defaults to `{"username"}`
- `ACCOUNT_SIGNUP_FIELDS` defaults to
  `["username*", "email", "password1*", "password2*"]`
- `ACCOUNT_USER_MODEL_USERNAME_FIELD` defaults to `"username"`

The first two control the form. The third tells allauth what the *model* has —
allauth introspects the field independently of form configuration, so leaving
it at its default raises `FieldDoesNotExist` on the signup page even when the
form asks for nothing but an email.

!!! note "Most tutorials are out of date here"
    `ACCOUNT_AUTHENTICATION_METHOD`, `ACCOUNT_EMAIL_REQUIRED` and
    `ACCOUNT_USERNAME_REQUIRED` have been consolidated into
    `ACCOUNT_LOGIN_METHODS` and `ACCOUNT_SIGNUP_FIELDS`.

`AUTHENTICATION_BACKENDS` lists allauth's backend alongside Django's
`ModelBackend`, so admin login keeps working.

### Email verification

`ACCOUNT_EMAIL_VERIFICATION` is `mandatory`, which means allauth actually sends
mail. With no `EMAIL_BACKEND` configured Django falls back to SMTP, pointed at
the `mail` service — see [Configuration](../reference/configuration.md).

Verification is required despite the intended audience being older and
non-technical. They already deal with online banking, tax, share trading and
2FA, so the step is familiar ground. What matters is that the UI is explicit
about what is happening and what to do next.

## Social providers

Google, Apple and Facebook sign-in are the reason the model has no username.
`allauth.socialaccount` is installed and its tables migrated, but no providers
are configured yet.
