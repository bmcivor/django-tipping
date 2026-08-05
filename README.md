# django-tipping

A Django application for managing and conducting sports tipping competitions.

## Getting started

```bash
docker compose up
```

Starts Postgres, waits for it to report healthy, applies migrations, then
brings up the backend on <http://localhost:8000> and the frontend on
<http://localhost:5173>.

## Documentation

Everything else lives in [`docs/`](docs/), built with
[mkdocs-material](https://squidfunk.github.io/mkdocs-material/):

```bash
docker compose up docs
```

Serves on <http://localhost:8001> with live reload. Or read the markdown
directly:

| | |
|---|---|
| [Getting started](docs/getting-started.md) | Requirements, first run, creating a superuser |
| [Running commands](docs/guides/running-commands.md) | `manage.py` through compose, and the traps |
| [Testing](docs/guides/testing.md) | `./scripts/test.sh` |
| [Quality checks](docs/guides/quality-checks.md) | `./scripts/lint.sh`, and fixing what it finds |
| [Dependencies](docs/guides/dependencies.md) | uv and npm |
| [Releases](docs/guides/releases.md) | python-semantic-release |
| [Services](docs/reference/services.md) | Compose services, ports, profiles |
| [Configuration](docs/reference/configuration.md) | Environment variables and settings |
| [Repository layout](docs/reference/repository-layout.md) | What lives where |
| [Users and authentication](docs/explanation/users-and-auth.md) | Custom user model, allauth |
| [Docker images](docs/explanation/docker-images.md) | Stage structure for the backend and frontend images |
| [CI](docs/explanation/ci.md) | The Jenkins pipeline |

## Layout

| Path | Contents |
|---|---|
| `backend/` | Django project (`tipping`) and its apps. See [backend/README.md](backend/README.md). |
| `frontend/` | Vite + React + TypeScript SPA. See [frontend/README.md](frontend/README.md). |
| `docs/` | Documentation source. |
| `scripts/` | Developer entry points. |

## Licence

MIT — see [LICENSE](backend/LICENSE).
