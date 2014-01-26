
METER = ('m', 1.)
FEET = ('ft', 0.3048)
KILOMETER = ('km', 1000.)
STATUTE_MILE = ('ml', 1609.344)
NAUTICAL_MILE = ('NM', 1852.)


def to_SI(value, unit):
    return value * unit[1]
