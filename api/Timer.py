import datetime


class Timer:

    def __init__(self, seconds):
        self.start_time = None
        self.seconds = seconds

    def start(self):
        self.start_time = datetime.datetime.now()

    def expired(self):
        if self.start_time is None:
            return True

        elapsed_time = datetime.datetime.now() - self.start_time
        return elapsed_time.seconds >= self.seconds
