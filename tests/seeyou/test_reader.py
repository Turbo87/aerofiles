from os import path

import pytest

from aerofiles.errors import ParserError
from aerofiles.seeyou import Reader, Converter

from tests import assert_waypoint

FOLDER = path.dirname(path.realpath(__file__))
DATA_PATH = path.join(FOLDER, 'data', 'SEEYOU.CUP')
SIMPLE_CUPFILE = path.join(FOLDER, 'data', 'simple.cup')

if_data_available = pytest.mark.skipif(
    not path.exists(DATA_PATH),
    reason="requires SEEYOU.CUP"
)

WAYPOINTS = [
    ('"Meiersberg","MEIER",DE,5117.983N,00657.383E,164m,4,130,800m,130.125,"Flugplatz"', {  # noqa
        'name': 'Meiersberg',
        'code': 'MEIER',
        'country': 'DE',
        'latitude': 51.29972222222222,
        'longitude': 6.956388888888889,
        'elevation': {
            'value': 164,
            'unit': 'm',
        },
        'style': 4,
        'runway_direction': 130,
        'runway_length': {
            'value': 800,
            'unit': 'm',
        },
        'frequency': '130.125',
        'description': 'Flugplatz',
    }),
    ('"Manosque Pont D9","MANOSQ",FR,4348.267N,00549.467E,295m,14,,,,"PONT D907"', {  # noqa
        'name': 'Manosque Pont D9',
        'code': 'MANOSQ',
        'country': 'FR',
        'latitude': 43.80444444444444,
        'longitude': 5.8244444444444445,
        'elevation': {
            'value': 295,
            'unit': 'm',
        },
        'style': 14,
        'runway_direction': None,
        'runway_length': {
            'value': None,
            'unit': None,
        },
        'frequency': None,
        'description': 'PONT D907',
    }),
    ('"MarcouX Champ 8","MARCO2",FR,4407.650N,00617.233E,694m,3,130,250m,,"Landefeld"', {  # noqa
        'name': 'MarcouX Champ 8',
        'code': 'MARCO2',
        'country': 'FR',
        'latitude': 44.1275,
        'longitude': 6.287222222222222,
        'elevation': {
            'value': 694,
            'unit': 'm',
        },
        'style': 3,
        'runway_direction': 130,
        'runway_length': {
            'value': 250,
            'unit': 'm',
        },
        'frequency': None,
        'description': 'Landefeld',
    }),
    ('"Sydney Nsw Kinss","SYDNE",AU,3356.767S,15110.633E,6m,5,160,3950m,120.500,"Flugplatz"   ', {  # noqa
        'name': 'Sydney Nsw Kinss',
        'code': 'SYDNE',
        'country': 'AU',
        'latitude': -33.94611111111111,
        'longitude': 151.1772222222222,
        'elevation': {
            'value': 6,
            'unit': 'm',
        },
        'style': 5,
        'runway_direction': 160,
        'runway_length': {
            'value': 3950,
            'unit': 'm',
        },
        'frequency': '120.500',
        'description': 'Flugplatz',
    }),
    ('"Ulm H Bf","ULMHBF",DE,4823.967N,00958.983E,480m,1,,,,"BAHNHOF"', {
        'name': 'Ulm H Bf',
        'code': 'ULMHBF',
        'country': 'DE',
        'latitude': 48.39944444444444,
        'longitude': 9.983055555555556,
        'elevation': {
            'value': 480,
            'unit': 'm',
        },
        'style': 1,
        'runway_direction': None,
        'runway_length': {
            'value': None,
            'unit': None,
        },
        'frequency': None,
        'description': 'BAHNHOF',
    }),
    ('"Vettweiss Soller","VETTW2",DE,5044.850N,00634.033E,159m,3,150,380m,120.975,"Landefeld"', {  # noqa
        'name': 'Vettweiss Soller',
        'code': 'VETTW2',
        'country': 'DE',
        'latitude': 50.7475,
        'longitude': 6.567222222222222,
        'elevation': {
            'value': 159,
            'unit': 'm',
        },
        'style': 3,
        'runway_direction': 150,
        'runway_length': {
            'value': 380,
            'unit': 'm',
        },
        'frequency': '120.975',
        'description': 'Landefeld',
    }),
    ('"Weisweiler Kw 10","WEISWE",DE,5050.383N,00619.367E,144m,15,,,,"KW1011FT"', {  # noqa
        'name': 'Weisweiler Kw 10',
        'code': 'WEISWE',
        'country': 'DE',
        'latitude': 50.83972222222222,
        'longitude': 6.322777777777778,
        'elevation': {
            'value': 144,
            'unit': 'm',
        },
        'style': 15,
        'runway_direction': None,
        'runway_length': {
            'value': None,
            'unit': None,
        },
        'frequency': None,
        'description': 'KW1011FT',
    }),
    ('"Eddln0 Eddl N P","EDDLN0",DE,5124.400N,00644.900E,28m,1,,,,"EDDLN P"', {  # noqa
        'name': 'Eddln0 Eddl N P',
        'code': 'EDDLN0',
        'elevation': 28,
        'latitude': 51.406666666666666,
        'longitude': 6.748333333333333,
        'country': 'DE',
        'elevation': {
            'value': 28,
            'unit': 'm',
        },
        'style': 1,
        'runway_direction': None,
        'runway_length': {
            'value': None,
            'unit': None,
        },
        'frequency': None,
        'description': 'EDDLN P',
    })
]


def test_comments():
    line = '* this is a comment'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 0


def assert_elevation(elevation, expected_value, expected_unit):
    assert 'value' in elevation
    if expected_value is None:
        assert elevation['value'] is None
    else:
        assert abs(elevation['value'] - expected_value) < 0.0001
    assert 'unit' in elevation
    assert elevation['unit'] == expected_unit


def assert_coordinate(coordinate, expected_value):
    if expected_value is None:
        assert coordinate is None
    else:
        assert abs(coordinate - expected_value) < 0.0001


def test_decode_elevation():
    assert_elevation(Reader().decode_elevation('125m'), 125, 'm')
    assert_elevation(Reader().decode_elevation('300ft'), 300, 'ft')
    assert_elevation(Reader().decode_elevation('300 m'), 300, 'm')
    assert_elevation(Reader().decode_elevation('-25.4m'), -25.4, 'm')
    assert_elevation(Reader().decode_elevation('m'), None, 'm')
    assert_elevation(Reader().decode_elevation('23'), 23, None)
    assert_elevation(Reader().decode_elevation(''), None, None)

    with pytest.raises(ParserError):
        Reader().decode_elevation('x')

    with pytest.raises(ParserError):
        Reader().decode_elevation('12a50m')


def test_decode_runway_length():
    assert_elevation(Reader().decode_runway_length('1250m'), 1250, 'm')
    assert_elevation(Reader().decode_runway_length('3.5ml'), 3.5, 'ml')
    assert_elevation(Reader().decode_runway_length('0 m'), 0, 'm')
    assert_elevation(Reader().decode_runway_length('2.4NM'), 2.4, 'NM')
    assert_elevation(Reader().decode_runway_length('23'), 23, None)
    assert_elevation(Reader().decode_runway_length(''), None, None)

    with pytest.raises(ParserError):
        Reader().decode_runway_length('x')

    with pytest.raises(ParserError):
        Reader().decode_runway_length('12a50m')


def test_decode_latitude():
    assert_coordinate(Reader().decode_latitude('5117.983N'), 51.29972222222222)
    assert_coordinate(Reader().decode_latitude('3356.767S'), -33.94611111111111)

    with pytest.raises(ParserError):
        Reader().decode_latitude('9117.983N')

    with pytest.raises(ParserError):
        Reader().decode_latitude('9117.983S')

    with pytest.raises(ParserError):
        Reader().decode_latitude('5117a983N')


def test_decode_longitude():
    assert_coordinate(Reader().decode_longitude('00657.383E'), 6.956388888888889)
    assert_coordinate(Reader().decode_longitude('09942.706W'), -99.71176666666662)

    with pytest.raises(ParserError):
        Reader().decode_longitude('-09942.706W')

    with pytest.raises(ParserError):
        Reader().decode_longitude('09942a706W')

    with pytest.raises(ParserError):
        Reader().decode_longitude('18142.706W')


def test_decode_frequency():
    assert Reader().decode_frequency('120.500') == '120.500'
    assert Reader().decode_frequency('') is None

    with pytest.raises(ParserError):
        Reader().decode_frequency('120a500')


@pytest.fixture(params=WAYPOINTS)
def waypoint(request):
    return request.param


def test_parse_waypoint(waypoint):
    waypoints = list(Reader([waypoint[0]]))
    assert len(waypoints) == 1
    assert_waypoint(waypoints[0], waypoint[1])


@if_data_available
def test_base_original():
    with open(DATA_PATH) as f:
        for waypoint in Reader(f):
            assert waypoint is not None


@if_data_available
def test_original():
    with open(DATA_PATH) as f:
        for waypoint in Converter(f):
            check_waypoint(waypoint)


def test_read():
    with open(SIMPLE_CUPFILE) as f:
        waypoints = Reader().read(f)['waypoints']
        for index in range(len(waypoints)):
            assert_waypoint(waypoints[index], WAYPOINTS[index][1])


def check_waypoint(waypoint):
    assert 'name' in waypoint
    assert 'shortname' in waypoint

    assert 'classifiers' in waypoint
    assert isinstance(waypoint['classifiers'], set)

    if 'icao' in waypoint and waypoint['icao']:
        assert 'airfield' in waypoint['classifiers']

    if 'runways' in waypoint:
        assert isinstance(waypoint['runways'], list)
        assert 0 <= len(waypoint['runways']) <= 1
        for runway in waypoint['runways']:
            assert isinstance(runway, dict)
            if 'length' in runway:
                assert 0 < runway['length'] <= 9999
            if 'directions' in runway:
                assert isinstance(runway['directions'], list)
                assert 1 <= len(runway['directions']) <= 2

    if 'frequencies' in waypoint:
        assert isinstance(waypoint['frequencies'], list)
        assert 0 <= len(waypoint['frequencies']) <= 1
        for frq in waypoint['frequencies']:
            assert 'frequency' in frq
            assert len(frq['frequency']) == 7
            assert frq['frequency'][3] == '.'

    assert 'elevation' in waypoint

    assert 'latitude' in waypoint
    assert -90 <= waypoint['latitude'] <= 90

    assert 'longitude' in waypoint
    assert -180 <= waypoint['longitude'] <= 180

    assert 'country' in waypoint
    assert len(waypoint['country']) == 2


def test_task():
    with open(SIMPLE_CUPFILE) as f:

        tasks = Reader().read(f)['tasks']
        assert len(tasks) == 1

        assert tasks[0]['name'] == '3 turnpoints'
        assert tasks[0]['Options'] == {
            'no_start': None,
            'task_time': '03:00:00',
            'wp_dis': True,
            'near_dis': None,
            'near_alt': None,
            'min_dis': True,
            'random_order': False,
            'max_pts': 13,
            'before_pts': None,
            'after_pts': None,
            'bonus': None,

        }

        assert tasks[0]['waypoints'] == ['Meiersberg', 'Meiersberg', 'Vettweiss Soller', 'Weisweiler Kw 10',
                                         'Eddln0 Eddl N P', 'Meiersberg', 'Meiersberg']

        obs_zones = tasks[0]['obs_zones']
        assert len(obs_zones) == 5

        assert tasks[0]['obs_zones'][0] == {
            "obs_zone": 0,
            "style": 2,
            "r1": 2500,
            "a1": None,
            "r2": None,
            "a2": None,
            "a12": None,
            "line": True,
            "move": False,
            "reduce": False
        }

        assert tasks[0]['obs_zones'][2] == {
            "obs_zone": 2,
            "style": 1,
            "r1": 500,
            "a1": 180,
            "r2": None,
            "a2": None,
            "a12": None,
            "line": False,
            "move": False,
            "reduce": False
        }
