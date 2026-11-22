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

- A short code that is also a language or country code (`HI`, `AD`) has the tag `after-language`. The
  rule `RemoveCodeWithoutLanguage` removes it when no language comes before it.
- A common word that is a flag only in some positions (`signs`, `foreign`) has the tag
  `start-or-next-to-language`. The rule `RemoveWordNotAtStartOrNextToLanguage` keeps it only at the start
  of the title, or when only separators come between the language and the word. `Styled Signs` and
  `English (Signs)` give `forced`. `Full Subtitles Signs` does not.
- A flag code that is also a country code (`cc`, `ad`) must be in `ignored_words`. See "Blocked words".

## Blocked words

Before it looks for a language, `find_language` in `trakit/language.py` blanks these words. They are
never a language and never a country.

1. The release names (`blank_release_names` in `trakit/words.py`).
2. The audio and video terms (`technical_term_re` in `trakit/words.py`), for example `DTS-HD MA`,
   `5.1 CH`, and `24-bit`. Only the full term is blanked. The code alone can still be a country:
   `French (MA)` gives `fr-MA`, and `DTS-HD MA 5.1 (Français)` gives `fr`.
3. The words in `ignored_words` in `tests/generator.json`, in every position. These are common words
   (`The Film`), names of people (`Jordan Peele`), and flag codes. `English CC (US)` gives `en-US` with
   `closed_caption`, and `Catalan AD` gives `ca` with `descriptive`.

These rules are for track names. File names use other rules. See "File names".

A flag code must be in the list because the country search stops at the first country. A rule after the
search cannot remove the code and continue to the next word.

## Countries and regions

After the language, `find_language` looks for a country or a region in the other words of the title. It
tries the largest group of words first. For each group, it applies these rules in order:

1. A code in `language-regions` for this language is a region. The case must be the same. `Spanish (LA)`
   gives `es-419`. `Español (la versión original)` gives `es`.
2. A country name is a country. `English (Costa Rica)` gives `en-CR`.
3. A code in `bracket-tags`, directly between `[` and `]`, is not a country. These are release tags of
   streaming services. `English [NF]` gives `en`. `English NF` gives `en-NF`.
4. A 2-letter code is a country only when the language is official in that country
   (`country-languages`). `Spanish (CR)` gives `es-CR`. `English (Signs) [CR]` gives `en`.
5. A region name (`regions`) or a script name (`scripts`).

A 2-letter country code is in upper case. A lower-case code is a country only when it is directly
between `(` `)` or `[` `]`, and when it is not the code of the language itself. `French (ca)` gives
`fr-CA`. `Français (fr)` gives `fr`. `Español de España` gives `es-ES`, because `de` is not in brackets.
Rules 3 and 4 also apply to a lower-case code.

The search stops at the first group that matches a rule, also when rule 3 or 4 rejects the country.

A code alone (`US`, `br`) gives the language of the country (`implicit-languages`). `US` gives `en-US`,
and `br` gives `pt-BR`. Exception: a lower-case code that is the code of that language gives the language
only. `fr` gives `fr`, and `FR` gives `fr-FR`.

## File names

For the input type `filename`, trakit reads the language as Jellyfin 12.4 does, and then as subliminal
does. Track names are more noisy, so they use the rules above. File names use only these rules:

1. Blank the base name (up to the first `.`) and the extension.
2. Split the rest on `.` and space. `pt-br` and `pt_BR` stay one word.
3. Read the words from right to left. The first word that is a language code is the language.
4. A language code is an IETF tag (`fr`, `pt-br`, `en-gb`, `zh-hans`, `es-419`, and `pt_BR` with `_` as
   `-`) or an ISO 639-2/B code (`fre`). The language must have an ISO 639-2 code. So `sdh`, `and`, and
   `dts` (ISO 639-3 codes) are not a language.
5. `hi` is Hindi only when no other language code comes before it. `movie.en.hi.srt` gives `en` with
   `hearing_impaired`.

A file name has no implicit languages, no country code alone, no language names, and no ignored
words. `movie.us.srt` and `movie.french.srt` give no language. `movie.uk.srt` gives `uk` (Ukrainian), but
the track name `uk` gives `en-GB`. `movie.pt.br.srt` gives `br`, because the last code wins. The flags
use the same patterns as track names.

Add an entry to `language-regions` or `bracket-tags` only when real data shows the case. `bracket-tags`
is a list of exceptions, not a list of all release tags. Most release tags have more than 2 letters
(`AMZN`, `DSNP`), so they are never a country code.

## Generated data

`trakit/data/config.json` holds the data for the language rules: the country and language synonyms, the
official languages of each country, the scripts, the regions, the language-specific regions, the
bracket tags, and the ignored words. It is generated data. Never edit it by hand.

To change it:

1. Update `tests/generator.json`, or the sources that it reads:
   [mledoze/countries](https://github.com/mledoze/countries),
   [mozilla/language-mapping-list](https://github.com/mozilla/language-mapping-list), and the CLDR
   [territoryInfo.json](https://github.com/unicode-org/cldr-json) (only the languages with an
   `_officialStatus`).
2. Run `uv run pytest -q tests/test_generate.py`. It downloads the sources (network access is necessary)
   and writes tests/generated/config.json (gitignored).
3. Copy that file over `trakit/data/config.json`.
4. Commit. The pre-commit hooks add the final newline, fix the line endings, and stop the commit. Stage
   the file again and commit again.

`test_generate_config` in `tests/test_generate.py` fails when the two files are different.
