from io import BytesIO
from os import path

from aerofiles.openair.writer import Writer

import pytest

DATA = path.join(path.dirname(path.realpath(__file__)), 'data')


# Fixtures ####################################################################

@pytest.fixture()
def output():
    return BytesIO()


@pytest.fixture()
def writer(output):
    return Writer(output)

# Tests #######################################################################


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == b'line\r\n'


def test_write_DP(writer):
    element = {"location": [-39.58333, -118.98888]}
    writer.write_DP(element)
    assert writer.fp.getvalue() == b'DP 39:35:00 S 118:59:20 W\r\n'


def test_write_DC(writer):
    element = {"center": [39.58333, 118.98888], "radius": 10}
    writer.write_DC(element)
    assert writer.fp.getvalue() == b'V X=39:35:00 N 118:59:20 E\r\nDC 10\r\n'


def test_write_DA(writer):
    element = {"center": [39.58333, 118.98888],
               "radius": 10.1,
               "start": 44.9, "end": 88, "clockwise": True}
    writer.write_DA(element)

    # Make sure, that "V X=" is not repeated but "V D=" is used:
    element["clockwise"] = False
    writer.write_DA(element)

    assert writer.fp.getvalue() == b'V X=39:35:00 N 118:59:20 E\r\nDA 10.1,44.9,88\r\nV D=-\r\nDA 10.1,44.9,88\r\n'


def test_write_DB(writer):
    element = {"center": [39.495, -119.775],
               "start": [39.61333, -119.76833],
               "end": [39.49833, -119.60166],
               "clockwise": True}
    writer.write_DB(element)

    assert writer.fp.getvalue() == b'V X=39:29:42 N 119:46:30 W\r\nDB 39:36:48 N 119:46:06 W, 39:29:54 N 119:36:06 W\r\n'


def test_write_record(writer):
    record = {
        "type": "airspace",
        "class": "C",
        "name": "RENO",
        "floor": "7200 ft",
        "ceiling": "8400 ft",
        "elements": [{
            "type": "arc",
            "center": [39.495, -119.775],
            "radius": 10,
            "start": 270,
            "end": 290,
            "clockwise": True
        }, {
            "type": "arc",
            "center": [39.495, -119.775],
            "radius": 7,
            "start": 290,
            "end": 320,
            "clockwise": False
        }, {
            "type": "arc",
            "center": [39.495, -119.775],
            "start": [39.61333, -119.76833],
            "end": [39.49833, -119.60166],
            "clockwise": True
        }, {
            "type": "point",
            "location": [39.495, -119.775]
        }, {
            "type": "circle",
            "center": [39.495, -119.775],
            "radius": 5,
        }]
    }
    writer.write_record(record)
    assert writer.fp.getvalue() == b'\r\n'.join([
        b'AC C',
        b'AN RENO',
        b'AH 8400 ft',
        b'AL 7200 ft',
        b'V X=39:29:42 N 119:46:30 W',
        b'DA 10,270,290',
        b'V D=-',
        b'DA 7,290,320',
        b'V D=+',
        b'DB 39:36:48 N 119:46:06 W, 39:29:54 N 119:36:06 W',
        b'DP 39:29:42 N 119:46:30 W',
        b'DC 5',
    ]) + b'\r\n'


# Assertions ##################################################################
