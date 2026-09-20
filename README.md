# TrakIt
Guess additional information from track titles

[![Latest
Version](https://img.shields.io/pypi/v/trakit.svg)](https://pypi.python.org/pypi/trakit)

[![tests](https://github.com/ratoaq2/trakit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/trakit/actions/workflows/test.yml)

[![License](https://img.shields.io/github/license/ratoaq2/trakit.svg)](https://github.com/ratoaq2/trakit/blob/main/LICENSE)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trakit)

  - Project page  
    <https://github.com/ratoaq2/trakit>

## Info

**TrakIt** is a track name parser.
It is a tiny library created to solve a very specific problem.
It's very common that video files do not have precise metadata information,
where you can have multiple subtitle tracks tagged as **Portuguese**,
but one of them is actually **Brazilian Portuguese**:
```json lines
{
  "codec": "SubRip/SRT",
  "id": 19,
  "properties": {
    "codec_id": "S_TEXT/UTF8",
    "codec_private_length": 0,
    "default_track": false,
    "enabled_track": true,
    "encoding": "UTF-8",
    "forced_track": false,
    "language": "por",
    "language_ietf": "pt",
    "number": 20,
    "text_subtitles": true,
    "track_name": "Português",
    "uid": 160224385584803173
  }
}

{
  "codec": "SubRip/SRT",
  "id": 20,
  "properties": {
    "codec_id": "S_TEXT/UTF8",
    "codec_private_length": 0,
    "default_track": false,
    "enabled_track": true,
    "encoding": "UTF-8",
    "forced_track": false,
    "language": "por",
    "language_ietf": "pt",
    "number": 21,
    "text_subtitles": true,
    "track_name": "Português (Brasil)",
    "uid": 1435945803220205
  }
}
```
Or you have multiple audio tracks in **English**,
but one of them is **British English** (`British English Forced (PGS)`) and others are **American English**
(`American English (PGS)`)

Given a track name, **TrakIt** can guess the language:

```bash
>> trakit "Português (Brasil)"
{
  "language": "pt-BR"
}
```

```bash
>> trakit -t filename "foobar.en.sdh.srt"
{
  "language": "en",
  "hearing_impaired": true
}
```

**TrakIt** is also able to identify:
* SDH: Subtitles for the Deaf or Hard of Hearing
* Forced flag
* Closed captions
* Alternate version tracks
* Commentary tracks

```bash
>> trakit "British English (SDH) (PGS)"
{
  "language": "en-GB",
  "hearing_impaired": true
}

>> trakit "English CC (SRT)"
{
  "language": "en",
  "closed_caption": true
}

>> trakit "Cast and Crew Commentary (English AC3 Stereo)"
{
  "language": "en",
  "commentary": true
}

>> trakit "Français Forced (SRT)"
{
  "language": "fr",
  "forced": true
}
```

All available CLI options:
```bash
>> trakit --help
usage: trakit [-h] [-l EXPECTED_LANGUAGE] [--debug] [-y] [--version] value

positional arguments:
  value                 track title to guess

options:
  -h, --help            show this help message and exit

Configuration:
  -l EXPECTED_LANGUAGE, --expected-language EXPECTED_LANGUAGE
                        The expected language to be guessed
  -t, --type TYPE       The input type: trackname or filename. Default is trackname

Output:
  --debug               Print information for debugging trakit and for reporting bugs.
  -y, --yaml            Display output in yaml format

Information:
  --version             show program's version number and exit
```


**TrakIt** is not a release parser. Use [GuessIt](https://github.com/guessit-io/guessit)

**TrakIt** is not a video metadata extractor.
Use [KnowIt](https://github.com/ratoaq2/knowit).
KnowIt already uses **trakit** to enhance the extracted information

## Installation

**TrakIt** requires Python 3.10 or later.

**TrakIt** is a command line tool. The simplest way to run it, with no install step,
is [uvx](https://docs.astral.sh/uv/guides/tools/) (part of [uv](https://docs.astral.sh/uv/)):

    $ uvx trakit "Português (Brasil)"

To install it instead, so it stays available on your `PATH`:

    $ uv tool install trakit

`pip` is also supported. Use a dedicated virtualenv or the `--user` flag for a
better isolation with your system:

    $ pip install --user trakit

**TrakIt** is also a library. To add it as a dependency to a uv-managed project:

    $ uv add trakit

The `-y`/`--yaml` option needs the optional `yaml` extra:

    $ uv tool install "trakit[yaml]"

## Development

**TrakIt** uses [uv](https://docs.astral.sh/uv/) to manage its environment and dependencies.

    $ uv sync --all-extras
    $ bash scripts/test.sh

This runs [ruff](https://docs.astral.sh/ruff/) (lint and format check), [mypy](https://mypy-lang.org/) and the test suite.

[pre-commit](https://pre-commit.com/) hooks mirror the same checks and run automatically on `git commit`:

    $ uv run pre-commit install

## Data
* Available languages are the same supported by [Diaoul/babelfish](https://github.com/Diaoul/babelfish)
* Localized country names were fetched from [mledoze/countries](https://github.com/mledoze/countries)
* Localized language names were fetched from [mozilla/language-mapping-list](https://github.com/mozilla/language-mapping-list)
