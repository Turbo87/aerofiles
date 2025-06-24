import math


class Writer:

    """
    A higher-level writer for the OpenAir airspace file format::

        with open('airspace.txt', 'wb') as fp:
            writer = Writer(fp)

    :param fp: file pointer to write to
    :param encoding: the encoding used for the output

    see `OpenAir file format specification
    <http://www.winpilot.com/UsersGuide/UserAirspace.asp>`_

    This class should be used to write records as described under Reader
    into a file.

        writer.write_record(record)

    Currently only airspace records are implemented. Terrain is missing.

    """

    def reset_V(self):
        self.V_X = None
        self.V_D = 1

    def __init__(self, fp=None, encoding='utf-8'):
        self.fp = fp
        self.encoding = encoding
        self.reset_V()

    def format_dms(self, decimal_degrees):
        decimals, number = math.modf(decimal_degrees)
        deg = int(number)
        mnt = int(decimals * 60)
        sec = round((decimal_degrees - deg - mnt / 60) * 3600.00)
        if sec == 60:
            sec = 0
            mnt += 1
            if mnt == 60:
                mnt = 0
                deg += 1
        return deg, mnt, sec

    def format_degree(self, v, width):
        (degrees, minutes, seconds) = self.format_dms(abs(v))
        result = "%0*d:%02d:%02d" % (width, degrees, minutes, seconds)
        return result

    def format_coord(self, P):
        result = self.format_degree(abs(P[0]), 2) + " "
        if P[0] >= 0:
            result = result + "N "
        else:
            result = result + "S "

        result = result + self.format_degree(abs(P[1]), 3) + " "
        if P[1] >= 0:
            result = result + "E"
        else:
            result = result + "W"
        return result

    def write_line(self, line):
        self.fp.write((line + u'\r\n').encode(self.encoding))

    def write_V_X(self, center):
        if center != self.V_X:
            self.V_X = center
            center = self.format_coord(center)
            self.write_line('V X=' + center)

    def write_V_D(self, clockwise):
        if clockwise != self.V_D:
            self.V_D = clockwise
            if clockwise:
                D = "+"
            else:
                D = "-"
            self.write_line('V D=' + D)

    def write_DC(self, element):
        self.write_V_X(element["center"])
        self.write_line('DC %s' % (str(element["radius"])))

    def write_DA(self, element):
        self.write_V_X(element["center"])
        self.write_V_D(element["clockwise"])
        self.write_line('DA %s,%s,%s' % (str(element["radius"]), str(
            element["start"]), str(element["end"])))

    def write_DB(self, element):
        self.write_V_X(element["center"])
        self.write_V_D(element["clockwise"])
        start = self.format_coord(element["start"])
        end = self.format_coord(element["end"])
        self.write_line('DB %s, %s' % (start, end))

    def write_DP(self, element):
        location = self.format_coord(element["location"])
        self.write_line('DP %s' % (location))

    def write_airspace_element(self, element):
        if element["type"] == "point":
            self.write_DP(element)
        elif element["type"] == "circle":
            self.write_DC(element)
        elif element["type"] == "arc":
            if "radius" in element:
                self.write_DA(element)
            else:
                self.write_DB(element)

    def write_airspace(self, record):
        self.reset_V()
        self.write_line('AC ' + record["class"])
        if "ident" in record and record["ident"]:
            self.write_line('AI ' + record["ident"])
        if "airspace_type" in record and record["airspace_type"]:
            self.write_line('AY ' + record["airspace_type"])
        self.write_line('AN ' + record["name"])
        self.write_line('AH ' + record["ceiling"])
        self.write_line('AL ' + record["floor"])
        if "ground_name" in record and record["ground_name"]:
            self.write_line('AG ' + record["ground_name"])
        if "freq" in record and record["freq"]:
            self.write_line('AF ' + record["freq"])
        element_prev = None
        for element in record["elements"]:
            if element_prev != element:
                element_prev = element
                self.write_airspace_element(element)

    def write_record(self, record):
        if record["type"] == "airspace":
            self.write_airspace(record)
        else:
            raise ValueError('unknown record type: ' + record["type"])
