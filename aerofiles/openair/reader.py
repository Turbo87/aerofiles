from aerofiles.openair import patterns


class Reader:

    def __init__(self, fp):
        self.fp = fp
        self.warnings = []

    def __iter__(self):
        return self.next()

    def next(self):
        block = None
        center = None
        clockwise = True

        for record in LowLevelReader(self.fp):
            if record['type'] == 'AC':
                if not block:
                    block = self.get_empty_airspace_block()
                    clockwise = True

                elif block.get("type") == "airspace":
                    if block.get("name") and block.get("class"):
                        yield block
                        block = self.get_empty_airspace_block()
                        clockwise = True

                elif block.get("type") == "terrain":
                    yield block
                    block = self.get_empty_airspace_block()
                    clockwise = True

                block["class"] = record["value"]

            elif record['type'] == 'AN':
                if not block:
                    block = self.get_empty_airspace_block()
                    clockwise = True

                elif block.get("type") == "airspace":
                    if block.get("name") and block.get("class"):
                        yield block
                        block = self.get_empty_airspace_block()
                        clockwise = True

                elif block.get("type") == "terrain":
                    yield block
                    block = self.get_empty_airspace_block()
                    clockwise = True

                block["name"] = record["value"]

            elif record['type'] == 'TC':
                if not block:
                    block = self.get_empty_terrain_block(False)
                    clockwise = True

                elif block.get("type") == "airspace":
                    if block.get("name") and block.get("class"):
                        yield block
                        block = self.get_empty_terrain_block(False)
                        clockwise = True

                elif block.get("type") == "terrain":
                    yield block
                    block = self.get_empty_terrain_block(False)
                    clockwise = True

                block["name"] = record["value"]

            elif record['type'] == 'TO':
                if not block:
                    block = self.get_empty_terrain_block(True)
                    clockwise = True

                elif block.get("type") == "airspace":
                    if block.get("name") and block.get("class"):
                        yield block
                        block = self.get_empty_terrain_block(True)
                        clockwise = True

                elif block.get("type") == "terrain":
                    yield block
                    block = self.get_empty_terrain_block(True)
                    clockwise = True

                block["name"] = record["value"]

            elif record['type'] == 'AH':
                block["ceiling"] = record["value"]

            elif record['type'] == 'AL':
                block["floor"] = record["value"]

            elif record['type'] == 'AT':
                block['labels'].append(record["value"])

            elif record['type'] == 'SP':
                block["outline"] = record["value"]

            elif record['type'] == 'SB':
                block["fill"] = record["value"]

            elif record['type'] == 'V':
                if record['name'] == 'X':
                    center = record["value"]
                elif record['name'] == 'D':
                    clockwise = record["value"]
                elif record['name'] == 'Z':
                    block['zoom'] = record["value"]

            elif record['type'] == 'DP':
                block['elements'].append({
                    "type": "point",
                    "location": record["value"],
                })

            elif record['type'] == 'DA':
                if not center:
                    raise ValueError('center undefined')

                block['elements'].append({
                    "type": "arc",
                    "center": center,
                    "clockwise": clockwise,
                    "radius": record["radius"],
                    "start": record["start"],
                    "end": record["end"],
                })

            elif record['type'] == 'DB':
                block['elements'].append({
                    "type": "arc",
                    "center": center,
                    "clockwise": clockwise,
                    "start": record["start"],
                    "end": record["end"],
                })

            elif record['type'] == 'DC':
                if not center:
                    raise ValueError('center undefined')

                block['elements'].append({
                    "type": "circle",
                    "center": center,
                    "radius": record["value"],
                })

            elif record['type'] == 'DY':
                block['elements'].append({
                    "type": "airway",
                    "location": record["value"],
                })

        if block and block.get("type") == "airspace":
            if block.get("name") and block.get("class"):
                yield block

        elif block and block.get("type") == "terrain":
            yield block

    def get_empty_airspace_block(self):
        return {
            "type": "airspace",
            "class": None,
            "name": None,
            "floor": None,
            "ceiling": None,
            "labels": [],
            "elements": []
        }

    def get_empty_terrain_block(self, open):
        return {
            "type": "terrain",
            "open": open,
            "name": None,
            "fill": None,
            "outline": None,
            "zoom": None,
            "elements": []
        }


class LowLevelReader:

    RECORD_TYPES = (
        # AIRSPACE related record types
        'AC', 'AN', 'AH', 'AL', 'AT',

        # TERRAIN related record types
        'TO', 'TC', 'SB', 'SP',

        # Common record types
        'V', 'DP', 'DA', 'DB', 'DC', 'DY',
    )

    def __init__(self, fp):
        self.fp = fp
        self.warnings = []

    def __iter__(self):
        return self.next()

    def next(self):
        for lineno, line in enumerate(self.fp, 1):
            try:
                result = self.parse_line(line)
                if result:
                    result['line'] = lineno
                    yield result

            except Exception as e:
                self.warnings.append((e, lineno, line))

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
        value = self._split(value, ',', 3, int, int, int)
        return {'type': 'SB', 'value': value}

    def handle_SP_record(self, value):
        value = self._split(value, ',', 5, int, int, int, int, int)
        return {'type': 'SP', 'value': value}

    def handle_V_record(self, value):
        value = self._split(value, '=', 2, str, str)

        if value[0] == 'X':
            value[1] = coordinate(value[1])

        elif value[0] == 'Z':
            value[1] = float(value[1])

        elif value[0] == 'D':
            if value[1].startswith('+'):
                value[1] = True
            elif value[1].startswith('-'):
                value[1] = False
            else:
                raise ValueError('invalid direction value: %s' % value[1])

        return {'type': 'V', 'name': value[0], 'value': value[1]}

    def handle_DP_record(self, value):
        return {'type': 'DP', 'value': coordinate(value)}

    def handle_DA_record(self, value):
        value = self._split(value, ',', 3, float, float, float)

        return {
            'type': 'DA',
            'radius': value[0], 'start': value[1], 'end': value[2]
        }

    def handle_DB_record(self, value):
        value = self._split(value, ',', 2, coordinate, coordinate)

        return {
            'type': 'DB',
            'start': value[0], 'end': value[1]
        }

    def handle_DC_record(self, value):
        return {'type': 'DC', 'value': float(value)}

    def handle_DY_record(self, value):
        return {'type': 'DY', 'value': coordinate(value)}

    def _split(self, value, separator, num, *types):
        values = value.split(separator)
        if len(values) != num:
            raise ValueError()

        return [cast(v) for v, cast in zip(values, types)]


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
