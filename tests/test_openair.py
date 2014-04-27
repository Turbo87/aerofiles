import pytest

from os import path
from json import load as load_json

from aerofiles.openair.reader import LowLevelReader, coordinate


DATA_PATH = path.join(path.dirname(path.realpath(__file__)), 'data')
TEXT_PATH = path.join(DATA_PATH, 'openair', 'sample.txt')
LL_JSON_PATH = path.join(DATA_PATH, 'openair', 'sample-low-level.json')


@pytest.fixture
def low_level_json():
    with open(LL_JSON_PATH) as fp:
        return load_json(fp)


def test_low_level_reader(low_level_json):
    with open(TEXT_PATH) as fp:
        reader = LowLevelReader(fp)

        for record, expected in zip(reader, low_level_json):
            assert_record(record, expected)

        assert reader.warnings == []


def assert_float(value, expected, threshold):
    assert abs(value - expected) < threshold


def assert_location(value, expected):
    # fallback because we're lazy
    if isinstance(expected, (str, unicode)):
        expected = coordinate(expected)

    assert isinstance(value, list)
    assert len(value) == 2
    assert_float(value[0], expected[0], 0.0001)
    assert_float(value[1], expected[1], 0.0001)


def assert_record(value, expected):
    assert value['type'] == expected['type']

    if value['type'] == 'V':
        assert value['name'] == expected['name']

        if value['name'] == 'X':
            assert_location(value['value'], expected['value'])
        else:
            assert value['value'] == expected['value']

    elif value['type'] == 'DA':
        assert value['radius'] == expected['radius']
        assert value['start'] == expected['start']
        assert value['end'] == expected['end']

    elif value['type'] == 'DB':
        assert value['start'] == expected['start']
        assert value['end'] == expected['end']

    elif value['type'] == 'AT' or \
            value['type'] == 'DP' or \
            value['type'] == 'DY':
        assert_location(value['value'], expected['value'])

    else:
        assert value['value'] == expected['value']
