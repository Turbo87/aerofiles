# -*- coding: utf-8 -*-

import pytest

from io import BytesIO

from aerofiles.flarmcfg import Writer

TASK_DICT_FIELDS = [  # list of tuples (key, input, output)
    ('pilot', 'FTV Spandau', b'$PFLAC,S,PILOT,FTV Spandau\r\n'),
    ('copilot', 'John Doe', b'$PFLAC,S,COPIL,John Doe\r\n'),
    ('competition_class', 'Club', b'$PFLAC,S,COMPCLASS,Club\r\n'),
    ('glider_type', 'Astir CS', b'$PFLAC,S,GLIDERTYPE,Astir CS\r\n'),
    ('glider_id', 'D-8551', b'$PFLAC,S,GLIDERID,D-8551\r\n'),
    ('competition_id', '75', b'$PFLAC,S,COMPID,75\r\n'),
    ('logger_interval', 4, b'$PFLAC,S,LOGINT,4\r\n'),
    ('task_name', 'My Task', b'$PFLAC,S,NEWTASK,My Task\r\n')
]

WAYPOINT_LISTS = [
    [
        (None, None, 'Hilversum'),
        (51.40375, 6.41275, 'Hilversum'),
        (50.38210, 8.82105, 'Borken Hoxfeld'),
        (50.59045, 7.03555, 'Hoogeveen'),
        (51.40375, 6.41275, 'Hilversum'),
        (None, None, 'Hilversum'),
    ],
    [
        (None, None, 'Hilversum'),
        (51.40375, 6.41275, 'Hilversum'),
        (51.40375, 6.41275, 'Hilversum'),
        (None, None, 'Hilversum'),
    ]
]

TASK_DICTS = [  #list op tuples (input dictionary, output string)
    ({  # complete task dictionary
         "competition_class": "Club",
         "competition_id": "GO4",
         "pilot": "John Doe",
         "copilot": "Roger",
         "glider_id": "PH-790",
         "glider_type": "LS4",
         "logger_interval": 1,
         "waypoints": WAYPOINT_LISTS[0],
         "task_name": "FAI-300k"},

     b'\r\n'.join([
         b'$PFLAC,S,PILOT,John Doe',
         b'$PFLAC,S,COPIL,Roger',
         b'$PFLAC,S,COMPCLASS,Club',
         b'$PFLAC,S,GLIDERTYPE,LS4',
         b'$PFLAC,S,GLIDERID,PH-790',
         b'$PFLAC,S,COMPID,GO4',
         b'$PFLAC,S,LOGINT,1',
         b'$PFLAC,S,NEWTASK,FAI-300k',
         b'$PFLAC,S,ADDWP,0000000N,00000000E,Hilversum',
         b'$PFLAC,S,ADDWP,5124225N,00624765E,Hilversum',
         b'$PFLAC,S,ADDWP,5022926N,00849263E,Borken Hoxfeld',
         b'$PFLAC,S,ADDWP,5035427N,00702133E,Hoogeveen',
         b'$PFLAC,S,ADDWP,5124225N,00624765E,Hilversum',
         b'$PFLAC,S,ADDWP,0000000N,00000000E,Hilversum']) + b'\r\n'
     ),
    ({  # Only waypoints and task_name, rest None
         "competition_class": None,
         "competition_id": None,
         "pilot": None,
         "copilot": None,
         "glider_id": None,
         "glider_type": None,
         "logger_interval": None,
         "waypoints": WAYPOINT_LISTS[0],
         "task_name": "FAI-300k"},

     b'\r\n'.join([
         b'$PFLAC,S,NEWTASK,FAI-300k',
         b'$PFLAC,S,ADDWP,0000000N,00000000E,Hilversum',
         b'$PFLAC,S,ADDWP,5124225N,00624765E,Hilversum',
         b'$PFLAC,S,ADDWP,5022926N,00849263E,Borken Hoxfeld',
         b'$PFLAC,S,ADDWP,5035427N,00702133E,Hoogeveen',
         b'$PFLAC,S,ADDWP,5124225N,00624765E,Hilversum',
         b'$PFLAC,S,ADDWP,0000000N,00000000E,Hilversum']) + b'\r\n'
     ),
    ({  # Only waypoints and task_name
         "task_name": "FAI-300k",
         "waypoints": WAYPOINT_LISTS[0]},

     b'\r\n'.join([
         b'$PFLAC,S,NEWTASK,FAI-300k',
         b'$PFLAC,S,ADDWP,0000000N,00000000E,Hilversum',
         b'$PFLAC,S,ADDWP,5124225N,00624765E,Hilversum',
         b'$PFLAC,S,ADDWP,5022926N,00849263E,Borken Hoxfeld',
         b'$PFLAC,S,ADDWP,5035427N,00702133E,Hoogeveen',
         b'$PFLAC,S,ADDWP,5124225N,00624765E,Hilversum',
         b'$PFLAC,S,ADDWP,0000000N,00000000E,Hilversum']) + b'\r\n'
     )
]

TASK_DICTS_WRONG = [  # list of tuples(input dictionary, exception, exception string)
    ({  # waypoints is None -> Error
         "competition_class": "Club",
         "competition_id": "GO4",
         "pilot": "John Doe",
         "copilot": "Roger",
         "glider_id": "PH-790",
         "glider_type": "LS4",
         "logger_interval": 1,
         "waypoints": None,
         "task_name": "FAI-300k"},

     TypeError,

     "waypoints and task_name should be contained in the task dictionary and can not be None"
     ),
    ({  # missing task_name -> Error
         "competition_class": "Club",
         "competition_id": "GO4",
         "pilot": "John Doe",
         "copilot": "Roger",
         "glider_id": "PH-790",
         "glider_type": "LS4",
         "logger_interval": 1,
         "waypoints": WAYPOINT_LISTS[0]},

     TypeError,

     "waypoints and task_name should be contained in the task dictionary and can not be None"
     ),
    ({  # waypoints has less than 5 entries -> Error
         "competition_class": "Club",
         "competition_id": "GO4",
         "pilot": "John Doe",
         "copilot": "Roger",
         "glider_id": "PH-790",
         "glider_type": "LS4",
         "logger_interval": 1,
         "waypoints": WAYPOINT_LISTS[1],
         "task_name": "FAI-300k"},

     ValueError,

     "There should be at least 5 waypoints (take-off, start, turnpoint, finish, landing"
     )
]


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


def test_write_field():
    for index in range(len(TASK_DICT_FIELDS)):
        writer = Writer(BytesIO())
        writer.write_field(TASK_DICT_FIELDS[index][0], TASK_DICT_FIELDS[index][1])
        assert writer.fp.getvalue() == TASK_DICT_FIELDS[index][2]


def test_invalid_field(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_field('invalid_key', 'invalid_value')

    assert "There is no functions to write invalid_key" in str(ex)


def test_write_field_waypoints(writer):
    writer.write_field('waypoints', [
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


def test_write_declared_task():

    # assertions on all good task dicts
    for index in range(len(TASK_DICTS)):
        writer = Writer(BytesIO())
        writer.write_declared_task(TASK_DICTS[index][0])
        assert writer.fp.getvalue() == TASK_DICTS[index][1]

    # assertions on all wrong task dicts
    for index in range(len(TASK_DICTS_WRONG)):
        writer = Writer(BytesIO())
        with pytest.raises(TASK_DICTS_WRONG[index][1]) as ex:
            writer.write_declared_task(TASK_DICTS_WRONG[index][0])
        assert TASK_DICTS_WRONG[index][2] in str(ex)
