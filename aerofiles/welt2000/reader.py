import re

from aerofiles.errors import ParserError


RE_WHITESPACE = re.compile(r'\s+')
RE_LATITUDE = re.compile(r'^([NS])([\d]{2})([\d]{2})([\d]{2})$')
RE_LONGITUDE = re.compile(r'^([EW])([\d]{3})([\d]{2})([\d]{2})$')
RE_FIELD_NUMBER = re.compile(r'^\*FL([\d]+)$')
RE_RUNWAY_LENGTH = re.compile(r'^\s*([\d]+)\s*$')
RE_RUNWAY_DIRECTION = re.compile(r'^\s*([\d]+)\s*$')
RE_FREQUENCY = re.compile(r'^(1[\d]{2})([\d]{2})$')
RE_ELEVATION = re.compile(r'^[\s]*(-?[\d]+)')

SURFACES = {
    'A': 'asphalt',
    'C': 'concrete',
    'L': 'loam',
    'S': 'sand',
    'Y': 'clay',
    'G': 'grass',
    'V': 'gravel',
    'D': 'dirt',
    'W': 'meadow',
}


class Reader:
    """
    A reader for the WELT2000 waypoint file format.

    see https://github.com/skylines-project/welt2000
    """

    def __init__(self, fp=None):
        self.fp = fp

    def __iter__(self):
        return self.next()

    def next(self):
        for line in self.fp:
            wp = self.decode_waypoint(line)
            if wp:
                yield wp

    def decode_waypoint(self, line):
        line = line.strip()

        if not line or line.startswith('$'):
            return

        # Check valid line length
        if len(line) != 64:
            raise ParserError('Line length does not match 64')

        return {
            'shortform': self.decode_shortform(line),
            'is_airfield': self.decode_is_airfield(line),
            'is_unclear': self.decode_is_unclear(line),
            'is_outlanding': self.decode_is_outlanding(line),
            'shortform_zander': self.decode_shortform_zander(line),
            'text': self.decode_text(line),
            'icao': self.decode_icao(line),
            'is_ulm': self.decode_is_ulm(line),
            'field_number': self.decode_field_number(line),
            'is_glidersite': self.decode_is_glidersite(line),
            'runway_surface': self.decode_runway_surface(line),
            'runway_length': self.decode_runway_length(line),
            'runway_directions': self.decode_runway_directions(line),
            'frequency': self.decode_frequency(line),
            'elevation': self.decode_elevation(line),
            'elevation_proved': self.decode_elevation_proved(line),
            'latitude': self.decode_latitude(line),
            'longitude': self.decode_longitude(line),
            'ground_check_necessary': self.decode_ground_check_necessary(line),
            'better_coordinates': self.decode_better_coordinates(line),
            'country': self.decode_country(line),
            'year_code': self.decode_year_code(line),
            'source_code': self.decode_source_code(line),
        }

    def has_metadata(self, line):
        return line[23] == '#' or line[23] == '*' or line[23] == '?'

    def decode_shortform(self, line):
        return line[0:6]

    def decode_is_airfield(self, line):
        return line[5] == '1'

    def decode_is_unclear(self, line):
        return line[4] == '2'

    def decode_is_outlanding(self, line):
        return line[5] == '2'

    def decode_shortform_zander(self, line):
        if line[6] == ' ' or line[6] == '-':
            return line[7:19].rstrip()
        else:
            return line[7:19] + line[6]

    def decode_text(self, line):
        if not self.has_metadata(line):
            return line[7:41].rstrip('?! ')
        elif line[20:23] == 'GLD':
            return line[7:20].rstrip('?! ')
        else:
            return line[7:23].rstrip('?! ')

    def decode_icao(self, line):
        if (line[23] == '#' and line[24] != ' ' and
                line[27] != '?' and line[27] != '!'):
            return line[24:28].rstrip()

    def decode_is_ulm(self, line):
        return (
            line[23:27] == '*ULM' or
            line[23:27] == '#ULM' or
            line[23:28] == '# ULM'
        )

    def decode_field_number(self, line):
        match = RE_FIELD_NUMBER.match(line[23:28])
        if match:
            return int(match.group(1))

    def decode_is_glidersite(self, line):
        return (
            line[23:28] == '# GLD' or
            line[23:27] == '#GLD' or
            line[23:27] == '*GLD' or
            line[19:24] == 'GLD #' or
            line[20:24] == 'GLD#' or
            line[20:24] == 'GLD*'
        )

    def decode_runway_surface(self, line):
        if self.has_metadata(line):
            return SURFACES.get(line[28], None)

    def decode_runway_length(self, line):
        if self.has_metadata(line):
            match = RE_RUNWAY_LENGTH.match(line[29:32])
            if match:
                return int(match.group(1)) * 10

    def decode_runway_directions(self, line):
        if self.has_metadata(line):
            directions = []

            match = RE_RUNWAY_DIRECTION.match(line[32:34])
            if match:
                direction = int(match.group(1)) * 10
                directions.append(direction)

            match = RE_RUNWAY_DIRECTION.match(line[34:36])
            if match:
                direction = int(match.group(1)) * 10
                if direction not in directions:
                    directions.append(direction)

            return directions or None

    def decode_frequency(self, line):
        if self.has_metadata(line):
            match = RE_FREQUENCY.match(line[36:41])
            if match:
                frq = match.group(1) + '.' + match.group(2)
                frq += '5' if frq.endswith('2') or frq.endswith('7') else '0'
                return frq

    def decode_elevation(self, line):
        match = RE_ELEVATION.match(line[41:45])
        if match:
            return int(match.group(1))

    def decode_elevation_proved(self, line):
        return line[41] == '0'

    def decode_latitude(self, line):
        match = RE_LATITUDE.match(line[45:52])
        if not match:
            raise ParserError('Reading latitude failed')

        lat = (
            int(match.group(2)) +
            int(match.group(3)) / 60. +
            int(match.group(4)) / 3600.
        )

        if not (0 <= lat <= 90):
            raise ParserError('Latitude out of bounds')

        if match.group(1) == 'S':
            lat = -lat

        return lat

    def decode_longitude(self, line):
        match = RE_LONGITUDE.match(line[52:60])
        if not match:
            raise ParserError('Reading longitude failed')

        lon = (
            int(match.group(2)) +
            int(match.group(3)) / 60. +
            int(match.group(4)) / 3600.
        )

        if not (0 <= lon <= 180):
            raise ParserError('Longitude out of bounds')

        if match.group(1) == 'W':
            lon = -lon

        return lon

    def decode_ground_check_necessary(self, line):
        return '?' in line

    def decode_better_coordinates(self, line):
        return line[6] == '-'

    def decode_country(self, line):
        return line[60:62].strip()

    def decode_year_code(self, line):
        return line[62].strip()

    def decode_source_code(self, line):
        return line[63].strip()
