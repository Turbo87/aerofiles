from aerofiles.openair import patterns


class Reader:

    def __init__(self, fp):
        self.reader = LowLevelReader(fp)
        self.warnings = []

    def __iter__(self):
        return self.next()

    class State:
        def __init__(self):
            self.center = None
            self.reset()

        def is_ready(self):
            if not self.block:
                return False

            block_type = self.block.get("type")

            return block_type == "terrain" or (block_type == "airspace" and
                self.block.get("name") and self.block.get("class"))

        def reset_airspace(self):
            self.block = {
                "type": "airspace",
                "class": None,
                "name": None,
                "floor": None,
                "ceiling": None,
                "labels": [],
                "elements": []
            }

        def reset_terrain(self, open):
            self.block = {
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
            self.block = None

    def next(self):
        state = self.State()

        for line, error in self.reader:
            line_type = line['type']

            if line_type in ('AC', 'AN', 'TC', 'TO'):
                if state.is_ready():
                    yield state.block
                    state.reset()

            if not state.block:
                if line_type in ('AC', 'AN'):
                    state.reset_airspace()
                elif line_type == 'TC':
                    state.reset_terrain(False)
                elif line_type == 'TO':
                    state.reset_terrain(True)

            if line_type == 'AC':
                state.block["class"] = line["value"]

            elif line_type == 'AN':
                state.block["name"] = line["value"]

            elif line_type == 'TC':
                state.block["name"] = line["value"]

            elif line_type == 'TO':
                state.block["name"] = line["value"]

            elif line_type == 'AH':
                state.block["ceiling"] = line["value"]

            elif line_type == 'AL':
                state.block["floor"] = line["value"]

            elif line_type == 'AT':
                state.block['labels'].append(line["value"])

            elif line_type == 'SP':
                state.block["outline"] = line["value"]

            elif line_type == 'SB':
                state.block["fill"] = line["value"]

            elif line_type == 'V':
                if line['name'] == 'X':
                    state.center = line["value"]
                elif line['name'] == 'D':
                    state.clockwise = line["value"]
                elif line['name'] == 'Z':
                    state.block['zoom'] = line["value"]

            elif line_type == 'DP':
                state.block['elements'].append({
                    "type": "point",
                    "location": line["value"],
                })

            elif line_type == 'DA':
                if not state.center:
                    raise ValueError('center undefined')

                state.block['elements'].append({
                    "type": "arc",
                    "center": state.center,
                    "clockwise": state.clockwise,
                    "radius": line["radius"],
                    "start": line["start"],
                    "end": line["end"],
                })

            elif line_type == 'DB':
                state.block['elements'].append({
                    "type": "arc",
                    "center": state.center,
                    "clockwise": state.clockwise,
                    "start": line["start"],
                    "end": line["end"],
                })

            elif line_type == 'DC':
                if not state.center:
                    raise ValueError('center undefined')

                state.block['elements'].append({
                    "type": "circle",
                    "center": state.center,
                    "radius": line["value"],
                })

            elif line_type == 'DY':
                state.block['elements'].append({
                    "type": "airway",
                    "location": line["value"],
                })

        if state.is_ready():
            yield state.block


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

    Most lines are just parsed into ``type`` and ``value`` strings. The
    following examples should show the lines that are parsed differently::

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
                yield (None, e)

    def parse_line(self, line):
        # Ignore comments
        if line.startswith('*'):
            return None

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
        return handler(value)

    def get_handler_method(self, type):
        handler = getattr(self, 'handle_%s_record' % type, None)
        if not handler:
            raise ValueError('unknown record type')

        return handler

    def handle_AC_record(self, value):
        return {'type': 'AC', 'value': value}

    def handle_AN_record(self, value):
        return {'type': 'AN', 'value': value}

    def handle_AH_record(self, value):
        return {'type': 'AH', 'value': value}

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

    raise ValueError('invalid coordinate format: %s' % value)
