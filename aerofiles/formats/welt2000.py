import re

from .base import Format

RE_WHITESPACE = re.compile(r'\s+')
RE_COORDINATES = re.compile(
    r'([NS])([\d]{2})([\d]{2})([\d]{2})([EW])([\d]{3})([\d]{2})([\d]{2})')
RE_ICAO = re.compile(r'[\w\d]{4}')
RE_FIELD_NUMBER = re.compile(r'FL[\d]{2}')

RE_CLASSIFIERS = [
    (re.compile(r'\bA[\d]+ B?AB[\d]*[abc]?\b'), ['highway-exit']),
    (re.compile(r'\bA[\d]+XA[\d]+\b'), ['highway-interchange']),
    (re.compile(r'\bA[\d]+YA[\d]+\b'),
        ['highway-interchange', 'y-interchange']),
    (re.compile(r'\bSTR\b'), ['road']),
    (re.compile(r'\bSX\b'), ['road-interchange']),
    (re.compile(r'\bSY\b'), ['road-interchange', 'y-interchange']),
    (re.compile(r'\bEX\b'), ['railway-interchange']),
    (re.compile(r'\bEY\b'), ['railway-interchange', 'y-interchange']),
    (re.compile(r'\bTR\b'), ['gas-station']),
    (re.compile(r'\b(BF|RS|RAIL(WAY)? STATION|GARE)\b'), ['railway-station']),
    (re.compile(r'\b(BR|BRIDGE|VIADUCT|PONT)\b'), ['bridge']),
    (re.compile(r'\b(TV|TURM|TWR|TOWER|SCHORNSTEIN)\b'), ['tower']),
    (re.compile(r'\b(CHURCH|KIRCHE|KERK|KIRKE|EGLISE|TEMPLE|TEMPLOM|DOM|'
                r'KLOSTER)\b'), ['church']),
    (re.compile(r'\b(HANGAR|HALLE)\b'), ['hangar']),
    (re.compile(r'\b(CASTLE|BURG|SCHLOSS|KOSTEL|KOSTOL|FESTUNG)\b'),
        ['castle']),
    (re.compile(r'\bVILLAGE\b'), ['village']),
    (re.compile(r'\b(TOP|PEAK|BERG|GIPFEL|MOUNTAIN|SPITZE|SUMMIT)\b'),
        ['mountain-top']),
    (re.compile(r'^(MT|MOUNT|MONT|MONTE)\b'), ['mountain']),
    (re.compile(r'\b(COL|PASS)\b'), ['mountain-pass']),
    (re.compile(r'\b(KW|KKW|POWER (PLANT|ST|STA|STN|STATION))\b'),
        ['power-plant']),
    (re.compile(r'\b(DAM|(STAU)?DAMM|STAUMAUER)\b'), ['dam']),
    (re.compile(r'\b(SILO)\b'), ['silo']),
    (re.compile(r'\b(VULCAN|VULKAN|VOLCANO)\b'), ['volcano']),
    (re.compile(r'\b(LAKE|LAC|(STAU)?SEE|TEICH)\b'), ['lake']),
    (re.compile(r'\b(SENDER)\b'), ['sender']),
    (re.compile(r'\b(VOR)\b'), ['vor']),
    (re.compile(r'\b(NDB)\b'), ['ndb']),
    (re.compile(r'\b(TUNNEL)\b'), ['tunnel']),
    (re.compile(r'\b(PFLICHTMELDEPUNKT)\b'), ['reporting-point']),
]

SURFACES = {
    ' ': None,
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


class ParserError(RuntimeError):
    pass


class Welt2000Format(Format):
    """
    A reader for the WELT2000 waypoint file format.

    see http://www.segelflug.de/vereine/welt2000/download/WELT2000-SPEC.TXT
    """

    CAN_READ_WAYPOINTS = True

    @classmethod
    def parse_waypoint(cls, line):
        """
        Parses a single waypoint from the specified input.

        Examples:

        03VBTN 03VBT NADRAZI                      414N494931E0163518CZP5
        1111N2 1111 N HWY      *    A 8018361    1274N314405W1052217USQ0
        BALDI2 BALDISSERO     ?*ULM G 3013311     329N444633E0075247ITN0
        BRCK12 BRECKENRIDG OLD ?   !S 9916341    2860N393036W1060302USO0
        CHRRT2 CHARRAT         *FL34S 30062411    459N460704E0070726CHP6
        CRAZC2 CRAZY CREEK R1  #    G1030         305N384610W1223410USQ0
        MEIER1 MEIERSBERG      #GLD!G 80133113012 164N511759E0065723DEP0
        MANOSQ MANOSQUE PONT D907XDURANCE         295N434816E0054928FRQ0
        MARCO2 MARCOUX CHAMP 8!*FL08S 2513131     694N440739E0061714FRP0
        MASER1 MASERA AVIOSUPE!# ULMA 80011913000 283N460800E0081821ITZ6
        RSTCKR ROSTOCK RITZ 25+*ULM  120    12470 892S233227E0155033NAP9
        SYDNE1 SYDNEY NSW KINSS#YSSYA395160712050   6S335646E1511038AUQ0
        VARRAI VARRAINS SILOS                  !   38N471303W0000407FRQ0
        VOGEL2 VOGELSBERG WIESE*FL03W 2529291     680N482345E0082657DEJ0
        WEISWE WEISWEILER KW 1011FT WESTL KUEHLT  144N505023E0061922DEP5
        YLIKIB YLIKI BR A1 AB KANAL             ! 114N382615E0231350GRY0
        """

        # THE DOLLAR SIGN ($) AS FIRST CHARACTER MEANS: IGNORE LINE
        if line.startswith('$'):
            return None

        # Ignore empty lines
        line = line.strip()
        if line == '':
            return None

        # Check valid line length
        if len(line) != 64:
            raise ParserError('Line length does not match 64')

        waypoint = {}
        classifiers = set()
        has_metadata = False

        # COLUMN 1-6:    SHORTFORM FOR GPS INPUT 6 CHARACTERS
        waypoint['shortname'] = line[0:6]

        # NAMES FOR AIRFIELDS ARE 5 CHARS LONG YOU CAN DELETE THE '1'
        if line[5] == '1':
            classifiers.add('landable')
            classifiers.add('airfield')

        # ALL OUTLANDING FIELDS HAVE NUMBER '2' IN COL 6
        elif line[5] == '2':
            classifiers.add('landable')

        # Read waypoint name

        # If '#' or '*' at char 23 this is a short name
        if line[23] == '#' or line[23] == '*' or line[23] == '?':
            if line[20:23] == 'GLD':
                name = line[7:20].rstrip()
            else:
                name = line[7:23].rstrip()

            has_metadata = True
        else:
            name = line[7:41].rstrip()

        # Drop '?' or '!' at the end
        if name.endswith('?') or name.endswith('!'):
            name = name[:-1]

        # Drop e.g. '20+' at the end
        if name.endswith('+'):
            name = name[:-3]

        waypoint['name'] = name = RE_WHITESPACE.sub(' ', name.rstrip())

        # Detect glider sites
        if line[23] == '#' or line[23] == '*':
            if line[20:23] == 'GLD' or line[24:27] == 'GLD':
                classifiers.add('glidersite')

        # Detect ULM fields
        if (line[23:27] == '*ULM' or
                line[23:27] == '#ULM' or line[23:28] == '# ULM'):
            classifiers.add('ulm')

        # Read ICAO code
        if has_metadata:
            code = line[24:28]

            waypoint['icao'] = None
            if line[23] == '#' and RE_ICAO.match(line[24:28]):
                waypoint['icao'] = code

            if line[23] == '*' and RE_FIELD_NUMBER.match(code):
                classifiers.add('catalogued')
                waypoint['field_number'] = int(code[2:])

            waypoint['runways'] = cls.parse_runways(line)
            waypoint['frequencies'] = cls.parse_frequencies(line)

        # COL 42 - 45       ELEVATION IN METER
        # COL 42 - 42  0 =  ELEVATION IN METER NOT PROVED
        alt = line[41:45].strip() or '0'
        waypoint['altitude'] = int(alt)

        waypoint['longitude'], waypoint['latitude'] = \
            cls.parse_coordinates(line)

        waypoint['country'] = line[60:62]

        for regex, values in RE_CLASSIFIERS:
            if regex.search(name):
                classifiers.update(values)

        waypoint['classifiers'] = classifiers

        return waypoint

    @classmethod
    def parse_runways(cls, line):
        # COL29: A=ASPH C=CONC L=LOAM S=SAND Y=CLAY G=GRAS V=GRAVEL D=DIRT
        surface = SURFACES.get(line[28])
        if not surface and line[24:29] == 'WIESE':
            surface = 'meadow'

        # 30 - 32 LENGTH OF RUNWAY IN METERS TO MULTIPLY BY 10
        length = line[29:32].strip()
        length = int(length) * 10 if length != '' else None

        # 33 - 34  AND 35-36 DIRECTION OF RUNWAYS:
        #              INCLUDES SOME FURTHER INFORMATION:
        #           A: 08/26 MEANS THAT THERE IS ONLY ONE RUNWAYS
        #              08 AND (26=08 + 18)
        #           B: 17/07 MEANS THAT THERE ARE TWO RUNWAYS,
        #                    BUT 17 IS THE MAIN RWY SURFACE LENGTH
        #          C: IF BOTH DIRECTIONS ARE IDENTICAL (04/04)
        #              THIS DIRECTION IS STRONGLY RECOMMENDED
        r1 = line[32:34].strip()
        r2 = line[34:36].strip()

        if not (r1 and r2):
            r1 = r2 = None
        else:
            r1 = int(r1) % 36
            r2 = int(r2) % 36

        runways = []
        if surface or length or r1 or r1 == 0:
            runway = {}
            if surface:
                runway['surface'] = surface
            if length:
                runway['length'] = length
            if r1 or r1 == 0:
                runway['directions'] = \
                    [r1 * 10] if r1 == r2 else [r1 * 10, (r1 + 18) * 10]

            runways.append(runway)

        if (r2 or r2 == 0) and r2 != r1 and r2 != r1 + 18:
            runways.append({
                'directions': [r2 * 10, (r2 + 18) * 10],
            })

        return runways

    @classmethod
    def parse_frequencies(cls, line):
        # 37 - 41   FREQUENCY THE BEST FOR GLIDERS
        # 41 - 41   12337 BECOMES 123.375, 13102 IS 131.025
        frq = line[36:41].strip()
        if not frq or len(frq) != 5:
            return []

        frq += '5' if frq.endswith('2') or frq.endswith('7') else '0'

        return [{
            'frequency': frq[0:3] + '.' + frq[3:6],
        }]

    @classmethod
    def parse_coordinates(cls, line):
        # COL 46 - 62  KOORDINATEN  GRAD  MIN  SEC   DEG/MIN/SEC
        # e.g. N382615E0231350

        match = RE_COORDINATES.match(line[45:60])
        if not match:
            raise ParserError('Reading coordinates failed')

        lat = (
            int(match.group(2)) +
            int(match.group(3)) / 60. +
            int(match.group(4)) / 3600.
        )
        if not (0 <= lat <= 90):
            raise ParserError('Latitude out of bounds')
        if match.group(1) == 'S':
            lat = -lat

        lon = (
            int(match.group(6)) +
            int(match.group(7)) / 60. +
            int(match.group(8)) / 3600.
        )
        if not (0 <= lon <= 180):
            raise ParserError('Longitude out of bounds')
        if match.group(5) == 'W':
            lon = -lon

        return lon, lat
