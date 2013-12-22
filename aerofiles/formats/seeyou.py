import csv
import re

RE_LATITUDE = re.compile(r'([\d]{2})([\d]{2}.[\d]{3})([NS])', re.I)
RE_LONGITUDE = re.compile(r'([\d]{3})([\d]{2}.[\d]{3})([EW])', re.I)
RE_ALTITUDE = re.compile(r'(-?[\d]*)(m|ft)', re.I)
RE_FREQUENCY = re.compile(r'1[\d]{2}.[\d][0257][05]?')
RE_RUNWAY_LENGTH = re.compile(r'([\d]+)(m|ml|nm|ft)', re.I)


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


class ParserError(RuntimeError):
    pass


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
        for fields in csv.reader(self.fp):
            wp = self.fields_to_waypoint(fields)
            if wp:
                yield wp

    @classmethod
    def fields_to_waypoint(cls, fields):
        """
        Parses a single waypoint from the specified input.
        """

        #print fields
        if fields == ['name', 'code', 'country', 'lat', 'lon', 'elev',
                      'style', 'rwdir', 'rwlen', 'freq', 'desc']:
            return

        if len(fields) != 11:
            return

        waypoint = {}

        waypoint['longitude'], waypoint['latitude'] = \
            cls.parse_coordinates(fields)

        waypoint['name'] = fields[0].strip()
        waypoint['shortname'] = fields[1].strip()
        waypoint['country'] = fields[2].strip()

        # todo feet/float
        alt_match = RE_ALTITUDE.match(fields[5])
        if not alt_match:
            raise ParserError('Reading altitude failed')

        waypoint['altitude'] = int(alt_match.group(1) or '0')

        try:
            style = int(fields[6])
        except ValueError:
            style = 1

        if style not in WAYPOINT_STYLE_MAPPING:
            raise ParserError('Unknown waypoint style')

        waypoint['classifiers'] = set(WAYPOINT_STYLE_MAPPING[style])

        if 'landable' in waypoint['classifiers']:
            waypoint['icao'] = None
            waypoint['runways'] = cls.parse_runways(
                style, fields[7], fields[8])
            waypoint['frequencies'] = cls.parse_frequencies(fields[9])

        waypoint['description'] = fields[10].strip()

        return waypoint

    @classmethod
    def parse_runways(cls, style, dir, length):
        runways = []
        runway = {}

        if style == WaypointStyles.AIRFIELD_GRASS:
            runway['surface'] = 'grass'
        elif style == WaypointStyles.AIRFIELD_SOLID:
            runway['surface'] = 'solid'

        try:
            dir = int(dir)
            runway['directions'] = [dir % 360, (dir + 180) % 360]
        except ValueError:
            pass

        # todo floats / ml / NM
        len_match = RE_RUNWAY_LENGTH.match(length)
        if len_match:
            length = float(len_match.group(1))
            if length > 0:
                runway['length'] = length

        if runway:
            runways.append(runway)

        return runways

    @classmethod
    def parse_frequencies(cls, frq):
        if not RE_FREQUENCY.match(frq):
            return []

        if len(frq) < 7:
            frq += \
                '5' if frq.endswith('2') or frq.endswith('7') else '0'

        return [{
            'frequency': frq,
        }]

    @classmethod
    def parse_coordinates(cls, fields):
        lat_match = RE_LATITUDE.match(fields[3])
        lon_match = RE_LONGITUDE.match(fields[4])
        if not (lat_match and lon_match):
            raise ParserError('Reading coordinates failed')

        lat = (
            int(lat_match.group(1)) +
            float(lat_match.group(2)) / 60.
        )
        if not (0 <= lat <= 90):
            raise ParserError('Latitude out of bounds')
        if lat_match.group(3) == 'S':
            lat = -lat

        lon = (
            int(lon_match.group(1)) +
            float(lon_match.group(2)) / 60.
        )
        if not (0 <= lon <= 180):
            raise ParserError('Longitude out of bounds')
        if lon_match.group(3) == 'W':
            lon = -lon

        return lon, lat
