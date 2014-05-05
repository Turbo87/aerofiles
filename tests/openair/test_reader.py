import pytest

from os import path
from json import load as load_json

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from aerofiles.openair.reader import Reader, LowLevelReader, coordinate


DATA_PATH = path.join(path.dirname(path.realpath(__file__)), 'data')
TEXT_PATH = path.join(DATA_PATH, 'sample.txt')
JSON_PATH = path.join(DATA_PATH, 'sample.json')
LL_JSON_PATH = path.join(DATA_PATH, 'sample-low-level.json')


@pytest.fixture
def json():
    with open(JSON_PATH) as fp:
        return load_json(fp)


@pytest.fixture
def low_level_json():
    with open(LL_JSON_PATH) as fp:
        return load_json(fp)


def test_reader(json):
    with open(TEXT_PATH) as fp:
        reader = Reader(fp)

        for block, expected in zip_longest(reader, json):
            assert_block(block, expected)

        assert reader.warnings == []


def test_low_level_reader(low_level_json):
    with open(TEXT_PATH) as fp:
        reader = LowLevelReader(fp)

        for result, expected in zip_longest(reader, low_level_json):
            result, error = result
            assert error is None
            assert_record(result, expected)


def assert_float(value, expected, threshold):
    assert abs(value - expected) < threshold


def assert_location(value, expected):
    # fallback because we're lazy
    if not isinstance(expected, list):
        expected = coordinate(expected)

    assert isinstance(value, list)
    assert len(value) == 2
    assert_float(value[0], expected[0], 0.0001)
    assert_float(value[1], expected[1], 0.0001)


def assert_block(value, expected):
    assert value is not None
    assert value['type'] == expected['type']
    assert value['name'] == expected['name']

    if value['type'] == 'airspace':
        assert value['class'] == expected['class']
        assert value['floor'] == expected['floor']
        assert value['ceiling'] == expected['ceiling']

        for x in zip(value['labels'], expected['labels']):
            assert_location(*x)

    elif value['type'] == 'terrain':
        assert value['open'] == expected['open']
        assert value['fill'] == expected['fill']
        assert value['outline'] == expected['outline']
        assert value['zoom'] == expected['zoom']

    for v, e in zip(value['elements'], expected['elements']):
        assert_element(v, e)


def assert_element(value, expected):
    assert value['type'] == expected['type']

    if value['type'] == 'point':
        assert_location(value['location'], expected['location'])

    elif value['type'] == 'circle':
        assert_location(value['center'], expected['center'])
        assert value['radius'] == expected['radius']

    elif value['type'] == 'arc':
        assert_location(value['center'], expected['center'])
        assert value['clockwise'] == expected['clockwise']

        if 'radius' in value:
            assert value['radius'] == expected['radius']
            assert value['start'] == expected['start']
            assert value['end'] == expected['end']
        else:
            assert_location(value['start'], expected['start'])
            assert_location(value['end'], expected['end'])


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
        assert_location(value['start'], expected['start'])
        assert_location(value['end'], expected['end'])

    elif value['type'] == 'AT' or \
            value['type'] == 'DP' or \
            value['type'] == 'DY':
        assert_location(value['value'], expected['value'])

    else:
        assert value['value'] == expected['value']
