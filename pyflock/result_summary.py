import time

EXIT_CODES = {
    0: "Passed :money_mouth_face:",
    1: "Failed :disappointed_relieved:",
    2: "Interrupted :face_with_raised_eyebrow:",
    3: "Error :rage:",
    4: "Pytest error :face_with_thermometer:",
    5: "No tests :hole:"
}


class ResultSummary(object):
    """
    Test results summary object to to send via hook.
    """

    def __init__(self):
        self._reporter = None
        self._status = None
        self._start_time = time.time()

    @property
    def reporter(self):
        return self._reporter

    @reporter.setter
    def reporter(self, tr):
        self._reporter = tr

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, es):
        self._status = EXIT_CODES.get(es)

    @property
    def passed(self):
        return len(self._reporter.stats.get("passed", []))

    @property
    def failed(self):
        return len(self._reporter.stats.get("failed", []))

    @property
    def skipped(self):
        return len(self._reporter.stats.get("skipped", []))

    @property
    def xpassed(self):
        return len(self._reporter.stats.get("xpassed", []))

    @property
    def xfailed(self):
        return len(self._reporter.stats.get("xfailed", []))

    @property
    def errors(self):
        return len(self._reporter.stats.get("errors", []))

    @property
    def total(self):
        return self.passed + self.failed + self.skipped + self.xpassed + self.xfailed + self.errors

    @property
    def executed(self):
        return self.total - self.skipped

    @property
    def duration(self):
        return round(time.time() - self._start_time, 2)
