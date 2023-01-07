# TrackIt
Guess additional information from track titles

[![Latest
Version](https://img.shields.io/pypi/v/trackit.svg)](https://pypi.python.org/pypi/trackit)

[![tests](https://github.com/ratoaq2/trackit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/trackit/actions/workflows/test.yml)

[![License](https://img.shields.io/github/license/ratoaq2/trackit.svg)](https://github.com/ratoaq2/trackit/blob/master/LICENSE)

  - Project page  
    <https://github.com/ratoaq2/trackit>

## Info

**TrackIt** is a track name parser.
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

Given a track name, **TrackIt** can guess the language:

```bash
> trackit "Português (Brasil)"
{
  "language": "pt-BR"
}
```

**TrackIt** is also able to identify:
* SDH: Subtitles for the Deaf or Hard of Hearing
* Forced flag
* Closed captions
* Alternate version tracks
* Commentary tracks

```bash
>> trackit "British English (SDH) (PGS)"
{
  "language": "en-GB",
  "hearing_impaired": true
}

>> trackit "English CC (SRT)"
{
  "language": "en",
  "closed_caption": true
}

>> trackit "Cast and Crew Commentary (English AC3 Stereo)"
{
  "language": "en",
  "commentary": true
}

>> trackit "Français Forced (SRT)"
{
  "language": "fr",
  "forced": true
}
```

**TrackIt** is not a release parser. Use [GuessIt](https://github.com/guessit-io/guessit)

**TrackIt** is not a video metadata extractor.
Use [KnowIt](https://github.com/ratoaq2/knowit).
KnowIt already uses **trackit** to enhance the extracted information

## Installation

**TrackIt** can be installed as a regular python module by running:

    $ [sudo] pip install trackit

For a better isolation with your system you should use a dedicated
virtualenv or install for your user only using the `--user` flag.

## Data
* Available languages are the same supported by [Diaoul/babelfish](https://github.com/Diaoul/babelfish)
* Localized country names were fetched from [mledoze/countries](https://github.com/mledoze/countries)
* Localized language names were fetched from [mozilla/language-mapping-list](https://github.com/mozilla/language-mapping-list)
