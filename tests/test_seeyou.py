import pytest
from . import assert_waypoint

from os import path
from aerofiles.formats import SeeYouReader

FOLDER = path.dirname(path.realpath(__file__))
DATA_PATH = path.join(FOLDER, 'data', 'SEEYOU.CUP')

data_available = pytest.mark.skipif(
    not path.exists(DATA_PATH),
    reason="requires SEEYOU.CUP"
)


def test_comments():
    line = '* this is a comment'
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 0


def test_meiersberg():
    line = '"Meiersberg","MEIER",DE,5117.983N,00657.383E,164m,4,130,800m,130.125,"Flugplatz"'  # noqa
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'Meiersberg',
        'shortname': 'MEIER',
        'description': 'Flugplatz',
        'icao': None,
        'classifiers': set([
            'airfield',
            'glidersite',
            'landable',
        ]),
        'runways': [{
            'length': 800,
            'directions': [130, 310],
        }],
        'frequencies': [{
            'frequency': '130.125',
        }],
        'altitude': 164,
        'latitude': 51.29972222222222,
        'longitude': 6.956388888888889,
        'country': 'DE',
    })


def test_manosque():
    line = '"Manosque Pont D9","MANOSQ",FR,4348.267N,00549.467E,295m,14,,,,"PONT D907"'  # noqa
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'Manosque Pont D9',
        'shortname': 'MANOSQ',
        'description': 'PONT D907',
        'classifiers': set([
            'bridge',
        ]),
        'altitude': 295,
        'latitude': 43.80444444444444,
        'longitude': 5.8244444444444445,
        'country': 'FR',
    })


def test_marcoux():
    line = '"MarcouX Champ 8","MARCO2",FR,4407.650N,00617.233E,694m,3,130,250m,,"Landefeld"'  # noqa
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'MarcouX Champ 8',
        'shortname': 'MARCO2',
        'description': 'Landefeld',
        'icao': None,
        'classifiers': set([
            'landable',
        ]),
        'runways': [{
            'length': 250,
            'directions': [130, 310],
        }],
        'frequencies': [],
        'altitude': 694,
        'latitude': 44.1275,
        'longitude': 6.287222222222222,
        'country': 'FR',
    })


def test_sydney():
    line = '"Sydney Nsw Kinss","SYDNE",AU,3356.767S,15110.633E,6m,5,160,3950m,120.500,"Flugplatz"   '  # noqa
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'Sydney Nsw Kinss',
        'shortname': 'SYDNE',
        'description': 'Flugplatz',
        'icao': None,
        'classifiers': set([
            'airfield',
            'landable',
        ]),
        'runways': [{
            'surface': 'solid',
            'length': 3950,
            'directions': [160, 340],
        }],
        'frequencies': [{
            'frequency': '120.500',
        }],
        'altitude': 6,
        'latitude': -33.94611111111111,
        'longitude': 151.1772222222222,
        'country': 'AU',
    })


def test_ulm():
    line = '"Ulm H Bf","ULMHBF",DE,4823.967N,00958.983E,480m,1,,,,"BAHNHOF"'
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'Ulm H Bf',
        'shortname': 'ULMHBF',
        'description': 'BAHNHOF',
        'classifiers': set([
        ]),
        'altitude': 480,
        'latitude': 48.39944444444444,
        'longitude': 9.983055555555556,
        'country': 'DE',
    })


def test_vettweis():
    line = '"Vettweiss Soller","VETTW2",DE,5044.850N,00634.033E,159m,3,150,380m,120.975,"Landefeld"'  # noqa
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'Vettweiss Soller',
        'shortname': 'VETTW2',
        'description': 'Landefeld',
        'icao': None,
        'classifiers': set([
            'landable',
        ]),
        'runways': [{
            'length': 380,
            'directions': [150, 330],
        }],
        'frequencies': [{
            'frequency': '120.975',
        }],
        'altitude': 159,
        'latitude': 50.7475,
        'longitude': 6.567222222222222,
        'country': 'DE',
    })


def test_weisweiler():
    line = '"Weisweiler Kw 10","WEISWE",DE,5050.383N,00619.367E,144m,15,,,,"KW1011FT"'  # noqa
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'Weisweiler Kw 10',
        'shortname': 'WEISWE',
        'description': 'KW1011FT',
        'classifiers': set([
            'power-plant',
        ]),
        'altitude': 144,
        'latitude': 50.83972222222222,
        'longitude': 6.322777777777778,
        'country': 'DE',
    })


def test_eddl_n():
    line = '"Eddln0 Eddl N P","EDDLN0",DE,5124.400N,00644.900E,28m,1,,,,"EDDLN P"'  # noqa
    waypoints = list(SeeYouReader([line]))
    assert len(waypoints) == 1

    assert_waypoint(waypoints[0], {
        'name': 'Eddln0 Eddl N P',
        'shortname': 'EDDLN0',
        'description': 'EDDLN P',
        'classifiers': set([
        ]),
        'altitude': 28,
        'latitude': 51.406666666666666,
        'longitude': 6.748333333333333,
        'country': 'DE',
    })


@data_available
def test_original():
    with open(DATA_PATH) as f:
        for waypoint in SeeYouReader(f):
            check_waypoint(waypoint)


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
            #if 'surface' in runway:
            #    assert runway['surface'] in welt2000.SURFACES.values()
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

    assert 'altitude' in waypoint

    assert 'latitude' in waypoint
    assert -90 <= waypoint['latitude'] <= 90

    assert 'longitude' in waypoint
    assert -180 <= waypoint['longitude'] <= 180

    assert 'country' in waypoint
    assert len(waypoint['country']) == 2
