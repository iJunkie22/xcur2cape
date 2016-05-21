import plistlib
import time
import os
import base64
import xcurnames
import os.path
import subprocess
import shlex


XCUR2PNG_EXECUTABLE = os.path.expanduser('~/Build/xcur2png/xcur2png')


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
        d1['Cursors'] = {}
        for k, v in self.cursors.items():
            assert isinstance(v, CapeCursor)
            d1['Cursors'][k] = v.export_dict()
        return d1

    def add_cursor(self, cc):
        assert isinstance(cc, CapeCursor)
        self.cursors[xcurnames.cursor_name_map[cc.mc_namekey]] = cc

    @classmethod
    def from_theme(cls, xct):
        assert isinstance(xct, XCursorTheme)
        new_co = cls()
        new_co.capename = xct.theme_name
        for xcs in xct.cursors:
            for cc in CapeCursor.from_xcursor_set(xcs, 32):
                new_co.add_cursor(cc)
        return new_co


class CapeCursor(object):
    def __init__(self):
        self.mc_namekey = ""
        self.frame_count = 1
        self.frame_duration = float(1).real
        self.hotspotx = float(0.0).real
        self.hotspoty = float(0.0).real
        self.height = float(32).real
        self.width = float(32).real
        self.images = []

    def add_img(self, img_fn):
        with open(img_fn, 'rb') as img_fd:
            self.images.append(base64.b64encode(img_fd.read()))

    @property
    def has_valid_name(self):
        return self.mc_namekey in xcurnames.cursor_name_map.keys()

    @property
    def plist_namekey(self):
        return xcurnames.cursor_name_map.get(self.mc_namekey)

    def export_dict(self):
        d2 = {}
        d2['FrameCount'] = self.frame_count
        d2['FrameDuration'] = self.frame_duration
        d2['HotSpotX'] = self.hotspotx
        d2['HotSpotY'] = self.hotspoty
        d2['PointsHigh'] = self.height
        d2['PointsWide'] = self.width
        print self.images[0]
        print d2['PointsHigh']
        d2['Representations'] = [plistlib.Data.fromBase64(x) for x in self.images]
        return d2

    @classmethod
    def from_xcursor_set(cls, xcs, chosen_size):
        assert isinstance(xcs, XCursorSet)
        assert isinstance(chosen_size, int)
        for line in [table_line for table_line in xcurnames.name_table if table_line[2] == xcs.xc_name]:
            new_cc = cls()
            for xc in xcs.xcursors:
                assert isinstance(xc, XCursor)
                if xc.img_size == chosen_size:
                    print xc.img_size
                    new_cc.images.append(xc.img_data)
                    new_cc.hotspotx = float(xc.hs_x)
                    new_cc.hotspoty = float(xc.hs_y)
                    new_cc.height = float(xc.img_size)
                    new_cc.width = float(xc.img_size)
            new_cc.mc_namekey = line[1]
            yield new_cc


class XCursorTheme(object):
    def __init__(self):
        self.cursors = []
        self.theme_name = "Untitled"

    @classmethod
    def unpack_theme(cls, theme_fp, xcur2png_exe_fp=XCUR2PNG_EXECUTABLE):
        xct = cls()
        with open(os.path.join(theme_fp, 'index.theme'), 'r') as index_fd:
            for line in index_fd:
                p1, p2, p3 = line.partition("=")
                if p1.startswith("Name"):
                    xct.theme_name = p3.strip().rstrip()
        for xcur_bn in set([x[2] for x in xcurnames.name_table if x[2] != xcurnames.nXCUR]):
            xct.cursors.append(XCursorSet.from_xcur_file(os.path.join(theme_fp, 'cursors', xcur_bn), xcur2png_exe_fp))
        return xct


class XCursorSet(object):
    def __init__(self):
        self.conf_fp = ""
        self.conf_file_str = ""
        self.xcursors = []
        self.xc_name = ""

    @property
    def is_known_xc(self):
        return self.xc_name in [x[2] for x in xcurnames.name_table]

    def unpack_from_conf(self):
        for line in self.conf_file_str.splitlines():
            if not line.startswith("#"):
                self.xcursors.append(XCursor.from_conf_file_line(self.conf_fp, line))

    @classmethod
    def from_conf_file(cls, conf_fp):
        new_xcs = cls()
        new_xcs.conf_fp = conf_fp
        new_xcs.xc_name = new_xcs.conf_fp.rpartition(os.sep)[2].rpartition(".")[0]
        with open(new_xcs.conf_fp, 'r') as conf_fd:
            new_xcs.conf_file_str = conf_fd.read()

        new_xcs.unpack_from_conf()
        return new_xcs

    @classmethod
    def from_xcur_file(cls, xcur_fp, xcur2png_exe_fp=XCUR2PNG_EXECUTABLE):
        ripped_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(xcur_fp)), 'ripped/'))
        if not os.path.isdir(ripped_dir):
            os.mkdir(ripped_dir)
        arg_str = '{} -d {} -c {} {}'.format(xcur2png_exe_fp, ripped_dir, xcur_fp + '.conf', xcur_fp)
        p1 = subprocess.Popen(arg_str, shell=True, stdout=subprocess.PIPE)
        p1.wait()
        return cls.from_conf_file(xcur_fp + '.conf')


class XCursor(object):
    def __init__(self):
        self.img_size = 0
        self.hs_x = 0
        self.hs_y = 0
        self.fp = ""
        self.img_data = ""

    @classmethod
    def from_conf_file_line(cls, conf_fp, conf_line_str):
        new_xc = cls()
        assert isinstance(conf_line_str, str)
        secs = conf_line_str.split()
        new_xc.img_size = int(secs[0])
        new_xc.hs_x = int(secs[1])
        new_xc.hs_y = int(secs[2])
        if not os.path.isabs(secs[3]):
            new_xc.fp = os.path.normpath(os.path.join(conf_fp, secs[3]))
        else:
            new_xc.fp = secs[3]
        with open(new_xc.fp, 'rb') as xcur_fd:
            new_xc.img_data = base64.b64encode(xcur_fd.read())

        return new_xc


test_xct1 = XCursorTheme.unpack_theme(os.path.expanduser('~/Downloads/Breeze-Obsidian/'))
print test_xct1.theme_name
print len(test_xct1.cursors)
test_co1 = CapeObject.from_theme(test_xct1)

test_pl_dict = test_co1.export_dict()
plistlib.writePlist(test_pl_dict, test_pl_dict['Identifier'] + '.cape')

