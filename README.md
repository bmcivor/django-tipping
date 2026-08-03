# django-tipping

A Django application for managing and conducting sports tipping competitions.

## Layout

| Path | Contents |
|---|---|
| `backend/` | Django project (`tipping`) and its apps. See [backend/README.md](backend/README.md). |
| `frontend/` | Vite + React + TypeScript SPA. See [frontend/README.md](frontend/README.md). |
| `scripts/` | Developer entry points. |
| `docker-compose.yml` | Service definitions for the whole stack. |
| `docker-compose.override.yml` | Dev-only source bind mounts, merged automatically by compose. |
| `Jenkinsfile` | CI pipeline. |

## Services

| Service | Purpose | Host port |
|---|---|---|
| `backend` | Django dev server | 8000 |
| `frontend` | Vite dev server | 5173 |
| `db` | PostgreSQL 18 | not published |
| `migrate` | One-shot `manage.py migrate`, runs before `backend` starts | — |
| `backend-test` | pytest | — |
| `frontend-test` | Vitest | — |

`db` is deliberately not published to the host — everything reaches it as `db:5432` over the compose network.

## Running

```bash
docker compose up
```

Starts Postgres, waits for it to report healthy, applies migrations, then brings up the backend and frontend.

## Tests

```bash
./scripts/test.sh            # backend then frontend
./scripts/test.sh backend    # backend only
./scripts/test.sh frontend   # frontend only
```

Arguments after `backend` are passed through to pytest:

```bash
./scripts/test.sh backend -k smoke
```

The script tears the stack down before and after each run and always rebuilds, so a run never uses stale images. It invokes compose with `-f docker-compose.yml`, which excludes the dev bind mounts in the override file — test containers run the source baked into the image, matching what CI does.

## CI

`Jenkinsfile` runs backend tests then frontend tests on the Jenkins instance managed by vertex-studio, where the repo is registered via `jenkins_repos` in that project's inventory.

## Licence

MIT — see [LICENSE](backend/LICENSE).
