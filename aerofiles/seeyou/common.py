
class WaypointStyle:
    NORMAL = 1
    AIRFIELD_GRASS = 2
    OUTLANDING = 3
    GLIDERSITE = 4
    AIRFIELD_SOLID = 5
    MOUNTAIN_PASS = 6
    MOUNTAIN_TOP = 7
    SENDER = 8
    VOR = 9
    NDB = 10
    COOL_TOWER = 11
    DAM = 12
    TUNNEL = 13
    BRIDGE = 14
    POWER_PLANT = 15
    CASTLE = 16
    INTERSECTION = 17
    MARKER = 18
    CONTROL_POINT = 19
    PG_TAKE_OFF = 20
    PG_LANDING_ZONE = 21


class ObservationZoneStyle:
    FIXED = 0
    SYMMETRICAL = 1
    TO_NEXT_POINT = 2
    TO_PREVIOUS_POINT = 3
    TO_START_POINT = 4


class SeeYouFileFormat:
    ELEVEN = 0
    TWELVE = 1
    FORTEEN = 2

    HEADER_11 = ['name', 'code', 'country', 'lat', 'lon',
                 'elev', 'style', 'rwdir', 'rwlen', 'freq', 'desc']
    HEADER_12 = ['name', 'code', 'country', 'lat', 'lon', 'elev',
                 'style', 'rwdir', 'rwlen', 'rwwidth', 'freq', 'desc']
    HEADER_14 = ['name', 'code', 'country', 'lat', 'lon', 'elev', 'style',
                 'rwdir', 'rwlen', 'rwwidth', 'freq', 'desc', 'userdata', 'pics']
