import typing

import pytest

from tests import parameters_from_yaml

from trakit import api


@pytest.mark.parametrize('value, expected', parameters_from_yaml(__file__, 'default_api'))
def test_default_api(value: str, expected: typing.Mapping[str, typing.Any]):
    # when
    actual = api.trakit(value)

    # then
    assert actual == expected


@pytest.mark.parametrize('value, expected', parameters_from_yaml(__file__, 'options'))
def test_options(value: str, expected: typing.Dict[str, typing.Any]):
    # given
    options = expected['options']
    del expected['options']

    # when
    actual = api.trakit(value, options)

    # then
    assert actual == expected
