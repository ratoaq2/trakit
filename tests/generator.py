import json
import os
import re
import typing
from urllib.request import urlretrieve

from babelfish import Country, Language, LanguageReverseError

from unidecode import unidecode

CUR_PATH = os.path.dirname(__file__)
GENERATED_PATH = os.path.join(CUR_PATH, 'generated')
DOWNLOADED_PATH = os.path.join(CUR_PATH, 'downloaded')

suppress_re = re.compile(r"[\(\)'\,\.\u200f]")

with open(os.path.join(CUR_PATH, 'generator.json'), 'r', encoding='utf-8') as cfg_file:
    CONFIG: typing.Dict[str, typing.Any] = json.load(cfg_file)
    CONFIG['ignored_words'] = set(CONFIG['ignored_words'])
    CONFIG['countries']['ignore-extraction'] = set(CONFIG['countries']['ignore-extraction'])
    CONFIG['languages']['ignore-extraction'] = set(CONFIG['languages']['ignore-extraction'])
    additional_languages: typing.Mapping[str, str] = dict(CONFIG['languages']['additional'])
    for lang_syn, code in additional_languages.items():
        CONFIG['languages']['additional'][unidecode(lang_syn)] = code


class ConfigGenerator:
    def __init__(self,
                 country_demonyms: typing.Dict[str, str],
                 country_native_names: typing.Dict[str, typing.List[str]],
                 language_english_names: typing.Dict[str, str],
                 language_native_names: typing.Dict[str, str]):
        self.country_demonyms = country_demonyms
        self.country_native_names = country_native_names
        self.language_english_names = language_english_names
        self.language_native_names = language_native_names

    def register_duplicate(self,
                           name: str,
                           previous_value: str,
                           new_value: str,
                           duplicated: typing.Dict[str, typing.List[str]]):
        if name not in duplicated:
            duplicated[name] = []
        duplicated[name].append(previous_value)
        duplicated[name].append(new_value)

    def to_unique_values(self, values: typing.Iterable[str]):
        values = set([suppress_re.sub('', v).replace('-', ' ').strip() for v in values])
        unidecoded = [suppress_re.sub('', unidecode(v)) for v in values]
        values.update([v.strip() for v in unidecoded if '@' not in v])
        return [v for v in values if len(v) > 0]

    def register_country_synonym(self, country: Country, name: str,
                                 country_synonyms: typing.Dict[str, str],
                                 dup_country_syns: typing.Dict[str, typing.List[str]]):
        name = suppress_re.sub('', name)
        if name.upper() == country.name:
            return
        if name in country_synonyms and country_synonyms[name] != country.alpha2:
            self.register_duplicate(name, country_synonyms[name], country.alpha2, dup_country_syns)
            return

        country_synonyms[name] = country.alpha2

    @property
    def config(self):
        country_synonyms = dict(CONFIG['countries']['additional'])
        dup_country_syns = {}
        for alpha2, names in self.country_native_names.items():
            country = Country(alpha2)
            for name in self.to_unique_values(names):
                self.register_country_synonym(country, name, country_synonyms, dup_country_syns)

        for alpha2, demonym in self.country_demonyms.items():
            if alpha2 in CONFIG['countries']['ignored-ambiguous-demonyms']:
                continue

            country = Country(alpha2)
            for d in self.to_unique_values([demonym]):
                self.register_country_synonym(country, d, country_synonyms, dup_country_syns)

        for alpha2, demonyms in CONFIG['countries']['additional-demonyms'].items():
            country = Country(alpha2)
            for d in self.to_unique_values(demonyms):
                self.register_country_synonym(country, d, country_synonyms, dup_country_syns)

        language_synonyms = dict(CONFIG['languages']['additional'])
        ignore_extraction = CONFIG['countries']['ignore-extraction']
        dup_language_syns = {}
        all_names = dict(self.language_english_names)
        all_names.update(self.language_native_names)
        country_re = re.compile(r'^(?P<pre>.*)[\(\uff08](?P<country>[^)\uff09]+)[\)\uff09](?P<pos>.*)$')
        for ietf, synonym in all_names.items():
            language = Language.fromietf(ietf)
            m = country_re.match(synonym)
            country_extracted = m and language.country and language.alpha3 not in ignore_extraction
            c = m.group('country').strip() if country_extracted else None
            syn = (m.group('pre') or m.group('pos')).strip() if country_extracted else synonym
            if c:
                for name in self.to_unique_values([c]):
                    self.register_country_synonym(language.country, name, country_synonyms, dup_country_syns)
            lang_code = str(language) if language.script else language.alpha3
            for name in self.to_unique_values([syn]):
                name = suppress_re.sub('', name)
                if name.lower() == language.name.lower():
                    continue
                if name in language_synonyms and language_synonyms[name] != lang_code:
                    self.register_duplicate(name, language_synonyms[name], lang_code, dup_language_syns)
                    continue

                language_synonyms[name] = lang_code

        if dup_country_syns:
            print(f'Duplicated country synonyms: {dup_country_syns}')
        if dup_language_syns:
            print(f'Duplicated language synonyms: {dup_language_syns}')

        scripts = dict(CONFIG['scripts'])
        scripts.update({unidecode(k): v for k, v in scripts.items()})

        regions = dict(CONFIG['regions'])
        regions.update({unidecode(k): v for k, v in regions.items()})

        return {
            'ignored': sorted([v for v in CONFIG['ignored_words']]),
            'countries': country_synonyms,
            'languages': language_synonyms,
            'implicit-languages': CONFIG['languages']['implicit'],
            'scripts': scripts,
            'regions': regions
        }

    def generate(self):
        config = self.config
        with open(os.path.join(GENERATED_PATH, 'config.json'), 'w', encoding='utf-8') as out:
            json.dump(config, out, ensure_ascii=False, indent=2, sort_keys=True)


class Generator:

    def __init__(self):
        self.country_demonyms: typing.Dict[str, str] = {}
        self.country_additional_demonyms: typing.Dict[str, typing.List[str]] = {}
        self.country_native_names: typing.Dict[str, typing.List[str]] = {}
        self.language_english_names: typing.Dict[str, str] = {}
        self.language_native_names: typing.Dict[str, str] = {}

    def generate(self):
        self.download_files()
        self.process_countries()
        self.process_languages()
        self.generate_files()
        ConfigGenerator(self.country_demonyms,
                        self.country_native_names,
                        self.language_english_names,
                        self.language_native_names).generate()

    def generate_files(self):
        if not os.path.isdir(GENERATED_PATH):
            os.mkdir(GENERATED_PATH)
        with open(os.path.join(GENERATED_PATH, 'country-demonyms.json'), 'w', encoding='utf-8') as out:
            json.dump(self.country_demonyms, out, ensure_ascii=False, indent=2)
        with open(os.path.join(GENERATED_PATH, 'country-native-names.json'), 'w', encoding='utf-8') as out:
            json.dump(self.country_native_names, out, ensure_ascii=False, indent=2)
        with open(os.path.join(GENERATED_PATH, 'language-english-names.json'), 'w', encoding='utf-8') as out:
            json.dump(self.language_english_names, out, ensure_ascii=False, indent=2)
        with open(os.path.join(GENERATED_PATH, 'language-native-names.json'), 'w', encoding='utf-8') as out:
            json.dump(self.language_native_names, out, ensure_ascii=False, indent=2)
        with open(os.path.join(GENERATED_PATH, 'country-demonyms.txt'), 'w', encoding='utf-8') as out:
            for k, v in self.country_demonyms.items():
                if v:
                    if k in CONFIG['countries']['ignored-ambiguous-demonyms']:
                        out.write('#')
                    out.write(f'{k}={v}\n')

    def download_files(self):
        countries_path = os.path.join(DOWNLOADED_PATH, 'countries.json')
        language_mapping_list_path = os.path.join(DOWNLOADED_PATH, 'language-mapping-list.js')
        language_mapping_json_path = os.path.join(DOWNLOADED_PATH, 'language-mapping-list.json')

        if not os.path.isdir(DOWNLOADED_PATH):
            os.mkdir(DOWNLOADED_PATH)
        if not os.path.isfile(countries_path):
            urlretrieve(CONFIG['urls']['countries'], countries_path)
        if not os.path.isfile(language_mapping_list_path):
            urlretrieve(CONFIG['urls']['local-language-names'], language_mapping_list_path)
        if not os.path.isfile(language_mapping_json_path):
            with open(language_mapping_list_path, 'r', encoding='utf-8') as f:
                content: str = f.read()
                content = content[content.index('  return {')+9:content.index('  };')+3]
                content = re.sub(r"'(?P<ietf>\w+([\-\@]\w+)?)'\:", r'"\g<ietf>":', content)
                content = re.sub(r"\b(?P<name>\w+)\b\:", r'"\g<name>":', content)
                with open(language_mapping_json_path, 'w', encoding='utf-8') as out:
                    out.write(content)

    def process_country_demonym(self,
                                country: Country,
                                c: typing.Mapping[str, typing.Any]):
        demonym = c['demonyms']['eng']['m']
        if demonym:
            self.country_demonyms[country.alpha2] = demonym

    def process_country_native_names(self,
                                     country: Country,
                                     c: typing.Mapping[str, typing.Any]):
        for v in c['name']['native'].values():
            name = v['common']
            if country.alpha2 not in self.country_native_names:
                self.country_native_names[country.alpha2] = []
            names = self.country_native_names[country.alpha2]
            if name not in names:
                names.append(name)

    def process_language_names(self,
                               language: Language,
                               names: typing.Mapping[str, str]):
        ietf = str(language)
        self.language_english_names[ietf] = names['englishName']
        self.language_native_names[ietf] = names['nativeName']

    def process_countries(self):
        with open(os.path.join(DOWNLOADED_PATH, 'countries.json'), 'r', encoding='utf-8') as f:
            countries = json.load(f)
            for c in countries:
                try:
                    country = Country(c['cca2'])
                    self.process_country_demonym(country, c)
                    self.process_country_native_names(country, c)
                except ValueError:
                    print(f'Unknown babelfish.Country {c["cca2"]}: {c["name"]["common"]}')
        self.country_demonyms.update(CONFIG['countries']['overriden-demonyms'])

    def process_languages(self):
        with open(os.path.join(DOWNLOADED_PATH, 'language-mapping-list.json'), 'r', encoding='utf-8') as f:
            languages = json.load(f)
            for ietf, names in languages.items():
                if ietf in CONFIG['languages']['ignore-extraction']:
                    continue

                try:
                    language = Language.fromietf(ietf)
                    self.process_language_names(language, names)
                except (ValueError, LanguageReverseError):
                    print(f'Unknown babelfish.Language {ietf}: {names}')
