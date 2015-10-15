import datetime


class Uptime(object):
    def __init__(self):
        self.start_time = datetime.datetime.now()

    def uptime(self):
        return datetime.datetime.now() - self.start_time

    def uptime_str(self):
        td = self.uptime()
        s = ''
        if td.days > 0:
            s = '%sd' % td.days

        secs = td.seconds
        hours = secs / (60 * 60)
        if hours > 0:
            s += '%sh' % hours
            secs = secs - (hours * 60 * 60)

        mins = secs / 60
        if mins > 0:
            s += '%sm' % mins
            secs = secs - (mins * 60)

        s += '%ss' % secs
        return s
