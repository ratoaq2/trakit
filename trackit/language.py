import typing

from babelfish import (
    COUNTRIES,
    Country,
    CountryReverseError,
    LANGUAGE_MATRIX,
    Language,
    LanguageReverseError,
    SCRIPTS,
    Script,
    country_converters,
    language_converters
)
from babelfish.converters import CaseInsensitiveDict

from rebulk import Rebulk
from rebulk.match import Match

from trackit.config import Config
from trackit.converters.country import GuessCountryConverter
from trackit.converters.language import GuessLanguageConverter
from trackit.words import blank_match, blank_release_names, to_combinations, to_match, to_sentence, to_words


class LanguageFinder:

    def __init__(self, config: Config):
        self.country_max_words = 1
        for k, v in COUNTRIES.items():
            self.country_max_words = max(self.country_max_words, v.count(' '))

        self.language_max_words = 1
        for v in LANGUAGE_MATRIX:
            self.language_max_words = max(self.language_max_words, v.name.count(' '))

        self.script_max_words = 1
        for v in config.scripts.keys():
            self.script_max_words = max(self.script_max_words, v.count(' '))

        self.region_max_words = 1
        for v in config.regions.keys():
            self.region_max_words = max(self.region_max_words, v.count(' '))

        SCRIPTS['419'] = 'Latin America and the Caribbean'  # Until babelfish support UN.M49
        country_converters['guess'] = GuessCountryConverter(config.countries)
        language_converters['guess'] = GuessLanguageConverter(config.languages)
        self.regions = CaseInsensitiveDict(config.regions)
        self.scripts = CaseInsensitiveDict(config.scripts)
        self.common_words = CaseInsensitiveDict(dict.fromkeys(config.ignored, 0))
        self.implicit = CaseInsensitiveDict(config.implicit_languages)

    def _find_country(self, value: str):
        combinations = to_combinations(to_words(value), self.country_max_words)
        for c in combinations:
            code = to_sentence(c)
            try:
                return to_match(c, Country.fromguess(code))
            except CountryReverseError:
                continue

    def _find_script(self, value: str):
        combinations = to_combinations(to_words(value), self.script_max_words)
        for c in combinations:
            code = to_sentence(c)
            try:
                return to_match(c, Script(self.scripts.get(code, code)))
            except ValueError:
                continue

    def _find_region(self, value: str):
        combinations = to_combinations(to_words(value), self.region_max_words)
        for c in combinations:
            code = to_sentence(c)
            try:
                return to_match(c, Script(self.regions.get(code, code)))
            except ValueError:
                continue

    def _find_implicit_language(self, combinations: typing.List[typing.List[Match]]):
        for c in combinations:
            sentence = to_sentence(c)
            if sentence in self.implicit:
                return to_match(c, Language.fromietf(self.implicit[sentence]))

            region = self._find_region(sentence)
            if region and region.value.code in self.implicit:
                lang = Language.fromietf(self.implicit[region.value.code])
                return Match(region.start, region.end, value=lang, input_string=region.input_string)

            try:
                country = Country.fromguess(sentence)
                if country.alpha2 in self.implicit:
                    lang = Language.fromietf(self.implicit[country.alpha2])
                    if lang.name.lower() == sentence.lower():
                        lang = Language.fromname(sentence)

                    return to_match(c, lang)
            except CountryReverseError:
                pass

    def find_language(self, value: str):
        value = blank_release_names(value)
        all_words = to_words(value, predicate=lambda x: x.lower() not in self.common_words and not x.isnumeric())
        combinations = to_combinations(all_words, self.language_max_words)
        implicit_lang = self._find_implicit_language(combinations)
        if implicit_lang and implicit_lang.value.script and implicit_lang.value.script.code.isnumeric():
            return implicit_lang

        for c in combinations:
            language_sentence = to_sentence(c)
            try:
                lang = Language.fromguess(language_sentence)
            except LanguageReverseError:
                continue

            match_lang = to_match(c, lang)
            remaining_sentence = blank_match(match_lang)
            for combination in to_combinations(to_words(remaining_sentence), self.country_max_words):
                sentence = to_sentence(combination)
                country = self._find_country(sentence)
                if country:
                    lang = Language(lang.alpha3, country=country.value, script=lang.script)
                    break

                region = self._find_region(sentence)
                if region:
                    lang = Language(lang.alpha3, country=lang.country, script=region.value)
                    break

                script = self._find_script(sentence)
                if script:
                    lang = Language(lang.alpha3, country=lang.country, script=script.value)
                    break

            if implicit_lang and implicit_lang.value.alpha3 == lang.alpha3 and not lang.country and not lang.script:
                return implicit_lang

            return to_match(c, lang)

        return implicit_lang

    # noinspection PyUnusedLocal
    def find(self, value: str, context: typing.Mapping[str, typing.Any]):
        match = self.find_language(value)
        if match:
            return match.start, match.end, {'value': match.value}


def language(config: Config):
    rebulk = Rebulk()
    rebulk.functional(LanguageFinder(config).find, name='language')

    return rebulk
