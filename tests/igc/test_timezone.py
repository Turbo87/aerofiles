import copy

from aerofiles.util import TimeZoneFix


def test_not_equal():
    tz1 = TimeZoneFix(1)
    tz2 = TimeZoneFix(2)
    assert (tz1 != tz2)


def test_equal():
    tz1 = TimeZoneFix(1)
    tz2 = TimeZoneFix(1)
    assert (tz1 == tz2)


def test_deepcopy():
    tz1 = TimeZoneFix(1)
    tz2 = copy.deepcopy(tz1)
    assert (tz1 == tz2)
