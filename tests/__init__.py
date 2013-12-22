
def assert_waypoint(value, expected):
    # copy arguments to be able to modify them
    value, expected = dict(value), dict(expected)

    # save latitudes and longitudes
    value_lon, value_lat = value['longitude'], value['latitude']
    expected_lon, expected_lat = expected['longitude'], expected['latitude']

    # remove floats from the dicts
    del value['longitude']
    del value['latitude']
    del expected['longitude']
    del expected['latitude']

    # compare
    assert value == expected
    assert abs(value_lat - expected_lat) < 0.00001
    assert abs(value_lon - expected_lon) < 0.00001


def assert_runway(runway, directions, length, surface):
    if directions is not None:
        assert 'directions' in runway and runway['directions'] == directions
    else:
        assert 'directions' not in runway

    if length is not None:
        assert 'length' in runway and abs(runway['length'] - length) < 0.1
    else:
        assert 'length' not in runway

    if surface is not None:
        assert 'surface' in runway and runway['surface'] == surface
    else:
        assert 'surface' not in runway
