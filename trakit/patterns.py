import re
import typing
from functools import partial

from rebulk import Rebulk
from rebulk.match import Match, Matches
from rebulk.rules import RemoveMatch, Rule
from rebulk.validators import chars_surround

from trakit.config import Config
from trakit.context import Context
from trakit.language import language
from trakit.words import blank_base_name_and_extension, seps


class RemoveCodeWithoutLanguage(Rule):
    """Remove a short flag code (HI, AD) that does not come after a language."""

    consequence = RemoveMatch

    def when(self, matches: Matches, context: dict[str, typing.Any] | None) -> list[Match]:
        return [m for m in matches.tagged('after-language') if not matches.previous(m, lambda x: x.name == 'language')]


class RemoveWordNotAtStartOrNextToLanguage(Rule):
    """Remove a word (signs, foreign) that is not at the start, and not directly after a language."""

    consequence = RemoveMatch

    def when(self, matches: Matches, context: dict[str, typing.Any] | None) -> list[Match]:
        value = matches.input_string
        assert value is not None
        if isinstance(context, Context) and context.type == 'filename':
            value = blank_base_name_and_extension(value)

        def keep(match: Match) -> bool:
            language = matches.previous(match, lambda x: x.name == 'language', 0)
            start = language.end if language else 0
            return bool(value[match.start : match.end].strip()) and not value[start : match.start].strip(''.join(seps))

        return [m for m in matches.tagged('start-or-next-to-language') if not keep(m)]


def configure(config: Config) -> Rebulk:
    seps_surround = partial(chars_surround, seps)

    others = Rebulk()
    others.defaults(ignore_case=True, validator=seps_surround)
    others.regex_defaults(
        flags=re.IGNORECASE, abbreviations=[(r'-', rf'[{re.escape("".join(seps))}]')], validator=seps_surround
    )
    for name in ('forced', 'commentary', 'external'):
        others.string(name, name=name, value=True)

    others.regex(
        r'signs?-*(?:&|and|/)-*songs?',
        r'songs?-*(?:&|and|/)-*signs?',
        r'non-[^\W\d_]+-parts',
        r'(?:un)?styled-signs',
        r's&s',
        name='forced',
        value=True,
    )
    others.string('signs', 'foreign', name='forced', value=True, tags=['start-or-next-to-language'])
    others.string('sdh', name='hearing_impaired', value=True)
    others.regex('hearing-impaired', name='hearing_impaired', value=True)
    others.string('hi', name='hearing_impaired', value=True, tags=['after-language'])
    others.string('alternate', name='version', value='alternate')
    others.string('descriptive', name='descriptive', value=True)
    others.regex('audio-descri(?:ption|bed)', 'described-video', name='descriptive', value=True)
    others.string('ad', name='descriptive', value=True, tags=['after-language'])
    others.regex('cc', 'closed-captions?', name='closed_caption', value=True)

    rebulk = Rebulk()
    rebulk.rebulk(language(config))
    rebulk.rebulk(others)
    rebulk.rules(RemoveCodeWithoutLanguage, RemoveWordNotAtStartOrNextToLanguage)

    return rebulk
