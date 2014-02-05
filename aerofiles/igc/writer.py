import datetime

from aerofiles.igc import patterns


class Writer:
    """
    A writer for the IGC flight log file format.

    see http://www.fai.org/gnss-recording-devices/igc-approved-flight-recorders
    or http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html
    """

    REQUIRED_HEADERS = [
        'manufacturer_code',
        'logger_id',
        'date',
        'logger_type',
        'gps_receiver',
    ]

    def __init__(self, fp=None):
        self.fp = fp

    def write_line(self, line):
        self.fp.write(line + '\r\n')

    def write_record(self, type, record):
        self.write_line(type + record)

    def write_logger_id(self, manufacturer, logger_id, extension=None,
                        validate=True):
        """
        Write the manufacturer and logger id header line::

            writer.write_logger_id('XXX', 'ABC', extension='FLIGHT:1')
            # -> AXXXABCFLIGHT:1

        Some older loggers have decimal logger ids which can be written like
        this::

            writer.write_logger_id('FIL', '13961', validate=False)
            # -> AFIL13961

        :param manufacturer: the three-letter-code of the manufacturer
        :param logger_id: the logger id as three-letter-code
        :param extension: anything else that should be appended to this header
            (e.g. ``FLIGHT:1``)
        :param validate: whether to validate the manufacturer and logger_id
            three-letter-codes
        """

        if validate:
            if not patterns.MANUFACTURER_CODE.match(manufacturer):
                raise ValueError('Invalid manufacturer code')
            if not patterns.LOGGER_ID.match(logger_id):
                raise ValueError('Invalid logger id')

        record = '%s%s' % (manufacturer, logger_id)
        if extension:
            record = record + extension

        self.write_record('A', record)

    def write_header(self, source, subtype, value,
                     subtype_long=None, value_long=None):
        if source not in ('F', 'O'):
            raise ValueError('Invalid source')

        if not subtype_long:
            record = '%s%s%s' % (source, subtype, value)
        elif not value_long:
            record = '%s%s%s:%s' % (source, subtype, subtype_long, value)
        else:
            record = '%s%s%s%s:%s' % \
                (source, subtype, value, subtype_long, value_long)

        self.write_record('H', record)

    def write_fr_header(self, subtype, value,
                        subtype_long=None, value_long=None):
        self.write_header(
            'F', subtype, value,
            subtype_long=subtype_long, value_long=value_long
        )

    def write_date(self, date):
        """
        Write the date header::

            writer.write_date(datetime.date(2014, 5, 2))
            # -> HFDTE140502

        :param date: a :class:`datetime.date` instance
        """

        self.write_fr_header('DTE', date.strftime('%d%m%y'))

    def write_fix_accuracy(self, accuracy=None):
        """
        Write the GPS fix accuracy header::

            writer.write_fix_accuracy()
            # -> HFFXA500

            writer.write_fix_accuracy(25)
            # -> HFFXA025

        :param accuracy: the estimated GPS fix accuracy in meters (optional)
        """

        if accuracy is None:
            accuracy = 500

        accuracy = int(accuracy)
        if not 0 < accuracy < 1000:
            raise ValueError('Invalid fix accuracy')

        self.write_fr_header('FXA', '%03d' % accuracy)

    def write_pilot(self, pilot):
        """
        Write the pilot declaration header::

            writer.write_pilot('Tobias Bieniek')
            # -> HFPLTPILOTINCHARGE:Tobias Bieniek

        :param pilot: name of the pilot
        """
        self.write_fr_header('PLT', pilot, subtype_long='PILOTINCHARGE')

    def write_copilot(self, copilot):
        """
        Write the copilot declaration header::

            writer.write_copilot('John Doe')
            # -> HFCM2CREW2:John Doe

        :param copilot: name of the copilot
        """
        self.write_fr_header('CM2', copilot, subtype_long='CREW2')

    def write_glider_type(self, glider_type):
        """
        Write the glider type declaration header::

            writer.write_glider_type('Hornet')
            # -> HFGTYGLIDERTYPE:Hornet

        :param glider_type: the glider type (e.g. ``Hornet``)
        """
        self.write_fr_header('GTY', glider_type, subtype_long='GLIDERTYPE')

    def write_glider_id(self, glider_id):
        """
        Write the glider id declaration header::

            writer.write_glider_id('D-4449')
            # -> HFGIDGLIDERID:D-4449

        The glider id is usually the official registration number of the
        airplane. For example:``D-4449`` or ``N116EL``.

        :param glider_id: the glider registration number
        """
        self.write_fr_header('GID', glider_id, subtype_long='GLIDERID')

    def write_gps_datum(self, code=None, gps_datum=None):
        """
        Write the mandatory GPS datum header::

            writer.write_gps_datum()
            # -> HFDTM100GPSDATUM:WGS-1984

            writer.write_gps_datum(33, 'Guam-1963')
            # -> HFDTM033GPSDATUM:Guam-1963

        Note that the default GPS datum is WGS-1984 and you should use that
        unless you have very good reasons against it.

        :param code: the GPS datum code as defined in the IGC file
            specification, section A8
        :param gps_datum: the GPS datum in written form
        """

        if code is None:
            code = 100

        if gps_datum is None:
            gps_datum = 'WGS-1984'

        self.write_fr_header(
            'DTM',
            '%03d' % code,
            subtype_long='GPSDATUM',
            value_long=gps_datum,
        )

    def write_firmware_version(self, firmware_version):
        """
        Write the firmware version header::

            writer.write_firmware_version('6.4')
            # -> HFRFWFIRMWAREVERSION:6.4

        :param firmware_version: the firmware version of the flight recorder
        """
        self.write_fr_header(
            'RFW', firmware_version, subtype_long='FIRMWAREVERSION')

    def write_hardware_version(self, hardware_version):
        """
        Write the hardware version header::

            writer.write_hardware_version('1.2')
            # -> HFRHWHARDWAREVERSION:1.2

        :param hardware_version: the hardware version of the flight recorder
        """
        self.write_fr_header(
            'RHW', hardware_version, subtype_long='HARDWAREVERSION')

    def write_logger_type(self, logger_type):
        """
        Write the extended logger type header::

            writer.write_logger_type('Flarm-IGC')
            # -> HFFTYFRTYPE:Flarm-IGC

        :param logger_type: the extended type information of the flight
            recorder
        """
        self.write_fr_header('FTY', logger_type, subtype_long='FRTYPE')

    def write_gps_receiver(self, gps_receiver):
        """
        Write the GPS receiver header::

            writer.write_gps_receiver('uBLOX LEA-4S-2,16,max9000m')
            # -> HFGPSuBLOX LEA-4S-2,16,max9000m

        :param gps_receiver: the GPS receiver information
        """
        self.write_fr_header('GPS', gps_receiver)

    def write_pressure_sensor(self, pressure_sensor):
        """
        Write the pressure sensor header::

            writer.write_pressure_sensor('Intersema MS5534B,8191')
            # -> HFPRSPRESSALTSENSOR:Intersema MS5534B,8191

        :param pressure_sensor: the pressure sensor information
        """
        self.write_fr_header(
            'PRS', pressure_sensor, subtype_long='PRESSALTSENSOR')

    def write_competition_id(self, competition_id):
        """
        Write the optional competition id declaration header::

            writer.write_competition_id('TH')
            # -> HFCIDCOMPETITIONID:TH

        :param competition_id: competition id of the glider
        """
        self.write_fr_header(
            'CID', competition_id, subtype_long='COMPETITIONID')

    def write_competition_class(self, competition_class):
        """
        Write the optional competition class declaration header::

            writer.write_competition_class('Club')
            # -> HFCCLCOMPETITIONCLASS:Club

        :param competition_class: competition class of the glider
        """
        self.write_fr_header(
            'CCL', competition_class, subtype_long='COMPETITIONCLASS')

    def write_club(self, club):
        """
        Write the optional club declaration header::

            writer.write_club('LV Aachen')
            # -> HFCLBCLUB:LV Aachen

        :param club: club or organisation for which this flight should be
            scored
        """
        self.write_fr_header('CLB', club, subtype_long='CLUB')

    def write_headers(self, headers):
        """
        Write all the necessary headers in the correct order::

            writer.write_headers({
                'manufacturer_code': 'XCS',
                'logger_id': 'TBX',
                'date': datetime.date(1987, 2, 24),
                'fix_accuracy': 50,
                'pilot': 'Tobias Bieniek',
                'copilot': 'John Doe',
                'glider_type': 'Duo Discus',
                'glider_id': 'D-KKHH',
                'firmware_version': '2.2',
                'hardware_version': '2',
                'logger_type': 'LXNAVIGATION,LX8000F',
                'gps_receiver': 'uBLOX LEA-4S-2,16,max9000m',
                'pressure_sensor': 'INTERSEMA,MS5534A,max10000m',
                'competition_id': '2H',
                'competition_class': 'Doubleseater',
            })

            # -> AXCSTBX
            # -> HFDTE870224
            # -> HFFXA050
            # -> HFPLTPILOTINCHARGE:Tobias Bieniek
            # -> HFCM2CREW2:John Doe
            # -> HFGTYGLIDERTYPE:Duo Discus
            # -> HFGIDGLIDERID:D-KKHH
            # -> HFDTM100GPSDATUM:WGS-1984
            # -> HFRFWFIRMWAREVERSION:2.2
            # -> HFRHWHARDWAREVERSION:2
            # -> HFFTYFRTYPE:LXNAVIGATION,LX8000F
            # -> HFGPSuBLOX LEA-4S-2,16,max9000m
            # -> HFPRSPRESSALTSENSOR:INTERSEMA,MS5534A,max10000m
            # -> HFCIDCOMPETITIONID:2H
            # -> HFCCLCOMPETITIONCLASS:Doubleseater

        This method will throw a :class:`ValueError` if a mandatory header is
        missing and will fill others up with empty strings if no value was
        given. The optional headers are only written if they are part of the
        specified :class:`dict`.

        .. admonition:: Note

            The use of this method is encouraged compared to calling all the
            other header-writing methods manually!

        :param headers: a :class:`dict` of all the headers that should be
            written.
        """

        for header in self.REQUIRED_HEADERS:
            if not header in headers:
                raise ValueError('%s header missing' % header)

        self.write_logger_id(
            headers['manufacturer_code'],
            headers['logger_id'],
            extension=headers.get('logger_id_extension')
        )

        self.write_date(headers['date'])
        self.write_fix_accuracy(headers.get('fix_accuracy'))

        self.write_pilot(headers.get('pilot', ''))
        if 'copilot' in headers:
            self.write_copilot(headers['copilot'])

        self.write_glider_type(headers.get('glider_type', ''))
        self.write_glider_id(headers.get('glider_id', ''))

        self.write_gps_datum(
            code=headers.get('gps_datum_code'),
            gps_datum=headers.get('gps_datum'),
        )

        self.write_firmware_version(headers.get('firmware_version', ''))
        self.write_hardware_version(headers.get('hardware_version', ''))
        self.write_logger_type(headers['logger_type'])
        self.write_gps_receiver(headers['gps_receiver'])
        self.write_pressure_sensor(headers.get('pressure_sensor', ''))

        if 'competition_id' in headers:
            self.write_competition_id(headers['competition_id'])

        if 'competition_class' in headers:
            self.write_competition_class(headers['competition_class'])

        if 'club' in headers:
            self.write_club(headers['club'])

    def write_extensions(self, type, start_byte, extensions):
        num_extensions = len(extensions)
        if num_extensions >= 100:
            raise ValueError('Invalid number of extensions')

        record = '%02d' % num_extensions
        for extension, length in extensions:
            if not patterns.EXTENSION_CODE.match(extension):
                raise ValueError('Invalid extension: %s' % extension)

            end_byte = start_byte + length - 1
            record += '%02d%02d%s' % (start_byte, end_byte, extension)

            start_byte = start_byte + length

        self.write_record(type, record)

    def write_fix_extensions(self, extensions):
        """
        Write the fix extensions description header::

            writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])
            # -> I033638FXA3940SIU4143ENL

        :param extensions: a list of ``(extension, length)`` tuples
        """
        self.write_extensions('I', 36, extensions)

    def write_k_record_extensions(self, extensions):
        """
        Write the K record extensions description header::

            writer.write_k_record_extensions([('HDT', 5)])
            # -> J010812HDT

        :param extensions: a list of ``(extension, length)`` tuples
        """
        self.write_extensions('J', 8, extensions)

    def write_task_metadata(
            self, declaration_datetime=None, flight_date=None,
            task_number=None, turnpoints=None, text=None):
        """
        Write the task declaration metadata record::

            writer.write_task_metadata(
                datetime.datetime(2014, 4, 13, 12, 53, 02),
                task_number=42,
                turnpoints=3,
            )
            # -> C140413125302000000004203

        There are sensible defaults in place for all parameters except for the
        ``turnpoints`` parameter. If you don't pass that parameter the method
        will raise a :class:`ValueError`. The other parameter defaults are
        mentioned in the list below.

        :param declaration_datetime: a :class:`datetime.datetime` instance of
            the UTC date and time at the time of declaration (default: current
            date and time)
        :param flight_date: a :class:`datetime.date` instance of the intended
            date of the flight (default: ``000000``, which means "use
            declaration date")
        :param task_number: task number for the flight date or an integer-based
            identifier (default: ``0001``)
        :param turnpoints: the number of turnpoints in the task (not counting
            start and finish points!)
        :param text: optional text to append to the metadata record
        """

        if declaration_datetime is None:
            declaration_datetime = datetime.datetime.utcnow()

        if isinstance(declaration_datetime, datetime.datetime):
            declaration_datetime = \
                declaration_datetime.strftime('%d%m%y%H%M%S')
        elif not patterns.DATETIME.match(declaration_datetime):
            raise ValueError('Invalid declaration datetime')

        if isinstance(flight_date, datetime.date):
            flight_date = flight_date.strftime('%d%m%y')

        if flight_date is None:
            flight_date = '000000'
        elif not patterns.DATE.match(flight_date):
            raise ValueError('Invalid flight date')

        if task_number is None:
            task_number = 1
        elif not isinstance(task_number, int):
            raise ValueError('task number parameter must be an integer')

        if turnpoints is None:
            raise ValueError('turnpoints parameter must be set')
        elif not isinstance(turnpoints, int):
            raise ValueError('turnpoints parameter must be an integer')

        record = '{0}{1}{2:04d}{3:02d}'.format(
            declaration_datetime,
            flight_date,
            task_number,
            turnpoints,
        )

        if text:
            record += text

        self.write_record('C', record)

    def write_task_point(self, latitude=None, longitude=None, text=''):
        """
        Write a task declaration point::

            writer.write_task_point(
                latitude=(51 + 7.345 / 60.),
                longitude=(6 + 24.765 / 60.),
                text='Meiersberg',
            )
            # -> C5107345N00624765EMeiersberg

        If no ``latitude`` or ``longitude`` is passed, the fields will be
        filled with zeros (i.e. unknown coordinates). This however should only
        be used for ``TAKEOFF``  and ``LANDING`` points.

        :param latitude: latitude of the point (between -90 and 90 degrees)
        :param longitude: longitude of the point (between -180 and 180 degrees)
        :param text: type and/or name of the waypoint (e.g. ``TAKEOFF``,
            ``START``, ``TURN 1``, ``TURN 2``, ``FINISH`` or ``LANDING``)
        """

        if latitude is None:
            latitude = '0000000N'
        else:
            if not -90 <= latitude <= 90:
                raise ValueError('Invalid latitude')

            hemisphere = 'S' if latitude < 0 else 'N'

            latitude = abs(latitude)
            degrees = int(latitude)
            milliminutes = round((latitude - degrees) * 60000)
            latitude = '%02d%05d%s' % (degrees, milliminutes, hemisphere)

        if longitude is None:
            longitude = '00000000E'
        else:
            if not -180 <= longitude <= 180:
                raise ValueError('Invalid longitude')

            hemisphere = 'W' if longitude < 0 else 'E'

            longitude = abs(longitude)
            degrees = int(longitude)
            milliminutes = round((longitude - degrees) * 60000)
            longitude = '%03d%05d%s' % (degrees, milliminutes, hemisphere)

        record = latitude + longitude
        if text:
            record += text

        self.write_record('C', record)

    def write_task_points(self, points):
        """
        Write multiple task declaration points with one call::

            writer.write_task_points([
                (None, None, 'TAKEOFF'),
                (51.40375, 6.41275, 'START'),
                (50.38210, 8.82105, 'TURN 1'),
                (50.59045, 7.03555, 'TURN 2'),
                (51.40375, 6.41275, 'FINISH'),
                (None, None, 'LANDING'),
            ])
            # -> C0000000N00000000ETAKEOFF
            # -> C5124225N00624765ESTART
            # -> C5022926N00849263ETURN 1
            # -> C5035427N00702133ETURN 2
            # -> C5124225N00624765EFINISH
            # -> C0000000N00000000ELANDING

        see the :meth:`~aerofiles.igc.Writer.write_task_point` method for more
        information.

        :param points: a list of ``(latitude, longitude, text)`` tuples
        """
        for latitude, longitude, text in points:
            self.write_task_point(latitude, longitude, text)
