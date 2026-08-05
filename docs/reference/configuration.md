# Configuration

Settings live in `backend/tipping/settings.py`. Anything environment-dependent
reads from the environment with a default matching the compose stack, so a
clean `docker compose up` needs nothing set.

## Database

| Variable | Default |
|---|---|
| `POSTGRES_DB` | `django-tipping` |
| `POSTGRES_USER` | `django` |
| `POSTGRES_PASSWORD` | `django` |
| `POSTGRES_HOST` | `db` |
| `POSTGRES_PORT` | `5432` |

`POSTGRES_HOST` defaults to `db`, which only resolves inside the compose
network. Running `manage.py` on the host requires overriding it, and `db`
publishes no host port, so there is nothing to reach by default.

## Email

| Variable | Default |
|---|---|
| `EMAIL_HOST` | `mail` |
| `EMAIL_PORT` | `1025` |
| `DEFAULT_FROM_EMAIL` | `noreply@django-tipping.local` |

No `EMAIL_BACKEND` is set, so Django uses its SMTP backend. The defaults point
it at the `mail` service — Mailpit, which accepts everything and delivers
nothing, with a web interface on <http://localhost:8025>.

## Authentication

Set in `settings.py` rather than the environment:

| Setting | Value |
|---|---|
| `AUTH_USER_MODEL` | `users.User` |
| `ACCOUNT_LOGIN_METHODS` | `{"email"}` |
| `ACCOUNT_SIGNUP_FIELDS` | `["email*", "password1*", "password2*"]` |
| `ACCOUNT_EMAIL_VERIFICATION` | `mandatory` |
| `ACCOUNT_USER_MODEL_USERNAME_FIELD` | `None` |
| `SITE_ID` | `1` |

See [Users and authentication](../explanation/users-and-auth.md) for why each
of those is what it is.
