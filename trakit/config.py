import json
import typing
from importlib.resources import as_file, files


class Config:
    def __init__(self):
        with as_file(files('trakit.data').joinpath('config.json')) as f:
            cfg: typing.Mapping[str, typing.Any] = json.loads(f.read_text(encoding='utf-8'))

        self.ignored: typing.Set[str] = set(cfg.get('ignored', []))
        self.countries: typing.Mapping[str, str] = cfg.get('countries', {})
        self.languages: typing.Mapping[str, str] = cfg.get('languages', {})
        self.scripts: typing.Mapping[str, str] = cfg.get('scripts', {})
        self.regions: typing.Mapping[str, str] = cfg.get('regions', {})
        self.implicit_languages: typing.Mapping[str, str] = cfg.get('implicit-languages', {})
