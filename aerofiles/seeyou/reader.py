import re
import csv

from aerofiles.errors import ParserError


RE_COUNTRY = re.compile(r'^([\w]{2})?$', re.I)
RE_LATITUDE = re.compile(r'^([\d]{2})([\d]{2}\.[\d]{3})([NS])$', re.I)
RE_LONGITUDE = re.compile(r'^([\d]{3})([\d]{2}\.[\d]{3})([EW])$', re.I)
RE_ELEVATION = re.compile(r'^(-?[\d]*(?:\.[\d]+)?)\s?(m|ft)?$', re.I)
RE_RUNWAY_LENGTH = re.compile(r'^(?:([\d]+(?:\.[\d]+)?)\s?(ml|nm|m)?)?$', re.I)
RE_FREQUENCY = re.compile(r'^1[\d]{2}\.[\d]+?$')
RE_DISTANCE = re.compile(r'^(-?[\d]*(?:\.[\d]+)?)\s?(m|ft|km|ml|nm)?$', re.I)


class Reader:
    """
    A reader for the SeeYou CUP waypoint file format.

    see http://www.keepitsoaring.com/LKSC/Downloads/cup_format.pdf
    """

    def __init__(self, fp=None):
        self.fp = fp

    def __iter__(self):
        return self.next()

    def next(self):
        waypoints = self.read(self.fp)['waypoints']
        for waypoint in waypoints:
            yield waypoint

    def read(self, fp):
        waypoints = []
        tasks = []
        task_information = False
        for fields in csv.reader(fp):
            if fields == ["-----Related Tasks-----"]:
                task_information = True
                continue
            if task_information:
                if fields[0] == 'Options':
                    tasks[-1]['Options'] = self.decode_task_options(fields)
                elif fields[0].startswith('ObsZone'):
                    tasks[-1]['obs_zones'].append(self.decode_task_obs_zone(fields))
                else:
                    tasks.append(
                        {
                            'name': self.decode_task_name(fields),
                            'waypoints': self.decode_task_waypoints(fields),
                            'options': None,
                            'obs_zones': []
                        }
                    )
            else:
                waypoint = self.decode_waypoint(fields)
                if waypoint:
                    waypoints.append(waypoint)

        return dict(waypoints=waypoints, tasks=tasks)

    def decode_waypoint(self, fields):
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
            'name': self.decode_name(fields[0]),
            'code': self.decode_code(fields[1]),
            'country': self.decode_country(fields[2]),
            'latitude': self.decode_latitude(fields[3]),
            'longitude': self.decode_longitude(fields[4]),
            'elevation': self.decode_elevation(fields[5]),
            'style': self.decode_style(fields[6]),
            'runway_direction': self.decode_runway_direction(fields[7]),
            'runway_length': self.decode_runway_length(fields[8]),
            'frequency': self.decode_frequency(fields[9]),
            'description': self.decode_description(fields[10]),
        }

    def decode_name(self, name):
        if not name:
            raise ParserError('Name field must not be empty')

        return name

    def decode_code(self, code):
        if not code:
            return None

        return code

    def decode_country(self, country):
        if RE_COUNTRY.match(country):
            return country
        else:
            raise ParserError('Invalid country code')

    def decode_latitude(self, latitude):
        match = RE_LATITUDE.match(latitude)
        if not match:
            raise ParserError('Reading latitude failed')

        latitude = int(match.group(1)) + float(match.group(2)) / 60.

        if not (0 <= latitude <= 90):
            raise ParserError('Latitude out of bounds')

        if match.group(3).upper() == 'S':
            latitude = -latitude

        return latitude

    def decode_longitude(self, longitude):
        match = RE_LONGITUDE.match(longitude)
        if not match:
            raise ParserError('Reading longitude failed')

        longitude = int(match.group(1)) + float(match.group(2)) / 60.

        if not (0 <= longitude <= 180):
            raise ParserError('Longitude out of bounds')

        if match.group(3).upper() == 'W':
            longitude = -longitude

        return longitude

    def decode_elevation(self, elevation):
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

    def decode_style(self, style):
        try:
            style = int(style)
        except ValueError:
            raise ParserError('Reading style failed')

        if not (1 <= style <= 17):
            raise ParserError('Unknown waypoint style')

        return style

    def decode_runway_direction(self, runway_direction):
        if not runway_direction:
            return None

        try:
            runway_direction = int(runway_direction)
        except ValueError:
            raise ParserError('Reading runway direction failed')

        return runway_direction

    def decode_runway_length(self, runway_length):
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

    def decode_frequency(self, frequency):
        if not frequency:
            return None

        if not RE_FREQUENCY.match(frequency):
            raise ParserError('Reading frequency failed')

        return frequency

    def decode_description(self, description):
        if not description:
            return None

        return description

    def decode_task_options(self, fields):
        if not fields[0] == "Options":
            return

        task_options = {
            'no_start': None,
            'task_time': None,
            'wp_dis': False,
            'near_dis': None,
            'near_alt': None,
            'min_dis': False,
            'random_order': False,
            'max_pts': None,
            'before_pts': None,
            'after_pts': None,
            'bonus': None
        }

        for field in fields[1:]:
            field_type, field_entry = field.split("=")

            if field_type == 'NoStart':
                task_options['no_start'] = field_entry
            elif field_type == 'TaskTime':
                task_options['task_time'] = field_entry
            elif field_type == 'WpDis':
                task_options['wp_dis'] = field_entry == "True"
            elif field_type == 'NearDis':
                task_options['near_dis'] = self.decode_distance(field_entry)
            elif field_type == 'NearAlt':
                task_options['near_alt'] = self.decode_distance(field_entry)
            elif field_type == 'MinDis':
                task_options['min_dis'] = field_entry == "True"
            elif field_type == 'RandomOrder':
                task_options['random_order'] = field_entry == "True"
            elif field_type == 'MaxPts':
                task_options['max_pts'] = int(field_entry)
            elif field_type == 'BeforePts':
                task_options['before_pts'] = int(field_entry)
            elif field_type == 'AfterPts':
                task_options['after_pts'] = int(field_entry)
            elif field_type == 'Bonus':
                task_options['bonus'] = int(field_entry)
            else:
                raise Exception('Input contains unsupported option %s' % field)

        return task_options

    def decode_task_obs_zone(self, fields):
        task_obs_zone = {
            'obs_zone': None,
            'style': None,
            'r1': None,
            'a1': None,
            'r2': None,
            'a2': None,
            'a12': None,
            'line': False,
            'move': False,
            'reduce': False
        }

        for field in fields:
            field_type, field_entry = field.split("=")

            if field_type == 'ObsZone':
                task_obs_zone['obs_zone'] = int(field_entry)
            elif field_type == 'Style':
                task_obs_zone['style'] = int(field_entry)
            elif field_type == 'A1':
                task_obs_zone['a1'] = int(field_entry)
            elif field_type == 'A2':
                task_obs_zone['a2'] = int(field_entry)
            elif field_type == 'A12':
                task_obs_zone['a12'] = int(field_entry)
            elif field_type == 'R1':
                task_obs_zone['r1'] = self.decode_distance(field_entry)
            elif field_type == 'R2':
                task_obs_zone['r2'] = self.decode_distance(field_entry)
            elif field_type == 'Line' and field_entry == "1":
                task_obs_zone['line'] = True
            elif field_type == 'Move' and field_entry == "1":
                task_obs_zone['move'] = True
            elif field_type == 'Reduce' and field_entry == "1":
                task_obs_zone['reduce'] = True
            else:
                raise Exception('A taskpoint does not contain key %s' % field_type)

        return task_obs_zone

    def decode_task_name(self, fields):
        return fields[0]

    def decode_task_waypoints(self, fields):
        return fields[1::]

    def decode_distance(self, distance_str):
        if not distance_str:
            return {
                'value': None,
                'unit': None,
            }

        match = RE_DISTANCE.match(distance_str)
        if not match:
            raise ParserError('Reading neardis failed')

        try:
            value = float(match.group(1))
        except ValueError:
            value = None

        unit = match.group(2)
        if unit and unit.lower() not in ('m', 'ft', 'km', 'ml', 'nm'):
            raise ParserError('Unknown distance unit')
        return {
            'value': value,
            'unit': unit,
        }
