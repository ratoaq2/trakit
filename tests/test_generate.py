import json
import os

import trakit.config

from .generator import GENERATED_PATH, Generator

TRACKIT_PATH = os.path.join(os.path.dirname(trakit.__file__), 'data')


def test_generate_config():
    # given
    with open(os.path.join(TRACKIT_PATH, 'config.json'), 'r', encoding='utf-8') as f:
        expected = json.load(f)
    Generator().generate()

    # when
    with open(os.path.join(GENERATED_PATH, 'config.json'), 'r', encoding='utf-8') as f:
        actual = json.load(f)

    # then
    assert expected == actual
