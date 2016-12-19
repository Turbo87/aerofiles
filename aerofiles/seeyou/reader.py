import re
import csv

from aerofiles.errors import ParserError


RE_COUNTRY = re.compile(r'^([\w]{2})?$', re.I)
RE_LATITUDE = re.compile(r'^([\d]{2})([\d]{2}.[\d]{3})([NS])$', re.I)
RE_LONGITUDE = re.compile(r'^([\d]{3})([\d]{2}.[\d]{3})([EW])$', re.I)
RE_ELEVATION = re.compile(r'^(-?[\d]*(?:.[\d]+)?)\s?(m|ft)?$', re.I)
RE_RUNWAY_LENGTH = re.compile(r'^(?:([\d]+(?:.[\d]+)?)\s?(ml|nm|m)?)?$', re.I)
RE_FREQUENCY = re.compile(r'^1[\d]{2}.[\d]+?$')


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
        for fields in csv.reader(self.fp):
            wp = self.decode_waypoint(fields)
            if wp:
                yield wp

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

    def decode_taskname(self, fields):
        return fields[0]

    def decode_tasklist(self, fields, waypoints):
        task_list = fields[1::]
        task = []

        for index in range(len(task_list)):
            for waypoint in waypoints:
                if waypoint["name"] == task_list[index]:
                    taskpoint = {
                        "ObsZone": index-1,  # ObsZone take-off = -1
                        "name": waypoint["name"],
                        "latitude": waypoint["latitude"],
                        "longitude": waypoint["longitude"]
                    }
                    task.append(taskpoint)
                    break

        return task

    def decode_options(self, fields):
        if not fields[0] == "Options":
            return

        task_options = {
            "TaskTime": None,
            "WpDis": False,
            "MinDis": False,
            "RandomOrder": False,
            "MaxPts": None
        }

        for field in fields:
            if field == "Options":
                continue
            elif field.split("=")[0] in ["TaskTime"]:                                # string
                task_options[field.split("=")[0]] = field.split("=")[1]
            elif field.split("=")[0] in ["WpDis", "MinDis", "RandomOrder"]:          # boolean
                task_options[field.split("=")[0]] = bool(field.split("=")[1])
            elif field.split("=")[0] in ["MaxPts"]:                                  # int
                task_options[field.split("=")[0]] = int(field.split("=")[1])
            else:
                raise Exception("Input contains unsupported option %s" % field)

        return task_options

    def decode_taskpoint(self, fields, task):

        if len(task) == 0:
            raise ValueError("Task is empty, but should filled with taskpoints")

        taskpoint_info = {
            "Style": None,
            "R1": None,
            "A1": None,
            "R2": None,
            "A2": None,
            "A12": None,
            "Line": False,
            "Move": False,
            "Reduce": False
        }

        ObsZone = None
        for field in fields:
            if field.split("=")[0] == "ObsZone":
                ObsZone = int(field.split("=")[1])
            elif field.split("=")[0] in ["Style", "A1", "A2", "A12"]:
                taskpoint_info[field.split("=")[0]] = field.split("=")[1]
            elif field.split("=")[0] in ["R1", "R2"]:
                taskpoint_info[field.split("=")[0]] = field.split("=")[1][0:-1]  # taking off m
            elif (field.split("=")[0] in ["Line", "Move", "Reduce"]) and (field.split("=")[1] == "1"):
                taskpoint_info[field.split("=")[0]] = True
            else:
                raise Exception("A taskpoint does not contain key %s" % field.split("=")[0])

        return task[ObsZone+1].update(taskpoint_info)
