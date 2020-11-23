from datetime import datetime
from queue import Queue, Empty
from threading import Thread
from requests.auth import HTTPBasicAuth

from libqtile.widget import base
from libqtile import bar, images
from libqtile.log_utils import logger
from libqtile.popup import Popup

from .tvhlib import TVHJobServer, TVHTimeOut, ICON_PATH, ICONS


class TVHWidget(base._Widget, base.MarginMixin):

    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("refresh_interval", 30, "Time to update data"),
        ("startup_delay", 5, "Time before sending first web request"),
        ("host", "http://localhost:9981/api", "TVHeadend server address"),
        ("auth", None, "Auth details for accessing tvh. "
                       "Can be None, tuple of (username, password)."),
        ("tvh_timeout", 5, "Seconds before timeout for timeout request"),
        ("popup_format", "{start:%a %d %b %H:%M}: {title:.40}",
                         "Upcoming recording text."),
        ("popup_display_timeout", 10, "Seconds to show recordings."),
        ("warning_colour", "aaaa00", "Highlight when there is an error."),
        ("recording_colour", "bb0000", "Highlight when TVHeadend is recording")
    ]

    def __init__(self, **config):
        base._Widget.__init__(self, bar.CALCULATED, **config)
        self.add_defaults(TVHWidget.defaults)
        self.add_defaults(base.MarginMixin.defaults)
        self.data = []
        self.surfaces = {}
        self.iconsize = 0

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)
        self.setup_images()

        if type(self.auth) == tuple:
            self.auth = HTTPBasicAuth(*self.auth)

        self.tvh = TVHJobServer(host=self.host,
                                auth=self.auth,
                                timeout=self.tvh_timeout)

        self.timeout_add(self.startup_delay, self.refresh)

    def _get_data(self, queue=None):
        try:
            data = self.tvh.get_upcoming()
        except TVHTimeOut:
            logger.warning("Couldn't connect to TVH server")
            data = []

        queue.put(data)

    def _wait_for_data(self):
        try:
            data = self._queue.get(False)
            self._read_data(data)
        except Empty:
            self.timeout_add(1, self._wait_for_data)

    def _read_data(self, data):
        self.data = data

        self.timeout_add(1, self.draw)
        self.timeout_add(self.refresh_interval, self.refresh)

    def setup_images(self):
        d_images = images.Loader(ICON_PATH)(*ICONS)

        for name, img in d_images.items():
            new_height = self.bar.height - 1
            img.resize(height=new_height)
            self.iconsize = img.width
            self.surfaces[name] = img.pattern

    def refresh(self):
        self._queue = Queue()
        kwargs = {"queue": self._queue}
        self.worker = Thread(target=self._get_data, kwargs=kwargs)
        self.worker.daemon = True
        self.worker.start()
        self._wait_for_data()

    def set_refresh_timer(self):
        pass

    def calculate_length(self):
        return self.iconsize

    def draw_highlight(self, top=False, colour="000000"):

        self.drawer.set_source_rgb(colour)

        y = 0 if top else self.bar.height - 2

        # Draw the bar
        self.drawer.fillrect(0,
                             y,
                             self.width,
                             2,
                             2)

    def draw(self):
        # Remove background
        self.drawer.clear(self.background or self.bar.background)

        self.drawer.ctx.set_source(self.surfaces["icon"])
        self.drawer.ctx.paint()

        if not self.data:
            self.draw_highlight(top=True, colour=self.warning_colour)

        elif self.is_recording:
            self.draw_highlight(top=False, colour=self.recording_colour)

        self.drawer.draw(offsetx=self.offset, width=self.length)

    def button_press(self, x, y, button):
        self.show_recs()

    @property
    def is_recording(self):
        if not self.data:
            return False

        dtnow = datetime.now()

        for prog in self.data:
            if prog["start"] <= dtnow <= prog["stop"]:
                return True

        return False

    def mouse_enter(self, x, y):
        pass

    def show_recs(self):
        lines = []

        if not self.data:
            lines.append("No upcoming recordings.")

        else:
            lines.append("Upcoming recordings:")
            for rec in self.data:
                lines.append(self.popup_format.format(**rec))

        self.popup = Popup(self.qtile,
                           y=self.bar.height,
                           width=900,
                           height=900,
                           font="monospace",
                           horizontal_padding=10,
                           vertical_padding=10,
                           opacity=0.8)
        self.popup.text = "\n".join(lines)
        self.popup.height = (self.popup.layout.height +
                             (2 * self.popup.vertical_padding))
        self.popup.width = (self.popup.layout.width +
                            (2 * self.popup.horizontal_padding))
        self.popup.x = min(self.offsetx, self.bar.width - self.popup.width)
        self.popup.place()
        self.popup.draw_text()
        self.popup.unhide()
        self.popup.draw()
        self.timeout_add(self.popup_display_timeout, self.popup.kill)
