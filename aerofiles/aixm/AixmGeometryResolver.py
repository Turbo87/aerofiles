
from . import aixm
from . import gml
from . import geocalc


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

            (lat, lon) = geocalc.geo_destination(center, angle, radius_km)
            # print(f'lat={lat} lon={lon}')
            element = gml.Position(latitude=lat, longitude=lon)
            elements.append(element)
            angle = angle + dir

        if reverse:
            elements.reverse()

        return elements

    def resolve_DB(self, center: gml.Position, start: gml.Position, end: gml.Position, clockwise):

        (dist_s, bearing_s) = geocalc.geo_distance(center, start)
        (dist_e, bearing_e) = geocalc.geo_distance(center, end)

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
        radius_km = float(geocalc.nautical_miles_to_km(segment.radius))
        positions = self.compute_Arc(
            segment.center, radius_km, 0, 180, True, True)
        positions.extend(self.compute_Arc(
            segment.center, radius_km, 180, 0, True, True))
        return gml.ResolvedSegment(positions=positions, parent=segment)

    def resolve_ArcSegment(self, segment):
        # ic(segment)
        positions = []
        radius_km = float(geocalc.nautical_miles_to_km(segment.radius))
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
