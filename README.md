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

| Service | Purpose | Host port | Profile |
|---|---|---|---|
| `backend` | Django dev server | 8000 | — |
| `frontend` | Vite dev server | 5173 | — |
| `db` | PostgreSQL 18 | not published | — |
| `migrate` | One-shot `manage.py migrate`, runs before `backend` starts | — | — |
| `backend-test` | pytest | — | `test` |
| `frontend-test` | Vitest | — | `test` |
| `release` | python-semantic-release | — | `release` |

`db` is deliberately not published to the host — everything reaches it as `db:5432` over the compose network.

Services with a profile are excluded from `docker compose up`, so bringing the stack up starts the four unprofiled ones and nothing else. `docker compose run <service>` enables that service's own profile, which is why the scripts in `scripts/` reach them without naming one.

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

## Quality checks

```bash
./scripts/lint.sh            # backend then frontend
./scripts/lint.sh backend    # ruff format --check, ruff check, mypy
./scripts/lint.sh frontend   # eslint, prettier --check
```

Checks only — nothing here rewrites source. Every check runs even when an earlier one fails, so a single pass shows all outstanding work, and the script exits non-zero if any of them reported something.

Unlike `test.sh` there is no teardown, because linting needs no database and a run should not disturb a stack you already have up. It also passes `--no-deps`, so checking the backend doesn't boot Postgres and apply migrations first.

To fix what it reports, run the fixers against `backend` and `frontend`. Those always mount your source, so writes land on disk. `frontend-test` never has a mount and `backend-test` only gets one from the override file, so results there depend on how compose was invoked:

```bash
docker compose run --rm --no-deps backend ruff format .
docker compose run --rm --no-deps backend ruff check --fix .
docker compose run --rm --no-deps frontend npx prettier --write .
```

## CI

`Jenkinsfile` runs four stages — backend tests, frontend tests, then backend and frontend quality checks — on the Jenkins instance managed by vertex-studio, where the repo is registered via `jenkins_repos` in that project's inventory. Any stage failing fails the build, so lint findings block a merge.

## Licence

MIT — see [LICENSE](backend/LICENSE).
