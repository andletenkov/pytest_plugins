import os
from requests import Session

from logging import error as elog


class AllureServer(object):

    def __init__(self, url):
        self.url = url
        self._session = Session()

    def send_results(self, file_path):
        if not os.path.isfile(file_path):
            elog(f"Can't get ZIP-file by path : '{file_path}'")

        with open(file_path, "rb") as f:
            r = self._session.post(
                f"{self.url}/api/result",
                files={
                    "allureResults": f
                }

            )
        if not r.ok:
            elog(f" Can't send results to server. Invalid response: {r.text}")
            return
        return r.json()["uuid"]

    def get_build_num(self, path):
        r = self._session.get(
            f"{self.url}/api/report?path={path}",
        )

        if not r.ok:
            elog(f"Can't get report by path '{path}'. Invalid response: {r.text}")
            return
        return len(r.json()) + 1

    def generate_report(self, res_uid, path):
        assert isinstance(path, str), f"Path must be str format, got {type(path)}"

        path_as_list = path.split("/")

        r = self._session.post(
            f"{self.url}/api/report",
            json={
                "reportSpec": {
                    "path": path_as_list,
                    "executorInfo": {
                        "buildName": f"#{path_as_list[-1]}"
                    }
                },
                "results": [res_uid],
                "deleteResults": True
            }
        )
        if not r.ok:
            elog(f"Can't generate report. Invalid response: {r.text}")
            return

        report_url = r.json()["url"]
        return report_url
