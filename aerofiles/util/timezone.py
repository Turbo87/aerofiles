import datetime


class TimeZoneFix(datetime.tzinfo):

    def __init__(self, fix):
        self.fix = fix

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self.fix)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return str(self.fix)
