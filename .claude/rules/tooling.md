---
paths:
  - "pyproject.toml"
  - ".python-version"
  - ".pre-commit-config.yaml"
  - ".github/workflows/**"
  - "scripts/**"
---

# Tooling

These files define the commands and checks. When you change one, make sure that the commands in
`CLAUDE.md` and the setup in `CONTRIBUTING.md` are still correct, and that `scripts/test.sh` still runs the
same checks as CI. If a check must also run before a commit, add it to `.pre-commit-config.yaml`.

Python versions: the CI matrix (`.github/workflows/test.yml`), `requires-python`, and the `classifiers`
in `pyproject.toml` list each Python version that is not end of life. Change all three together.
`.python-version` is the newest version of the CI matrix. `.github/workflows/publish.yml` builds with it. Dependabot does not do this.
