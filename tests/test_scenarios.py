import pytest

from trakit import trakit

from . import parameters_from_yaml


@pytest.mark.parametrize('value, expected', parameters_from_yaml(__file__))
def test_scenarios(value, expected):
    # given

    # when
    actual = trakit(value)

    # then
    assert dict(actual) == expected
