import pytest
from . import assert_waypoint

from os import path
from aerofiles.welt2000 import (
    Reader, Converter, SURFACES
)

FOLDER = path.dirname(path.realpath(__file__))
DATA_PATH = path.join(FOLDER, 'data', 'WELT2000.TXT')

if_data_available = pytest.mark.skipif(
    not path.exists(DATA_PATH),
    reason="requires WELT2000.TXT"
)


def test_comments():
    line = '$ this is a comment'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 0


def test_parse_meiersberg():
    line = 'MEIER1 MEIERSBERG      #GLD!G 80133113012 164N511759E0065723DEP0'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'shortform': 'MEIER1',
        'is_airfield': True,
        'is_unclear': False,
        'is_outlanding': False,
        'shortform_zander': 'MEIERSBERG',
        'text': 'MEIERSBERG',
        'icao': None,
        'is_ulm': False,
        'field_number': None,
        'is_glidersite': True,
        'runway_surface': 'grass',
        'runway_length': 800,
        'runway_directions': [130, 310],
        'frequency': '130.125',
        'elevation': 164,
        'elevation_proved': False,
        'latitude': 51.29972222222222,
        'longitude': 6.956388888888889,
        'ground_check_necessary': False,
        'better_coordinates': False,
        'country': 'DE',
        'year_code': 'P',
        'source_code': '0',
    })


def test_manosque():
    line = 'MANOSQ MANOSQUE PONT D907XDURANCE         295N434816E0054928FRQ0'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'shortform': 'MANOSQ',
        'is_airfield': False,
        'is_unclear': False,
        'is_outlanding': False,
        'shortform_zander': 'MANOSQUE PON',
        'text': 'MANOSQUE PONT D907XDURANCE',
        'icao': None,
        'is_ulm': False,
        'field_number': None,
        'is_glidersite': False,
        'runway_surface': None,
        'runway_length': None,
        'runway_directions': None,
        'frequency': None,
        'elevation': 295,
        'elevation_proved': False,
        'latitude': 43.80444444444444,
        'longitude': 5.8244444444444445,
        'ground_check_necessary': False,
        'better_coordinates': False,
        'country': 'FR',
        'year_code': 'Q',
        'source_code': '0',
    })


def test_marcoux():
    line = 'MARCO2 MARCOUX CHAMP 8!*FL08S 2513131     694N440739E0061714FRP0'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'shortform': 'MARCO2',
        'is_airfield': False,
        'is_unclear': False,
        'is_outlanding': True,
        'shortform_zander': 'MARCOUX CHAM',
        'text': 'MARCOUX CHAMP 8',
        'icao': None,
        'is_ulm': False,
        'field_number': 8,
        'is_glidersite': False,
        'runway_surface': 'sand',
        'runway_length': 250,
        'runway_directions': [130],
        'frequency': None,
        'elevation': 694,
        'elevation_proved': False,
        'latitude': 44.1275,
        'longitude': 6.287222222222222,
        'ground_check_necessary': False,
        'better_coordinates': False,
        'country': 'FR',
        'year_code': 'P',
        'source_code': '0',
    })


def test_sydney():
    line = 'SYDNE1 SYDNEY NSW KINSS#YSSYA395160712050   6S335646E1511038AUQ0'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'shortform': 'SYDNE1',
        'is_airfield': True,
        'is_unclear': False,
        'is_outlanding': False,
        'shortform_zander': 'SYDNEY NSW K',
        'text': 'SYDNEY NSW KINSS',
        'icao': 'YSSY',
        'is_ulm': False,
        'field_number': None,
        'is_glidersite': False,
        'runway_surface': 'asphalt',
        'runway_length': 3950,
        'runway_directions': [160, 70],
        'frequency': '120.500',
        'elevation': 6,
        'elevation_proved': False,
        'latitude': -33.94611111111111,
        'longitude': 151.1772222222222,
        'ground_check_necessary': False,
        'better_coordinates': False,
        'country': 'AU',
        'year_code': 'Q',
        'source_code': '0',
    })


def test_ulm():
    line = 'ULMHBF ULM H BF                           480N482358E0095859DEJ0'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'shortform': 'ULMHBF',
        'is_airfield': False,
        'is_unclear': False,
        'is_outlanding': False,
        'shortform_zander': 'ULM H BF',
        'text': 'ULM H BF',
        'icao': None,
        'is_ulm': False,
        'field_number': None,
        'is_glidersite': False,
        'runway_surface': None,
        'runway_length': None,
        'runway_directions': None,
        'frequency': None,
        'elevation': 480,
        'elevation_proved': False,
        'latitude': 48.39944444444444,
        'longitude': 9.983055555555556,
        'ground_check_necessary': False,
        'better_coordinates': False,
        'country': 'DE',
        'year_code': 'J',
        'source_code': '0',
    })


def test_vettweis():
    line = 'VETTW2 VETTWEISS SOLLER*ULM!G 38153312097 159N504451E0063402DEP0'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'shortform': 'VETTW2',
        'is_airfield': False,
        'is_unclear': False,
        'is_outlanding': True,
        'shortform_zander': 'VETTWEISS SO',
        'text': 'VETTWEISS SOLLER',
        'icao': None,
        'is_ulm': True,
        'field_number': None,
        'is_glidersite': False,
        'runway_surface': 'grass',
        'runway_length': 380,
        'runway_directions': [150, 330],
        'frequency': '120.975',
        'elevation': 159,
        'elevation_proved': False,
        'latitude': 50.7475,
        'longitude': 6.567222222222222,
        'ground_check_necessary': False,
        'better_coordinates': False,
        'country': 'DE',
        'year_code': 'P',
        'source_code': '0',
    })


def test_weisweiler():
    line = 'WEISWE WEISWEILER KW 1011FT WESTL KUEHLT  144N505023E0061922DEP5'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'shortform': 'WEISWE',
        'is_airfield': False,
        'is_unclear': False,
        'is_outlanding': False,
        'shortform_zander': 'WEISWEILER K',
        'text': 'WEISWEILER KW 1011FT WESTL KUEHLT',
        'icao': None,
        'is_ulm': False,
        'field_number': None,
        'is_glidersite': False,
        'runway_surface': None,
        'runway_length': None,
        'runway_directions': None,
        'frequency': None,
        'elevation': 144,
        'elevation_proved': False,
        'latitude': 50.83972222222222,
        'longitude': 6.322777777777778,
        'ground_check_necessary': False,
        'better_coordinates': False,
        'country': 'DE',
        'year_code': 'P',
        'source_code': '5',
    })


def test_eddl_n():
    line = 'EDDLN0 EDDLN0 EDDL N  PFLICHTMELDEPUNKT    28N512424E0064454DEQ4'
    waypoints = list(Reader([line]))
    assert len(waypoints) == 1

    assert_waypoint(
        waypoints[0], {
            'shortform': 'EDDLN0',
            'is_airfield': False,
            'is_unclear': False,
            'is_outlanding': False,
            'shortform_zander': 'EDDLN0 EDDL',
            'text': 'EDDLN0 EDDL N  PFLICHTMELDEPUNKT',
            'icao': None,
            'is_ulm': False,
            'field_number': None,
            'is_glidersite': False,
            'runway_surface': None,
            'runway_length': None,
            'runway_directions': None,
            'frequency': None,
            'elevation': 28,
            'elevation_proved': False,
            'latitude': 51.406666666666666,
            'longitude': 6.748333333333333,
            'ground_check_necessary': False,
            'better_coordinates': False,
            'country': 'DE',
            'year_code': 'Q',
            'source_code': '4',
        })


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


def check_waypoint(waypoint):
    # Check name
    assert 'name' in waypoint
    assert not waypoint['name'].endswith(' ?')
    assert not waypoint['name'].endswith(' !')

    assert 'shortname' in waypoint
    assert len(waypoint['shortname']) == 6

    assert 'classifiers' in waypoint
    assert isinstance(waypoint['classifiers'], set)

    if 'icao' in waypoint and waypoint['icao']:
        assert 'airfield' in waypoint['classifiers']

    if 'runways' in waypoint:
        assert isinstance(waypoint['runways'], list)
        assert 0 <= len(waypoint['runways']) <= 2
        for runway in waypoint['runways']:
            assert isinstance(runway, dict)
            if 'surface' in runway:
                assert runway['surface'] in SURFACES.values()
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
    assert (
        waypoint['elevation'] is None or
        -999 <= waypoint['elevation'] <= 9999
    )

    assert 'latitude' in waypoint
    assert -90 <= waypoint['latitude'] <= 90

    assert 'longitude' in waypoint
    assert -180 <= waypoint['longitude'] <= 180

    assert 'country' in waypoint
    assert len(waypoint['country']) == 2
