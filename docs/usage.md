# Usage

This is the full reference for the trakit CLI and the Python API. The README has a short version.

## All options

```
$ trakit --help
usage: trakit [-h] [-l EXPECTED_LANGUAGE] [-t TYPE] [--debug] [-y] [--version]
              value

positional arguments:
  value                 track title to guess

options:
  -h, --help            show this help message and exit

Configuration:
  -l, --expected-language EXPECTED_LANGUAGE
                        The expected language to be guessed
  -t, --type TYPE       The input type: trackname or filename. Default is
                        trackname

Output:
  --debug               Print information for debugging trakit and for
                        reporting bugs.
  -y, --yaml            Display output in yaml format

Information:
  --version             show program's version number and exit
```

- `-l` gives the language that you expect, as an IETF tag (`en`, `pt-BR`, `es-419`). trakit then
  accepts only a language that agrees with it. Use it when the container already has a language tag for
  the track. See [Expected language](#expected-language).
- `-y` needs the `yaml` extra: `pip install "trakit[yaml]"`.
- `--debug` prints the rebulk matches. Add its output to a bug report.

## Input types

trakit reads one string. It does not open a media file. The input type tells trakit what the string is.

| Type | The string is | Example |
| --- | --- | --- |
| `trackname` (default) | The title of a track in a container, for example the track name in mkvmerge. | `British English (SDH) (PGS)` |
| `filename` | The name of an external subtitle or audio file. | `movie.pt-BR.cc.commentary.srt` |

The two types use different rules. A file name has language codes, flags, and a base name. A track name
has language names in many languages, country names, and codec words. `docs/matching.md` tells the rules.

```
$ trakit -t filename "movie.pt-BR.cc.commentary.srt"
...
{
  "language": "pt-BR",
  "closed_caption": true,
  "commentary": true
}
```

## Output

trakit prints two header lines, then the result as JSON. The second header line has the trakit version.
With `-y`, the result is YAML, and the `Parsing:` line is not there.

```
$ trakit "British English (SDH) (PGS)"
Parsing: British English (SDH) (PGS)
trakit <version> found:
{
  "language": "en-GB",
  "hearing_impaired": true
}

$ trakit -y "British English (SDH) (PGS)"
trakit <version> found:
British English (SDH) (PGS):
  language: en-GB
  hearing_impaired: true
```

The result has only the keys that trakit finds. When trakit finds nothing, the result is `{}`.

| Key | Value | Meaning | Example title |
| --- | --- | --- | --- |
| `language` | IETF tag | The language, with the country or the region when the title has one. | `Português (Brasil)` gives `pt-BR`. `Español (LA) Forced` gives `es-419`. |
| `hearing_impaired` | `true` | Subtitles for the deaf or hard of hearing (SDH). | `British English (SDH) (PGS)` |
| `forced` | `true` | Forced subtitles, also signs and songs tracks. | `Français Forced (SRT)`, `English Signs & Songs (ASS)` |
| `closed_caption` | `true` | Closed captions. | `English CC (SRT)` |
| `commentary` | `true` | A commentary track. | `Cast and Crew Commentary (English AC3 Stereo)` |
| `descriptive` | `true` | Audio description. | `English (Audio Description)` |
| `version` | `alternate` | An alternate version of the track. | `Alternate Score Version (English DTS-HD MA 5.1)` |

### Expected language

A title can name a person or a place that is also a language or a country. Give the language that you
expect with `-l`:

```
$ trakit "Commentary by director John Français (EU) (English PGS)"
...
{
  "commentary": true,
  "language": "fr"
}

$ trakit -l en "Commentary by director John Français (EU) (English PGS)"
...
{
  "commentary": true,
  "language": "en"
}
```

## Python API

```python
from trakit import trakit

info = trakit('Português (Brasil)')
info['language']  # <Language [pt-BR]>, a babelfish Language

trakit('movie.en.sdh.srt', {'type': 'filename'})
# MatchesDict({'language': <Language [en]>, 'hearing_impaired': True})

trakit('Commentary by director John Français (EU) (English PGS)', {'expected_language': 'en'})
# MatchesDict({'commentary': True, 'language': <Language [en]>})
```

`trakit(string, options=None)` returns a mapping with the keys of [Output](#output). The `language` value
is a [babelfish](https://github.com/Diaoul/babelfish) `Language`. `str(info['language'])` gives the IETF tag
(`pt-BR`). `info['language'].alpha3` gives the ISO 639-3 code (`por`).

The `options` keys:

| Key | Value | CLI option |
| --- | --- | --- |
| `type` | `'trackname'` (default) or `'filename'` | `-t` |
| `expected_language` | An IETF tag (`'en'`) or a babelfish `Language` | `-l` |

`TrakItApi(config)` makes a parser with a different configuration. `config` is a mapping. Each key replaces
the same top-level key of `trakit/data/config.json` (the full value, not a merge). `docs/matching.md`,
"Generated data", tells what the data is.

```python
from trakit import TrakItApi

api = TrakItApi()
api.trakit('English CC (SRT)')
# MatchesDict({'language': <Language [en]>, 'closed_caption': True})
```
