# django-tipping backend

Django project for django-tipping. Packaged with
[uv](https://docs.astral.sh/uv/); this directory is the Python project root.

## Layout

| Path | Contents |
|---|---|
| `manage.py` | Django entry point |
| `tipping/` | Project package — settings, URLs, WSGI/ASGI |
| `users/` | `users` app — holds the custom user model |
| `pyproject.toml` | Dependencies and tool configuration |
| `uv.lock` | Resolved dependency versions, committed |
| `Dockerfile` | `base` → `production` / `test` / `release` stages |

## Documentation

In [`docs/`](../docs/) at the repository root — `docker compose up docs` serves
it on <http://localhost:8001>.

| | |
|---|---|
| [Running commands](../docs/guides/running-commands.md) | `manage.py` through compose |
| [Testing](../docs/guides/testing.md) | pytest with pytest-django |
| [Quality checks](../docs/guides/quality-checks.md) | Ruff and mypy |
| [Dependencies](../docs/guides/dependencies.md) | uv |
| [Configuration](../docs/reference/configuration.md) | Database, email, auth settings |
| [Users and authentication](../docs/explanation/users-and-auth.md) | The custom user model and allauth |
| [Docker images](../docs/explanation/docker-images.md) | What each stage does |

## Licence

MIT — see [LICENSE](LICENSE).
