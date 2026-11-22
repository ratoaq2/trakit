import typing

from babelfish import (
    COUNTRIES,
    LANGUAGE_MATRIX,
    SCRIPTS,
    Country,
    CountryReverseError,
    Language,
    LanguageConvertError,
    LanguageReverseError,
    Script,
    country_converters,
    language_converters,
)
from babelfish.converters import CaseInsensitiveDict
from rebulk import Rebulk
from rebulk.match import Match

from trakit.config import Config
from trakit.context import Context
from trakit.converters.country import GuessCountryConverter
from trakit.converters.language import GuessLanguageConverter
from trakit.words import (
    blank_base_name_and_extension,
    blank_match,
    blank_release_names,
    blank_technical_terms,
    to_combinations,
    to_match,
    to_sentence,
    to_words,
)


def _convert(value: str) -> Language | None:
    try:
        return Language.fromguess(value)
    except LanguageReverseError:
        return None


def _from_code(code: str) -> Language | None:
    # only ISO 639-1 and ISO 639-2 codes, as Jellyfin: sdh and dts are ISO 639-3 codes
    for conv in (Language.fromietf, Language.fromalpha3b):
        try:
            lang: Language = conv(code.lower().replace('_', '-'))
            if lang.alpha3b:
                return lang
        except (ValueError, LanguageReverseError, LanguageConvertError):
            continue

    return None


def _alpha2(lang: Language) -> str | None:
    try:
        alpha2: str = lang.alpha2
        return alpha2
    except LanguageConvertError:
        return None


def _between(word: Match, *brackets: str) -> bool:
    value = word.input_string or ''
    return any(value[word.start - 1 : word.start] == b[0] and value[word.end : word.end + 1] == b[1] for b in brackets)


class LanguageFinder:
    def __init__(self, config: Config):
        self.country_max_words = 1
        for v in COUNTRIES.values():
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
        self.language_regions = config.language_regions
        self.scripts = CaseInsensitiveDict(config.scripts)
        self.common_words = CaseInsensitiveDict(dict.fromkeys(config.ignored, 0))
        self.implicit = CaseInsensitiveDict(config.implicit_languages)
        self.country_languages = config.country_languages
        self.bracket_tags = config.bracket_tags

    def _find_country(self, value: str) -> Match | None:
        combinations = to_combinations(to_words(value), self.country_max_words)
        for c in combinations:
            code = to_sentence(c)
            try:
                return to_match(c, Country.fromguess(code))
            except CountryReverseError:
                continue

        return None

    def _accept_country(self, lang: Language, country: Match, combination: list[Match]) -> bool:
        # a country code (CR, NF) is a country only when the language is official there, a name always is
        raw = country.raw or ''
        code = len(raw) == 2 and raw.isascii()
        if code and raw in self.bracket_tags:
            # a release tag in square brackets (English [NF]) is not a country
            if any(w.value == raw and _between(w, '[]') for w in combination):
                return False
        return not code or lang.alpha3 in self.country_languages.get(country.value.alpha2, [])

    def _find_lower_case_country(self, lang: Language, combination: list[Match]) -> Match | None:
        # a lower-case code in brackets (French (ca)) is a country, but not the code of the language (Français (fr))
        if len(combination) != 1:
            return None

        code = combination[0].value
        if len(code) != 2 or not code.islower() or code == _alpha2(lang) or not _between(combination[0], '()', '[]'):
            return None

        try:
            return to_match(combination, Country(code.upper()))
        except ValueError:
            return None

    def _find_script(self, value: str) -> Match | None:
        combinations = to_combinations(to_words(value), self.script_max_words)
        for c in combinations:
            code = to_sentence(c)
            try:
                return to_match(c, Script(self.scripts.get(code, code)))
            except ValueError:
                continue

        return None

    def _find_region(self, value: str) -> Match | None:
        combinations = to_combinations(to_words(value), self.region_max_words)
        for c in combinations:
            code = to_sentence(c)
            try:
                return to_match(c, Script(self.regions.get(code, code)))
            except ValueError:
                continue

        return None

    def _find_implicit_language(self, combinations: list[list[Match]]) -> Match | None:
        for c in combinations:
            sentence = to_sentence(c)
            if sentence in self.implicit:
                lang = Language.fromietf(self.implicit[sentence])
                # a lower-case code of the language itself (fr, id) is the language, not the country
                if sentence.islower() and sentence == _alpha2(lang):
                    lang = Language(lang.alpha3)
                return to_match(c, lang)

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

        return None

    def accept_word(self, string: str) -> bool:
        return string.lower() not in self.common_words and not string.isnumeric()

    def _find_filename_language(self, value: str, context: Context) -> Match | None:
        # as Jellyfin, then subliminal: the last code before the extension, read from right to left
        words = to_words(blank_base_name_and_extension(value), separators=frozenset(' .'))
        hindi: Match | None = None
        for word in reversed(words):
            lang = _from_code(word.value)
            if lang is None or not context.accept(lang):
                continue

            # hi is Hindi only when no other language comes before it
            if word.value.lower() == 'hi':
                hindi = hindi or to_match([word], lang)
                continue

            return to_match([word], lang)

        return hindi

    def find_language(self, value: str, context: Context) -> Match | None:
        if context.type == 'filename':
            return self._find_filename_language(value, context)

        value = blank_release_names(value)
        value = blank_technical_terms(value)
        all_words = to_words(value, predicate=self.accept_word)
        combinations = to_combinations(all_words, self.language_max_words)
        implicit_lang = self._find_implicit_language(combinations)
        implicit_accepted = implicit_lang and context.accept(implicit_lang.value)

        if (
            implicit_lang is not None
            and implicit_accepted
            and implicit_lang.value.script
            and implicit_lang.value.script.code.isnumeric()
        ):
            return implicit_lang
        elif implicit_lang and not implicit_accepted:
            value = blank_match(implicit_lang)
            all_words = to_words(value, predicate=self.accept_word)
            combinations = to_combinations(all_words, self.language_max_words)

        for c in combinations:
            # "Non-English" is not English
            i = all_words.index(c[0])
            if i and all_words[i - 1].value.lower() == 'non':
                continue

            language_sentence = to_sentence(c)
            lang: Language | None = _convert(language_sentence)
            if lang is None:
                continue

            match_lang = to_match(c, lang)
            remaining_sentence = blank_match(match_lang)
            for combination in to_combinations(to_words(remaining_sentence), self.country_max_words):
                sentence = to_sentence(combination)
                # a code that is a region only for this language, with the exact case (LA after Spanish)
                regions = self.language_regions.get(lang.alpha3, {})
                language_region = next((regions[w.value] for w in combination if w.value in regions), None)
                if language_region:
                    lang = Language(lang.alpha3, country=lang.country, script=Script(language_region))
                    break

                country = self._find_country(sentence) or self._find_lower_case_country(lang, combination)
                if country:
                    try:
                        # discard country if value is actually the language name
                        Language.fromguess(country.raw)
                    except LanguageReverseError:
                        if self._accept_country(lang, country, combination):
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

            if (
                implicit_lang is not None
                and implicit_accepted
                and implicit_lang.value.alpha3 == lang.alpha3
                and not lang.country
                and not lang.script
            ):
                return implicit_lang

            if context.accept(lang):
                return to_match(c, lang)

        if implicit_accepted:
            return implicit_lang

        return None

    def find(self, value: str, context: Context) -> tuple[int, int, dict[str, typing.Any]] | None:
        match = self.find_language(value, context)
        if match:
            return match.start, match.end, {'value': match.value}

        return None


def language(config: Config) -> Rebulk:
    rebulk = Rebulk()
    rebulk.functional(LanguageFinder(config).find, name='language')

    return rebulk
