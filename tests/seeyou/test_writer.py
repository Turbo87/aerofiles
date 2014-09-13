# -*- coding: utf-8 -*-

import pytest
import datetime

from io import BytesIO

from aerofiles.seeyou import Writer, WaypointStyle, ObservationZoneStyle


@pytest.fixture()
def output():
    return BytesIO()


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
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n'


def test_write_line(writer):
    writer.fp = BytesIO()
    writer.write_line('line')
    assert writer.fp.getvalue() == b'line\r\n'


def test_write_line_with_utf8(writer):
    writer.fp = BytesIO()
    writer.write_line(u'Köln')
    assert writer.fp.getvalue() == b'K\xc3\xb6ln\r\n'


def test_write_line_with_latin1(output):
    writer = Writer(output, 'latin1')
    writer.fp = BytesIO()
    writer.write_line(u'Köln')
    assert writer.fp.getvalue() == b'K\xf6ln\r\n'


def test_write_fields(writer):
    writer.fp = BytesIO()
    writer.write_fields([u'col1', u'col2', u'col3', u'bla'])
    assert writer.fp.getvalue() == b'col1,col2,col3,bla\r\n'


def test_write_waypoint(writer):
    writer.write_waypoint(
        'Meiersberg',
        'MEIER',
        'DE',
        (51 + 7.345 / 60.),
        (6 + 24.765 / 60.),
    )
    assert writer.fp.getvalue() == \
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        b'"Meiersberg","MEIER",DE,5107.345N,00624.765E,,1,,,,\r\n'


def test_write_waypoint_with_negative_coordinates(writer):
    writer.write_waypoint(
        'Somewhere else',
        'ABCDEF42',
        'NZ',
        latitude=-(12 + 32.112 / 60.),
        longitude=-(178 + .001 / 60.),
    )
    assert writer.fp.getvalue() == \
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        b'"Somewhere else","ABCDEF42",NZ,1232.112S,17800.001W,,1,,,,\r\n'


def test_write_waypoint_with_metadata(writer):
    writer.write_waypoint(
        'Meiersberg',
        'MEIER',
        'DE',
        (51 + 7.345 / 60.),
        (6 + 24.765 / 60.),
        (146., 'm'),
        WaypointStyle.AIRFIELD_GRASS,
        120,
        930,
        '130.125',
        'cozy little airfield'
    )
    assert writer.fp.getvalue() == \
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        b'"Meiersberg","MEIER",DE,5107.345N,00624.765E,146.0m,2,120,930m,' \
        b'"130.125","cozy little airfield"\r\n'


def test_write_task(writer_with_waypoints):
    writer_with_waypoints.write_task('TestTask', [
        'TP1', 'TP2', 'TP3', 'TP1',
    ])

    assert writer_with_waypoints.fp.getvalue() == \
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        b'"TP1","TP1",DE,5107.345N,00824.765E,,1,,,,\r\n' \
        b'"TP2","TP2",NL,5007.345N,00624.765E,,1,,,,\r\n' \
        b'"TP3","TP3",DE,4907.345N,00724.765E,,1,,,,\r\n' \
        b'\r\n' \
        b'-----Related Tasks-----\r\n' \
        b'"TestTask","TP1","TP2","TP3","TP1"\r\n'


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


def test_write_task_options(writer_with_waypoints):
    writer_with_waypoints.write_task('TestTask', [
        'TP1', 'TP2', 'TP3', 'TP1',
    ])

    writer_with_waypoints.write_task_options(
        start_time=datetime.time(12, 34, 56),
        task_time=datetime.timedelta(hours=1, minutes=45, seconds=12),
        waypoint_distance=False,
        distance_tolerance=(0.7, 'km'),
        altitude_tolerance=300.0,
    )

    assert writer_with_waypoints.fp.getvalue() == \
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        b'"TP1","TP1",DE,5107.345N,00824.765E,,1,,,,\r\n' \
        b'"TP2","TP2",NL,5007.345N,00624.765E,,1,,,,\r\n' \
        b'"TP3","TP3",DE,4907.345N,00724.765E,,1,,,,\r\n' \
        b'\r\n' \
        b'-----Related Tasks-----\r\n' \
        b'"TestTask","TP1","TP2","TP3","TP1"\r\n' \
        b'Options,NoStart=12:34:56,TaskTime=01:45:12,WpDis=False,' \
        b'NearDis=0.7km,NearAlt=300.0m\r\n'


def test_write_task_options2(writer_with_waypoints):
    writer_with_waypoints.write_task('TestTask', [
        'TP1', 'TP2', 'TP3', 'TP1',
    ])

    writer_with_waypoints.write_task_options(
        min_distance=False,
        random_order=False,
        max_points=5,
        before_points=1,
        after_points=2,
        bonus=200,
    )

    assert writer_with_waypoints.fp.getvalue() == \
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        b'"TP1","TP1",DE,5107.345N,00824.765E,,1,,,,\r\n' \
        b'"TP2","TP2",NL,5007.345N,00624.765E,,1,,,,\r\n' \
        b'"TP3","TP3",DE,4907.345N,00724.765E,,1,,,,\r\n' \
        b'\r\n' \
        b'-----Related Tasks-----\r\n' \
        b'"TestTask","TP1","TP2","TP3","TP1"\r\n' \
        b'Options,MinDis=False,RandomOrder=False,MaxPts=5,BeforePts=1,' \
        b'AfterPts=2,Bonus=200\r\n'


def test_write_task_options_in_waypoints_section(writer_with_waypoints):
    with pytest.raises(RuntimeError):
        writer_with_waypoints.write_task_options()


def test_write_observation_zone(writer_with_waypoints):
    writer_with_waypoints.write_task('TestTask', [
        'TP1', 'TP2', 'TP3', 'TP1',
    ])

    writer_with_waypoints.write_observation_zone(
        0, style=2, radius=400, angle=180, line=True,
    )

    writer_with_waypoints.write_observation_zone(
        1, style=ObservationZoneStyle.FIXED, radius=35000, angle=30,
        radius2=12000, angle2=12, angle12=123.4
    )

    writer_with_waypoints.write_observation_zone(
        2, style=3, radius=(2000, 'm'), angle=180, line=True,
    )

    assert writer_with_waypoints.fp.getvalue() == \
        b'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\r\n' \
        b'"TP1","TP1",DE,5107.345N,00824.765E,,1,,,,\r\n' \
        b'"TP2","TP2",NL,5007.345N,00624.765E,,1,,,,\r\n' \
        b'"TP3","TP3",DE,4907.345N,00724.765E,,1,,,,\r\n' \
        b'\r\n' \
        b'-----Related Tasks-----\r\n' \
        b'"TestTask","TP1","TP2","TP3","TP1"\r\n' \
        b'ObsZone=0,Style=2,R1=400m,A1=180,Line=1\r\n' \
        b'ObsZone=1,Style=0,R1=35000m,A1=30,R2=12000m,A2=12,A12=123.4\r\n' \
        b'ObsZone=2,Style=3,R1=2000m,A1=180,Line=1\r\n'


def test_write_observation_zone_in_waypoints_section(writer_with_waypoints):
    with pytest.raises(RuntimeError):
        writer_with_waypoints.write_observation_zone(0)
