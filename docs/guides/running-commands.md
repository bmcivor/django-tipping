# Running commands

## manage.py

From the repository root, since that is where the compose file lives:

```bash
docker compose run --rm --user "$(id -u):$(id -g)" backend python manage.py makemigrations
docker compose run --rm --user "$(id -u):$(id -g)" backend python manage.py createsuperuser
```

Two things make that work, and both fail quietly if you drop them.

**A service carrying a bind mount.** `backend` mounts source in the base
compose file, so it always works. `migrate` and `backend-test` only get a mount
from `docker-compose.override.yml`, so they work under a plain `docker compose`
and not under `test.sh`, `lint.sh` or `fix.sh`, which pass
`-f docker-compose.yml` and drop the override. Run `makemigrations` on a
service with no mount and the file is written inside the container and thrown
away with it.

**`--user`.** The Dockerfile sets no `USER`, so the container is root and
anything it writes through a bind mount is root-owned on your host.

Add `--no-deps` for commands that need no database — `makemigrations` compares
models against migration files on disk. It will warn that it could not check
migration history, which is harmless; drop the flag to silence it and let `db`
start.

`createsuperuser` prompts for email, first name and last name rather than a
username, since `USERNAME_FIELD` is `email` and `REQUIRED_FIELDS` names the
other two.

## Reaching the database

`POSTGRES_HOST` defaults to `db`, which only resolves inside the compose
network. Running `manage.py` on the host requires overriding it, and `db`
publishes no host port, so there is nothing to reach by default.

See [Configuration](../reference/configuration.md) for the full set of
variables.
