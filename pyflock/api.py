import requests


class FlockAPIClient(object):
    """
    Flock REST API client for sending data via webhooks
    """

    def __init__(self, hook_id, job_id):
        self.hook = f"https://api.flock.com/hooks/sendMessage/{hook_id}"
        self.job_id = "#" + job_id if job_id else ""

    def on_start(self, owner, ci_url):
        """Sends notification with session info when test execution starts"""
        owner = "by" + owner if owner else ""
        ci_url = f"<a href='{ci_url}'>{ci_url}</a>" if ci_url else "locally"

        r = requests.post(self.hook, json={
            "flockml": f"""<flockml><b>STARTED</b> test execution {self.job_id} | {ci_url} | {owner}</flockml>"""
        })
        return r

    def send_results(self, summary):
        """Send test results to Flock whet test execution ends"""
        r = requests.post(self.hook, json={
            "flockml": f"""<flockml><b>SUCCEED</b> test execution {self.job_id}
            <u>Results:</u>
            Collected: {summary.total}
            Executed: {summary.executed}
            Passed: {summary.passed}
            Failed: {summary.failed}
            Skipped: {summary.skipped}
            Expected to fail: {summary.xfailed} ({summary.xpassed} passed)
            Duration: {summary.duration} sec

            <u>{summary.status}</u>
            <a href="{summary.report_url}">Link to report</a>
            </flockml>"""
        })
        return r
