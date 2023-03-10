import typing

import pytest

from tests import parameters_from_yaml

from trakit.__main__ import main


@pytest.mark.parametrize('name, data', parameters_from_yaml(__file__, 'main'))
def test_main(name: str, data: typing.Mapping[str, typing.Any]):
    # given
    args = data['args']
    expected = data['expected']

    # when
    actual = main(args)

    # then
    assert actual == expected
