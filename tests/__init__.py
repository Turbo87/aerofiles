
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
