import json
import os
import unicodedata

import trakit.config

from .generator import GENERATED_PATH, Generator

TRACKIT_PATH = os.path.join(os.path.dirname(trakit.__file__), 'data')


def remove_invisible_chars(obj):
    if isinstance(obj, dict):
        return {remove_invisible_chars(k): remove_invisible_chars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [remove_invisible_chars(i) for i in obj]
    if isinstance(obj, str):
        return ''.join(c for c in obj if unicodedata.category(c) != 'Cf')  # Removes format chars
    return obj


def test_generate_config():
    # given
    with open(os.path.join(TRACKIT_PATH, 'config.json'), 'r', encoding='utf-8') as f:
        expected = json.load(f)
    Generator().generate()

    # when
    with open(os.path.join(GENERATED_PATH, 'config.json'), 'r', encoding='utf-8') as f:
        actual = json.load(f)

    # then
    assert remove_invisible_chars(expected) == remove_invisible_chars(actual)
