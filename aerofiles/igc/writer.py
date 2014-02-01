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
        self.write_fr_header('DTE', date.strftime('%y%m%d'))

    def write_fix_accuracy(self, accuracy=None):
        if accuracy is None:
            accuracy = 500

        accuracy = int(accuracy)
        if not 0 < accuracy < 1000:
            raise ValueError('Invalid fix accuracy')

        self.write_fr_header('FXA', '%03d' % accuracy)

    def write_pilot(self, pilot):
        self.write_fr_header('PLT', pilot, subtype_long='PILOTINCHARGE')

    def write_copilot(self, copilot):
        self.write_fr_header('CM2', copilot, subtype_long='CREW2')

    def write_glider_type(self, glider_type):
        self.write_fr_header('GTY', glider_type, subtype_long='GLIDERTYPE')

    def write_glider_id(self, glider_id):
        self.write_fr_header('GID', glider_id, subtype_long='GLIDERID')

    def write_gps_datum(self, code=None, gps_datum=None):
        if code is None:
            code = 100

        if gps_datum is None:
            gps_datum = 'WGS-1984'

        self.write_fr_header(
            'DTM', code, subtype_long='GPSDATUM', value_long=gps_datum)

    def write_firmware_version(self, firmware_version):
        self.write_fr_header(
            'RFW', firmware_version, subtype_long='FIRMWAREVERSION')

    def write_hardware_version(self, hardware_version):
        self.write_fr_header(
            'RHW', hardware_version, subtype_long='HARDWAREVERSION')

    def write_logger_type(self, logger_type):
        self.write_fr_header('FTY', logger_type, subtype_long='FRTYPE')

    def write_gps_receiver(self, gps_receiver):
        self.write_fr_header('GPS', gps_receiver)

    def write_pressure_sensor(self, pressure_sensor):
        self.write_fr_header(
            'PRS', pressure_sensor, subtype_long='PRESSALTSENSOR')

    def write_competition_id(self, competition_id):
        self.write_fr_header(
            'CID', competition_id, subtype_long='COMPETITIONID')

    def write_competition_class(self, competition_class):
        self.write_fr_header(
            'CCL', competition_class, subtype_long='COMPETITIONCLASS')

    def write_club(self, club):
        self.write_fr_header('CLB', club, subtype_long='CLUB')

    def write_headers(self, headers):
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

    def write_fix_extensions(self, extensions):
        num_extensions = len(extensions)
        if num_extensions >= 100:
            raise ValueError('Invalid number of extensions')

        record = '%02d' % num_extensions
        start_byte = 36
        for extension, length in extensions:
            if not patterns.EXTENSION_CODE.match(extension):
                raise ValueError('Invalid extension: %s' % extension)

            end_byte = start_byte + length - 1
            record += '%02d%02d%s' % (start_byte, end_byte, extension)

            start_byte = start_byte + length

        self.write_record('I', record)
