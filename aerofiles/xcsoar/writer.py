import datetime
from contextlib import contextmanager

from .constants import ObservationZoneType


class Writer:
    """
    A writer class for the `XCSoar <http://www.xcsoar.org>`_ task file format::

        with open('task.tsk', 'w') as fp:
            writer = Writer(fp)

    This task file format contains one task per file. Writing more than one
    task will cause an exception. A task can be written by using the
    :meth:`~aerofiles.xcsoar.Writer.write_task` method.
    """

    def __init__(self, fp, encoding='utf-8'):
        self.fp = fp
        self.encoding = encoding
        self.indent_level = 0

    def write_line(self, line):
        indent = '\t' * self.indent_level
        self.fp.write((indent + line + '\n').encode(self.encoding))

    def format_tag_content(self, _name, **kw):
        params = list(map(lambda item: '%s="%s"' % item, kw.items()))
        params.sort()
        return _name + ' ' + ' '.join(params)

    def convert_bool(self, kw, key):
        if key in kw:
            value = kw[key]
            if isinstance(value, bool):
                kw[key] = (1 if value else 0)

    def convert_time(self, kw, key):
        if key in kw:
            value = kw[key]
            if isinstance(value, datetime.time):
                kw[key] = value.strftime('%H:%M')

    def convert_timedelta(self, kw, key):
        if key in kw:
            value = kw[key]
            if isinstance(value, datetime.timedelta):
                kw[key] = value.seconds

    @contextmanager
    def write_tag_with_content(self, _name, **kw):
        self.write_line('<%s>' % self.format_tag_content(_name, **kw))
        self.indent_level += 1
        yield
        self.indent_level -= 1
        self.write_line('</%s>' % _name)

    def write_tag(self, _name, **kw):
        self.write_line('<%s/>' % self.format_tag_content(_name, **kw))

    def write_task(self, **kw):
        """
        Write the main task to the file::

            with writer.write_task(type=TaskType.RACING):
                ...

            # <Task type="RT"> ... </Task>

        Inside the with clause the :meth:`~aerofiles.xcsoar.Writer.write_point`
        method should be used to write the individual task points. All
        parameters are optional.

        :param type: type of the task (one of the constants in
            :class:`~aerofiles.xcsoar.constants.TaskType`)
        :param start_requires_arm: ``True``: start has to be armed manually,
            ``False``: task will be started automatically
        :param start_max_height: maximum altitude when the task is started
            (in m)
        :param start_max_height_ref: altitude reference of
            ``start_max_height`` (one of the constants in
            :class:`~aerofiles.xcsoar.constants.AltitudeReference`)
        :param start_max_speed: maximum speed when the task is started (in m/s)
        :param start_open_time: time that the start line opens as
            :class:`datetime.time`
        :param start_close_time: time that the start line is closing as
            :class:`datetime.time`
        :param aat_min_time: AAT time as :class:`datetime.timedelta`
        :param finish_min_height: minimum altitude when the task is finished
            (in m)
        :param finish_min_height_ref: altitude reference of
            ``finish_min_height`` (one of the constants in
            :class:`~aerofiles.xcsoar.constants.AltitudeReference`)
        :param fai_finish: ``True``: FAI finish rules apply
        """

        self.convert_timedelta(kw, 'aat_min_time')
        self.convert_time(kw, 'start_open_time')
        self.convert_time(kw, 'start_close_time')
        self.convert_bool(kw, 'fai_finish')
        self.convert_bool(kw, 'start_requires_arm')

        return self.write_tag_with_content('Task', **kw)

    def write_point(self, **kw):
        """
        Write a task point to the file::

            with writer.write_point(type=PointType.TURN):
                writer.write_waypoint(...)
                writer.write_observation_zone(...)

            # <Point type="Turn"> ... </Point>

        Inside the with clause the
        :meth:`~aerofiles.xcsoar.Writer.write_waypoint` and
        :meth:`~aerofiles.xcsoar.Writer.write_observation_zone` methods must be
        used to write the details of the task point.

        :param type: type of the task point (one of the constants in
            :class:`~aerofiles.xcsoar.constants.PointType`)
        """

        assert 'type' in kw

        self.convert_bool(kw, 'score_exit')

        return self.write_tag_with_content('Point', **kw)

    def write_waypoint(self, **kw):
        """
        Write a waypoint to the file::

            writer.write_waypoint(
                name='Meiersberg',
                latitude=51.4,
                longitude=7.1
            )

            # <Waypoint name="Meiersberg">
            #     <Location latitude="51.4" longitude="7.1"/>
            # </Waypoint>

        :param name: name of the waypoint
        :param latitude: latitude of the waypoint (in WGS84)
        :param longitude: longitude of the waypoint (in WGS84)
        :param altitude: altitude of the waypoint (in m, optional)
        :param id: internal id of the waypoint (optional)
        :param comment: extended description of the waypoint (optional)
        """

        assert 'name' in kw
        assert 'latitude' in kw
        assert 'longitude' in kw

        location_kw = {
            'latitude': kw['latitude'],
            'longitude': kw['longitude'],
        }

        del kw['latitude']
        del kw['longitude']

        with self.write_tag_with_content('Waypoint', **kw):
            self.write_tag('Location', **location_kw)

    def write_observation_zone(self, **kw):
        """
        Write an observation zone declaration to the file::

            writer.write_observation_zone(
                type=ObservationZoneType.CYLINDER,
                radius=30000,
            )

            # <ObservationZone type="Cylinder" radius="30000"/>

        The required parameters depend on the type parameter. Different
        observation zone types require different parameters.

        :param type: observation zone type (one of the constants in
            :class:`~aerofiles.xcsoar.constants.ObservationZoneType`)

        :param length: length of the line
            (only used with type
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.LINE`)
        :param radius: (outer) radius of the observation zone
            (used with types
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.CYLINDER`,
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.SECTOR`,
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.SYMMETRIC_QUADRANT` and
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.CUSTOM_KEYHOLE`)
        :param inner_radius: inner radius of the observation zone
            (only used with type
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.CUSTOM_KEYHOLE`)
        :param angle: angle of the observation zone
            (only used with type
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.CUSTOM_KEYHOLE`)
        :param start_radial: start radial of the observation zone
            (only used with type
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.SECTOR`)
        :param end_radial: end radial of the observation zone
            (only used with type
            :const:`~aerofiles.xcsoar.constants.ObservationZoneType.SECTOR`)
        """

        assert 'type' in kw

        if kw['type'] == ObservationZoneType.LINE:
            assert 'length' in kw

        elif kw['type'] == ObservationZoneType.CYLINDER:
            assert 'radius' in kw

        elif kw['type'] == ObservationZoneType.SECTOR:
            assert 'radius' in kw
            assert 'start_radial' in kw
            assert 'end_radial' in kw

        elif kw['type'] == ObservationZoneType.SYMMETRIC_QUADRANT:
            assert 'radius' in kw

        elif kw['type'] == ObservationZoneType.CUSTOM_KEYHOLE:
            assert 'radius' in kw
            assert 'inner_radius' in kw
            assert 'angle' in kw

        self.write_tag('ObservationZone', **kw)
