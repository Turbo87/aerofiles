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


@pytest.fixture()
def writer_with_waypoints(writer):
    writer.write_waypoint(
        'TP1',
        'TP1',
        'DE',
        (51 + 7.345 / 60.),
        (8 + 24.765 / 60.),
    )
    writer.write_waypoint(
        'TP2',
        'TP2',
        'NL',
        (50 + 7.345 / 60.),
        (6 + 24.765 / 60.),
    )
    writer.write_waypoint(
        'TP3',
        'TP3',
        'DE',
        (49 + 7.345 / 60.),
        (7 + 24.765 / 60.),
    )
    return writer


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


def test_write_task(writer_with_waypoints):
    writer_with_waypoints.write_task('TestTask', [
        'TP1', 'TP2', 'TP3', 'TP1',
    ])

    assert writer_with_waypoints.fp.getvalue() == \
        'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        '"TP1","TP1",DE,5107.345N,00824.765E,,1,,,,\r\n' \
        '"TP2","TP2",NL,5007.345N,00624.765E,,1,,,,\r\n' \
        '"TP3","TP3",DE,4907.345N,00724.765E,,1,,,,\r\n' \
        '\r\n' \
        '-----Related Tasks-----\r\n' \
        '"TestTask","TP1","TP2","TP3","TP1"\r\n'


def test_write_task_with_unknown_waypoint(writer_with_waypoints):
    with pytest.raises(ValueError):
        writer_with_waypoints.write_task('TestTask', [
            'TP1', 'TP2', 'TP3', 'TP4',
        ])


def test_write_waypoint_after_write_task(writer_with_waypoints):
    writer_with_waypoints.write_task('TestTask', [
        'TP1', 'TP2', 'TP3', 'TP1',
    ])

    with pytest.raises(RuntimeError):
        writer_with_waypoints.write_waypoint('XYZ', 'XYZ', 'DE', 0, 0)
