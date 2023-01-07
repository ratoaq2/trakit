import json
import typing

from pkg_resources import resource_stream


class Config:
    def __init__(self):
        with resource_stream('trakit', 'data/config.json') as f:
            cfg: typing.Mapping[str, typing.Any] = json.load(f)
        self.ignored: typing.Set[str] = set(cfg.get('ignored', []))
        self.countries: typing.Mapping[str, str] = cfg.get('countries', {})
        self.languages: typing.Mapping[str, str] = cfg.get('languages', {})
        self.scripts: typing.Mapping[str, str] = cfg.get('scripts', {})
        self.regions: typing.Mapping[str, str] = cfg.get('regions', {})
        self.implicit_languages: typing.Mapping[str, str] = cfg.get('implicit-languages', {})
