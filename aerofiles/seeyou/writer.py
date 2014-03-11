from .converter import WaypointStyles


class Writer:
    """
    A writer for SeeYou CUP files. Supports waypoints and tasks::

        with open('competition.cup', 'w') as fp:
            writer = Writer(fp)
    """

    HEADER = 'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc'

    DISTANCE_FORMAT_FLOAT = '%.1f%s'
    DISTANCE_FORMAT_INT = '%d%s'
    DISTANCE_FORMAT_OTHER = '%s%s'

    def __init__(self, fp):
        self.fp = fp
        self.write_line(self.HEADER)

    def escape(self, field):
        if not field:
            return ''

        return '"%s"' % field.replace('\\', '\\\\').replace('"', '\\"')

    def format_coordinate(self, value, is_latitude=True):
        if is_latitude:
            if not -90 <= value <= 90:
                raise ValueError('Invalid latitude: %s' % value)

            hemisphere = 'S' if value < 0 else 'N'
            format = '%02d%06.3f%s'

        else:
            if not -180 <= value <= 180:
                raise ValueError('Invalid longitude: %s' % value)

            hemisphere = 'W' if value < 0 else 'E'
            format = '%03d%06.3f%s'

        value = abs(value)
        degrees = int(value)
        minutes = (value - degrees) * 60
        return format % (degrees, minutes, hemisphere)

    def format_latitude(self, value):
        return self.format_coordinate(value, is_latitude=True)

    def format_longitude(self, value):
        return self.format_coordinate(value, is_latitude=False)

    def format_distance(self, distance):
        if distance is None or distance == '':
            return ''

        if isinstance(distance, tuple):
            unit = distance[1]
            distance = distance[0]
        else:
            unit = 'm'

        if isinstance(distance, float):
            return self.DISTANCE_FORMAT_FLOAT % (distance, unit)
        elif isinstance(distance, int):
            return self.DISTANCE_FORMAT_INT % (distance, unit)
        else:
            return self.DISTANCE_FORMAT_OTHER % (distance, unit)

    def write_line(self, line=''):
        self.fp.write(line + '\r\n')

    def write_fields(self, fields):
        self.write_line(','.join(fields))

    def write_waypoint(
            self, name, shortname, country, latitude, longitude, elevation='',
            style=WaypointStyles.NORMAL, runway_direction='', runway_length='',
            frequency='', description=''):

        """
        Write a waypoint::

            writer.write_waypoint(
                'Meiersberg',
                'MEIER',
                'DE',
                (51 + 7.345 / 60.),
                (6 + 24.765 / 60.),
            )
            # -> "Meiersberg","MEIER",DE,5107.345N,00624.765E,,1,,,,

        :param name: name of the waypoint (must not be empty)
        :param shortname: short name for depending GPS devices
        :param country: IANA top level domain country code (see
            http://www.iana.org/cctld/cctld-whois.htm)
        :param latitude: latitude of the point (between -90 and 90 degrees)
        :param longitude: longitude of the point (between -180 and 180 degrees)
        :param elevation: elevation of the waypoint in meters or as (elevation,
            unit) tuple
        :param style: the waypoint type (see official specification for the
            list of valid styles, defaults to "Normal")
        :param runway_direction: heading of the runway in degrees if the
            waypoint is landable
        :param runway_length: length of the runway in meters or as (length,
            unit) tuple if the waypoint is landable
        :param frequency: radio frequency of the airport
        :param description: optional description of the waypoint (no length
            limit)
        """

        if not name:
            raise ValueError('Waypoint name must not be empty')

        fields = [
            self.escape(name),
            self.escape(shortname),
            country,
            self.format_latitude(latitude),
            self.format_longitude(longitude),
            self.format_distance(elevation),
            str(style),
            str(runway_direction),
            self.format_distance(runway_length),
            self.escape(frequency),
            self.escape(description),
        ]

        self.write_fields(fields)
