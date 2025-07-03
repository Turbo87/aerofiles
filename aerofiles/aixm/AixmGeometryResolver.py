import decimal
import math

from . import aixm
from . import gml


# Converter function to convert nautical miles to km
#
# @param nm nautical miles
#
# @return corresponding value in km
def nautical_miles_to_km(nm):
    return nm * decimal.Decimal(1.852)


def geo_destination(p, angle, distance_km):
    lat1 = p.latitude
    lon1 = p.longitude

    angle = math.radians(angle)
    dx = math.sin(angle) * distance_km
    dy = math.cos(angle) * distance_km

    (kx, ky) = get_kx_ky(lat1)

    lon2 = lon1 + dx / kx
    lat2 = lat1 + dy / ky

    return (lat2, lon2)


# Compute the distance between two GPS points in 2 dimensions
# (without altitude). Latitude and longitude parameters must be given
# as fixed integers multiplied with GPS_COORD_MULT.
#
# \param lat1 the latitude of the 1st GPS point
# \param lon1 the longitude of the 1st GPS point
# \param lat2 the latitude of the 2nd GPS point
# \param lon2 the longitude of the 2nd GPS point
# \param FAI use FAI sphere instead of WGS ellipsoid
# \param bearing pointer to bearing (NULL if not used)
#
# \return the distance in cm.
#
def geo_distance(p1, p2):

    lat1 = p1.latitude
    lon1 = p1.longitude
    lat2 = p2.latitude
    lon2 = p2.longitude

    d_lon = (lon2 - lon1)
    d_lat = (lat2 - lat1)

    # DEBUG("#d_lon=%0.10f\n", d_lon);
    # DEBUG("#d_lat=%0.10f\n", d_lat);

    # DEBUG("lat1=%li\n", lat1);
    # DEBUG("lon1=%li\n", lon1);
    # DEBUG("lat2=%li\n", lat2);
    # DEBUG("lon2=%li\n", lon2);

    # WGS
    # DEBUG("f=0\n");
    # DEBUG("#lat=%0.10f\n", (lat1 + lat2) / ((float)GPS_COORD_MUL * 2));

    (kx, ky) = get_kx_ky((lat1 + lat2) / 2)

    # DEBUG("#kx=%0.10f\n", kx);
    # DEBUG("#ky=%0.10f\n", ky);

    d_lon = d_lon * kx
    d_lat = d_lat * ky

    # DEBUG("#d_lon=%0.10f\n", d_lon);
    # DEBUG("#d_lat=%0.10f\n", d_lat);

    dist = math.sqrt(math.pow(d_lon, 2) + math.pow(d_lat, 2)) * 100000.0

    if d_lon == 0 and d_lat == 0:
        bearing = 0
    else:
        bearing = (math.degrees(math.atan2(d_lon, d_lat)) + 360) % 360
        # DEBUG("a=%d\n", *bearing);

    # DEBUG("d=%lu\n\n", dist);

    return (dist, bearing)


def get_kx_ky(lat):
    fcos = math.cos(math.radians(lat))
    cos2 = 2. * fcos * fcos - 1.
    cos3 = 2. * fcos * cos2 - fcos
    cos4 = 2. * fcos * cos3 - cos2
    cos5 = 2. * fcos * cos4 - cos3
    # multipliers for converting longitude and latitude
    # degrees into distance (http://1.usa.gov/1Wb1bv7)
    kx = (111.41513 * fcos - 0.09455 * cos3 + 0.00012 * cos5)
    ky = (111.13209 - 0.56605 * cos2 + 0.0012 * cos4)
    return (kx, ky)


def decimal_degrees_to_dms(decimal_degrees):
    # mnt,sec = divmod(decimal_degrees*3600,60)
    # deg,mnt = divmod(mnt, 60)
    # return (round(deg),round(mnt),round(sec))

    # decimals, number = math.modf(decimal_degrees)
    # deg = int(number)
    # mnt = round(decimals * 60)
    # sec = (decimal_degrees - deg - mnt / 60) * 3600.00
    # return deg,mnt,round(sec)

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


def strDegree(v, width):
    (degrees, minutes, seconds) = decimal_degrees_to_dms(abs(v))
    return f'{degrees:0{width}d}:{minutes:02d}:{seconds:02d}'


def strLatLon(P):
    result = strDegree(abs(P[0]), 2) + " "
    if P[0] >= 0:
        result = result + "N "
    else:
        result = result + "S "

    result = result + strDegree(abs(P[1]), 3) + " "
    if P[1] >= 0:
        result = result + "E "
    else:
        result = result + "W "
    return result


class AixmGeometryResolver:
    """
    This class converts AIXM gemoetries (Arc, Circle, ..) into
    single points. This means, after the conversion, the
    airspaces will only contains points::

        parser = AixmAirspaceParser.AixmAirspaceParser()
        airspaces, borders = parser.parse("airspace-aixm.xml")
        resolver = AixmGeometryResolver()
        resolver.resolve_airspaces(airspaces)
        converter = AixmAirspaceParser.AixmOpenairConverter()
        openairs = converter.convert_airspaces(airspaces)

        fp = open("airspace-openair.txt", 'wb')
        writer = aerofiles.openair.writer.Writer(fp)
        for openair in openairs:
            writer.write_record(openair)

    `arc_angle_step` is the number of degrees, which will be used to convert
    arcs into points. A value of `1` means, that a circle has 360 points.
    """

    def __init__(self, arc_angle_step=1):
        self.arc_angle_step = arc_angle_step

    def compute_Arc(self, center: gml.Position, radius_km, start_angle, end_angle, clockwise, use_edge):
        elements = []

        if clockwise:
            reverse = False
        else:
            reverse = True
            clockwise = True
            tmp = start_angle
            start_angle = end_angle
            end_angle = tmp

        dir = self.arc_angle_step

        if clockwise:
            while start_angle > end_angle:
                end_angle = end_angle + 360
        else:
            dir = -dir
            while start_angle < end_angle:
                start_angle = start_angle + 360

        # icstart_angle)
        # ic(end_angle)
        # ic(clockwise)

        if not use_edge:
            start_angle = start_angle + dir
            end_angle = end_angle - dir

        angle = start_angle

        while True:
            # print("loop angle:", angle)
            if clockwise:
                if angle >= end_angle:
                    angle = end_angle
                    break
            else:
                if angle <= end_angle:
                    angle = end_angle
                    break

            (lat, lon) = geo_destination(center, angle, radius_km)
            # print(f'lat={lat} lon={lon}')
            element = gml.Position(latitude=lat, longitude=lon)
            elements.append(element)
            angle = angle + dir

        if reverse:
            elements.reverse()

        return elements

    def resolve_DB(self, center: gml.Position, start: gml.Position, end: gml.Position, clockwise):

        (dist_s, bearing_s) = geo_distance(center, start)
        (dist_e, bearing_e) = geo_distance(center, end)

        dist_s_km = (dist_s / 100) / 1000

        elements = self.compute_Arc(
            center, dist_s_km, bearing_s, bearing_e, clockwise, False)
        elements.insert(0, start)
        elements.append(end)

        return elements

    def resolve_PointSegment(self, segment):
        # ic(segment)
        positions = []
        positions.append(segment.point)
        return gml.ResolvedSegment(positions=positions, parent=segment)

    def resolve_CircleSegment(self, segment):
        # ic(segment)
        positions = []
        radius_km = float(nautical_miles_to_km(segment.radius))
        positions = self.compute_Arc(
            segment.center, radius_km, 0, 180, True, True)
        positions.extend(self.compute_Arc(
            segment.center, radius_km, 180, 0, True, True))
        return gml.ResolvedSegment(positions=positions, parent=segment)

    def resolve_ArcSegment(self, segment):
        # ic(segment)
        positions = []
        radius_km = float(nautical_miles_to_km(segment.radius))
        positions = self.compute_Arc(
            segment.center, radius_km, segment.start_bearing, segment.end_bearing, segment.clockwise, True)
        return gml.ResolvedSegment(positions=positions, parent=segment)

    def resolve_ResolvedSegment(self, segment):
        return segment

    def resolve_segment(self, segment: gml.GeometrySegment):
        type_name = segment.__class__.__name__
        method_name = f'resolve_{type_name}'
        method = getattr(self, method_name)
        return method(segment)

    def resolve_curve(self, curve: gml.Curve):
        if curve.__class__.__name__ == "CurveRef":
            print(f'Skipping {curve}')
            return

        segments_resolved = []
        for segment in curve.segments:
            segments_resolved.append(self.resolve_segment(segment))
        curve.segments = segments_resolved

    def resolve_volume(self, volume: aixm.AirspaceVolume):
        for curve in volume.curves:
            self.resolve_curve(curve)

    def resolve_airspace(self, airspace):
        for component in airspace.components:
            self.resolve_volume(component.volume)

    def resolve_airspaces(self, airspaces):
        for airspace in airspaces:
            self.resolve_airspace(airspace)

    def find_border(self, borders, gml_id):
        for border in borders:
            # ic(gml_id, border.gml_id)
            if border.gml_id == gml_id:
                return border
        return None
