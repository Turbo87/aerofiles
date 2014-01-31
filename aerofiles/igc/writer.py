from aerofiles.igc import patterns


class Writer:
    """
    A writer for the IGC flight log file format.

    see http://www.fai.org/gnss-recording-devices/igc-approved-flight-recorders
    or http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html
    """

    def __init__(self, fp=None):
        self.fp = fp

    def write_line(self, line):
        self.fp.write(line + '\r\n')

    def write_logger_id(self, manufacturer, logger_id, extension=None,
                        validate=True):
        if validate:
            if not patterns.MANUFACTURER_CODE.match(manufacturer):
                raise ValueError('Invalid manufacturer code')
            if not patterns.LOGGER_ID.match(logger_id):
                raise ValueError('Invalid logger id')

        line = 'A%s%s' % (manufacturer, logger_id)
        if extension:
            line = line + extension

        self.write_line(line)

    def write_header(self, origin, type, value):
        if origin not in ('F', 'O'):
            raise ValueError('Invalid origin')

        self.write_line('H%s%s%s' % (origin, type, value))

    def write_fr_header(self, type, value):
        self.write_header('F', type, value)

    def write_date(self, date):
        self.write_fr_header('DTE', date.strftime('%y%m%d'))
