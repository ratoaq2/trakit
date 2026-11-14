# Architecture

trakit is a library and a CLI. It guesses metadata from a track title or a file name: language, SDH,
forced, closed caption, commentary, descriptive, and alternate version. It uses
[rebulk](https://github.com/guessit-io/rebulk) for the rule-based matching and
[babelfish](https://github.com/Diaoul/babelfish) for the language and country codes. It comes from the
same family as [GuessIt](https://github.com/guessit-io/guessit) and [KnowIt](https://github.com/ratoaq2/knowit).

## Modules

| Module | Role |
| --- | --- |
| `trakit/api.py` | `TrakItApi`, the module-level `trakit()`, and `default_api`. The public entry point. |
| `trakit/__main__.py` | The CLI (argparse) with JSON and YAML output. The `trakit` entry point in `[project.scripts]`. |
| `trakit/config.py` | Loads `trakit/data/config.json`: synonyms, scripts, regions, and ignored words. |
| `trakit/context.py` | `Context` for one call: the expected language and the input type (track name or file name). |
| `trakit/patterns.py` | Configures the rebulk matcher: the rules and the patterns. See `docs/matching.md`. |
| `trakit/words.py` | Word helpers: `to_words`, `to_combinations`, `to_sentence`, `blank_match`, and others. |
| `trakit/language.py` | The language rules. They use babelfish. |
| `trakit/converters/` | rebulk adapters: `GuessCountryConverter` and `GuessLanguageConverter`. |
| `trakit/data/config.json` | Generated data. See `docs/matching.md`, "Generated data". |
