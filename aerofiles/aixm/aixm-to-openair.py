#!/usr/bin/python
#
# Convert AIXM 5.1.1 XML files into openair airspaces.
#
# This script is licensed under GPLv2.
#
# 2025-07-02, tilmann@bubecks.de
#

import argparse

import aerofiles.openair.writer
from aerofiles.aixm import AixmAirspaceParser, AixmGeometryResolver, AixmOpenairConverter


def main():
    parser = argparse.ArgumentParser(
        description='Convert AIXM 5.1.1 airspaces into openair')
    parser.add_argument('-x', '--xml', required=True, help='AIXM filename to read from',
                        default="ED_Airspace_StrokedBorders_2024-03-21_2024-03-21_snapshot.xml")
    parser.add_argument('-o', '--output', required=True,
                        help='openair filename for ourpur')
    parser.add_argument('-r', '--resolve', required=False,
                        help='Resolve all arcs to points with given degree step.')
    parser.add_argument('-b', '--borders', required=False,
                        action='store_true', help='Include GeoBorder into openair output')
    args = parser.parse_args()

    parser = AixmAirspaceParser()

    airspaces, borders = parser.parse(args.xml)

    if parser.contains_curveref:
        print('WARN: the AIXM file contains references curves. For "Germany" we recommend "ED_Airspace_StrokedBorders...xml"')

    if args.resolve:
        resolver = AixmGeometryResolver(int(args.resolve))
        resolver.resolve_airspaces(airspaces)
        # resolver.crop_borders(airspaces, borders)

    converter = AixmOpenairConverter(
        airspaces, borders, convert_DA_to_DB=False)
    openairs = converter.convert_airspaces()

    fp = open(args.output, 'wb')
    writer = aerofiles.openair.writer.Writer(fp)
    for openair in openairs:
        writer.write_record(openair)
        writer.write_line("")

    if args.borders:
        borders = converter.convert_borders()
        for border in borders:
            border["type"] = "airspace"
            border["floor"] = "GND"
            border["ceiling"] = "GND"
            writer.write_record(border)
            writer.write_line("")

    print(f'Converted {len(airspaces)} AIXM airspaces into {
          len(openairs)} openair airspaces')


if __name__ == '__main__':
    main()
