# Quality checks

```bash
./scripts/lint.sh            # backend then frontend
./scripts/lint.sh backend    # ruff format --check, ruff check, mypy
./scripts/lint.sh frontend   # eslint, prettier --check
```

Checks only — nothing here rewrites source. Every check runs even when an
earlier one fails, so a single pass shows all outstanding work, and the script
exits non-zero if any of them reported something.

Unlike `test.sh` there is no teardown, because linting needs no database and a
run should not disturb a stack you already have up. It also passes `--no-deps`,
so checking the backend doesn't boot Postgres and apply migrations first.

## Fixing what it reports

```bash
./scripts/fix.sh             # backend then frontend
./scripts/fix.sh backend     # ruff format, ruff check --fix
./scripts/fix.sh frontend    # prettier --write, eslint --fix
```

The write counterpart to `lint.sh` — everything it runs modifies source. Same
shape otherwise: every step runs even when an earlier one fails, it exits
non-zero if any did, and there is no teardown.

It runs against `backend` and `frontend`, not `backend-test` or
`frontend-test`. Those two are where writes go missing: `frontend-test` never
has a bind mount, and `backend-test` only gets one from
`docker-compose.override.yml`, which these scripts drop by passing
`-f docker-compose.yml`. A fixer run there appears to succeed and changes
nothing.

It also passes `--user "$(id -u):$(id -g)"`, so rewritten files are owned by
you rather than root.

## Backend tooling

Ruff and mypy, both configured in `backend/pyproject.toml`.

`ruff format` is a Black-compatible formatter and `ruff check` is the linter,
so neither Black nor isort is needed separately. With no `[tool.ruff.lint]`
block the defaults apply — `E4`, `E7`, `E9` and `F`. Import sorting (`I`) is
not in that set and has to be selected explicitly.

mypy uses `django-stubs` through the `mypy_django_plugin.main` plugin, with
`[tool.django-stubs] django_settings_module` pointing at `tipping.settings`.
Without that plugin registration the stubs are installed but inert.

That plugin walks `INSTALLED_APPS` and imports each app's models. allauth ships
no `py.typed` marker, so an override tells mypy to treat it as untyped rather
than erroring:

```toml
[[tool.mypy.overrides]]
module = ["allauth.*"]
ignore_missing_imports = true
```

## Frontend tooling

`npm run lint` (ESLint, configured in `eslint.config.js`) and
`npx prettier --check .`.

Prettier has no config file, so it runs on its defaults.
`eslint-config-prettier` — the package that turns off ESLint rules Prettier
would otherwise fight over — is not installed; current typescript-eslint
presets carry few stylistic rules, so the two have not collided yet.
