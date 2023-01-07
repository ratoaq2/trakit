import typing

import pytest

from rebulk.match import Match

from trakit.words import blank_match, blank_release_names, to_combinations, to_sentence, to_words

from . import parameters_from_yaml


@pytest.mark.parametrize('value, expected', parameters_from_yaml(__file__, 'to_words'))
def test_to_words(value: str, expected: typing.List[typing.Mapping[str, typing.Union[str, int]]]):
    # given
    expected_matches = [Match(d['start'], d['end'], value=d['value'], input_string=value) for d in expected]

    # when
    actual = to_words(value)

    # then
    assert actual == expected_matches
    for w in actual:
        assert w.input_string[w.start:w.end] == value[w.start:w.end]
        assert w.value == value[w.start:w.end]


@pytest.mark.parametrize('value, expected', parameters_from_yaml(__file__, 'to_combinations'))
def test_to_combinations(value: str, expected: typing.List[typing.List[typing.Mapping[str, typing.Union[str, int]]]]):
    # given
    expected_combinations = [[
            Match(d['start'], d['end'], value=d['value'], input_string=value) for d in items
        ] for items in expected]

    # when
    actual = to_combinations(to_words(value), 4)

    # then
    assert actual == expected_combinations


@pytest.mark.parametrize('expected, data', parameters_from_yaml(__file__, 'to_sentence'))
def test_to_sentence(expected: str, data: typing.List[typing.Mapping[str, typing.Union[str, int]]]):
    # given
    combination = [Match(m['start'], m['end'], value=m['value']) for m in data]

    # when
    actual = to_sentence(combination)

    # then
    assert actual == expected


@pytest.mark.parametrize('value, data', parameters_from_yaml(__file__, 'blank_match'))
def test_blank_match(value: str, data: typing.Mapping[str, typing.Union[str, int]]):
    # given
    match = Match(data['start'], data['end'], input_string=value)
    expected = data['expected']

    # when
    actual = blank_match(match)

    # then
    assert actual == expected


@pytest.mark.parametrize('value, expected', parameters_from_yaml(__file__, 'blank_release_names'))
def test_blank_release_names(value: str, expected: str):
    # given

    # when
    actual = blank_release_names(value)

    # then
    assert actual == expected
