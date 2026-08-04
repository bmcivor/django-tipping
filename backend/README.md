# django-tipping backend

Django project for django-tipping. Packaged with [uv](https://docs.astral.sh/uv/); this directory is the Python project root.

## Layout

| Path | Contents |
|---|---|
| `manage.py` | Django entry point |
| `tipping/` | Project package — settings, URLs, WSGI/ASGI |
| `users/` | `users` app — holds the custom user model |
| `pyproject.toml` | Dependencies and tool configuration |
| `uv.lock` | Resolved dependency versions, committed |
| `Dockerfile` | `base` → `production` / `test` stages |

## Users

`AUTH_USER_MODEL` is `users.User`, not Django's default. Email is the login
identifier — `username` is removed and `USERNAME_FIELD` is `email`, since
sign-in is expected to go through social providers that supply no username.

Email is unique and mandatory. `CustomUserManager` rejects a missing address
with a readable error, and a check constraint makes an empty one unreachable
regardless of how the row is written. The reasoning is in the model's
docstring.

## Dependencies

```bash
uv sync --frozen
```

`--frozen` installs exactly what `uv.lock` specifies. To change a dependency, edit `pyproject.toml` and run `uv lock`, or use `uv add` / `uv add --dev` to do both.

Note that `uv` creates its environment in `.venv/` here and ignores an already-activated virtualenv elsewhere. Use `uv run <command>` rather than calling `python` directly.

## Database settings

`DATABASES` is configured from the environment, with defaults matching the compose `db` service:

| Variable | Default |
|---|---|
| `POSTGRES_DB` | `django-tipping` |
| `POSTGRES_USER` | `django` |
| `POSTGRES_PASSWORD` | `django` |
| `POSTGRES_HOST` | `db` |
| `POSTGRES_PORT` | `5432` |

`POSTGRES_HOST` defaults to `db`, which only resolves inside the compose network. Running `manage.py` on the host requires overriding it, and `db` publishes no host port, so there is nothing to reach by default.

## Running manage.py commands

From the repository root, since that is where the compose file lives:

```bash
docker compose run --rm --user "$(id -u):$(id -g)" backend python manage.py makemigrations
docker compose run --rm --user "$(id -u):$(id -g)" backend python manage.py createsuperuser
```

Two things make that work, and both fail quietly if you drop them.

**A service carrying a bind mount.** `backend` mounts source in the base compose file, so it always works. `migrate` and `backend-test` only get a mount from `docker-compose.override.yml`, so they work under a plain `docker compose` and not under `test.sh`, `lint.sh` or `fix.sh`, which pass `-f docker-compose.yml` and drop the override. Run `makemigrations` on a service with no mount and the file is written inside the container and thrown away with it.

**`--user`.** The Dockerfile sets no `USER`, so the container is root and anything it writes through a bind mount is root-owned on your host.

Add `--no-deps` for commands that need no database — `makemigrations` compares models against migration files on disk. It will warn that it could not check migration history, which is harmless; drop the flag to silence it and let `db` start.

`createsuperuser` prompts for email, first name and last name rather than a username, since `USERNAME_FIELD` is `email` and `REQUIRED_FIELDS` names the other two.

## Tests

pytest with `pytest-django`. Django creates and drops its own `test_django-tipping` database inside the running Postgres instance, so no separate test database service exists.

Run them through the stack from the repository root:

```bash
../scripts/test.sh backend
```

## Quality checks

Ruff and mypy, both configured in `pyproject.toml`:

```bash
../scripts/lint.sh backend
```

Runs `ruff format --check`, then `ruff check`, then `mypy`. All three run even if an earlier one fails, and nothing rewrites source — fixing is manual:

```bash
docker compose run --rm --no-deps backend ruff format .
docker compose run --rm --no-deps backend ruff check --fix .
```

`backend-test` also works for this, but only because `docker-compose.override.yml` adds a bind mount to it. Under `lint.sh`, which passes `-f docker-compose.yml` and so drops the override, it has no mount and anything it rewrites is lost with the container. `backend` mounts source in the base file, so it works either way.

`ruff format` is a Black-compatible formatter and `ruff check` is the linter, so neither Black nor isort is needed separately. With no `[tool.ruff.lint]` block the defaults apply — `E4`, `E7`, `E9` and `F`. Import sorting (`I`) is not in that set and has to be selected explicitly.

mypy uses `django-stubs` through the `mypy_django_plugin.main` plugin, with `[tool.django-stubs] django_settings_module` pointing at `tipping.settings`. Without that plugin registration the stubs are installed but inert.

## Docker

Three stages. `base` installs uv and copies only `pyproject.toml` and `uv.lock`, so the dependency layer is cached independently of source changes. `production` and `test` each sync from that base — `--no-dev` and `--group dev` respectively — then copy the source.

Both sync with `--no-install-project`: `manage.py` puts `/app` on `sys.path`, so the package itself never needs installing.
