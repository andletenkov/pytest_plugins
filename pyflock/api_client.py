import requests


# TODO: add proper report link rendering
def send_results(hook_id, summary):
    """Send test results to Flock via web hook."""
    url = f"https://api.flock.com/hooks/sendMessage/{hook_id}"
    return requests.post(url, json={
        "flockml": f"""<flockml><b>Hi! I'm a test result bot! :robot_face:</b>
            <u>Test results:</u>
            Collected: {summary.total}
            Executed: {summary.executed}
            Passed: {summary.passed}
            Failed: {summary.failed}
            Skipped: {summary.skipped}
            Expected to fail: {summary.xfailed} ({summary.xpassed} passed)
            Duration: {summary.duration} sec

            <u>{summary.status}</u>
            <a href="https://www.google.com/">Link to report</a>
            </flockml>"""
    })
