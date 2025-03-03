import datetime


class TimeZoneFix(datetime.tzinfo):
    """
    A simple implementation of tzinfo to store timezone of IGC fixes.

    An alternative would be, to use "timezone" which is part of
    Python since v3.2. However, because we try to be python 2.6+
    compatible, we use this implementation. It can be replaced,
    if we set Python 3.x as a minimum requirement for aerofiles.
    """

    def __init__(self, fix=0):
        self.fix = fix

    def __eq__(self, other):
        if isinstance(other, TimeZoneFix):
            return self.fix == other.fix
        return NotImplemented

    def __hash__(self):
        return hash(self.fix)

    def __repr__(self):
        """Convert to formal string, for repr().
        """
        return "%s.%s(%r)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              self.fix)

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self.fix)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return str(self.fix)
