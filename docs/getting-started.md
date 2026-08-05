# Getting started

## Requirements

Docker with the Compose plugin. Nothing else — Python, Node and PostgreSQL all
run inside containers, and the dependency managers never touch your host.

## Bring the stack up

```bash
docker compose up
```

Starts Postgres, waits for it to report healthy, applies migrations, then
brings up the backend and frontend.

| What | Where |
|---|---|
| Django | <http://localhost:8000> |
| Django admin | <http://localhost:8000/admin/> |
| Vite dev server | <http://localhost:5173> |
| Mailpit | <http://localhost:8025> |

Only the unprofiled services start. The test, release and docs services are
excluded — see [Services](reference/services.md).

## Create a superuser

Nothing exists to log into the admin with until you make an account:

```bash
docker compose run --rm --user "$(id -u):$(id -g)" backend python manage.py createsuperuser
```

It prompts for email, first name and last name rather than a username. The
`--user` flag matters — see [Running commands](guides/running-commands.md) for
why.

## Serve these docs

```bash
docker compose up docs
```

On <http://localhost:8001>, with live reload over the bind mount.

## Next

- [Testing](guides/testing.md)
- [Quality checks](guides/quality-checks.md)
- [Running commands](guides/running-commands.md)
