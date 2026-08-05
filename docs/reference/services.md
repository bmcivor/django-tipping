# Services

| Service | Purpose | Host port | Profile |
|---|---|---|---|
| `backend` | Django dev server | 8000 | — |
| `frontend` | Vite dev server | 5173 | — |
| `db` | PostgreSQL 18 | not published | — |
| `mail` | Mailpit — catches outbound mail | 8025 | — |
| `migrate` | One-shot `manage.py migrate`, runs before `backend` starts | — | — |
| `backend-test` | pytest | — | `test` |
| `frontend-test` | Vitest | — | `test` |
| `docs` | mkdocs-material dev server | 8001 | `docs` |
| `release` | python-semantic-release | — | `release` |

`db` is deliberately not published to the host — everything reaches it as
`db:5432` over the compose network.

## Profiles

Services with a profile are excluded from `docker compose up`, so bringing the
stack up starts the unprofiled ones and nothing else.

Two things reach a profiled service without naming its profile:

- `docker compose run <service>` enables that service's own profiles, which is
  how the scripts in `scripts/` reach `backend-test`, `frontend-test` and
  `release`.
- `docker compose up <service>` does the same, which is how `docs` starts.

## Compose files

| File | Contents |
|---|---|
| `docker-compose.yml` | Every service definition |
| `docker-compose.override.yml` | Dev-only source bind mounts, merged automatically |

Compose merges the override file into every invocation unless told otherwise.
`test.sh`, `lint.sh` and `fix.sh` pass `-f docker-compose.yml` explicitly,
which drops it — so under those scripts `migrate` and `backend-test` have no
bind mount and run the source baked into the image. That is deliberate: it
matches what CI does.
