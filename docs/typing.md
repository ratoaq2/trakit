# Typing

`mypy --strict` checks all of the repository: `trakit/` and `tests/`. The settings are in `[tool.mypy]`
in `pyproject.toml`.

- Every function has a return type, also `-> None`.
- Type the test fixture data with a `typing.TypedDict`, not with a loose `Mapping[str, str | int]`. See
  `WordFixture` in `tests/test_words.py`.
- Use `typing.Any` only at a real dynamic boundary: the JSON config load (`trakit/config.py`), the YAML
  fixture load, and the loose types of rebulk (`Match`, `Rebulk`). Do not use it to skip a type.

## The two `type: ignore`

`trakit/converters/` has two `# type: ignore[misc]`. They are necessary. The converters are subclasses of
the babelfish classes `LanguageReverseConverter` and `CountryReverseConverter`. babelfish has no stubs, so
mypy sees these base classes as `Any`. Do not add a new blanket ignore without the same level of reason.

## Libraries without stubs

The mypy overrides in `pyproject.toml` list the libraries without stubs.
