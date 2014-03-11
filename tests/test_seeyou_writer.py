import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from aerofiles.seeyou import Writer, WaypointStyles


@pytest.fixture()
def output():
    return StringIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def test_header(writer):
    assert writer.fp.getvalue() == \
        'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n'


def test_write_line(writer):
    writer.fp = StringIO()
    writer.write_line('line')
    assert writer.fp.getvalue() == 'line\r\n'


def test_write_fields(writer):
    writer.fp = StringIO()
    writer.write_fields(['col1', 'col2', 'col3', 'bla'])
    assert writer.fp.getvalue() == 'col1,col2,col3,bla\r\n'


def test_write_waypoint(writer):
    writer.write_waypoint(
        'Meiersberg',
        'MEIER',
        'DE',
        (51 + 7.345 / 60.),
        (6 + 24.765 / 60.),
    )
    assert writer.fp.getvalue() == \
        'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        '"Meiersberg","MEIER",DE,5107.345N,00624.765E,,1,,,,\r\n'


def test_write_waypoint_with_negative_coordinates(writer):
    writer.write_waypoint(
        'Somewhere else',
        'ABCDEF42',
        'NZ',
        latitude=-(12 + 32.112 / 60.),
        longitude=-(178 + .001 / 60.),
    )
    assert writer.fp.getvalue() == \
        'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        '"Somewhere else","ABCDEF42",NZ,1232.112S,17800.001W,,1,,,,\r\n'


def test_write_waypoint_with_metadata(writer):
    writer.write_waypoint(
        'Meiersberg',
        'MEIER',
        'DE',
        (51 + 7.345 / 60.),
        (6 + 24.765 / 60.),
        (146., 'm'),
        WaypointStyles.AIRFIELD_GRASS,
        120,
        930,
        '130.125',
        'cozy little airfield'
    )
    assert writer.fp.getvalue() == \
        'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        '"Meiersberg","MEIER",DE,5107.345N,00624.765E,146.0m,2,120,930m,' \
        '"130.125","cozy little airfield"\r\n'
