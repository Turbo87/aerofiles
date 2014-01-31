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
