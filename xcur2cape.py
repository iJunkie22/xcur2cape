import numbers
import plistlib
import time
import os
import base64


class CapeObject(object):
    def __init__(self):
        self.author = os.getenv("LOGNAME")
        self.capename = "Untitled"
        self._version = float(2).real
        self.cape_version = float(1).real
        self.isRetina = False
        self.tstamp = time.time()
        self.cursors = {}

    def export_dict(self):
        d1 = {}
        d1['Author'] = self.author
        d1['CapeName'] = self.capename
        d1['Cloud'] = False
        d1['CapeVersion'] = self.cape_version
        d1['Version'] = self._version
        d1['HiDPI'] = self.isRetina
        d1['MinimumVersion'] = self._version
        d1['Identifier'] = "local.{}.{}.{}".format(self.author, self.capename, str(self.tstamp))
        return d1


class CapeCursor(object):
    def __init__(self):
        self.namekey = ""
        self.frame_counnt = 1
        self.frame_duration = float(1).real
        self.hotspotx = float(0.0).real
        self.hotspoty = float(0.0).real
        self.height = float(32).real
        self.width = float(32).real
        self.images = []

    def add_img(self, img_fn):
        with open(img_fn, 'rb') as img_fd:
            self.images.append(base64.b64encode(img_fd.read()))

    def export_dict(self):
        d2 = {}
        return d2


class XCursor(object):
    def __init__(self):
        pass


