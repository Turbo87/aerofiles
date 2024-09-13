
class Writer:

    """
    A writer for the Flarm configuration file format::

        with open('flarmcfg.txt', 'w') as fp:
            writer = Writer(fp)

    see `FTD-14 FLARM Configuration Specification
    <https://www.flarm.com/de/support/downloads/>`.
    """

    def __init__(self, fp=None):
        self.fp = fp

    def format_coordinate(self, value, default=None, is_latitude=True):
        if value is None:
            return default

        if is_latitude:
            if not -90 <= value <= 90:
                raise ValueError('Invalid latitude: %s' % value)

            hemisphere = 'S' if value < 0 else 'N'
            format = '%02d%05d%s'

        else:
            if not -180 <= value <= 180:
                raise ValueError('Invalid longitude: %s' % value)

            hemisphere = 'W' if value < 0 else 'E'
            format = '%03d%05d%s'

        value = abs(value)
        degrees = int(value)
        milliminutes = round((value - degrees) * 60000)
        return format % (degrees, milliminutes, hemisphere)

    def format_latitude(self, value):
        return self.format_coordinate(
            value, default='0000000N', is_latitude=True)

    def format_longitude(self, value):
        return self.format_coordinate(
            value, default='00000000E', is_latitude=False)

    def write_line(self, line):
        self.fp.write((line + u'\r\n').encode('ascii', 'replace'))

    def write_config(self, key, value):
        self.write_line('$PFLAC,S,%s,%s' % (key, value))

    def write_pilot(self, pilot):
        """
        Write the pilot name configuration::

            writer.write_pilot('Tobias Bieniek')
            # -> $PFLAC,S,PILOT,Tobias Bieniek

        :param pilot: name of the pilot
        """
        self.write_config('PILOT', pilot)

    def write_copilot(self, copilot):
        """
        Write the copilot name configuration::

            writer.write_copilot('John Doe')
            # -> $PFLAC,S,COPIL,John Doe

        :param copilot: name of the copilot
        """
        self.write_config('COPIL', copilot)

    def write_glider_type(self, glider_type):
        """
        Write the glider type configuration::

            writer.write_glider_type('Hornet')
            # -> $PFLAC,S,GLIDERTYPE,Hornet

        :param glider_type: the type of glider
        """
        self.write_config('GLIDERTYPE', glider_type)

    def write_glider_id(self, glider_id):
        """
        Write the glider registration configuration::

            writer.write_glider_id('D-4449')
            # -> $PFLAC,S,GLIDERID,D-4449

        :param glider_id: the registration of the glider
        """
        self.write_config('GLIDERID', glider_id)

    def write_competition_id(self, competition_id):
        """
        Write the competition id configuration::

            writer.write_competition_id('TH')
            # -> $PFLAC,S,COMPID,TH

        :param competition_id: competition id of the glider
        """
        self.write_config('COMPID', competition_id)

    def write_competition_class(self, competition_class):
        """
        Write the competition class configuration::

            writer.write_competition_class('Club')
            # -> $PFLAC,S,COMPCLASS,Club

        :param competition_class: competition class of the glider
        """
        self.write_config('COMPCLASS', competition_class)

    def write_logger_interval(self, interval):
        """
        Write the logger interval configuration::

            writer.write_logger_interval(4)
            # -> $PFLAC,S,LOGINT,4

        :param interval: competition class of the glider
        """
        self.write_config('LOGINT', str(interval))

    def write_task_declaration(self, description=None):
        """
        Start a new task declaration. Any old task declaration will be cleared
        by this command::

            writer.write_task_declaration('My Task')
            # -> $PFLAC,S,NEWTASK,My Task

        :param description: optional text description of task, e.g.
            "500km triangle"; can be an empty string; will be trimmed to
            50 characters
        """
        if not description:
            description = ''

        self.write_config('NEWTASK', description[0:50])

    def write_waypoint(self, latitude=None, longitude=None, description=None):
        """
        Adds a waypoint to the current task declaration. The first and the
        last waypoint added will be treated as takeoff and landing location,
        respectively.

        ::

            writer.write_waypoint(
                latitude=(51 + 7.345 / 60.),
                longitude=(6 + 24.765 / 60.),
                text='Meiersberg',
            )
            # -> $PFLAC,S,ADDWP,5107345N,00624765E,Meiersberg

        If no ``latitude`` or ``longitude`` is passed, the fields will be
        filled with zeros (i.e. unknown coordinates). This however should only
        be used for takeoff  and landing points.

        :param latitude: latitude of the point (between -90 and 90 degrees)
        :param longitude: longitude of the point (between -180 and 180 degrees)
        :param description: arbitrary text description of waypoint
        """

        if not description:
            description = ''

        latitude = self.format_latitude(latitude)
        longitude = self.format_longitude(longitude)

        self.write_config(
            'ADDWP', '%s,%s,%s' % (latitude, longitude, description[0:50])
        )

    def write_waypoints(self, points):
        """
        Write multiple task declaration points with one call::

            writer.write_waypoints([
                (None, None, 'TAKEOFF'),
                (51.40375, 6.41275, 'START'),
                (50.38210, 8.82105, 'TURN 1'),
                (50.59045, 7.03555, 'TURN 2'),
                (51.40375, 6.41275, 'FINISH'),
                (None, None, 'LANDING'),
            ])
            # -> $PFLAC,S,ADDWP,0000000N,00000000E,TAKEOFF
            # -> $PFLAC,S,ADDWP,5124225N,00624765E,START
            # -> $PFLAC,S,ADDWP,5022926N,00849263E,TURN 1
            # -> $PFLAC,S,ADDWP,5035427N,00702133E,TURN 2
            # -> $PFLAC,S,ADDWP,5124225N,00624765E,FINISH
            # -> $PFLAC,S,ADDWP,0000000N,00000000E,LANDING

        see the :meth:`~aerofiles.flarmcfg.Writer.write_waypoint` method for
        more information.

        :param points: a list of ``(latitude, longitude, text)`` tuples.
        """
        for args in points:
            if len(args) != 3:
                raise ValueError('Invalid number of task point tuple items')

            self.write_waypoint(*args)
