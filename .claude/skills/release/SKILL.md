---
name: release
description: Release a new version to PyPI through a GitHub release, with clean release notes.
disable-model-invocation: true
---

# Release

A GitHub release starts the `.github/workflows/publish.yml` workflow. It builds the package and publishes
it to PyPI with Trusted Publishing. There is no PyPI token and no manual `uv publish` step. You cannot undo
a publish.

## Steps

1. Be on an up-to-date `main` with a clean tree. `bash scripts/test.sh` must pass.
2. Find the version in `pyproject.toml` and the last tag (`git describe --tags --abbrev=0`). Propose the
   new version from the changes since the last tag. The tag has no `v` prefix, for example `0.4.0`.
3. Update `[project].version` in `pyproject.toml`. It is the only place of the version. Run `uv lock`.
   Commit both files with `chore: release <version>` through a PR.
4. Create `plans/release-<tag>/` and generate the notes:

   ```bash
   gh api repos/{owner}/{repo}/releases/generate-notes -f tag_name=<tag> -f target_commitish=main --jq .body > plans/release-<tag>/notes.md
   ```

5. Edit `plans/release-<tag>/notes.md` (gitignored):
   - Remove the "What's Changed" lines for PRs from `dependabot[bot]` or from `dependabot/` branches.
   - Remove the "New Contributors" lines for `dependabot[bot]` and for the repository owner.
   - Remove each section that is then empty, with its heading.
6. **Show the tag, the target branch, and the notes to the user. Wait for approval.**
7. Run `gh release create <tag> --target main --title <tag> --notes-file plans/release-<tag>/notes.md`.
8. Check the `publish.yml` run: `gh run list --workflow publish.yml --limit 1`.
9. After the publish, set the next development version (`<next>-dev`) in `pyproject.toml`, run `uv lock`,
   and commit with `chore: back to development`.
