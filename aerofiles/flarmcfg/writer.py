
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

    def write_pilot(self, pilot):
        """
        Write the pilot name configuration::

            writer.write_pilot('Tobias Bieniek')
            # -> $PFLAC,S,PILOT,Tobias Bieniek

        :param pilot: name of the pilot
        """
        self.write_config('PILOT', pilot)

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
