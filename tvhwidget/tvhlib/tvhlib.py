from datetime import datetime
import os
import requests


UPCOMING_RECORDINGS = "/dvr/entry/grid_upcoming"
TUNER_STATUS = "/status/inputs"

STATUS_INFO = [("Bit error rate", "ber"),
               ("Continuity errors", "cc"),
               ("Bit error count", "ec_bit"),
               ("Block error count", "ec_block"),
               ("Transport errors", "te")]


class TimeOut(Exception):
    pass


class TVHJobServer(object):

    def __init__(self, host=None, auth=None, timeout=5):
        self.host = host
        self.auth = auth
        self.timeout = timeout

    def _send_api_request(self, path, args=None):
        url = self.host + path
        try:
            r = requests.post(url,
                              data=args,
                              auth=self.auth,
                              timeout=self.timeout)
            return r.json(strict=False)
        except (requests.exceptions.Timeout, requests.ConnectionError):
            raise TimeOut()

    def _tidy_prog(self, prog, uuid=None):

        x = prog

        return {"subtitle": x["disp_subtitle"],
                "title": x["disp_title"],
                "start_epoch": x["start"],
                "stop_epoch": x["stop"],
                "start": datetime.fromtimestamp(x["start"]),
                "stop": datetime.fromtimestamp(x["stop"]),
                "filename": x["filename"],
                "basename": os.path.basename(x["filename"]),
                "creator": x["creator"],
                "channelname": x["channelname"],
                "error": x["errorcode"],
                "uuid": uuid if uuid else x["uuid"],
                "duplicate": x.get("duplicate", 0) > 0}

    def get_upcoming(self, hide_duplicates=True):
        programmes = self._send_api_request(UPCOMING_RECORDINGS)
        programmes = [self._tidy_prog(x) for x in programmes["entries"]]
        programmes = sorted(programmes, key=lambda x: x["start_epoch"])
        if hide_duplicates:
            programmes = [p for p in programmes if not p["duplicate"]]
        return programmes

    def get_tuner_status(self):
        return self._send_api_request(TUNER_STATUS).get("entries", list())
