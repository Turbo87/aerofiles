import pytest

import datetime
from StringIO import StringIO

from aerofiles.igc import Writer


@pytest.fixture()
def output():
    return StringIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == 'line\r\n'


@pytest.fixture(params=['XXX', 'GCS', 'FIL', 'FLA'])
def manufacturer_code(request):
    return request.param


@pytest.fixture(params=['ABC', 'NG6', 'ART'])
def logger_id(request):
    return request.param


def test_logger_id(writer, manufacturer_code, logger_id):
    writer.write_logger_id(manufacturer_code, logger_id)
    assert writer.fp.getvalue() == \
        'A%s%s\r\n' % (manufacturer_code, logger_id)


def test_logger_id_with_extension(writer, manufacturer_code, logger_id):
    writer.write_logger_id(manufacturer_code, logger_id, 'FLIGHT:1')
    assert writer.fp.getvalue() == \
        'A%s%sFLIGHT:1\r\n' % (manufacturer_code, logger_id)


def test_logger_id_with_invalid_manufacturer_code(writer):
    with pytest.raises(ValueError):
        writer.write_logger_id('x_1', 'ABC')


def test_logger_id_with_invalid_logger_id(writer):
    with pytest.raises(ValueError):
        writer.write_logger_id('XXX', '12345')


def test_logger_id_without_validation(writer):
    writer.write_logger_id('a4%', '12345', validate=False)
    assert writer.fp.getvalue() == 'Aa4%12345\r\n'


@pytest.fixture(params=[
    (1996, 12, 24),
    (2014, 1, 31),
    (2032, 8, 5),
])
def date(request):
    return datetime.date(*request.param)


def test_date(writer, date):
    writer.write_date(date)
    assert writer.fp.getvalue() == date.strftime('HFDTE%y%m%d\r\n')


@pytest.fixture(params=[
    'Tobias Bieniek',
    'Some guy named FOO',
    'Deep Thought',
])
def pilot(request):
    return request.param


def test_pilot(writer, pilot):
    writer.write_pilot(pilot)
    assert writer.fp.getvalue() == 'HFPLTPILOTINCHARGE:%s\r\n' % pilot


def test_copilot(writer, pilot):
    writer.write_copilot(pilot)
    assert writer.fp.getvalue() == 'HFCM2CREW2:%s\r\n' % pilot
