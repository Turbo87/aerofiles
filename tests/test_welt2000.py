from aerofiles.formats import Welt2000Format


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
        'classifiers': [
            'airfield',
            'glidersite',
            'landable',
        ],
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
