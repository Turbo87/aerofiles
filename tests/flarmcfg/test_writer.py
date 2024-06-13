# -*- coding: utf-8 -*-

from io import BytesIO

from aerofiles.flarmcfg import Writer

import pytest


@pytest.fixture()
def output():
    return BytesIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == b'line\r\n'


def test_write_config(writer):
    writer.write_config('ID', '4B3E60')
    assert writer.fp.getvalue() == b'$PFLAC,S,ID,4B3E60\r\n'


def test_write_pilot(writer):
    writer.write_pilot('FTV Spandau')
    assert writer.fp.getvalue() == b'$PFLAC,S,PILOT,FTV Spandau\r\n'


def test_write_copilot(writer):
    writer.write_copilot('John Doe')
    assert writer.fp.getvalue() == b'$PFLAC,S,COPIL,John Doe\r\n'


def test_write_glider_type(writer):
    writer.write_glider_type('Astir CS')
    assert writer.fp.getvalue() == b'$PFLAC,S,GLIDERTYPE,Astir CS\r\n'


def test_write_glider_id(writer):
    writer.write_glider_id('D-8551')
    assert writer.fp.getvalue() == b'$PFLAC,S,GLIDERID,D-8551\r\n'


def test_write_competition_id(writer):
    writer.write_competition_id('75')
    assert writer.fp.getvalue() == b'$PFLAC,S,COMPID,75\r\n'


def test_write_competition_class(writer):
    writer.write_competition_class('Club')
    assert writer.fp.getvalue() == b'$PFLAC,S,COMPCLASS,Club\r\n'


def test_write_logger_interval(writer):
    writer.write_logger_interval(4)
    assert writer.fp.getvalue() == b'$PFLAC,S,LOGINT,4\r\n'


def test_write_task_declaration(writer):
    writer.write_task_declaration('My Task')
    assert writer.fp.getvalue() == b'$PFLAC,S,NEWTASK,My Task\r\n'


def test_write_default_task_declaration(writer):
    writer.write_task_declaration()
    assert writer.fp.getvalue() == b'$PFLAC,S,NEWTASK,\r\n'


def test_waypoint(writer):
    writer.write_waypoint(
        latitude=(51 + 7.345 / 60.),
        longitude=(6 + 24.765 / 60.),
        description='Meiersberg',
    )
    assert writer.fp.getvalue() == \
        b'$PFLAC,S,ADDWP,5107345N,00624765E,Meiersberg\r\n'


def test_waypoint_with_negative_coordinates(writer):
    writer.write_waypoint(
        latitude=-(12 + 32.112 / 60.),
        longitude=-(178 + .001 / 60.),
        description='TAKEOFF',
    )
    assert writer.fp.getvalue() == \
        b'$PFLAC,S,ADDWP,1232112S,17800001W,TAKEOFF\r\n'


def test_default_waypoint(writer):
    writer.write_waypoint()
    assert writer.fp.getvalue() == b'$PFLAC,S,ADDWP,0000000N,00000000E,\r\n'


def test_waypoints(writer):
    writer.write_waypoints([
        (None, None, 'TAKEOFF'),
        (51.40375, 6.41275, 'START'),
        (50.38210, 8.82105, 'TURN 1'),
        (50.59045, 7.03555, 'TURN 2'),
        (51.40375, 6.41275, 'FINISH'),
        (None, None, 'LANDING'),
    ])

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'$PFLAC,S,ADDWP,0000000N,00000000E,TAKEOFF',
        b'$PFLAC,S,ADDWP,5124225N,00624765E,START',
        b'$PFLAC,S,ADDWP,5022926N,00849263E,TURN 1',
        b'$PFLAC,S,ADDWP,5035427N,00702133E,TURN 2',
        b'$PFLAC,S,ADDWP,5124225N,00624765E,FINISH',
        b'$PFLAC,S,ADDWP,0000000N,00000000E,LANDING',
    ]) + b'\r\n'


def test_invalid_waypoints(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_waypoints([
            (None, None, None, None),
        ])

    assert 'Invalid number of task point tuple items' in str(ex)
