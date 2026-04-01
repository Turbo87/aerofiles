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
import re

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

    def convert_volume_curves(self, volume: aixm.AirspaceVolume):
        elements = []
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

    def convert_date(self, d):
        match = re.fullmatch(r"(\d{2})-(\d{2})", d)
        if match:
            return f'{match.group(1)}.{match.group(2)}.'
        else:
            return d

    def convert_timesheet(self, ts):
        # ic(ts)
        day = None
        hours = None
        dates = None

        if ts.day is not None:
            if ts.day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN", "HOL", "WORK_DAY"]:
                day = ts.day
                if ts.day_til is not None:
                    if ts.day_til != ts.day:
                        day += "-" + ts.day_til
                        # ic(ts, day)
            elif ts.day == "ANY":
                day = None
                if ts.day_til is not None and ts.day_til != "ANY":
                    print(f'{ts}: day is ANY and dayTil is wrong')
                    sys.exit(2)
            else:
                print(f"unknown day: {ts.day} in {ts}")
                sys.exit(1)
        else:
            if ts.day_til is not None:
                print(f'{ts}: day is None and dayTil is not None')
                sys.exit(2)

        start_time = ts.start_time
        end_time = ts.end_time

        # Use "start_time" or "start_event":
        if ts.start_time is None and ts.start_event is not None:
            start_time = ts.start_event
            if ts.start_time_relative_event is not None:
                start_time += f'{ts.start_time_relative_event.value:+d}{ts.start_time_relative_event.uom}'

        # Use "end_time" or "end_event":
        if ts.end_time is None and ts.end_event is not None:
            end_time = ts.end_event
            if ts.end_time_relative_event is not None:
                end_time += f'{ts.end_time_relative_event.value:+d}{ts.end_time_relative_event.uom}'

        if (start_time is None and end_time is None) or (start_time == "00:00" and end_time in ["00:00", "23:59", "24:00"]):
            hours = "H24"
        elif start_time is None:
            hours = f'-{end_time}'
        elif end_time is None:
            hours = f'{start_time}-'
        else:
            hours = f'{start_time}-{end_time}'

        if ts.daylight_saving_adjust:
            if hours is not None and hours != "H24":
                hours += "[DSA]"

        if (ts.start_date is None and ts.end_date is None) or (ts.start_date in ["01-01"] and ts.end_date in ["31-12"]):
            # result += ""
            dates = None
        else:
            s = self.convert_date(ts.start_date)
            e = self.convert_date(ts.end_date)
            dates = f'{s}-{e}'

        return [day, hours, dates]

    def abbreviate_weekdays(self, days_string):
        """
        Erzeugt eine abgekürzte Schreibweise für sortierte Wochentage.

        Args:
        days_string (str): String mit sortierten Wochentagen (MON, TUE, WED, THU, FRI, SAT, SUN)

        Returns:
        str: Abgekürzte Schreibweise (z.B. "MON-SUN", "TUE-FRI", "MON-WED,FRI-SUN")
        """
        # Wochentage in der richtigen Reihenfolge
        weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

        # Extrahiere die vorhandenen Tage aus dem String
        present_days = []
        for day in weekdays:
            if day in days_string:
                present_days.append(day)

        if not present_days:
            return ""

        # Finde zusammenhängende Bereiche
        ranges = []
        start = 0

        while start < len(present_days):
            end = start

            # Finde das Ende des aktuellen Bereichs
            while (end + 1 < len(present_days) and
                   weekdays.index(present_days[end + 1]) == weekdays.index(present_days[end]) + 1):
                end += 1

            # Füge den Bereich hinzu
            if start == end:
                # Einzelner Tag
                ranges.append(present_days[start])
            else:
                # Bereich von start bis end
                ranges.append(f"{present_days[start]}-{present_days[end]}")

            start = end + 1

        return ",".join(ranges)

    def combine_times(self, times):
        result = []

        # Wochentag-Mapping für die Sortierung
        weekday_order = {
            'MON': 0,
            'TUE': 1,
            'WED': 2,
            'THU': 3,
            'FRI': 4,
            'SAT': 5,
            'SUN': 6,
            None: 7
        }

        times_other = []
        times_weekday = []
        for time in times:
            if time[0] not in weekday_order:
                times_other.append(time)
            else:
                times_weekday.append(time)

        # ic(times_weekday)

        # Sortieren nach Wochentag
        times = sorted(times_weekday, key=lambda x: weekday_order[x[0]])

        # if times[0][1] == "06:00-17:30":
        #    ic("AA")

        # Combine days:
        for i in range(len(times)):
            if i >= len(times):
                break

            result = []
            for j in range(i + 1, len(times)):
                if times[i][0] != times[j][0] and times[i][1] == times[j][1] and times[i][2] == times[j][2]:
                    # day is different, the rest identical
                    result.append(j)

            if len(result) > 0:
                times2 = times[:i + 1]
                # ic(i, times, result)
                # ic(times2)
                days = [times[i][0]]
                for j in range(i + 1, len(times)):
                    if j in result:
                        days.append(times[j][0])
                    else:
                        times2.append(times[j])
                times[i][0] = self.abbreviate_weekdays("".join(days))
                times = times2

        result = []
        result.extend(times_other)
        result.extend(times)

        return result

    def convert_activation(self, activation, include_time):
        if activation is None:
            return None

        debug = False
        times = []
        for timesheet in activation.timesheets:
            if timesheet.start_date is not None and timesheet.start_date != "01-01":
                debug = True
            times.append(self.convert_timesheet(timesheet))

        if not include_time:
            for time in times:
                time[1] = None

        debug = False
        if len(times) > 1:
            # debug = True
            if debug:
                print(times)
                #ic(activation)
                #ic(times)
            times = self.combine_times(times)
            # ic(times)

        #if debug:
        #    ic(times)

        # Ensure, that all time lines have identical dates
        if False:
            dates = times[0][2]
            for time in times:
                if time[2] != dates:
                    print(f'Different dates in TimeSheets {activation}')
                    sys.exit(1)

        dates = []
        for time in times:
            if time[2] not in dates:
                dates.append(time[2])

        lines = []
        for date in dates:
            s = ""
            for time in times:
                if time[2] == date:
                    if s != "":
                        s += ";"
                    if time[0] is not None:
                        s += time[0]
                    if time[0] is not None and time[1] is not None:
                        s += " "
                    if time[1] is not None:
                        s += time[1].replace(":", "")
            if date is not None:
                s += " (" + date + ")"
            if s != "":
                lines.append(s.strip())

        #if debug:
        #    ic(lines)

        # Combine each line into a single string
        # result = []
        # for time in times:
        #    print(time)
        #    result.append("|" + "|".join(x or '' for x in time) + "|")

        result = lines
        # ic(lines)

        return result

    def find_best_class_airspace(self, airspaces):

        c = airspaces[-1].class_airspace

        if len(airspaces) > 1 and c in ["PART", "SECTOR"]:
            # Remove last element and try above
            return self.find_best_class_airspace(airspaces[:-1])

        return airspaces[-1].class_airspace, airspaces[-1].type_airspace

    def convert_airspace(self, airspace, parents):

        openairs = []

        parents2 = list(parents)
        parents2.append(airspace)

        for component in airspace.components:
            volume = component.volume
            if len(volume.dependencies) > 0:
                assert (len(volume.curves) == 0)
                # This volume has airspaces as dependencies. Convert them
                for volume_dependency in volume.dependencies:
                    if volume_dependency.dependency_airspace is not None:
                        openairs.extend(self.convert_airspace(
                            volume_dependency.dependency_airspace, parents2))
            else:
                assert (len(volume.curves) > 0)

                # ic(airspace)
                openair = dict()
                openair["type"] = "airspace"
                c, t = self.find_best_class_airspace(parents2)
                openair["class"] = c
                openair["airspace_type"] = t
                openair["ground_name"] = airspace.designator
                openair["name"] = airspace.name
                openair["ident"] = airspace.gml_id
                openair["elements"] = []
                # ic(openair["class"])

                # ic(airspace)
                openair["ceiling"] = self.convert_vertical_limit(
                    volume.upper_limit, volume.upper_limit_reference)
                openair["floor"] = self.convert_vertical_limit(
                    volume.lower_limit, volume.lower_limit_reference)
                activation = self.convert_activation(
                    airspace.activation, include_time=True)
                if activation is not None:
                    lines = self.convert_activation(
                        airspace.activation, include_time=False)
                    for line in lines:
                        activation.append("WO_TIME: " + line)
                    openair["activation"] = []
                    for line in activation:
                        openair["activation"].append({"value": line})
                openair["elements"] = self.convert_volume_curves(volume)
                #if openair["name"] == "MUENSTER-off":
                #    ic(openair)
                openairs.append(openair)

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
            # if airspace.reference_count > 1:
            #    print(f'{airspace.name} is referenced more than once.')
            if not only_referenced_airspaces or not airspace.reference_count > 0:
                oa = self.convert_airspace(airspace, [])
                if oa is not None:
                    openairs.extend(oa)

        return openairs
