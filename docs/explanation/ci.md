# CI

`Jenkinsfile` runs four stages on the Jenkins instance managed by
vertex-studio, where the repo is registered via `jenkins_repos` in that
project's inventory.

| Stage | Command |
|---|---|
| Backend tests | `./scripts/test.sh backend` |
| Frontend tests | `./scripts/test.sh frontend` |
| Backend quality checks | `./scripts/lint.sh backend` |
| Frontend quality checks | `./scripts/lint.sh frontend` |

Any stage failing fails the build, so lint findings block a merge.

The `post { always }` block tears the stack down with
`docker compose down -v --remove-orphans`, tolerant of failure so a build that
fell over before starting anything doesn't fail again during cleanup.

## Documentation

Not built in CI. `mkdocs build --strict` is a local check:

```bash
docker compose run --rm docs build --strict -d /tmp/site
```
