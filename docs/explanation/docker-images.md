# Docker images

Two Dockerfiles, one per build context.

## Backend

`backend/Dockerfile`. `base` installs uv and copies only `pyproject.toml` and
`uv.lock`, so the dependency layer is cached independently of source changes.
`production` and `test` each sync from that base — `--no-dev` and
`--group dev` respectively — then copy the source. `release` builds on `test`
and adds git, which semantic-release needs.

Both sync with `--no-install-project`: `manage.py` puts `/app` on `sys.path`,
so the package itself never needs installing.

## Frontend

`frontend/Dockerfile`. `base` → `test` / `production`.

## Docs

No Dockerfile. The `docs` compose service runs `squidfunk/mkdocs-material`
directly against a bind mount, so edits reload without a rebuild, and CI runs
the same service with a different command:

```bash
docker compose -f docker-compose.yml run --rm docs build --strict -d /tmp/site
```

`-d` keeps the output off the read-only mount. Building an image for this would
mean a third Dockerfile at the repository root — `mkdocs.yml` and `docs/` sit
outside both existing build contexts — for no gain over mounting them.
