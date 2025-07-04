import sys
from pprint import pprint

from aerofiles.openair import patterns


class Reader:

    """A higher-level reader for the OpenAir airspace file format::

        with open('airspace.txt') as fp:
            reader = Reader(fp)

    see `OpenAir file format specification
    <https://github.com/naviter/seeyou_file_formats/blob/main/OpenAir_File_Format_Support.md>`. It is able
    to handle standard and extended file format.

    This class should be used as a generator and will return ``(record,
    error)`` tuples for each airspace or terrain record::

        for record, error in reader:
            if error:
                raise error  # or handle it otherwise

            # handle record

    If there is a parsing error while reading a record the whole record is
    skipped and the parsing error will be returned from the generator. It is
    up to the calling code whether that parsing error should be handled as
    fatal or not.

    Airspace records have the following structure::

        {
            "type": "airspace",
            "class": "C",
            "name": "Sacramento",
            "ident": "b3836bab-6bc3-48c1-b918-01c2559e26fa",
            "ground_name": "Sacramento Radio",
            "freq": "123.456",
            "airspace_type": "CTR",
            "floor": "500ft",
            "ceiling": "UNLIM",
            "labels": [
                [39.61333, -119.76833],
            ],
            "elements": [
                ...
            ],
        }

    where "ident", "ground_name", "freq", and "airspace_type" is only
    used on extended openair file format by using "AI", "AG", "AF",
    and "AY".

    Terrain records have the following structure::

        {
            "type": "terrain",
            "open": False,
            "name": "Lake Michigan",
            "fill": [200, 200, 255],
            "outline": [0, 1, 0, 0, 255],
            "zoom": 30.0,
            "elements": [
                ...
            ],
        }

    Possible elements in both record types, where "lineno" contains
    the line number of the OpenAir file, in which the element is
    defined::

        # DP elements
        {
            "type": "point",
            "location": [39.61333, -119.76833],
            "lineno": 100,
        }

        # DA elements
        {
            "type": "arc",
            "center": [39.61333, -119.76833],
            "clockwise": True,
            "radius": 30.0,
            "start": 70.0,
            "end": 180.0,
            "lineno": 105,
        }

        # DB elements
        {
            "type": "arc",
            "center": [39.61333, -119.76833],
            "clockwise": False,
            "start": [39.61333, -119.76833],
            "end": [39.61333, -119.76833],
            "lineno": 110,
        }

        # DC elements
        {
            "type": "circle",
            "center": [39.61333, -119.76833],
            "radius": 15.0,
            "lineno": 115,
        }

        # DY elements
        {
            "type": "airway",
            "location": [39.61333, -119.76833],
            "lineno": 120,
        }

    """

    def __init__(self, fp):
        self.reader = LowLevelReader(fp)

    def __iter__(self):
        return self.next()

    def next(self):
        state = self.State()

        for line, error in self.reader:
            if error:
                yield None, error
                state.reset()
                continue

            line_type = line['type']

            if line_type in ('AC', 'AN', 'TC', 'TO') and state.is_ready():
                yield state.record, None
                state.reset()

            if not state.record:
                if line_type in ('AC', 'AN'):
                    state.reset_airspace()
                elif line_type == 'TC':
                    state.reset_terrain(False)
                elif line_type == 'TO':
                    state.reset_terrain(True)

            if state.record:
                try:
                    self.handle_line(line, state)

                except Exception as e:
                    e.lineno = self.reader.lineno
                    yield None, e
                    state.reset()

        if state.is_ready():
            yield state.record, None

    def handle_line(self, line, state):
        line_type = line['type']

        if line_type == 'AC':
            state.record["class"] = line["value"]

        elif line_type == 'AF':
            state.record["freq"] = line["value"]

        elif line_type == 'AG':
            state.record["ground_name"] = line["value"]

        elif line_type == 'AY':
            state.record["airspace_type"] = line["value"]

        elif line_type == 'AN':
            state.record["name"] = line["value"]

        elif line_type == 'AI':
            state.record["ident"] = line["value"]

        elif line_type == 'TC':
            state.record["name"] = line["value"]

        elif line_type == 'TO':
            state.record["name"] = line["value"]

        elif line_type == 'AH':
            state.record["ceiling"] = line["value"]

        elif line_type == 'AL':
            state.record["floor"] = line["value"]

        elif line_type == 'AT':
            state.record['labels'].append(line["value"])

        elif line_type == 'SP':
            state.record["outline"] = line["value"]

        elif line_type == 'SB':
            state.record["fill"] = line["value"]

        elif line_type == 'V':
            if line['name'] == 'X':
                state.center = line["value"]
            elif line['name'] == 'D':
                state.clockwise = line["value"]
            elif line['name'] == 'Z':
                state.record['zoom'] = line["value"]

        elif line_type == 'DP':
            state.add_element({
                "type": "point",
                "location": line["value"],
                "lineno": line["lineno"],
            })

        elif line_type == 'DA':
            if not state.center:
                raise ValueError('center undefined')

            state.add_element({
                "type": "arc",
                "center": state.center,
                "clockwise": state.clockwise,
                "radius": line["radius"],
                "start": line["start"],
                "end": line["end"],
                "lineno": line["lineno"],
            })

        elif line_type == 'DB':
            state.add_element({
                "type": "arc",
                "center": state.center,
                "clockwise": state.clockwise,
                "start": line["start"],
                "end": line["end"],
                "lineno": line["lineno"],
            })

        elif line_type == 'DC':
            if not state.center:
                raise ValueError('center undefined')

            state.add_element({
                "type": "circle",
                "center": state.center,
                "radius": line["value"],
                "lineno": line["lineno"],
            })

        elif line_type == 'DY':
            state.add_element({
                "type": "airway",
                "location": line["value"],
                "lineno": line["lineno"],
            })

    class State:
        def __init__(self):
            self.center = None
            self.reset()

        def is_ready(self):
            if not self.record:
                return False

            record_type = self.record.get("type")

            return record_type == "terrain" or (record_type == "airspace" and
                self.record.get("name") and self.record.get("class"))  # noqa

        def reset_airspace(self):
            self.record = {
                "type": "airspace",
                "class": None,
                "name": None,
                "floor": None,
                "ceiling": None,
                "ident": None,
                "ground_name": None,
                "freq": None,
                "airspace_type": None,
                "labels": [],
                "elements": []
            }

        def reset_terrain(self, open):
            self.record = {
                "type": "terrain",
                "open": open,
                "name": None,
                "fill": None,
                "outline": None,
                "zoom": None,
                "elements": []
            }

        def reset(self):
            self.clockwise = True
            self.record = None

        def add_element(self, element):
            self.record['elements'].append(element)


class LowLevelReader:

    """
    A low-level reader for the OpenAir airspace file format::

        with open('airspace.txt') as fp:
            reader = LowLevelReader(fp)

    see `OpenAir file format specification
    <http://www.winpilot.com/UsersGuide/UserAirspace.asp>`_

    Instances of this class read OpenAir files line by line and extract the
    information in each line as a dictionary. A line like ``AN Sacramento`` for
    example is converted to ``{"type": "AN", "value": "Sacramento"}``.

    The reader should be used as a generator and will return a ``(result,
    error)`` tuple for each line that is not empty or a comment::

        for result, error in reader:
            if error:
                raise error  # or handle it otherwise

            # handle result

    Most lines are just parsed into ``type`` and ``value`` strings. In
    addition they have ``lineno`` which contains the line number of
    the parsed OpenAir file. The following examples should show the
    lines that are parsed differently::

        # AT 39:36.8 N 119:46.1W
        {"type": "AT", "value": [39.61333, -119.76833]}

        # DA 10,320,200
        {"type": "DA", "radius": 10, "start": 320, "end": 200}

        # DC 1.5
        {"type": "DC", "value": 1.5}

        # DP 39:35:00 N 118:59:20 W
        {"type": "DP", "value": [39.58333, -118.98888]}

        # SB 200,200,255
        {"type": "SB", "value": [200, 200, 255]}

        # SP 0,1,0,0,255
        {"type": "SP", "value": [0, 1, 0, 0, 255]}

        # V D=-
        {"type": "V", "name": "D", "value": False}

        # V X=39:29.7 N 119:46.5 W
        {"type": "V", "name": "X", "value": [39.495, -119.775]}

        # V Z=100
        {"type": "V", "name": "Z", "value": 100}
    """

    def __init__(self, fp):
        self.fp = fp
        self.lineno = 0

    def __iter__(self):
        return self.next()

    def next(self):
        for line in self.fp:
            self.lineno += 1

            try:
                result = self.parse_line(line)
                if result:
                    yield (result, None)

            except Exception as e:
                e.lineno = self.lineno
                yield (None, e)

    def parse_line(self, line):
        # Ignore comments
        pos = line.find('*')
        if pos >= 0:
            line = line[:pos]

        # Strip whitespace
        line = line.strip()

        # Ignore empty lines
        if line == '':
            return None

        # Split record type from line
        record = line.split(' ', 1)

        # Find handler method
        handler = self.get_handler_method(record[0])

        # Get value from record
        value = None if len(record) < 2 else record[1]

        # Run handler method and return result
        result = handler(value)
        result["lineno"] = self.lineno

        return result

    def get_handler_method(self, type):
        handler = getattr(self, 'handle_%s_record' % type, None)
        if not handler:
            raise ValueError('unknown record type %s in line %d' %
                             (type, self.lineno))

        return handler

    def handle_AC_record(self, value):
        return {'type': 'AC', 'value': value}

    def handle_AN_record(self, value):
        return {'type': 'AN', 'value': value}

    def handle_AF_record(self, value):
        return {'type': 'AF', 'value': value}

    def handle_AG_record(self, value):
        return {'type': 'AG', 'value': value}

    def handle_AY_record(self, value):
        return {'type': 'AY', 'value': value}

    def handle_AH_record(self, value):
        return {'type': 'AH', 'value': value}

    def handle_AI_record(self, value):
        return {'type': 'AI', 'value': value}

    def handle_AL_record(self, value):
        return {'type': 'AL', 'value': value}

    def handle_AT_record(self, value):
        return {'type': 'AT', 'value': coordinate(value)}

    def handle_TO_record(self, value):
        return {'type': 'TO', 'value': value}

    def handle_TC_record(self, value):
        return {'type': 'TC', 'value': value}

    def handle_SB_record(self, value):
        value = split(value, ',', 3, int, int, int)
        return {'type': 'SB', 'value': value}

    def handle_SP_record(self, value):
        value = split(value, ',', 5, int, int, int, int, int)
        return {'type': 'SP', 'value': value}

    def handle_V_record(self, value):
        name, value = split(value, '=', 2, str, str)

        if name == 'X':
            value = coordinate(value)

        elif name == 'Z':
            value = float(value)

        elif name == 'D':
            if value.startswith('+'):
                value = True
            elif value.startswith('-'):
                value = False
            else:
                raise ValueError('invalid direction value: %s' % value)

        return {'type': 'V', 'name': name, 'value': value}

    def handle_DP_record(self, value):
        return {'type': 'DP', 'value': coordinate(value)}

    def handle_DA_record(self, value):
        radius, start, end = split(value, ',', 3, float, float, float)

        return {
            'type': 'DA',
            'radius': radius, 'start': start, 'end': end,
        }

    def handle_DB_record(self, value):
        start, end = split(value, ',', 2, coordinate, coordinate)

        return {
            'type': 'DB',
            'start': start, 'end': end
        }

    def handle_DC_record(self, value):
        return {'type': 'DC', 'value': float(value)}

    def handle_DY_record(self, value):
        return {'type': 'DY', 'value': coordinate(value)}


def split(value, separator, num, *types):
    values = value.split(separator)
    if len(values) != num:
        raise ValueError()

    return [cast(v.strip()) for v, cast in zip(values, types)]


def coordinate(value):
    # 39:35:00 N 118:59:20 W
    match = patterns.LOCATION_FORMAT_1.match(value)
    if match:
        lat = \
            int(match.group(1)) + \
            int(match.group(2)) / 60. + \
            float(match.group(3)) / 3600.

        if match.group(4) == 'S':
            lat = -lat

        lon = \
            int(match.group(5)) + \
            int(match.group(6)) / 60. + \
            float(match.group(7)) / 3600.

        if match.group(8) == 'W':
            lon = -lon

        return [lat, lon]

    # 39:29.9 N 119:46.1 W
    match = patterns.LOCATION_FORMAT_2.match(value)
    if match:
        lat = \
            int(match.group(1)) + \
            float(match.group(2)) / 60.

        if match.group(3) == 'S':
            lat = -lat

        lon = \
            int(match.group(4)) + \
            float(match.group(5)) / 60.

        if match.group(6) == 'W':
            lon = -lon

        return [lat, lon]

    raise ValueError('invalid coordinate format: "%s"' % value)


def main(files):
    # Read every file and print result
    for file in files:
        with open(file, 'r') as fp:
            reader = Reader(fp)
            for record, error in reader:
                if error:
                    print("Error in file", file, error)
                else:
                    pprint(record)


if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print("Please give at least 1 openair file to read.")
        sys.exit(1)

    main(files)
