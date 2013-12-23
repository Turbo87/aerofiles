import csv
import re
from aerofiles import units

RE_COUNTRY = re.compile(r'^([\w]{2})?$', re.I)
RE_LATITUDE = re.compile(r'^([\d]{2})([\d]{2}.[\d]{3})([NS])$', re.I)
RE_LONGITUDE = re.compile(r'^([\d]{3})([\d]{2}.[\d]{3})([EW])$', re.I)
RE_ELEVATION = re.compile(r'^(-?[\d]*(?:.[\d]+)?)\s?(m|ft)?$', re.I)
RE_RUNWAY_LENGTH = re.compile(r'^(?:([\d]+(?:.[\d]+)?)\s?(ml|nm|m)?)?$', re.I)
RE_FREQUENCY = re.compile(r'^1[\d]{2}.[\d]+?$')


class WaypointStyles:
    NORMAL = 1
    AIRFIELD_GRASS = 2
    OUTLANDING = 3
    GLIDERSITE = 4
    AIRFIELD_SOLID = 5
    MOUNTAIN_PASS = 6
    MOUNTAIN_TOP = 7
    SENDER = 8
    VOR = 9
    NDB = 10
    COOL_TOWER = 11
    DAM = 12
    TUNNEL = 13
    BRIDGE = 14
    POWER_PLANT = 15
    CASTLE = 16
    INTERSECTION = 17


WAYPOINT_STYLE_MAPPING = {
    WaypointStyles.NORMAL: [],
    WaypointStyles.AIRFIELD_GRASS: ['landable', 'airfield'],
    WaypointStyles.OUTLANDING: ['landable'],
    WaypointStyles.GLIDERSITE: ['landable', 'airfield', 'glidersite'],
    WaypointStyles.AIRFIELD_SOLID: ['landable', 'airfield'],
    WaypointStyles.MOUNTAIN_PASS: ['mountain-pass'],
    WaypointStyles.MOUNTAIN_TOP: ['mountain-top'],
    WaypointStyles.SENDER: ['sender'],
    WaypointStyles.VOR: ['vor'],
    WaypointStyles.NDB: ['ndb'],
    WaypointStyles.COOL_TOWER: ['tower'],
    WaypointStyles.DAM: ['dam'],
    WaypointStyles.TUNNEL: ['tunnel'],
    WaypointStyles.BRIDGE: ['bridge'],
    WaypointStyles.POWER_PLANT: ['power-plant'],
    WaypointStyles.CASTLE: ['castle'],
    WaypointStyles.INTERSECTION: ['intersection'],
}

UNITS_MAPPING = {
    'm': units.METER,
    'ft': units.FEET,
    'km': units.KILOMETER,
    'ml': units.STATUTE_MILE,
    'nm': units.NAUTICAL_MILE,
}


class ParserError(RuntimeError):
    pass


class SeeYouBaseReader:
    """
    A reader for the SeeYou CUP waypoint file format.

    see http://www.keepitsoaring.com/LKSC/Downloads/cup_format.pdf
    """

    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        return self.next()

    def next(self):
        for fields in csv.reader(self.fp):
            wp = self.decode_waypoint(fields)
            if wp:
                yield wp

    @classmethod
    def decode_waypoint(cls, fields):
        # Ignore header line
        if fields == ['name', 'code', 'country', 'lat', 'lon', 'elev',
                      'style', 'rwdir', 'rwlen', 'freq', 'desc']:
            return

        # Ignore empty lines
        num_fields = len(fields)
        if num_fields == 0:
            return

        # Ignore comments
        if fields[0].startswith('*'):
            return

        if num_fields != 11:
            raise ParserError('Fields are missing')

        fields = [field.strip() for field in fields]

        return {
            'name': cls.decode_name(fields[0]),
            'code': cls.decode_code(fields[1]),
            'country': cls.decode_country(fields[2]),
            'latitude': cls.decode_latitude(fields[3]),
            'longitude': cls.decode_longitude(fields[4]),
            'elevation': cls.decode_elevation(fields[5]),
            'style': cls.decode_style(fields[6]),
            'runway_direction': cls.decode_runway_direction(fields[7]),
            'runway_length': cls.decode_runway_length(fields[8]),
            'frequency': cls.decode_frequency(fields[9]),
            'description': cls.decode_description(fields[10]),
        }

    @classmethod
    def decode_name(cls, name):
        if not name:
            raise ParserError('Name field must not be empty')

        return name

    @classmethod
    def decode_code(cls, code):
        if not code:
            return None

        return code

    @classmethod
    def decode_country(cls, country):
        if RE_COUNTRY.match(country):
            return country
        else:
            raise ParserError('Invalid country code')

    @classmethod
    def decode_latitude(cls, latitude):
        match = RE_LATITUDE.match(latitude)
        if not match:
            raise ParserError('Reading latitude failed')

        latitude = int(match.group(1)) + float(match.group(2)) / 60.

        if not (0 <= latitude <= 90):
            raise ParserError('Latitude out of bounds')

        if match.group(3).upper() == 'S':
            latitude = -latitude

        return latitude

    @classmethod
    def decode_longitude(cls, longitude):
        match = RE_LONGITUDE.match(longitude)
        if not match:
            raise ParserError('Reading longitude failed')

        longitude = int(match.group(1)) + float(match.group(2)) / 60.

        if not (0 <= longitude <= 180):
            raise ParserError('Longitude out of bounds')

        if match.group(3).upper() == 'W':
            longitude = -longitude

        return longitude

    @classmethod
    def decode_elevation(cls, elevation):
        match = RE_ELEVATION.match(elevation)
        if not match:
            raise ParserError('Reading elevation failed')

        try:
            value = float(match.group(1))
        except ValueError:
            value = None

        unit = match.group(2)
        if unit and unit.lower() not in ('m', 'ft'):
            raise ParserError('Unknown elevation unit')

        return {
            'value': value,
            'unit': unit,
        }

    @classmethod
    def decode_style(cls, style):
        try:
            style = int(style)
        except ValueError:
            raise ParserError('Reading style failed')

        if not (1 <= style <= 17):
            raise ParserError('Unknown waypoint style')

        return style

    @classmethod
    def decode_runway_direction(cls, runway_direction):
        if not runway_direction:
            return None

        try:
            runway_direction = int(runway_direction)
        except ValueError:
            raise ParserError('Reading runway direction failed')

        return runway_direction

    @classmethod
    def decode_runway_length(cls, runway_length):
        if not runway_length:
            return {
                'value': None,
                'unit': None,
            }

        match = RE_RUNWAY_LENGTH.match(runway_length)
        if not match:
            raise ParserError('Reading runway length failed')

        try:
            value = float(match.group(1))
        except ValueError:
            value = None

        unit = match.group(2)
        if unit and unit.lower() not in ('m', 'nm', 'ml'):
            raise ParserError('Unknown runway length unit')

        return {
            'value': value,
            'unit': unit,
        }

    @classmethod
    def decode_frequency(cls, frequency):
        if not frequency:
            return None

        if not RE_FREQUENCY.match(frequency):
            raise ParserError('Reading frequency failed')

        return frequency

    @classmethod
    def decode_description(cls, description):
        if not description:
            return None

        return description


class SeeYouReader:
    """
    A reader for the SeeYou CUP waypoint file format.

    see http://www.keepitsoaring.com/LKSC/Downloads/cup_format.pdf
    """

    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        return self.next()

    def next(self):
        for old in SeeYouBaseReader(self.fp):
            new = self.convert_waypoint(old)
            if new:
                yield new

    @classmethod
    def convert_waypoint(cls, old):
        waypoint = {}

        waypoint['name'] = old['name']
        waypoint['shortname'] = old['code']
        waypoint['country'] = old['country']
        waypoint['description'] = old['description']

        waypoint['latitude'] = old['latitude']
        waypoint['longitude'] = old['longitude']

        waypoint['elevation'] = cls.convert_elevation(old['elevation'])

        if old['style'] not in WAYPOINT_STYLE_MAPPING:
            raise ParserError('Unknown waypoint style')

        waypoint['classifiers'] = set(WAYPOINT_STYLE_MAPPING[old['style']])

        if 'landable' in waypoint['classifiers']:
            waypoint['icao'] = None
            waypoint['runways'] = cls.convert_runways(
                old['style'], old['runway_direction'], old['runway_length'])
            waypoint['frequencies'] = cls.convert_frequencies(
                old['frequency'])

        return waypoint

    @classmethod
    def convert_elevation(cls, elevation):
        if elevation['value'] is None and elevation['unit'] is None:
            return None

        unit = UNITS_MAPPING.get(elevation['unit'].lower(), units.METER)
        return units.to_SI(elevation['value'] or 0, unit)

    @classmethod
    def convert_runways(cls, style, dir, length):
        runways = []
        runway = {}

        if style == WaypointStyles.AIRFIELD_GRASS:
            runway['surface'] = 'grass'
        elif style == WaypointStyles.AIRFIELD_SOLID:
            runway['surface'] = 'solid'

        if dir is not None:
            runway['directions'] = [dir % 360, (dir + 180) % 360]

        if length['value']:
            unit = UNITS_MAPPING.get(length['unit'].lower(), units.METER)
            runway['length'] = units.to_SI(length['value'], unit)

        if runway:
            runways.append(runway)

        return runways

    @classmethod
    def convert_frequencies(cls, frq):
        if not frq:
            return []

        if len(frq) < 7:
            frq += \
                '5' if frq.endswith('2') or frq.endswith('7') else '0'

        return [{
            'frequency': frq,
        }]
