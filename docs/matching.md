# Matching rules

trakit is a rule-based matcher, not a general parser. The rules are in `trakit/patterns.py`,
`trakit/words.py`, `trakit/language.py`, `trakit/context.py`, and `trakit/converters/`.

## Change a rule

- Add a case to `tests/test_scenarios.yml` for each new behavior. The format is `input: {expected guess}`,
  or `input: {}` when trakit must find nothing. This file is the main regression suite for the matching.
- Add negative cases too. A new word changes the result for each trakit user. Show that the current
  results do not change.

## Flags

The flag patterns are in the `others` Rebulk in `trakit/patterns.py`. Each match must have a separator on
both sides (`seps` in `trakit/words.py`). A pattern can contain a character that is not in `seps`, for
example `&`.

- A flag code that is also a country code (`cc`, `ad`) must be in `ignored_words` in `tests/generator.json`.
  If it is not there, the language rule reads it as a country (`English AD` gives `en-AD`).
- A short code that is also a language or country code (`HI`, `AD`) has the tag `after-language`. The
  rule `RemoveCodeWithoutLanguage` removes it when no language comes before it.
- A common word that is a flag only in some positions (`signs`, `foreign`) has the tag
  `start-or-next-to-language`. The rule `RemoveWordNotAtStartOrNextToLanguage` keeps it only at the start
  of the title, or when only separators come between the language and the word. `Styled Signs` and
  `English (Signs)` give `forced`. `Full Subtitles Signs` does not.

## Generated data

`trakit/data/config.json` holds the country and language synonyms, the scripts, the regions, and the
ignored words. It is generated data. Never edit it by hand.

To change it:

1. Update `tests/generator.json`, or the sources that it reads:
   [mledoze/countries](https://github.com/mledoze/countries) and
   [mozilla/language-mapping-list](https://github.com/mozilla/language-mapping-list).
2. Run `uv run pytest -q tests/test_generate.py`. It downloads the sources (network access is necessary)
   and writes tests/generated/config.json (gitignored).
3. Copy that file over `trakit/data/config.json`.

`test_generate_config` in `tests/test_generate.py` fails when the two files are different.
