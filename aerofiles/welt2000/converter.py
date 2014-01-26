import re

from .reader import Reader


RE_ICAO = re.compile(r'^[\w\d]{4}$')

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


class Converter:
    """
    A reader for the WELT2000 waypoint file forrmat.

    see http://www.segelflug.de/vereine/welt2000/download/WELT2000-SPEC.TXT
    """

    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        return self.next()

    def next(self):
        for old in Reader(self.fp):
            new = self.convert_waypoint(old)
            if new:
                yield new

    def convert_waypoint(self, old):
        waypoint = {}

        waypoint['name'] = old['text']
        waypoint['shortname'] = old['shortform']
        waypoint['country'] = old['country']
        waypoint['description'] = None

        waypoint['latitude'] = old['latitude']
        waypoint['longitude'] = old['longitude']

        waypoint['elevation'] = old['elevation']

        waypoint['classifiers'] = set()

        if old['is_glidersite']:
            waypoint['classifiers'].add('glidersite')

        if old['is_ulm']:
            waypoint['classifiers'].add('ulm')

        if old['is_airfield']:
            waypoint['classifiers'].add('landable')
            waypoint['classifiers'].add('airfield')

        if old['is_outlanding']:
            waypoint['classifiers'].add('landable')

        if 'landable' in waypoint['classifiers']:
            waypoint['icao'] = self.convert_icao(old['icao'])
            waypoint['runways'] = self.convert_runways(
                old['runway_surface'],
                old['runway_directions'],
                old['runway_length']
            )
            waypoint['frequencies'] = self.convert_frequencies(
                old['frequency']
            )

            if old['field_number'] is not None:
                waypoint['classifiers'].add('catalogued')
                waypoint['field_number'] = old['field_number']

        for regex, values in RE_CLASSIFIERS:
            if regex.search(old['text']):
                waypoint['classifiers'].update(values)

        return waypoint

    def convert_icao(self, icao):
        if icao and RE_ICAO.match(icao):
            return icao

    def convert_runways(self, surface, directions, length):
        runways = []
        if surface or length or directions:
            runway = {}
            if surface:
                runway['surface'] = surface
            if length:
                runway['length'] = length
            if directions:
                if len(directions) == 1:
                    runway['directions'] = [directions[0] % 360]
                else:
                    runway['directions'] = \
                        [directions[0] % 360, (directions[0] + 180) % 360]

            runways.append(runway)

        if (directions and len(directions) == 2 and
                (directions[0] + 180) % 360 != directions[1]):
            runways.append({
                'directions': [
                    directions[1] % 360,
                    (directions[1] + 180) % 360
                ],
            })

        return runways

    def convert_frequencies(self, frq):
        if not frq:
            return []

        return [{
            'frequency': frq,
        }]
