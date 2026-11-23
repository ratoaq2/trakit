<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ratoaq2/trakit/main/docs/images/logo-dark.png">
    <img alt="trakit: Identify a track from its title" src="https://raw.githubusercontent.com/ratoaq2/trakit/main/docs/images/logo-light.png" width="400">
  </picture>
</h1>

trakit reads a track title or a file name and guesses the language and the track flags: SDH, forced,
closed caption, commentary, audio description, and alternate version.

[![PyPI version](https://img.shields.io/pypi/v/trakit.svg)](https://pypi.org/project/trakit/)
[![Python versions](https://img.shields.io/pypi/pyversions/trakit.svg)](https://pypi.org/project/trakit/)
[![Tests](https://github.com/ratoaq2/trakit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/trakit/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/ratoaq2/trakit.svg)](https://github.com/ratoaq2/trakit/blob/main/LICENSE)

<p align="center">
  <img alt="trakit guesses the language and the flags of three track titles" src="https://raw.githubusercontent.com/ratoaq2/trakit/main/docs/images/demo.gif" width="760">
</p>

## Why trakit

The language tag of a track in a video file is often not precise. Two subtitle tracks can both have the
tag `por`, but one title says `Português` and the other says `Português (Brasil)`. The track title often
has more information than the tags: SDH, forced, commentary. trakit reads the title, so that your tools
can select the correct track.

| Track title | Language tag | trakit |
| --- | --- | --- |
| `Português` | `por` | `language: pt` |
| `Português (Brasil)` | `por` | `language: pt-BR` |
| `British English (SDH) (PGS)` | `eng` | `language: en-GB`, `hearing_impaired: true` |

## What trakit detects

| Key | Meaning | Example title |
| --- | --- | --- |
| `language` | The language, with the country or the region when the title has one | `Español (LA) Forced` gives `es-419` |
| `hearing_impaired` | Subtitles for the deaf or hard of hearing (SDH) | `British English (SDH) (PGS)` |
| `forced` | Forced subtitles, also signs and songs tracks | `English Signs & Songs (ASS)` |
| `closed_caption` | Closed captions | `English CC (SRT)` |
| `commentary` | A commentary track | `Cast and Crew Commentary (English AC3 Stereo)` |
| `descriptive` | Audio description | `English (Audio Description)` |
| `version` | An alternate version (`alternate`) | `Alternate Score Version (English DTS-HD MA 5.1)` |

The result has only the keys that trakit finds. The full reference is in
[docs/usage.md](https://github.com/ratoaq2/trakit/blob/main/docs/usage.md#output).

## Quick start

Run trakit with no install step, with [uvx](https://docs.astral.sh/uv/guides/tools/):

```
$ uvx trakit "Português (Brasil)"
...
{
  "language": "pt-BR"
}
```

Read the name of an external subtitle file:

```
$ uvx trakit -t filename "movie.pt-BR.cc.commentary.srt"
...
{
  "language": "pt-BR",
  "closed_caption": true,
  "commentary": true
}
```

Use it in Python:

```python
from trakit import trakit

trakit('British English (SDH) (PGS)')
# MatchesDict({'language': <Language [en-GB]>, 'hearing_impaired': True})
```

## Installation

trakit needs Python 3.11 or later.

| To | Run |
| --- | --- |
| Run the CLI with no install | `uvx trakit "<title>"` |
| Install the CLI | `uv tool install trakit` |
| Add the library to a project | `uv add trakit` |
| Install with pip | `pip install trakit` |

The `-y` (YAML) option needs the `yaml` extra, for example `uv tool install "trakit[yaml]"`.

## Usage

A track title:

```
$ trakit "Cast and Crew Commentary (English AC3 Stereo)"
...
{
  "commentary": true,
  "language": "en"
}
```

A file name. trakit reads the language codes and the flags between the dots:

```
$ trakit -t filename "movie.en.forced.srt"
...
{
  "language": "en",
  "forced": true
}
```

The expected language. A title can name a person or a place that is also a language. Give the language
that you expect, for example the language tag of the track:

```
$ trakit -l en "Commentary by director John Français (EU) (English PGS)"
...
{
  "commentary": true,
  "language": "en"
}
```

YAML output:

```
$ trakit -y "British English (SDH) (PGS)"
...
British English (SDH) (PGS):
  language: en-GB
  hearing_impaired: true
```

The Python API. The `options` keys are the same as the CLI options:

```python
from trakit import trakit

trakit('movie.en.sdh.srt', {'type': 'filename'})
# MatchesDict({'language': <Language [en]>, 'hearing_impaired': True})

info = trakit('Commentary by director John Français (EU) (English PGS)', {'expected_language': 'en'})
str(info['language'])  # 'en'
```

### Main options

| Option | Use |
| --- | --- |
| `-t filename` | Read a file name. The default is `trackname`. |
| `-l <language>` | The expected language, as an IETF tag (`en`, `pt-BR`). |
| `-y` | YAML output. |
| `--debug` | Print the debug information. Add it to a bug report. |

All the options, the output keys, `TrakItApi`, and the babelfish `Language` values are in
[docs/usage.md](https://github.com/ratoaq2/trakit/blob/main/docs/usage.md).

## What trakit is not

- trakit is not a release name parser. Use [GuessIt](https://github.com/guessit-io/guessit).
- trakit does not read media files. Use [knowit](https://github.com/ratoaq2/knowit). knowit uses trakit to
  read the track titles.

## FAQ

**trakit gives `{}`. Why?**
The title has no word that trakit knows, for example a release name. If the title has a language or a
flag, report it.

**trakit gives the wrong language. What can I do?**
Give the expected language with `-l`. Then report the title.

**Does trakit read the media file?**
No. It reads only the string that you give. Use knowit to read the tracks of a file.

**Which languages does trakit know?**
The languages of babelfish, with their names in many languages. See [Data sources](#data-sources).

## Report a bug

[Open an issue](https://github.com/ratoaq2/trakit/issues) with:

- The track title or the file name.
- The result that you expect.
- The output of `trakit --debug "<title>"`.

## Data sources

- The languages are the languages of [Diaoul/babelfish](https://github.com/Diaoul/babelfish).
- The country names in many languages come from [mledoze/countries](https://github.com/mledoze/countries).
- The language names in many languages come from
  [mozilla/language-mapping-list](https://github.com/mozilla/language-mapping-list).
- The official languages of each country come from [Unicode CLDR](https://github.com/unicode-org/cldr-json)
  (`territoryInfo.json`).

## Contributing

See [CONTRIBUTING.md](https://github.com/ratoaq2/trakit/blob/main/CONTRIBUTING.md).

## License

[MIT](https://github.com/ratoaq2/trakit/blob/main/LICENSE).

The trakit name, logo, and icon are not covered by the MIT license. All rights reserved.
