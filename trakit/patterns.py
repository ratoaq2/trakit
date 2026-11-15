import re
import typing
from functools import partial

from rebulk import Rebulk
from rebulk.match import Match, Matches
from rebulk.rules import RemoveMatch, Rule
from rebulk.validators import chars_surround

from trakit.config import Config
from trakit.language import language
from trakit.words import seps


class RemoveCodeWithoutLanguage(Rule):
    """Remove a short flag code (HI, AD) that does not come after a language.

    In a file name, the language span is not in the input string, so the code is always removed.
    """

    consequence = RemoveMatch

    def when(self, matches: Matches, context: dict[str, typing.Any] | None) -> list[Match]:
        filename = context is not None and context.get('type') == 'filename'
        return [
            m
            for m in matches.tagged('after-language')
            if filename or not matches.previous(m, lambda x: x.name == 'language')
        ]


def configure(config: Config) -> Rebulk:
    seps_surround = partial(chars_surround, seps)

    others = Rebulk()
    others.defaults(ignore_case=True, validator=seps_surround)
    others.regex_defaults(
        flags=re.IGNORECASE, abbreviations=[(r'-', rf'[{re.escape("".join(seps))}]')], validator=seps_surround
    )
    for name in ('forced', 'commentary', 'external'):
        others.string(name, name=name, value=True)

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
    rebulk.rules(RemoveCodeWithoutLanguage)

    return rebulk
