import re
from datetime import datetime
from json import load as load_json
from os import path

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from aerofiles.openair.reader import LowLevelReader, Reader, coordinate

import pytest


DATA = path.join(path.dirname(path.realpath(__file__)), 'data')

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z$")


# hook used during load_json: whenever we find a string like "2023-12-16T12:00Z"
# we convert it into datetime:
def convert_datetime(obj):
    for k, v in obj.items():
        if isinstance(v, str) and ISO_RE.match(v):
            obj[k] = datetime.fromisoformat(v.replace("Z", "+00:00"))
    return obj

# Fixtures ####################################################################


@pytest.fixture
def json():
    with open(path.join(DATA, 'sample.json')) as fp:
        return load_json(fp, object_hook=convert_datetime)


@pytest.fixture
def low_level_json():
    with open(path.join(DATA, 'sample-low-level.json')) as fp:
        return load_json(fp, object_hook=convert_datetime)


# Tests #######################################################################

def test_low_level_reader(low_level_json):
    with open(path.join(DATA, 'sample.txt')) as fp:
        reader = LowLevelReader(fp)

        for line_err, expected in zip_longest(reader, low_level_json):
            line, error = line_err

            assert error is None
            assert_line(line, expected)


def test_low_level_reader_error():
    with open(path.join(DATA, 'broken.txt')) as fp:
        reader = LowLevelReader(fp)

        for i, line_err in enumerate(reader):
            line, error = line_err

            if i == 7:
                assert isinstance(error, ValueError)
                assert error.lineno == 9
                assert line is None
            else:
                assert error is None
                assert line is not None

        assert i == 16


def test_reader(json):
    with open(path.join(DATA, 'sample.txt')) as fp:
        reader = Reader(fp)

        for record_err, expected in zip_longest(reader, json):
            record, error = record_err

            assert error is None
            assert_block(record, expected)


def test_reader_germany(json):
    with open(path.join(DATA, '2026_03_Airspace_Germany_OA1.txt')) as fp:
        reader = Reader(fp)

        count = 0
        for record_err, expected in zip_longest(reader, json):
            record, error = record_err

            assert error is None
            count += 1

        assert count == 678


def test_reader_error():
    with open(path.join(DATA, 'broken.txt')) as fp:
        reader = Reader(fp)

        for i, record_err in enumerate(reader):
            record, error = record_err

            if i == 0:
                assert isinstance(error, ValueError)
                assert error.lineno == 5
                assert record is None
            elif i == 1:
                assert isinstance(error, ValueError)
                assert error.lineno == 9
                assert record is None
            else:
                assert error is None
                assert record is not None

        assert i == 2


# Assertions ##################################################################

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
        assert value['ident'] == expected['ident']
        assert value['ground_name'] == expected['ground_name']
        assert value['freq'] == expected['freq']
        assert value['airspace_type'] == expected['airspace_type']
        assert value['floor'] == expected['floor']
        assert value['ceiling'] == expected['ceiling']
        for i in range(len(expected["activation"])):
            assert_dict_value_expected(value['activation'][i], expected['activation'][i])

        for x in zip(value['labels'], expected['labels']):
            assert_location(*x)

    elif value['type'] == 'terrain':
        assert value['open'] == expected['open']
        assert value['fill'] == expected['fill']
        assert value['outline'] == expected['outline']
        assert value['zoom'] == expected['zoom']

    for v, e in zip(value['elements'], expected['elements']):
        assert_element(v, e)


def assert_dict_value_expected(value, expected):
    for key in expected.keys():
        assert value[key] == expected[key]


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


def assert_line(value, expected):
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

    elif value['type'] == 'AA':
        assert_dict_value_expected(value, expected)

    else:
        assert value['value'] == expected['value']
