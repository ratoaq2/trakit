import json
import typing
from importlib import resources


class Config:
    def __init__(self):
        content = resources.read_text('trakit.data', 'config.json', 'utf-8')
        cfg: typing.Mapping[str, typing.Any] = json.loads(content)
        self.ignored: typing.Set[str] = set(cfg.get('ignored', []))
        self.countries: typing.Mapping[str, str] = cfg.get('countries', {})
        self.languages: typing.Mapping[str, str] = cfg.get('languages', {})
        self.scripts: typing.Mapping[str, str] = cfg.get('scripts', {})
        self.regions: typing.Mapping[str, str] = cfg.get('regions', {})
        self.implicit_languages: typing.Mapping[str, str] = cfg.get('implicit-languages', {})
