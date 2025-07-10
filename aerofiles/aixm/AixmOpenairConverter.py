#!/usr/bin/python
#
# Convert AIXM airspaces into openair.
#
# Walk though all aixm.Airspace and convert them to openair.
#
# This script is licensed under GPLv2.
#
# 2025-07-02, tilmann@bubecks.de
#

import sys

from . import aixm
from . import gml
from . import geocalc

# from icecream import ic


class AixmOpenairConverter:
    """
    Convert all AIXM airspaces returned from AixmAirspaceParser into openair records.
    These can then be written by `aerofiles.openair.writer`::

        parser = AixmAirspaceParser.AixmAirspaceParser()
        airspaces, borders = parser.parse("airspace-aixm.xml")
        converter = AixmAirspaceParser.AixmOpenairConverter()
        openairs = converter.convert_airspaces(airspaces)

        fp = open("airspace-openair.txt", 'wb')
        writer = aerofiles.openair.writer.Writer(fp)
        for openair in openairs:
            writer.write_record(openair)

    """

    def __init__(self, airspaces, borders, convert_DA_to_DB=False):
        self.airspaces = airspaces
        self.borders = borders
        self.convert_DA_to_DB = convert_DA_to_DB

    def convert_PointSegment(self, segment: gml.PointSegment):
        # ic(segment)
        element = dict()
        element["type"] = "point"
        element["location"] = [segment.point.latitude, segment.point.longitude]

        return [element]

    def convert_CircleSegment(self, segment):
        # ic(segment)
        element = dict()
        element["type"] = "circle"
        element["center"] = [segment.center.latitude, segment.center.longitude]
        element["radius"] = segment.radius

        return [element]

    def convert_ArcSegment(self, segment):
        # ic(segment)
        element = dict()
        element["type"] = "arc"
        element["center"] = [segment.center.latitude, segment.center.longitude]
        element["clockwise"] = segment.clockwise
        if self.convert_DA_to_DB:
            element["start"] = geocalc.geo_destination(segment.center,
                                                       segment.start_bearing,
                                                       float(geocalc.nautical_miles_to_km(segment.radius)))
            element["end"] = geocalc.geo_destination(segment.center,
                                                     segment.end_bearing,
                                                     float(geocalc.nautical_miles_to_km(segment.radius)))
        else:
            element["start"] = segment.start_bearing
            element["end"] = segment.end_bearing
            element["radius"] = segment.radius

        return [element]

    def convert_ResolvedSegment(self, segment):
        elements = []
        for position in segment.positions:
            element = dict()
            element["type"] = "point"
            element["location"] = [position.latitude, position.longitude]
            elements.append(element)
        return elements

    def convert_segment(self, segment):
        type_name = segment.__class__.__name__
        method_name = f'convert_{type_name}'
        method = getattr(self, method_name)
        return method(segment)

    def find_airspace(self, identifier):
        for airspace in self.airspaces:
            if airspace.gml_id == identifier:
                return airspace
        return None

    def convert_volume(self, volume: aixm.AirspaceVolume):
        elements = []
        if len(volume.dependencies) > 0:
            assert (len(volume.dependencies) == 1)
            dependency = volume.dependencies[0]
            airspace = self.find_airspace(dependency.xlink)
            if airspace is not None:
                print(f'airspace {dependency.xlink} not found')
                sys.exit(1)
            print(len(airspace.components))
            assert (len(airspace.components) == 1)
            volume = airspace.components[0].volume
            # ic(volume)
            # sys.exit(0)

        for curve in volume.curves:
            if curve.__class__.__name__ == "CurveRef":
                print(f'Skipping {curve} [not implemented]')
            else:
                for segment in curve.segments:
                    elements.extend(self.convert_segment(segment))
        return elements

    def convert_vertical_limit(self, limit, limit_reference):
        if limit.uom == "FL":
            if limit_reference != "STD":
                print("Unknown limit reference", limit.dump())
                sys.exit(1)
            return f'FL{limit.value}'

        if limit_reference == "MSL":
            limit_reference = "AMSL"
        if limit_reference == "SFC":
            limit_reference = "AGL"

        if limit.value == "0" and limit_reference == "AGL":
            return "GND"

        return f'{limit.value} {limit.uom} {limit_reference}'

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

    def convert_border(self, border):

        openairs = []

        # ic(border)
        openair = dict()
        openair["type"] = "airspace"
        openair["class"] = "BORDER"
        openair["name"] = border.name
        openair["ident"] = border.gml_id
        openair["ceiling"] = "GND"
        openair["floor"] = "1000 FT AGL"

        elements = []
        for segment in border.curve.segments:
            elements.extend(self.convert_segment(segment))
        openair["elements"] = elements

        openairs.append(openair)

        return openairs

    def convert_airspace(self, airspace):

        openairs = []

        # ic(airspace)
        openair = dict()
        openair["type"] = "airspace"
        openair["class"] = airspace.class_airspace
        openair["airspace_type"] = airspace.type_airspace
        openair["ground_name"] = airspace.designator
        openair["name"] = airspace.name
        openair["ident"] = airspace.gml_id
        openair["elements"] = []
        # ic(openair["class"])

        components = self.get_dependant_components(airspace)

        if len(components) < 1:
            print(f'No components in {airspace}')
            sys.exit(1)

        volume_base = components[0].volume

        # ic(airspace)
        openair["ceiling"] = self.convert_vertical_limit(
            volume_base.upper_limit, volume_base.upper_limit_reference)
        openair["floor"] = self.convert_vertical_limit(
            volume_base.lower_limit, volume_base.lower_limit_reference)

        for component in components:
            oa = openair.copy()
            oa["elements"] = self.convert_volume(component.volume)
            openairs.append(oa)

        # ic(openairs)
        return openairs

    def convert_borders(self):
        openairs = []

        for border in self.borders:
            openairs.extend(self.convert_border(border))

        return openairs

    def convert_airspaces(self, only_referenced_airspaces=True):
        openairs = []

        for airspace in self.airspaces:
            if not only_referenced_airspaces or not airspace.is_referenced:
                oa = self.convert_airspace(airspace)
                if oa is not None:
                    openairs.extend(oa)

        return openairs
