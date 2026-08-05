# Releases

[python-semantic-release](https://python-semantic-release.readthedocs.io/), run
inside the `release` container so it has git and the dev dependencies:

```bash
./scripts/release.sh --noop version --minor   # report the bump, write nothing
./scripts/release.sh version --minor          # bump, commit, tag
```

`--noop` is a global flag and has to come before the subcommand. Always worth
running first — it prints every command it would execute, including the exact
`git add` and `git push`.

!!! warning "Releases are cut from the `tag-release` branch"
    `[tool.semantic_release.branches.main] match = "tag-release"` in
    `backend/pyproject.toml` names it, and semantic-release declines to release
    from anywhere else.

The bump level comes from conventional commit messages since the last tag —
`fix:` gives a patch, `feat:` a minor, `feat!:` or a `BREAKING CHANGE:` footer
a major. Passing `--patch`, `--minor` or `--major` forces it instead.

## What a release rewrites

- `backend/pyproject.toml` and `frontend/package.json` — the two version files
- `backend/uv.lock` — regenerated via the configured `build_command`
- `backend/CHANGELOG.md`

Then it commits the lot, tags `vX.Y.Z`, and pushes.

`assets` paths in that config resolve from the git root, unlike `version_toml`
and `version_variables`, which resolve from the working directory. That is why
the lockfile is listed as `backend/uv.lock`.

## Known failure

The push currently fails: the `GH_TOKEN` in use is a fine-grained PAT with no
access to this repository, so git falls back to prompting for credentials. The
version commit and tag are created locally before that point, so a failed
release leaves them behind.
