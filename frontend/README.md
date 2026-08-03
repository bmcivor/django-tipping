# django-tipping frontend

Vite + React + TypeScript SPA, scaffolded from the `react-compiler-ts` template. The React Compiler runs as a Babel pass via `@vitejs/plugin-react`.

## Layout

| Path | Contents |
|---|---|
| `src/` | Application source |
| `index.html` | Vite entry point |
| `vite.config.ts` | Dev server and plugin configuration |
| `eslint.config.js` | ESLint configuration |
| `tsconfig*.json` | TypeScript configuration |
| `Dockerfile` | `base` → `test` / `production` stages |

## Dependencies

Install through the container so nothing lands on the host:

```bash
docker compose run --rm frontend npm i -D <package>
```

The bind mount writes `package.json` and `package-lock.json` back to the host, while `node_modules` stays in the container's anonymous volume. Running `npm install` directly on the host works too, but then the host and container copies diverge.

## Running

From the repository root:

```bash
docker compose up frontend
```

Serves on 5173 with HMR over the bind mount. The dev server binds `0.0.0.0` so the published port is reachable from the host.

## Tests

Vitest, run through the stack from the repository root:

```bash
../scripts/test.sh frontend
```

The `test` script is `vitest run` — a single pass that exits, rather than watch mode, so CI does not hang. For a watching loop locally, use `npx vitest`.

Component tests will need a DOM environment (`jsdom` or `happy-dom`) and `@testing-library/react`; neither is installed yet.

## Quality checks

ESLint and Prettier:

```bash
../scripts/lint.sh frontend
```

Runs `npm run lint` (ESLint, configured in `eslint.config.js`) and `npx prettier --check .`. Both run even if the first fails, and neither rewrites source:

```bash
npx prettier --write .
```

Prettier has no config file, so it runs on its defaults. `eslint-config-prettier` — the package that turns off ESLint rules Prettier would otherwise fight over — is not installed; current typescript-eslint presets carry few stylistic rules, so the two have not collided yet.

## Talking to the backend

The backend is reachable as `backend:8000` over the compose network. Proxy API calls through the dev server rather than hardcoding an origin, by adding to `vite.config.ts`:

```ts
server: {
  proxy: {
    '/api': { target: 'http://backend:8000', changeOrigin: true },
  },
}
```

No proxy is configured yet — Django currently serves only `/admin/`.
