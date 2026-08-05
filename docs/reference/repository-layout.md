# Repository layout

## Root

| Path | Contents |
|---|---|
| `backend/` | Django project (`tipping`) and its apps |
| `frontend/` | Vite + React + TypeScript SPA |
| `docs/` | This documentation |
| `scripts/` | Developer entry points |
| `mkdocs.yml` | Documentation site configuration |
| `docker-compose.yml` | Service definitions for the whole stack |
| `docker-compose.override.yml` | Dev-only source bind mounts, merged automatically by compose |
| `Jenkinsfile` | CI pipeline |

## Backend

| Path | Contents |
|---|---|
| `manage.py` | Django entry point |
| `tipping/` | Project package — settings, URLs, WSGI/ASGI |
| `users/` | `users` app — holds the custom user model |
| `pyproject.toml` | Dependencies and tool configuration |
| `uv.lock` | Resolved dependency versions, committed |
| `Dockerfile` | `base` → `production` / `test` / `release` stages |
| `LICENSE` | MIT |

## Frontend

| Path | Contents |
|---|---|
| `src/` | Application source |
| `index.html` | Vite entry point |
| `vite.config.ts` | Dev server and plugin configuration |
| `eslint.config.js` | ESLint configuration |
| `tsconfig*.json` | TypeScript configuration |
| `Dockerfile` | `base` → `test` / `production` stages |
