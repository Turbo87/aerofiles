import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from aerofiles.flarmcfg import Writer


@pytest.fixture()
def output():
    return StringIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == 'line\r\n'


def test_write_config(writer):
    writer.write_config('ID', '4B3E60')
    assert writer.fp.getvalue() == '$PFLAC,S,ID,4B3E60\r\n'


def test_write_pilot(writer):
    writer.write_pilot('FTV Spandau')
    assert writer.fp.getvalue() == '$PFLAC,S,PILOT,FTV Spandau\r\n'


def test_write_glider_type(writer):
    writer.write_glider_type('Astir CS')
    assert writer.fp.getvalue() == '$PFLAC,S,GLIDERTYPE,Astir CS\r\n'
