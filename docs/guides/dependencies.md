# Dependencies

## Backend

Packaged with [uv](https://docs.astral.sh/uv/); `backend/` is the Python
project root.

```bash
uv sync --frozen
```

`--frozen` installs exactly what `uv.lock` specifies. To change a dependency,
edit `pyproject.toml` and run `uv lock`, or use `uv add` / `uv add --dev` to do
both.

Note that `uv` creates its environment in `backend/.venv/` and ignores an
already-activated virtualenv elsewhere. Use `uv run <command>` rather than
calling `python` directly.

## Frontend

Install through the container so nothing lands on the host:

```bash
docker compose run --rm frontend npm i -D <package>
```

The bind mount writes `package.json` and `package-lock.json` back to the host,
while `node_modules` stays in the container's anonymous volume. Running
`npm install` directly on the host works too, but then the host and container
copies diverge.
