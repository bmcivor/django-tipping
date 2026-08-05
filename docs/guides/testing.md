# Testing

```bash
./scripts/test.sh            # backend then frontend
./scripts/test.sh backend    # backend only
./scripts/test.sh frontend   # frontend only
```

Arguments after `backend` are passed through to pytest:

```bash
./scripts/test.sh backend -k smoke
```

The script tears the stack down before and after each run and always rebuilds,
so a run never uses stale images. It invokes compose with
`-f docker-compose.yml`, which excludes the dev bind mounts in the override
file — test containers run the source baked into the image, matching what CI
does.

## Backend

pytest with `pytest-django`. Django creates and drops its own
`test_django-tipping` database inside the running Postgres instance, so no
separate test database service exists.

## Frontend

Vitest. The `test` script is `vitest run` — a single pass that exits, rather
than watch mode, so CI does not hang. For a watching loop locally, use
`npx vitest`.

Component tests will need a DOM environment (`jsdom` or `happy-dom`) and
`@testing-library/react`; neither is installed yet.
