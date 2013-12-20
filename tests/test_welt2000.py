import pytest
from os import path
from aerofiles.formats import Welt2000Format, welt2000

FOLDER = path.dirname(path.realpath(__file__))
DATA_PATH = path.join(FOLDER, 'data', 'WELT2000.TXT')

data_available = pytest.mark.skipif(
    not path.exists(DATA_PATH),
    reason="requires WELT2000.TXT"
)


def test_comments():
    line = '$ this is a comment'
    waypoint = Welt2000Format.parse_waypoint(line)

    assert waypoint is None


def test_parse_meiersberg():
    line = 'MEIER1 MEIERSBERG      #GLD!G 80133113012 164N511759E0065723DEP0'
    waypoint = Welt2000Format.parse_waypoint(line)

    assert waypoint == {
        'name': 'Meiersberg',
        'shortname': 'MEIER1',
        'classifiers': set([
            'airfield',
            'glidersite',
            'landable',
        ]),
        'runways': [
            {
                'surface': 'grass',
                'length': 800,
                'directions': [130, 310],
            },
        ],
        'frequencies': [
            {
                'frequency': '130.125',
            },
        ],
        'altitude': 164,
        'latitude': 51.29972222222222,
        'longitude': 6.956388888888889,
        'country': 'DE',
    }


@data_available
def test_original():
    with open(DATA_PATH) as f:
        for line in f:
            check_waypoint(line)


def check_waypoint(line):
    waypoint = Welt2000Format.parse_waypoint(line)

    if not waypoint:
        assert line.startswith('$') or line.strip() == ''
        return

    # Check name
    assert 'name' in waypoint
    assert ('A' <= waypoint['name'][0] <= 'Z' or
            '0' <= waypoint['name'][0] <= '9')
    assert not waypoint['name'].endswith(' ?')
    assert not waypoint['name'].endswith(' !')
    assert not waypoint['name'].endswith('+')

    assert 'shortname' in waypoint
    assert len(waypoint['shortname']) == 6

    assert 'classifiers' in waypoint
    assert isinstance(waypoint['classifiers'], set)

    if '*ULM' in line or '#ULM' in line or '# ULM' in line:
        assert 'ulm' in waypoint['classifiers']

    if 'runways' in waypoint:
        assert isinstance(waypoint['runways'], list)
        assert 0 <= len(waypoint['runways']) <= 2
        for runway in waypoint['runways']:
            assert isinstance(runway, dict)
            if 'surface' in runway:
                assert runway['surface'] in welt2000.SURFACES.values()
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
    assert -999 <= waypoint['altitude'] <= 9999

    assert 'latitude' in waypoint
    assert -90 <= waypoint['latitude'] <= 90

    assert 'longitude' in waypoint
    assert -180 <= waypoint['longitude'] <= 180

    assert 'country' in waypoint
    assert len(waypoint['country']) == 2
