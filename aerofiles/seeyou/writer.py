import datetime

from .common import SeeYouFileFormat
from .converter import WaypointStyle


class Writer:
    """
    A writer for SeeYou CUP files. Supports waypoints and tasks::

        with open('competition.cup', 'wb') as fp:
            writer = Writer(fp)

    :param fp: file pointer to write to
    :param encoding: the encoding used for the output
    :param file_format: Can be one of the SeeYouFileFormat.

    """

    DIVIDER = u'-----Related Tasks-----'

    DISTANCE_FORMAT_FLOAT = u'%.1f%s'
    DISTANCE_FORMAT_INT = u'%d%s'
    DISTANCE_FORMAT_OTHER = u'%s%s'

    ANGLE_FORMAT_FLOAT = u'%.1f'
    ANGLE_FORMAT_INT = u'%d'
    ANGLE_FORMAT_OTHER = u'%s'

    def __init__(self, fp, encoding='utf-8',
                 file_format=SeeYouFileFormat.ELEVEN):
        self.fp = fp
        self.encoding = encoding
        self.wps = set()
        self.in_task_section = False

        if file_format == SeeYouFileFormat.ELEVEN:
            self.headers = SeeYouFileFormat.HEADER_11
        elif file_format == SeeYouFileFormat.TWELVE:
            self.headers = SeeYouFileFormat.HEADER_12
        elif file_format == SeeYouFileFormat.FORTEEN:
            self.headers = SeeYouFileFormat.HEADER_14

        self.write_fields(self.headers)

    def escape(self, field):
        if not field:
            return ''

        return u'"%s"' % field.replace('\\', '\\\\').replace('"', '\\"')

    def format_coordinate(self, value, is_latitude=True):
        if is_latitude:
            if not -90 <= value <= 90:
                raise ValueError(u'Invalid latitude: %s' % value)

            hemisphere = u'S' if value < 0 else u'N'
            format = u'%02d%06.3f%s'

        else:
            if not -180 <= value <= 180:
                raise ValueError(u'Invalid longitude: %s' % value)

            hemisphere = u'W' if value < 0 else u'E'
            format = u'%03d%06.3f%s'

        value = abs(value)
        degrees = int(value)
        minutes = (value - degrees) * 60
        return format % (degrees, minutes, hemisphere)

    def format_latitude(self, value):
        return self.format_coordinate(value, is_latitude=True)

    def format_longitude(self, value):
        return self.format_coordinate(value, is_latitude=False)

    def format_angle(self, angle):
        if angle is None or angle == '':
            return u''

        if isinstance(angle, float):
            return self.ANGLE_FORMAT_FLOAT % angle
        elif isinstance(angle, int):
            return self.ANGLE_FORMAT_INT % angle
        else:
            return self.ANGLE_FORMAT_OTHER % angle

    def format_distance(self, distance):
        if distance is None or distance == '':
            return u''

        if isinstance(distance, tuple):
            unit = distance[1]
            distance = distance[0]
        else:
            unit = u'm'

        if isinstance(distance, float):
            return self.DISTANCE_FORMAT_FLOAT % (distance, unit)
        elif isinstance(distance, int):
            return self.DISTANCE_FORMAT_INT % (distance, unit)
        else:
            return self.DISTANCE_FORMAT_OTHER % (distance, unit)

    def format_pics(self, pics):
        if pics is None or pics == []:
            return u''
        return self.escape(';'.join(pics))

    def format_time(self, time):
        if isinstance(time, datetime.datetime):
            time = time.time()

        if isinstance(time, datetime.time):
            time = time.strftime(u'%H:%M:%S')

        return time

    def format_timedelta(self, timedelta):
        if isinstance(timedelta, datetime.timedelta):
            hours, remainder = divmod(timedelta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            timedelta = u'%02d:%02d:%02d' % (hours, minutes, seconds)

        return timedelta

    def write_line(self, line=u''):
        self.fp.write((line + u'\r\n').encode(self.encoding))

    def write_fields(self, fields):
        self.write_line(u','.join(fields))

    def set_field(self, field, key, value):
        if key in self.headers:
            field[self.headers.index(key)] = value
        else:
            raise RuntimeError(
                "Writing value to non existing column '%s'. Check for correct SeeYouFileFormat when creating Writer." % key)

    def write_waypoint(
            self, name, shortname, country, latitude, longitude, elevation=u'',
            style=WaypointStyle.NORMAL, runway_direction=u'', runway_length=u'',
            frequency=u'', description=u'', runway_width=u'', userdata=u'', pics=u''):
        """
        Write a waypoint::

            writer.write_waypoint(
                'Meiersberg',
                'MEIER',
                'DE',
                (51 + 7.345 / 60.),
                (6 + 24.765 / 60.),
            )
            # -> "Meiersberg","MEIER",DE,5107.345N,00624.765E,,1,,,,

        :param name: name of the waypoint (must not be empty)
        :param shortname: short name for depending GPS devices
        :param country: IANA top level domain country code (see
            http://www.iana.org/cctld/cctld-whois.htm)
        :param latitude: latitude of the point (between -90 and 90 degrees)
        :param longitude: longitude of the point (between -180 and 180 degrees)
        :param elevation: elevation of the waypoint in meters or as
            ``(elevation, unit)`` tuple
        :param style: the waypoint type (see official specification for the
            list of valid styles, defaults to "Normal")
        :param runway_direction: heading of the runway in degrees if the
            waypoint is landable
        :param runway_length: length of the runway in meters or as ``(length,
            unit)`` tuple if the waypoint is landable
        :param frequency: radio frequency of the airport
        :param description: optional description of the waypoint (no length
            limit)
        :param runway_width: width of the runway in meters or as ``(width,
            unit)`` tuple if the waypoint is landable
        :param userdata: arbitrary string with user data (no length
            limit)
        :param pics: list of filenames of pictures

        """

        if self.in_task_section:
            raise RuntimeError(u'Waypoints must be written before any tasks')

        if not name:
            raise ValueError(u'Waypoint name must not be empty')

        fields = [""] * len(self.headers)
        self.set_field(fields, 'name', self.escape(name))
        self.set_field(fields, 'code', self.escape(shortname))
        self.set_field(fields, 'country', country)
        self.set_field(fields, 'lat', self.format_latitude(latitude))
        self.set_field(fields, 'lon', self.format_longitude(longitude))
        self.set_field(fields, 'elev', self.format_distance(elevation))
        self.set_field(fields, 'style', str(style))
        self.set_field(fields, 'rwdir', str(runway_direction))
        self.set_field(fields, 'rwlen', self.format_distance(runway_length))
        if runway_width:
            self.set_field(fields, 'rwwidth',
                           self.format_distance(runway_width))
        self.set_field(fields, 'freq', self.escape(frequency))
        self.set_field(fields, 'desc', self.escape(description))
        if userdata:
            self.set_field(fields, 'userdata', self.escape(userdata))
        if pics:
            self.set_field(fields, 'pics', self.format_pics(pics))

        self.write_fields(fields)

        self.wps.add(name)

    def write_task(self, description, waypoints):
        """
        Write a task definition::

            writer.write_task('500 km FAI', [
                'MEIER',
                'BRILO',
                'AILER',
                'MEIER',
            ])
            # -> "500 km FAI","MEIER","BRILO","AILER","MEIER"

        Make sure that the referenced waypoints have been written with
        :meth:`~aerofiles.seeyou.Writer.write_waypoint` before writing the
        task. The task section divider will be written to automatically when
        :meth:`~aerofiles.seeyou.Writer.write_task` is called the first time.
        After the first task is written
        :meth:`~aerofiles.seeyou.Writer.write_waypoint` must not be called
        anymore.

        :param description: description of the task (may be blank)
        :param waypoints: list of waypoints in the task (names must match the
            long names of previously written waypoints)
        """

        if not self.in_task_section:
            self.write_line()
            self.write_line(self.DIVIDER)
            self.in_task_section = True

        fields = [self.escape(description)]

        for waypoint in waypoints:
            if waypoint not in self.wps:
                raise ValueError(u'Waypoint "%s" was not found' % waypoint)

            fields.append(self.escape(waypoint))

        self.write_fields(fields)

    def write_task_options(self, **kw):
        """
        Write an options line for a task definition::

            writer.write_task_options(
                start_time=time(12, 34, 56),
                task_time=timedelta(hours=1, minutes=45, seconds=12),
                waypoint_distance=False,
                distance_tolerance=(0.7, 'km'),
                altitude_tolerance=300.0,
            )
            # -> Options,NoStart=12:34:56,TaskTime=01:45:12,WpDis=False,NearDis=0.7km,NearAlt=300.0m

        :param start_time: opening time of the start line as
            :class:`datetime.time` or string
        :param task_time: designated time for the task as
            :class:`datetime.timedelta` or string
        :param waypoint_distance: task distance calculation (``False``: use
            fixes, ``True``: use waypoints)
        :param distance_tolerance: distance tolerance in meters or as
            ``(distance, unit)`` tuple
        :param altitude_tolerance: altitude tolerance in meters or as
            ``(distance, unit)`` tuple
        :param min_distance: "uncompleted leg (``False``: calculate maximum
            distance from last observation zone)"
        :param random_order: if ``True``, then Random order of waypoints is
            checked
        :param max_points: maximum number of points
        :param before_points: number of mandatory waypoints at the beginning.
            ``1`` means start line only, ``2`` means start line plus first
            point in task sequence (Task line).
        :param after_points: number of mandatory waypoints at the end. ``1``
            means finish line only, ``2`` means finish line and one point
            before finish in task sequence (Task line).
        :param bonus: bonus for crossing the finish line
        """

        if not self.in_task_section:
            raise RuntimeError(
                u'Task options have to be written in task section')

        fields = ['Options']

        if 'start_time' in kw:
            fields.append(u'NoStart=' + self.format_time(kw['start_time']))

        if 'task_time' in kw:
            fields.append(
                u'TaskTime=' + self.format_timedelta(kw['task_time']))

        if 'waypoint_distance' in kw:
            fields.append(u'WpDis=%s' % kw['waypoint_distance'])

        if 'distance_tolerance' in kw:
            fields.append(
                u'NearDis=' + self.format_distance(kw['distance_tolerance']))

        if 'altitude_tolerance' in kw:
            fields.append(
                u'NearAlt=' + self.format_distance(kw['altitude_tolerance']))

        if 'min_distance' in kw:
            fields.append(u'MinDis=%s' % kw['min_distance'])

        if 'random_order' in kw:
            fields.append(u'RandomOrder=%s' % kw['random_order'])

        if 'max_points' in kw:
            fields.append(u'MaxPts=%d' % kw['max_points'])

        if 'before_points' in kw:
            fields.append(u'BeforePts=%d' % kw['before_points'])

        if 'after_points' in kw:
            fields.append(u'AfterPts=%d' % kw['after_points'])

        if 'bonus' in kw:
            fields.append(u'Bonus=%d' % kw['bonus'])

        self.write_fields(fields)

    def write_observation_zone(self, num, **kw):
        """
        Write observation zone information for a taskpoint::

            writer.write_task_options(
                start_time=time(12, 34, 56),
                task_time=timedelta(hours=1, minutes=45, seconds=12),
                waypoint_distance=False,
                distance_tolerance=(0.7, 'km'),
                altitude_tolerance=300.0,
            )
            # -> Options,NoStart=12:34:56,TaskTime=01:45:12,WpDis=False,NearDis=0.7km,NearAlt=300.0m

        :param num: consecutive number of a waypoint (``0``: Start)
        :param style: direction (``0``: Fixed value, ``1``: Symmetrical, ``2``:
            To next point, ``3``: To previous point, ``4``: To start point
        :param radius: radius 1 in meter or as ``(radius, unit)`` tuple
        :param angle: angle 1 in degrees
        :param radius2: radius 2 in meter or as ``(radius, unit)`` tuple
        :param angle 2: angle 2 in degrees
        :param angle12: angle 12 in degress
        :param line: should be ``True`` if start or finish line
        """

        if not self.in_task_section:
            raise RuntimeError(
                u'Observation zones have to be written in task section')

        fields = [u'ObsZone=%d' % num]

        if 'style' in kw:
            fields.append(u'Style=%d' % kw['style'])

        if 'radius' in kw:
            fields.append(u'R1=' + self.format_distance(kw['radius']))

        if 'angle' in kw:
            fields.append(u'A1=' + self.format_angle(kw['angle']))

        if 'radius2' in kw:
            fields.append(u'R2=' + self.format_distance(kw['radius2']))

        if 'angle2' in kw:
            fields.append(u'A2=' + self.format_angle(kw['angle2']))

        if 'angle12' in kw:
            fields.append(u'A12=' + self.format_angle(kw['angle12']))

        if 'line' in kw:
            fields.append(u'Line=' + ('1' if kw['line'] else '0'))

        self.write_fields(fields)
