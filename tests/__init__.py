import os
import typing

import yaml


def read_yaml(file_path: str) -> typing.Any:
    with open(file_path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def parameters_from_yaml(test_filename: str, test_name: str | None = None) -> list[tuple[typing.Any, typing.Any]]:
    base_path = os.path.splitext(test_filename)[0]
    yml_file = f'{base_path}__{test_name}.yml' if test_name else f'{base_path}.yml'
    data = read_yaml(yml_file)

    return list(data.items())
