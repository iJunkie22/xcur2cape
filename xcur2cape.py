from __future__ import print_function
import argparse
import base64
import collections
import glob
import math
import os
import os.path
import plistlib
import re
import struct
import subprocess
import sys
import time

try:
    # noinspection PyUnresolvedReferences
    from typing import Dict, List, Union
except ImportError:
    pass

import xcurnames

XCUR2PNG_EXECUTABLE = os.path.expanduser('~/Build/xcur2png/xcur2png')
DO_TEXTMATE_FIX = True


class FrameOverFlowHandler(object):
    MAX_FRAME_COUNT = 24

    @classmethod
    def use(cls, frame_list, choice=2):
        choices = (cls.truncate, cls.rtruncate, cls.smart_step)
        return choices[choice](frame_list)

    @classmethod
    def calc_oflw(cls, frame_list):
        """
        :type frame_list: list
        """
        assert isinstance(frame_list, list)
        return len(frame_list) - cls.MAX_FRAME_COUNT

    @classmethod
    def truncate(cls, frame_list):
        """
        :type frame_list: list
        """
        assert isinstance(frame_list, list)
        frame_list = frame_list[:cls.MAX_FRAME_COUNT]
        return frame_list

    @classmethod
    def rtruncate(cls, frame_list):
        """
        :type frame_list: list
        """
        assert isinstance(frame_list, list)
        o = cls.calc_oflw(frame_list)
        frame_list = frame_list[o:]
        return frame_list

    @classmethod
    def smart_step(cls, frame_list):    # see frametests.py for tests of this
        """
        :type frame_list: list
        """
        assert isinstance(frame_list, list)
        o = cls.calc_oflw(frame_list)
        if o > 0:
            k = math.ceil((float((o % cls.MAX_FRAME_COUNT) + len(frame_list)) / float(cls.MAX_FRAME_COUNT)))
            frame_list = frame_list[0::int(k)]

        return frame_list


class CapeObject(object):
    def __init__(self):
        self.author = os.getenv("LOGNAME")
        self.capename = "Untitled"
        self._version = 2.0
        self.cape_version = 1.0
        self.isRetina = False
        self.tstamp = time.time()
        self.cursors = {}  # type: Dict[str,CapeCursor]

    def export_dict(self):
        d1 = {'Author': self.author,
              'CapeName': self.capename,
              'Cloud': False,
              'CapeVersion': self.cape_version,
              'Version': self._version,
              'HiDPI': self.isRetina,
              'MinimumVersion': self._version,
              'Identifier': "local.{}.{}.{}".format(self.author, self.capename, str(self.tstamp)),
              'Cursors': {k: v.export_dict() for k, v in self.cursors.items()}
              }
        return d1

    def add_cursor(self, cc):
        """
        :type cc: CapeCursor
        """
        assert isinstance(cc, CapeCursor)
        self.cursors[xcurnames.cursor_name_map[cc.mc_namekey]] = cc

    @classmethod
    def from_theme(cls, xct):
        """
        :type xct: XCursorTheme
        """
        assert isinstance(xct, XCursorTheme)
        new_co = cls()
        new_co.capename = xct.theme_name
        for xcs in xct.cursors:
            for cc in CapeCursor.from_xcursor_set(xcs):
                new_co.add_cursor(cc)
        return new_co

    def matches_other_cape(self, candidate_cape_fp):
        """
        Tests whether this cape is the same as another (aside from Identifier).

        :param str candidate_cape_fp: path to other cape file
        :rtype: bool
        """
        print("Testing if \"{}\" matches...".format(candidate_cape_fp))
        with open(candidate_cape_fp, 'rb') as candidate_cape_fd:
            other_dict = plistlib.load(candidate_cape_fd)

        # for other_cursor_name in other_dict.get('Cursors', {}).keys():
        #     patched_reps = list(plistlib.Data(x) for x in
        #                         other_dict['Cursors'][other_cursor_name].get('Representations', []))
        #     other_dict['Cursors'][other_cursor_name].update({'Representations': patched_reps})
        my_dict = self.export_dict()
        for my_cursor in my_dict['Cursors'].values():
            my_cursor.update({'Representations': list(x.data for x in my_cursor['Representations'])})

        for k in my_dict.keys():
            if k == 'Identifier':
                continue  # Do NOT expect Identifier to match
            if my_dict[k] != other_dict.get(k):
                a = my_dict[k]
                b = other_dict.get(k)
                if k == 'Cursors':
                    for a_k in a.keys():
                        c = a[a_k]
                        d = b.get(a_k, {'Representations': []})
                        if c != d:
                            for c_k in c.keys():
                                if c[c_k] != d.get(c_k):

                                    print("Cursor {} mismatched at {}".format(a_k, c_k))
                                    if c_k == 'Representations':
                                        print(hash(c[c_k][0]), hash(d[c_k][0]))
                                    print(repr(c[c_k])[-30:])
                                    print(repr(d.get(c_k))[-30:])
                            return False
                else:
                    print("{} mismatched".format(k))
                    print(repr(a)[:100])
                    print(repr(b)[:100])
                    return False

        return True


class CapeCursor(object):
    def __init__(self):
        self.mc_namekey = ""
        self.frame_count = 1
        self.frame_duration = 1.0
        self.hot_spot_x = 0.0
        self.hot_spot_y = 0.0
        self.height = 32.0
        self.width = 32.0
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

    def __eq__(self, other):
        if isinstance(other, CapeCursor):
            return self.export_dict() == other.export_dict()
        else:
            raise NotImplementedError

    def export_dict(self):
        d2 = {'FrameCount': self.frame_count,
              'FrameDuration': 1.000 / float(self.frame_count),
              'HotSpotX': self.hot_spot_x,
              'HotSpotY': self.hot_spot_y,
              'PointsHigh': self.height,
              'PointsWide': self.width,
              'Representations': list(plistlib.Data.fromBase64(x) for x in self.images)
              }
        return d2

    @classmethod
    def from_exported_dict(cls, exported_dict):
        new_cc = cls()
        new_cc.frame_count = exported_dict['FrameCount']
        new_cc.frame_duration = 1.000 / float(exported_dict['FrameCount'])
        new_cc.hot_spot_x = exported_dict['HotSpotX']
        new_cc.hot_spot_y = exported_dict['HotSpotY']
        new_cc.height = exported_dict['PointsHigh']
        new_cc.width = exported_dict['PointsWide']
        new_cc.images = list(plistlib.Data.asBase64(x) for x in exported_dict['Representations'])
        return new_cc

    def apply_textmate_fix(self):
        if DO_TEXTMATE_FIX and self.mc_namekey == 'IBeam':
            convert_path = subprocess.check_output(["/usr/bin/which", "convert"]).strip()
            p3 = subprocess.Popen([convert_path, "-", "-fuzz", "1%", "-trim", "+repage", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            p4 = subprocess.Popen([convert_path, "-", "-gravity", "center", "-background", "transparent",
                                   "-extent", "16x24", "-"],
                                  stdin=p3.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p3.communicate(base64.b64decode(self.images[0]))
            stdout, stderr = p4.communicate()
            # TODO: make it 16 x 24
            self.images[0] = base64.b64encode(stdout)
            self.width = 16
            self.height = 24
            self.hot_spot_x = 6
            self.hot_spot_y = 10

    @classmethod
    def from_xcursor_set(cls, xcs, chosen_size=32):
        """
        :type xcs: XCursorSet
        :type chosen_size: int
        :return:
        """
        assert isinstance(xcs, XCursorSet)
        assert isinstance(chosen_size, int)
        for line in [table_line for table_line in xcurnames.name_table if table_line[2] == xcs.xc_name]:
            new_cc = cls()
            for xc in xcs.xcursors:  # type: XCursor
                assert isinstance(xc, XCursor)
                if xc.img_size == chosen_size:
                    new_cc.images.append(xc.img_data)
                    new_cc.hot_spot_x = float(xc.hs_x)
                    new_cc.hot_spot_y = float(xc.hs_y)
                    new_cc.height = float(xc.img_size)
                    new_cc.width = float(xc.img_size)
                    new_cc.frame_count = xc.frame_count
            new_cc.mc_namekey = line[1]
            new_cc.apply_textmate_fix()
            yield new_cc


class XCursorTheme(object):
    def __init__(self):
        self.cursors = []  # type: List[XCursorSet]
        self.theme_name = "Untitled"

    @staticmethod
    def test_if_theme_directory(candidate_theme_fp):
        if not os.path.isdir(candidate_theme_fp):
            return False
        if not os.path.exists(os.path.join(candidate_theme_fp, 'index.theme')):
            return False
        if not os.path.isdir(os.path.join(candidate_theme_fp, 'cursors')):
            return False
        return True

    @classmethod
    def unpack_theme(cls, theme_fp, xcur2png_exe_fp=XCUR2PNG_EXECUTABLE, dump=True):
        xct = cls()
        with open(os.path.join(theme_fp, 'index.theme'), 'r') as index_fd:
            for line in index_fd:
                p1, p2, p3 = line.partition("=")
                if p1.startswith("Name"):
                    xct.theme_name = p3.strip().rstrip()
        for xcur_bn in set([x[2] for x in xcurnames.name_table if x[2] != xcurnames.nXCUR]):
            xct.cursors.append(XCursorSet.from_xcur_file(os.path.join(theme_fp, 'cursors', xcur_bn),
                                                         xcur2png_exe_fp, dump=dump))
        return xct


class XCursorSet(object):

    def __init__(self):
        self.conf_fp = ""
        self.conf_file_str = ""
        self.xcursors = []  # type: List[XCursor]
        self.xc_name = ""

    @property
    def is_known_xc(self):
        return self.xc_name in [x[2] for x in xcurnames.name_table]

    def unpack_from_conf(self):
        conf_line_groups = collections.defaultdict(list)

        for line in self.conf_file_str.splitlines():
            xcur_line_match = XCursor.Conf_file_line_pat.match(line)
            if xcur_line_match:
                conf_line_groups[xcur_line_match.group("imgSize")].append(line)

        for k, v in conf_line_groups.items():
            if len(v) == 1:   # there is only one frame to show
                self.xcursors.append(XCursor.from_conf_file_line(self.conf_fp, v[0]))
            else:                               # there is more than one frame to show
                safe_size_list = FrameOverFlowHandler.smart_step(v)  # enforce 24 frame limit
                self.xcursors.append(XCursor.animated_from_conf_file_lines(self.conf_fp, safe_size_list))

    @classmethod
    def from_conf_file(cls, conf_fp):
        new_xcs = cls()
        new_xcs.conf_fp = conf_fp
        new_xcs.xc_name = os.path.basename(conf_fp).rpartition(".")[0]
        with open(new_xcs.conf_fp, 'r') as conf_fd:
            new_xcs.conf_file_str = conf_fd.read()

        new_xcs.unpack_from_conf()
        return new_xcs

    @classmethod
    def from_xcur_file(cls, xcur_fp, xcur2png_exe_fp=XCUR2PNG_EXECUTABLE, dump=True):
        ripped_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(xcur_fp)), 'ripped/'))
        conf_fp = "{}.conf".format(xcur_fp)
        if not os.path.isdir(ripped_dir):
            os.mkdir(ripped_dir)
        if dump:
            subprocess.check_call([xcur2png_exe_fp, '-d', ripped_dir, '-c', conf_fp, xcur_fp], stdout=subprocess.PIPE)
        return cls.from_conf_file(conf_fp)


class XCursorConfLine(object):
    Conf_file_line_pat = re.compile(r"((?P<imgSize>\d+)\t(?P<hsX>\d+)\t(?P<hsY>\d+)\t(?P<fpRaw>[^\t]+))")

    def __init__(self, match_object):
        self._match_dict = match_object.groupdict()

    @property
    def img_size(self):
        return int(self._match_dict["imgSize"])

    @property
    def hs_x(self):
        return int(self._match_dict["hsX"])

    @property
    def hs_y(self):
        return int(self._match_dict["hsY"])

    @property
    def fp_raw(self):
        return self._match_dict["fpRaw"]

    def fp(self, parent_directory_path):
        if os.path.isabs(self.fp_raw):
            return self.fp_raw
        else:
            return os.path.normpath(os.path.join(parent_directory_path, self.fp_raw))

    @classmethod
    def from_string(cls, conf_line_str):
        return cls(cls.Conf_file_line_pat.match(conf_line_str))


class XCursor(object):
    Conf_file_line_pat = re.compile(r"((?P<imgSize>\d+)\t(?P<hsX>\d+)\t(?P<hsY>\d+)\t(?P<fpRaw>[^\t]+))")

    def __init__(self):
        self.img_size = 0
        self.hs_x = 0
        self.hs_y = 0
        self.fp = ""
        self.img_data = ""
        self.frame_count = 1

    def hotfixes(self, size_lie):
        def tests(a, b):
            if (a > b) or ((a / b) == (15.0 / 16.0)):
                return b / 2.0
            else:
                return a

        error_scale = self.img_size / float(size_lie)
        self.hs_x *= error_scale
        self.hs_y *= error_scale
        self.hs_x = tests(self.hs_x, self.img_size)
        self.hs_y = tests(self.hs_y, self.img_size)

    @classmethod
    def from_conf_file_line(cls, conf_fp, conf_line_str):
        new_xc = cls()
        assert isinstance(conf_line_str, str)

        conf_line_match = XCursorConfLine.from_string(conf_line_str)
        new_xc.img_size = conf_line_match.img_size
        new_xc.hs_x = conf_line_match.hs_x
        new_xc.hs_y = conf_line_match.hs_y
        new_xc.fp = conf_line_match.fp(conf_fp)

        with open(new_xc.fp, 'rb') as xcur_fd:
            new_xc.img_data = base64.b64encode(xcur_fd.read())
        z = base64.b64decode(new_xc.img_data)[16:][:8]
        x1, y1 = struct.unpack('>ii', z)
        new_xc.img_size = x1
        new_xc.hotfixes(conf_line_match.img_size)
        return new_xc

    @classmethod
    def animated_from_conf_file_lines(cls, conf_fp, conf_lines_list):
        new_xc = cls()
        assert isinstance(conf_lines_list, list)
        conf_img_size, conf_hs_x, conf_hs_y, sample_fp, trash = str(conf_lines_list[0]).split()
        del trash
        if not os.path.isabs(sample_fp):
            sample_fp = os.path.normpath(os.path.join(conf_fp, sample_fp))
        with open(sample_fp, 'rb') as sample_fd:
            sample_img_header = sample_fd.read()[16:][:8]

        sample_x1, sample_y1 = struct.unpack('>ii', sample_img_header)
        sample_img_size = sample_x1
        frame_fns = [conf_line.split()[3] for conf_line in conf_lines_list]
        frame_fns = map(lambda x: x if os.path.isabs(x) else os.path.normpath(os.path.join(conf_fp, x)), frame_fns)

        # frame_fns_str = ' '.join(map("\'{}\'".format, frame_fns))
        montage_path = subprocess.check_output(["/usr/bin/which", "montage"]).strip()
        ripped_dir = os.path.abspath(os.path.dirname(sample_fp))
        export_fp = os.path.join(ripped_dir, 'JOINED_' + os.path.basename(sample_fp))
        args = [montage_path]
        args.extend(frame_fns)
        args.extend(["-tile", "1x", "-background", "transparent", "-geometry",
                     "{0}x{0}+0+0>".format(sample_img_size), export_fp])
        # print(args)
        subprocess.check_call(args, stdout=subprocess.PIPE)

        new_xc.fp = export_fp
        with open(export_fp, 'rb') as export_fd:
            new_xc.img_data = base64.b64encode(export_fd.read())

        new_xc.hs_x = float(conf_hs_x)
        new_xc.hs_y = float(conf_hs_y)
        new_xc.img_size = sample_x1
        new_xc.hotfixes(conf_img_size)

        new_xc.frame_count = len(conf_lines_list)

        return new_xc


def run_tool(theme_fp, dump=True):
    theme_fp = os.path.abspath(os.path.expanduser(os.path.expandvars(theme_fp)))
    if not XCursorTheme.test_if_theme_directory(theme_fp):
        raise ValueError("\"{}\" does not contain a cursor theme".format(theme_fp))

    test_xct1 = XCursorTheme.unpack_theme(theme_fp, dump=dump)
    print(test_xct1.theme_name)
    print(len(test_xct1.cursors))
    test_co1 = CapeObject.from_theme(test_xct1)
    test_pl_dict = test_co1.export_dict()
    cape_dir = os.path.join(theme_fp, 'capes')
    if not os.path.isdir(cape_dir):
        os.mkdir(cape_dir)

    sibling_glob_name = "local.{}.{}.*.cape".format(test_co1.author, test_co1.capename)
    for candidate_sibling_cape_fp in glob.iglob(os.path.join(cape_dir, sibling_glob_name)):
        if test_co1.matches_other_cape(candidate_sibling_cape_fp):
            print("Skipping saving a duplicate of \"{}\"".format(candidate_sibling_cape_fp))
            return False
    out_cape_fp = os.path.join(cape_dir, test_pl_dict['Identifier'] + '.cape')
    plistlib.writePlist(test_pl_dict, out_cape_fp)
    print("Saved new cape \"{}\" to \"{}\"".format(test_xct1.theme_name, out_cape_fp))


if __name__ == '__main__':
    parser = argparse.ArgumentParser("xcur2cape")
    parser.add_argument(dest="xcur_theme_fp",
                        help="Path to the XCursor theme you want to convert (should contain an index.theme file).")
    args = parser.parse_args()
    run_tool(args.xcur_theme_fp)

# run_tool(os.path.expanduser('~/Downloads/Breeze-Obsidian/'))
# run_tool(os.path.expanduser('~/Downloads/Breeze-Snow/'))
# run_tool(os.path.expanduser('~/Downloads/Breeze-Hacked/'))
# run_tool(os.path.expanduser('~/Downloads/Breeze-Hacked-green/'), False)
# run_tool(os.path.expanduser('~/Downloads/Breeze-Hacked-red/'), True)
# run_tool(os.path.expanduser('~/Downloads/Breeze/'))
# run_tool( os.path.expanduser('~/Developer/Themes/capitaine-cursors/bin/xcursor/'))

