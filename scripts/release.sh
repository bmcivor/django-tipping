#!/usr/bin/env bash
set -euo pipefail

# Runs python-semantic-release inside the release container, which has git
# installed and the dev dependency group synced.
#
# Arguments pass straight through:
#
#   ./scripts/release.sh --noop version --minor   # report the bump, write nothing
#   ./scripts/release.sh version --patch          # bump, commit, tag
#
# --noop is a global flag and must come before the subcommand.
#
# Runs as the invoking user so pyproject.toml and uv.lock stay owned by you
# rather than root, and passes your git identity through so the release commit
# is attributed correctly.

docker compose -f docker-compose.yml run --rm --no-deps --build \
    --user "$(id -u):$(id -g)" \
    -e GIT_AUTHOR_NAME="$(git config user.name)" \
    -e GIT_AUTHOR_EMAIL="$(git config user.email)" \
    -e GIT_COMMITTER_NAME="$(git config user.name)" \
    -e GIT_COMMITTER_EMAIL="$(git config user.email)" \
    -e GH_TOKEN="${GH_TOKEN:-}" \
    release semantic-release "$@"
