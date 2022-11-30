# -*- coding: utf-8 -*-
#
#   ChineseUtilities
#
#   Craig Farrow
#   May 2011
#
#
#

from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

import codecs
import re

import os, sys

class SortStringDB(dict):
    FNAME = 'ch2sort.txt'
    def __init__(self):
        dict.__init__(self)
        self.loaded = False

    def __load(self):
        if self.loaded: return
        self.loaded = True              # Set True even if fail to load file
        # This stack-frame code is all that I've found to work from
        # Idle, command-line AND Python.NET
        # (Use of __file__ failed for Idle)
        mypath = os.path.dirname(sys._getframe().f_code.co_filename)
        fname = os.path.join(mypath, self.FNAME)
        print(fname)
        try:
            f = codecs.open(fname, encoding="gb18030")
        except IOError:
            return

        for line in f.readlines():
            line = line.strip("\n\r")
            parts = line.split("\t")
            if len(parts) == 2:
                self[parts[0]] = parts[1]
            else:
                ambiguities = {}
                hz = parts.pop(0)
                while (parts):
                    py = parts.pop(0)
                    sortKey = parts.pop(0)
                    ambiguities[py] = sortKey
                self[hz] = ambiguities

        f.close()

    def Lookup(self, hz, py):
        self.__load()
        try:
            sortInfo = self[hz]
        except KeyError:
            return "[HZ not in DB: %s]" % repr(hz)
        if type(sortInfo) == str:
            if sortInfo.startswith(py):
                return "(" + sortInfo + ")"
            else:
                return "[PY mismatch]"
        else:
            try:
                match = sortInfo[py]
                return "(" + match + ")"
            except KeyError:
                return "[PY invalid]"
        
Sorter = SortStringDB()
    
def PinyinTonenumSplit(pinyin):
    pinyin = re.sub(" ", "", pinyin)
    return re.findall("[^1-5]*[1-5]", pinyin)

def ChineseSortString(hz, py):
    global Sorter
    if not hz or not py:
        return ""
    hzList = [x for x in hz]
    pyList = PinyinTonenumSplit(py)
    if len(hzList) != len(pyList):
        return "[PY different length]"

    return ";".join([Sorter.Lookup(h,p) for h, p in zip(hzList, pyList)])


if __name__ == "__main__":
    if sys.stdout.encoding == None:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

    testSet = [
               ("路", "lu4"),
               ("你好", "ni3hao3"),
               ("中国", "zhong1 guo2"),
               ("录音", "lu4yin1"),
               ("录", ""),
               ("孩子", "hai2zi5"),
               ]

    for t in testSet:
        print(t[0], t[1], ChineseSortString(t[0], t[1]))
    



