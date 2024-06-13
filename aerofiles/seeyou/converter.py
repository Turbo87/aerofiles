from aerofiles.errors import ParserError
from aerofiles.util import units

from .common import WaypointStyle
from .reader import Reader


WAYPOINT_STYLE_MAPPING = {
    WaypointStyle.NORMAL: [],
    WaypointStyle.AIRFIELD_GRASS: ['landable', 'airfield'],
    WaypointStyle.OUTLANDING: ['landable'],
    WaypointStyle.GLIDERSITE: ['landable', 'airfield', 'glidersite'],
    WaypointStyle.AIRFIELD_SOLID: ['landable', 'airfield'],
    WaypointStyle.MOUNTAIN_PASS: ['mountain-pass'],
    WaypointStyle.MOUNTAIN_TOP: ['mountain-top'],
    WaypointStyle.SENDER: ['sender'],
    WaypointStyle.VOR: ['vor'],
    WaypointStyle.NDB: ['ndb'],
    WaypointStyle.COOL_TOWER: ['tower'],
    WaypointStyle.DAM: ['dam'],
    WaypointStyle.TUNNEL: ['tunnel'],
    WaypointStyle.BRIDGE: ['bridge'],
    WaypointStyle.POWER_PLANT: ['power-plant'],
    WaypointStyle.CASTLE: ['castle'],
    WaypointStyle.INTERSECTION: ['intersection'],
}

UNITS_MAPPING = {
    'm': units.METER,
    'ft': units.FEET,
    'km': units.KILOMETER,
    'ml': units.STATUTE_MILE,
    'nm': units.NAUTICAL_MILE,
}


class Converter:
    """
    A reader for the SeeYou CUP waypoint file format.

    see http://www.keepitsoaring.com/LKSC/Downloads/cup_format.pdf
    """

    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        return self.next()

    def next(self):
        for old in Reader(self.fp):
            new = self.convert_waypoint(old)
            if new:
                yield new

    def convert_waypoint(self, old):
        waypoint = {}

        waypoint['name'] = old['name']
        waypoint['shortname'] = old['code']
        waypoint['country'] = old['country']
        waypoint['description'] = old['description']

        waypoint['latitude'] = old['latitude']
        waypoint['longitude'] = old['longitude']

        waypoint['elevation'] = self.convert_elevation(old['elevation'])

        if old['style'] not in WAYPOINT_STYLE_MAPPING:
            raise ParserError('Unknown waypoint style')

        waypoint['classifiers'] = set(WAYPOINT_STYLE_MAPPING[old['style']])

        if 'landable' in waypoint['classifiers']:
            waypoint['icao'] = None
            waypoint['runways'] = self.convert_runways(
                old['style'], old['runway_direction'], old['runway_length'])
            waypoint['frequencies'] = self.convert_frequencies(
                old['frequency'])

        return waypoint

    def convert_elevation(self, elevation):
        if elevation['value'] is None and elevation['unit'] is None:
            return None

        unit = UNITS_MAPPING.get(elevation['unit'].lower(), units.METER)
        return units.to_SI(elevation['value'] or 0, unit)

    def convert_runways(self, style, dir, length):
        runways = []
        runway = {}

        if style == WaypointStyle.AIRFIELD_GRASS:
            runway['surface'] = 'grass'
        elif style == WaypointStyle.AIRFIELD_SOLID:
            runway['surface'] = 'solid'

        if dir is not None:
            runway['directions'] = [dir % 360, (dir + 180) % 360]

        if length['value']:
            unit = UNITS_MAPPING.get(length['unit'].lower(), units.METER)
            runway['length'] = units.to_SI(length['value'], unit)

        if runway:
            runways.append(runway)

        return runways

    def convert_frequencies(self, frq):
        if not frq:
            return []

        if len(frq) < 7:
            frq += \
                '5' if frq.endswith('2') or frq.endswith('7') else '0'

        return [{
            'frequency': frq,
        }]
