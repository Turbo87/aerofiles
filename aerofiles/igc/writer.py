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

    def write_logger_id(self, manufacturer, logger_id, extension=None):
        if not patterns.MANUFACTURER_CODE.match(manufacturer):
            raise ValueError('Invalid manufacturer code')
        if not patterns.LOGGER_ID.match(logger_id):
            raise ValueError('Invalid logger id')

        line = 'A%s%s' % (manufacturer, logger_id)
        if extension:
            line = line + extension

        self.write_line(line)

    def write_header(self, type, value):
        self.write_line('H%s%s' % (type, value))

    def write_date(self, date):
        self.write_header('FDTE', date.strftime('%y%m%d'))
