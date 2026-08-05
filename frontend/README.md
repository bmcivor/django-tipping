# django-tipping frontend

Vite + React + TypeScript SPA, scaffolded from the `react-compiler-ts`
template. The React Compiler runs as a Babel pass via `@vitejs/plugin-react`.

## Layout

| Path               | Contents                              |
| ------------------ | ------------------------------------- |
| `src/`             | Application source                    |
| `index.html`       | Vite entry point                      |
| `vite.config.ts`   | Dev server and plugin configuration   |
| `eslint.config.js` | ESLint configuration                  |
| `tsconfig*.json`   | TypeScript configuration              |
| `Dockerfile`       | `base` → `test` / `production` stages |

## Running

From the repository root:

```bash
docker compose up frontend
```

Serves on 5173 with HMR over the bind mount. The dev server binds `0.0.0.0` so
the published port is reachable from the host.

## Talking to the backend

The backend is reachable as `backend:8000` over the compose network. Proxy API
calls through the dev server rather than hardcoding an origin, by adding to
`vite.config.ts`:

```ts
server: {
  proxy: {
    '/api': { target: 'http://backend:8000', changeOrigin: true },
  },
}
```

No proxy is configured yet — Django currently serves only `/admin/` and
`/accounts/`.

## Documentation

In [`docs/`](../docs/) at the repository root — `docker compose up docs` serves
it on <http://localhost:8001>.

|                                                    |                                   |
| -------------------------------------------------- | --------------------------------- |
| [Testing](../docs/guides/testing.md)               | Vitest                            |
| [Quality checks](../docs/guides/quality-checks.md) | ESLint and Prettier               |
| [Dependencies](../docs/guides/dependencies.md)     | Installing through the container  |
| [Services](../docs/reference/services.md)          | Compose services, ports, profiles |
