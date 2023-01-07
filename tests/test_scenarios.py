import pytest

from trackit import trackit

from . import parameters_from_yaml


@pytest.mark.parametrize('value, expected', parameters_from_yaml(__file__))
def test_scenarios(value, expected):
    # given

    # when
    actual = trackit(value)

    # then
    assert dict(actual) == expected
