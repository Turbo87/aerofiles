#!/usr/bin/python
#
# 2025-07-01, tilmann@bubecks.de
#

import decimal
import sys
import xml.etree.ElementTree as ET

# from icecream import ic

from . import aixm
from . import gml

writer = None

GML = "{http://www.opengis.net/gml/3.2}"
AIXM = "{http://www.aixm.aero/schema/5.1.1}"
XLINK = "{http://www.w3.org/1999/xlink}"


class AixmAirspaceParser:
    """
    Parse an AIXM 5.1.1 document to find all Airspaces::

        parser = AixmAirspaceParser.AixmAirspaceParser()
        airspaces, borders = parser.parse(args.xml)
        parser.resolve()
        if parser.contains_curveref:
            print(f'WARN: the AIXM file contains references curves. For "Germany" we recommend "ED_Airspace_StrokedBorders...xml"')

    Use `parser.resolve()` to resolve all referenced Airspaces.
    """

    def __init__(self):
        self.contains_curveref = False
        self.airspaces = []
        self.borders = []

    def parse_pos(self, pos):
        p = pos.split()
        # ic(p)
        return [float(p[0]), float(p[1])]
        # return [decimal.Decimal(p[0]), decimal.Decimal(p[1])]

    def parseGeodesigString(self, gds):
        positions = []

        for element in gds.findall("./"):
            if element.tag == GML + "pos":
                # ic(p)
                ll = self.parse_pos(element.text)
                p = gml.PointSegment(gml.Position(ll[0], ll[1]))
                positions.append(p)
            elif element.tag == GML + "posList":
                # ic(p)
                p = element.text.split()
                if len(p) % 2 != 0:
                    print("ERROR: keine paare", element.text)
                    sys.exit(1)
                for i in range(int(len(p) / 2)):
                    ps = gml.PointSegment(gml.Position(
                        float(p[i * 2]), float(p[i * 2 + 1])))
                    positions.append(ps)
            else:
                print("Unbekanntest GeodesigElement", element.tag)
                sys.exit(1)

        return positions

    def parseCircleByCenterPoint(self, circle2):
        pos = circle2.find(GML + "pos")
        radius = circle2.find(GML + "radius")

        ll = self.parse_pos(pos.text)
        circle = gml.CircleSegment(center=gml.Position(
            ll[0], ll[1]), radius=decimal.Decimal(radius.text))

        return circle

    def parseArcByCenterPoint(self, circle):
        pos = circle.find(GML + "pos")
        radius = circle.find(GML + "radius")

        ll = self.parse_pos(pos.text)

        start_bearing = decimal.Decimal(circle.find(GML + "startAngle").text)
        end_bearing = decimal.Decimal(circle.find(GML + "endAngle").text)
        arc = gml.ArcSegment(center=gml.Position(ll[0], ll[1]),
                             radius=decimal.Decimal(radius.text),
                             start_bearing=start_bearing,
                             end_bearing=end_bearing,
                             clockwise=start_bearing < end_bearing
                             )

        return arc

    def parseSegments(self, segments_element):
        segments = []
        for element in segments_element.findall("./"):
            # ic(element.tag)
            if "GeodesicString" in element.tag:
                segments.extend(self.parseGeodesigString(element))
            elif "LineStringSegment" in element.tag:
                segments.extend(self.parseGeodesigString(element))
            elif "CircleByCenterPoint" in element.tag:
                segments.append(self.parseCircleByCenterPoint(element))
            elif "ArcByCenterPoint" in element.tag:
                segments.append(self.parseArcByCenterPoint(element))
            else:
                print("Unbekanntes Segment", element.tag)
                sys.exit(1)

        return segments

    def parseCurve(self, curve_element):
        curve = gml.CurveImpl()
        for segment in curve_element.iter(GML + "segments"):
            segments = self.parseSegments(segment)
            curve.add_segments(segments)
        return curve

    def parseCurveMember(self, curveMember):
        curves = []
        href = curveMember.get(XLINK + "href")
        if href is not None:
            self.contains_curveref = True
            # ET.dump(curveMember)
            if href.startswith("urn:uuid:"):
                href = href[9:]
            curve = gml.CurveRef(href)
            return curve

        count = 0
        for curve in curveMember.iter(GML + "Curve"):
            count += 1
            c = self.parseCurve(curve)
            curves.append(c)

        assert (count == 1)

        return curves[0]

    def parseRing(self, ring):
        curves = []
        for member in ring.iter(GML + "curveMember"):
            c2 = self.parseCurveMember(member)
            curves.append(c2)

        return curves

    def parseAirspaceVolume(self, volume_element):

        volume = aixm.AirspaceVolume()
        # ET.dump(volume_element)
        volume.gml_id = volume_element.get(GML + "id")
        # sys.exit(0)

        contributorAirspace = volume_element.find(
            ".//" + AIXM + "AirspaceVolumeDependency")
        if contributorAirspace is not None:
            # ic("CONTRIBUTOR")
            # ET.dump(contributorAirspace)
            for airspace in contributorAirspace.iter(AIXM + "theAirspace"):
                # ET.dump(airspace)
                # ic(airspace.keys())
                dependency = volume_element.find(".//" + AIXM + "dependency")
                href = airspace.get(XLINK + "href")
                if href.startswith("urn:uuid:"):
                    href = href[9:]
                avd = aixm.AirspaceVolumeDependency()
                avd.type_dependency = dependency.text
                avd.xlink = href
                volume.add_dependency(avd)

                # ic(avd)
                # sys.exit(0)
                return volume

        (volume.upper_limit, volume.upper_limit_reference) = self.parseLimit(
            volume_element, "upper")
        (volume.lower_limit, volume.lower_limit_reference) = self.parseLimit(
            volume_element, "lower")

        # Ensure, that we have the following elements. Our logic depends on this.
        # If not, then Exception will be thrown
        ring = (
            volume_element.find(AIXM + "horizontalProjection")
            .find(AIXM + "Surface")
            .find(GML + "patches")
            .find(GML + "PolygonPatch")
            .find(GML + "exterior")
            .find(GML + "Ring")
        )

        count = 0
        for ring in volume_element.iter(GML + "Ring"):
            count += 1
            curves = self.parseRing(ring)
            # elements.extend(segments)
            volume.add_curves(curves)
        assert (count == 1)

        return volume

    def parseLimit(self, airspace, low_or_up):
        key = low_or_up + "Limit"
        limit_element = airspace.find(AIXM + key)
        if limit_element is not None:
            uom = limit_element.get("uom")
            limitRef = airspace.find(AIXM + key + "Reference")
            ref = limitRef.text
            value = limit_element.text
            return (aixm.ValDistanceVertical(value=value, uom=uom), ref)

        return (None, None)

    def parseTimesheet(self, timesheet_element):
        time_reference = timesheet_element.find(AIXM + "timeReference")
        start_date = timesheet_element.find(AIXM + "startDate")
        end_date = timesheet_element.find(AIXM + "endDate")
        start_time = timesheet_element.find(AIXM + "startTime")
        end_time = timesheet_element.find(AIXM + "endTime")
        day = timesheet_element.find(AIXM + "day")
        daylightSavingAdjust = timesheet_element.find(
            AIXM + "daylightSavingAdjust").text
        daylightSavingAdjust = daylightSavingAdjust == "YES"

        timesheet = aixm.AixmTimesheet(time_reference=time_reference.text,
                                       start_date=start_date.text,
                                       end_date=end_date.text,
                                       start_time=start_time.text,
                                       end_time=end_time.text,
                                       daylight_saving_adjust=daylightSavingAdjust,
                                       day=day.text
                                       )
        return timesheet

    def parseAirspaceActivation(self, element):
        activation = aixm.AirspaceActivation()
        activation.activity = element.find(AIXM + "activity").text
        activation.status = element.find(AIXM + "status").text

        count = 0
        for timesheet in element.iter(AIXM + "Timesheet"):
            count += 1
            sheet = self.parseTimesheet(timesheet)
            if sheet is not None:
                # ic(sheet)
                activation.add_timesheet(sheet)

        # AirspaceActivation without Timesheet is invalid
        if count == 0:
            return None

        return activation

    def parseAirspaceGeometryComponent(self, airspace: aixm.Airspace, airspaceGeometryComponent):

        component = aixm.AirspaceGeometryComponent()
        operation = airspaceGeometryComponent.find(AIXM + "operation")
        operationSequence = airspaceGeometryComponent.find(
            AIXM + "operationSequence")
        if operation is not None and operationSequence is not None:
            component.set_operation(
                operation.text, int(operationSequence.text))

        count = 0
        for volume in airspaceGeometryComponent.iter(AIXM + "AirspaceVolume"):
            count += 1
            # ic(count)
            component.set_volume(self.parseAirspaceVolume(volume))
            # if len(positions) == 0:
            #    ic("Empty positions", openair)
            #    sys.exit(1)
            #    return
            # openair["elements"] = positions
            # ic(positions)

        assert (count == 1)

        return component

    def parseAirspace(self, element):

        airspace = aixm.Airspace()

        airspace.gml_id = element.find(GML + "identifier").text
        airspace.designator = element.find(".//" + AIXM + "designator").text
        airspace.name = element.find(".//" + AIXM + "name").text
        airspace.type_airspace = element.find(".//" + AIXM + "localType").text
        airspace.class_airspace = element.find(".//" + AIXM + "type").text
        if airspace.class_airspace == "CLASS":
            classification = element.find(".//" + AIXM + "classification")
            if classification is not None:
                airspace.class_airspace = classification.text

        # ic(as_name, as_type)
        # ic(airspace)

        count = 0
        for airspaceGeometryComponent in element.iter(AIXM + "AirspaceGeometryComponent"):
            count += 1
            airspace.add_component(self.parseAirspaceGeometryComponent(
                airspace, airspaceGeometryComponent))

        # ic(airspace)

        count = 0
        for activation in element.iter(AIXM + "AirspaceActivation"):
            act = self.parseAirspaceActivation(activation)
            if act is not None:
                # ic(sheet)
                count += 1
                airspace.activation = act

        assert count <= 1, f'More than 1 AirspaceActivation in {airspace}'

        return airspace

    def parseGeoBorder(self, geoBorder):
        gml_id = geoBorder.find(GML + "identifier").text
        geo_name = geoBorder.find(".//" + AIXM + "name").text
        curve = geoBorder.find(".//" + AIXM + "Curve")

        border = aixm.GeoBorder(gml_id, geo_name)
        border.curve = self.parseCurve(curve)

        return border

    def find_airspace(self, identifier):
        for airspace in self.airspaces:
            if airspace.gml_id == identifier:
                return airspace
        return None

    def get_dependant_components(self, airspace):
        components = []
        for component in airspace.components:
            volume = component.volume
            if len(volume.dependencies) > 0:
                assert (len(volume.curves) == 0)
                for volume_dependency in volume.dependencies:
                    airspace_dep = self.find_airspace(volume_dependency.xlink)
                    if airspace_dep is None:
                        print(
                            f'Unable to find dependant airspace "{volume_dependency.xlink}" for AirspaceVolume "{volume.gml_id}"')
                        continue
                    airspace_dep.is_referenced = True
                    components.extend(
                        self.get_dependant_components(airspace_dep))
            else:
                components.append(component)

        return components

    def mark_referenced_airspaces(self):
        for airspace in self.airspaces:
            _ = self.get_dependant_components(airspace)

    def resolve_airspace(self, airspace):
        # ic(airspace)
        airspace.components = self.get_dependant_components(airspace)

    def resolve(self):
        """
         Walk through all airspaces and resolve airspace.component.  If
         an airspace has AirspaceVolumes with dependencies, these will
         be collected and replaced with the referenced Volumes.

         This means, that after calling this method, all airspaces
         will have only airspace.components and no dependencies. This
         will ease the usage of airspaces by following methods.
        """

        for airspace in self.airspaces:
            self.resolve_airspace(airspace)

    def parse(self, xml):
        """

        Parse the given AXML 5.1.1 document and returns all airspaces and borders.
        """

        self.borders = []
        self.airspaces = []

        tree = ET.parse(xml)
        root = tree.getroot()

        for element in root.iter(AIXM + "GeoBorder"):
            border = self.parseGeoBorder(element)
            # ic(border)
            self.borders.append(border)

        for airspace in root.iter(AIXM + "Airspace"):
            airspace = self.parseAirspace(airspace)
            if airspace is not None:
                self.airspaces.append(airspace)

        self.mark_referenced_airspaces()

        return (self.airspaces, self.borders)
