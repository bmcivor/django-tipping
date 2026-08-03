# django-tipping backend

Django project for django-tipping. Packaged with [uv](https://docs.astral.sh/uv/); this directory is the Python project root.

## Layout

| Path | Contents |
|---|---|
| `manage.py` | Django entry point |
| `tipping/` | Project package — settings, URLs, WSGI/ASGI |
| `users/` | `users` app |
| `pyproject.toml` | Dependencies and tool configuration |
| `uv.lock` | Resolved dependency versions, committed |
| `Dockerfile` | `base` → `production` / `test` stages |

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
| `POSTGRES_DB` | `django` |
| `POSTGRES_USER` | `django` |
| `POSTGRES_PASSWORD` | `django` |
| `POSTGRES_HOST` | `db` |
| `POSTGRES_PORT` | `5432` |

`POSTGRES_HOST` defaults to `db`, which only resolves inside the compose network. Running `manage.py` on the host requires overriding it, and `db` publishes no host port, so there is nothing to reach by default.

## Tests

pytest with `pytest-django`. Django creates and drops its own `test_django` database inside the running Postgres instance, so no separate test database service exists.

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
docker compose run --rm --no-deps backend-test ruff format .
docker compose run --rm --no-deps backend-test ruff check --fix .
```

`ruff format` is a Black-compatible formatter and `ruff check` is the linter, so neither Black nor isort is needed separately. With no `[tool.ruff.lint]` block the defaults apply — `E4`, `E7`, `E9` and `F`. Import sorting (`I`) is not in that set and has to be selected explicitly.

mypy uses `django-stubs` through the `mypy_django_plugin.main` plugin, with `[tool.django-stubs] django_settings_module` pointing at `tipping.settings`. Without that plugin registration the stubs are installed but inert.

## Docker

Three stages. `base` installs uv and copies only `pyproject.toml` and `uv.lock`, so the dependency layer is cached independently of source changes. `production` and `test` each sync from that base — `--no-dev` and `--group dev` respectively — then copy the source.

Both sync with `--no-install-project`: `manage.py` puts `/app` on `sys.path`, so the package itself never needs installing.
