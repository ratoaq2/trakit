# trakit

Tiny library + CLI that guesses metadata (language, SDH, forced, closed caption,
commentary, alternate version) from a track title or filename. Same lineage as
[GuessIt](https://github.com/guessit-io/guessit)/[KnowIt](https://github.com/ratoaq2/knowit):
built on [rebulk](https://github.com/guessit-io/rebulk) for rule-based pattern matching, and
[babelfish](https://github.com/Diaoul/babelfish) for language/country codes.

## Commands

All commands run through [uv](https://docs.astral.sh/uv/) — never call `pip`/`python -m venv` directly.

```bash
uv sync --all-extras          # install/update the dev environment
bash scripts/test.sh          # ruff check, ruff format --check, mypy, pytest — the full CI gate
uv run pytest tests -vv       # tests only
uv run mypy trakit tests      # type-check only
uv run ruff check trakit tests --fix   # lint, autofixing
uv run ruff format trakit tests        # format
uv run pre-commit install     # one-time: enable git hooks
uv run pre-commit run --all-files      # run all hooks on demand
```

`scripts/test.sh` is the single source of truth for what CI runs — if you change a check, change it there
(and mirror it in `.pre-commit-config.yaml` if it's something that should also run pre-commit).

## Project map

```
trakit/
  api.py            TrakItApi + module-level trakit()/default_api — the public entry point
  __main__.py        CLI (argparse), JSON/YAML output, entry point `trakit` (see [project.scripts])
  config.py          Loads trakit/data/config.json (synonyms/scripts/regions/ignored words)
  context.py          Per-call Context(dict): expected_language, input type (trackname|filename)
  patterns.py         Wires up the rebulk Rebulk() matcher (rules, patterns) — the matching engine
  words.py            Tokenizing helpers: to_words, to_combinations, to_sentence, blank_match, ...
  language.py          Language-matching rule(s) against babelfish
  converters/          rebulk-facing adapters: GuessCountryConverter, GuessLanguageConverter
  data/config.json     Generated data: country/language synonyms, scripts, regions (see below)
tests/
  generator.py, generator.json          Fetches source data and regenerates tests/generated/*
  test_generate.py                      Diffs tests/generated/config.json against trakit/data/config.json
  test_scenarios.py + test_scenarios.yml  End-to-end input -> expected-guess cases (the main regression suite)
  test_*.py + test_*__*.yml              Unit tests, each paired with a YAML fixture of the same base name
```

## Working with matching rules

This is a rule-based matcher, not a general parser — when changing behavior in `patterns.py`, `words.py`,
`language.py`, or `converters/`:

- **Add/extend a case in `tests/test_scenarios.yml`** (`input string: {expected: guess}` or `{}` for no match).
  This YAML-driven scenario suite is the primary coverage mechanism for matching behavior, not just unit tests
  of individual functions.
- **Never hand-edit `trakit/data/config.json`** (country/language synonyms, scripts, regions). It's derived
  data. To change it: update `tests/generator.json` or the upstream sources it pulls from
  ([mledoze/countries](https://github.com/mledoze/countries),
  [mozilla/language-mapping-list](https://github.com/mozilla/language-mapping-list)), then run the generator
  (see `tests/generator.py: Generator.generate()`) to regenerate `tests/generated/config.json`, and copy that
  over `trakit/data/config.json`. `test_generate_config` in `tests/test_generate.py` fails if the two drift.
- Fixture files follow a strict naming convention: `tests/test_x.py` pairs with `tests/test_x.yml`
  (whole-module fixture) or `tests/test_x__case_name.yml` (per-test-function fixture), read via
  `tests/__init__.py::parameters_from_yaml`. Follow this convention for new tests rather than inlining
  parametrize data.

## Typing rules

- `mypy --strict` covers the **entire repo** (`trakit/` and `tests/`) — see `[tool.mypy]` in `pyproject.toml`.
  Every function needs a return type (`-> None` included); test fixture data should be typed with a
  `typing.TypedDict` (see `tests/test_words.py: WordFixture`) rather than loose `Mapping[str, str | int]`.
- `typing.Any` is allowed only at genuine dynamic boundaries — JSON config loading (`config.py`), YAML fixture
  loading, and rebulk's own loosely-typed `Match`/`Rebulk` API. It's not a shortcut for "didn't want to type
  this."
- The two `# type: ignore[misc]` in `converters/` are justified (subclassing rebulk's dynamically-constructed
  `LanguageReverseConverter`/`CountryReverseConverter` base classes) — don't add new blanket ignores without
  the same level of justification.

## Python support

`requires-python = ">=3.10"`. CI matrix and classifiers track every Python version that isn't EOL — when a
version goes EOL, drop it from `requires-python`, CI matrix (`.github/workflows/test.yml`), and
`classifiers` together; when a new version stabilizes, add it the same way (Dependabot does not do this part
automatically).

## Releasing

Version lives only in `[project].version` in `pyproject.toml` (read at runtime via `importlib.metadata`,
not hardcoded anywhere else). Bump it, run `uv lock`, commit both files. `publish.yml` builds and publishes
to PyPI via Trusted Publishing whenever a GitHub Release is created — there is no manual `uv publish` step
and no PyPI token in this repo.
