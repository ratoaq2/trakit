# Testing

Run the tests with `uv run pytest -q --tb=short tests`. `bash scripts/test.sh` runs all the checks of CI.

## Test files

| File | Content |
| --- | --- |
| `tests/test_scenarios.py`, `tests/test_scenarios.yml` | End-to-end cases: an input and the expected guess. The main regression suite. |
| `tests/test_generate.py` | Compares tests/generated/config.json (gitignored) with `trakit/data/config.json`. |
| `tests/generator.py`, `tests/generator.json` | Get the source data and generate tests/generated/ (gitignored). |
| Other `tests/test_*.py` | Unit tests with YAML fixtures. See below. |

## YAML fixtures

`tests/__init__.py` has `parameters_from_yaml`. It finds the fixture by name:

- `tests/test_<name>.py` reads `tests/test_<name>.yml` for the whole module.
- A test function `<case_name>` reads `tests/test_<name>__<case_name>.yml`.

Put the test data in a YAML fixture. Do not put it in `pytest.mark.parametrize`.

## Bug fix

For a matching bug, the failing test is a new case in `tests/test_scenarios.yml`. The order of the commits
is in `docs/workflow.md`.
