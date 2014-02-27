
class Writer:

    """
    A writer for the Flarm configuration file format.

    see http://flarm.de/support/manual/FLARM_DataportManual_v6.00E.pdf

    Example:
    http://www.ftv-spandau.de/streckenfluege/flarm-informationen/flarmcfg.txt
    """

    def __init__(self, fp=None):
        self.fp = fp

    def write_line(self, line):
        self.fp.write(line + '\r\n')

    def write_config(self, key, value):
        self.write_line('$PFLAC,S,%s,%s' % (key, value))
